"""Tests for training season detection."""

import contextlib
import datetime
import io
import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

import jsonschema

from scripts.detect_seasons import format_output, main
from src.one_rep_max import brzycki_1rm, percentage_of_1rm
from src.seasons import (
    SeasonConfig,
    TrainingSession,
    TrainingSet,
    analyse_seasons,
    detect_seasons,
    exercise_intensities,
    format_report,
    rest_days,
    session_from_set_centric,
    sessions_from_directory,
    validate_report_dict,
)


def d(value: str) -> datetime.date:
    """Shorthand for building dates in tests."""
    return datetime.date.fromisoformat(value)


class TestSeasonConfig(unittest.TestCase):
    """Test configuration loading and validation."""

    def test_defaults(self) -> None:
        config = SeasonConfig()
        self.assertEqual(config.min_break_days, 21)
        self.assertEqual(config.min_sessions, 1)
        self.assertEqual(config.max_reps_for_1rm, 10)

    def test_load_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "seasons.yaml"
            path.write_text("min_break_days: 10\nmin_sessions: 3\n")
            config = SeasonConfig.load(path)
        self.assertEqual(config, SeasonConfig(min_break_days=10, min_sessions=3))

    def test_empty_yaml_uses_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "seasons.yaml"
            path.write_text("")
            self.assertEqual(SeasonConfig.load(path), SeasonConfig())

    def test_repository_config_is_valid(self) -> None:
        config = SeasonConfig.load(Path("config/seasons.yaml"))
        self.assertGreaterEqual(config.min_break_days, 1)

    def test_rejects_invalid_values(self) -> None:
        with self.assertRaises(ValueError):
            SeasonConfig(min_break_days=0)
        with self.assertRaises(ValueError):
            SeasonConfig(min_sessions=0)
        with self.assertRaises(ValueError):
            SeasonConfig.from_dict({"min_break_days": "two weeks"})
        with self.assertRaises(ValueError):
            SeasonConfig.from_dict({"min_break": 14})
        with self.assertRaises(ValueError):
            SeasonConfig(max_reps_for_1rm=37)


class TestDetectSeasons(unittest.TestCase):
    """Test the season splitting logic."""

    def test_rest_days(self) -> None:
        self.assertEqual(rest_days(d("2023-01-01"), d("2023-01-02")), 0)
        self.assertEqual(rest_days(d("2023-01-01"), d("2023-01-15")), 13)
        self.assertEqual(rest_days(d("2023-01-01"), d("2023-01-01")), 0)

    def test_no_dates(self) -> None:
        report = detect_seasons([], SeasonConfig())
        self.assertEqual(report.seasons, ())
        self.assertEqual(report.ignored, ())

    def test_single_season(self) -> None:
        dates = [d("2023-01-01"), d("2023-01-05"), d("2023-01-10")]
        report = detect_seasons(dates, SeasonConfig(min_break_days=14))
        self.assertEqual(len(report.seasons), 1)
        season = report.seasons[0]
        self.assertEqual(season.start, d("2023-01-01"))
        self.assertEqual(season.end, d("2023-01-10"))
        self.assertEqual(season.session_count, 3)
        self.assertEqual(season.duration_days, 10)
        self.assertEqual(season.longest_break_days, 4)
        self.assertIsNone(season.break_before_days)

    def test_break_threshold_is_inclusive(self) -> None:
        # 2023-01-01 -> 2023-01-16: 14 days without training in between
        config = SeasonConfig(min_break_days=14)
        report = detect_seasons([d("2023-01-01"), d("2023-01-16")], config)
        self.assertEqual(len(report.seasons), 2)
        self.assertEqual(report.seasons[1].break_before_days, 14)

        # 13 days without training: same season
        report = detect_seasons([d("2023-01-01"), d("2023-01-15")], config)
        self.assertEqual(len(report.seasons), 1)

    def test_unsorted_and_duplicate_dates(self) -> None:
        dates = [d("2023-03-01"), d("2023-01-01"), d("2023-01-01"), d("2023-01-03")]
        report = detect_seasons(dates, SeasonConfig(min_break_days=7))
        self.assertEqual([s.start for s in report.seasons], [d("2023-01-01"), d("2023-03-01")])
        self.assertEqual(report.seasons[0].session_count, 2)

    def test_min_sessions_ignores_short_seasons(self) -> None:
        dates = [d("2023-01-01"), d("2023-03-01"), d("2023-03-02")]
        report = detect_seasons(dates, SeasonConfig(min_break_days=7, min_sessions=2))
        self.assertEqual(len(report.seasons), 1)
        self.assertEqual(report.seasons[0].start, d("2023-03-01"))
        self.assertEqual(len(report.ignored), 1)
        self.assertEqual(report.ignored[0].start, d("2023-01-01"))


class TestOneRepMax(unittest.TestCase):
    """Test the Brzycki 1RM formula and %1RM."""

    def test_single_rep_is_the_weight(self) -> None:
        self.assertAlmostEqual(brzycki_1rm(100, 1), 100.0)

    def test_brzycki(self) -> None:
        # 60 kg x 10 -> 60 * 36 / 27 = 80 kg
        self.assertAlmostEqual(brzycki_1rm(60, 10), 80.0)

    def test_invalid_repetitions(self) -> None:
        with self.assertRaises(ValueError):
            brzycki_1rm(60, 0)
        with self.assertRaises(ValueError):
            brzycki_1rm(60, 37)

    def test_percentage(self) -> None:
        # 1RM of 100 kg, training with 50 kg -> 50%
        self.assertAlmostEqual(percentage_of_1rm(50, 100), 50.0)
        with self.assertRaises(ValueError):
            percentage_of_1rm(50, 0)


def session(date: str, *sets: tuple[str, int, float]) -> TrainingSession:
    """Build a session from (exercise, repetitions, weight) tuples in kg."""
    return TrainingSession(d(date), tuple(TrainingSet(e, r, w, "kg") for e, r, w in sets))


class TestExerciseIntensities(unittest.TestCase):
    """Test the per-season 1RM and %1RM computation."""

    def test_percentage_of_season_1rm(self) -> None:
        sessions = [
            session("2023-01-01", ("Squat", 1, 100), ("Squat", 5, 50)),
            session("2023-01-03", ("Squat", 10, 50)),
        ]
        (squat,) = exercise_intensities(sessions, d("2023-01-01"), d("2023-01-31"))
        self.assertEqual(squat.exercise, "Squat")
        self.assertAlmostEqual(squat.one_rep_max, 100.0)
        self.assertEqual(squat.best_set.date, d("2023-01-01"))
        self.assertEqual([s.percentage_1rm for s in squat.sets], [100.0, 50.0, 50.0])
        self.assertAlmostEqual(squat.average_percentage_1rm, 200 / 3)

    def test_high_rep_sets_do_not_drive_the_estimate(self) -> None:
        # 40 x 25 would give 120 kg; 60 x 10 gives 80 kg
        sessions = [session("2023-01-01", ("Bench", 25, 40), ("Bench", 10, 60))]
        (bench,) = exercise_intensities(sessions, d("2023-01-01"), d("2023-01-01"), 10)
        self.assertAlmostEqual(bench.one_rep_max, 80.0)
        self.assertAlmostEqual(bench.sets[0].percentage_1rm, 50.0)

    def test_fallback_to_high_rep_sets(self) -> None:
        sessions = [session("2023-01-01", ("Row", 15, 60), ("Row", 40, 20))]
        (row,) = exercise_intensities(sessions, d("2023-01-01"), d("2023-01-01"), 10)
        self.assertAlmostEqual(row.one_rep_max, 60 * 36 / 22)
        self.assertEqual(len(row.sets), 2)

    def test_skips_unloaded_exercises_and_other_periods(self) -> None:
        sessions = [
            session("2023-01-01", ("Pull-up", 10, 0)),
            session("2023-06-01", ("Squat", 5, 100)),
        ]
        self.assertEqual(exercise_intensities(sessions, d("2023-01-01"), d("2023-01-31")), ())

    def test_1rm_is_computed_per_season(self) -> None:
        sessions = [
            session("2023-01-01", ("Squat", 1, 100), ("Squat", 1, 50)),
            session("2023-06-01", ("Squat", 1, 80), ("Squat", 1, 40)),
        ]
        report = analyse_seasons(sessions, SeasonConfig(min_break_days=21))
        self.assertEqual(len(report.seasons), 2)
        first, second = (season.exercises[0] for season in report.seasons)
        self.assertAlmostEqual(first.one_rep_max, 100.0)
        self.assertAlmostEqual(second.one_rep_max, 80.0)
        self.assertEqual([s.percentage_1rm for s in second.sets], [100.0, 50.0])


class TestSeasonReportSchema(unittest.TestCase):
    """Test validation of a season report dict against its JSON schema."""

    def test_real_report_validates(self) -> None:
        sessions = [
            session("2023-01-01", ("Squat", 1, 100), ("Squat", 5, 50)),
            session("2023-01-05", ("Squat", 10, 50)),
            session("2023-03-01"),
        ]
        report = analyse_seasons(sessions, SeasonConfig(min_break_days=7))
        validate_report_dict(report.to_dict())  # must not raise

    def test_empty_report_validates(self) -> None:
        report = analyse_seasons([], SeasonConfig())
        validate_report_dict(report.to_dict())  # must not raise

    def test_missing_required_key_is_rejected(self) -> None:
        data = {"config": {"min_break_days": 21, "min_sessions": 1, "max_reps_for_1rm": 10}, "seasons": []}
        with self.assertRaises(jsonschema.exceptions.ValidationError):
            validate_report_dict(data)

    def test_wrong_type_is_rejected(self) -> None:
        data = {
            "config": {"min_break_days": 21, "min_sessions": 1, "max_reps_for_1rm": 10},
            "seasons": [
                {
                    "start": "2023-01-01",
                    "end": "2023-01-01",
                    "sessions": "one",
                    "duration_days": 1,
                    "longest_break_days": 0,
                    "break_before_days": None,
                    "exercises": [],
                }
            ],
            "ignored": [],
        }
        with self.assertRaises(jsonschema.exceptions.ValidationError):
            validate_report_dict(data)

    def test_unknown_property_is_rejected(self) -> None:
        data = {
            "config": {"min_break_days": 21, "min_sessions": 1, "max_reps_for_1rm": 10},
            "seasons": [],
            "ignored": [],
            "unexpected": True,
        }
        with self.assertRaises(jsonschema.exceptions.ValidationError):
            validate_report_dict(data)


def set_centric(date: str, *exercises: tuple[str, list[tuple[int, float]]]) -> dict[str, Any]:
    """Build an enveloped set-centric workout from (name, [(repetitions, kg), ...])."""
    return {
        "type": "set-centric.v1",
        "schema": "http://com.trainingparser/set-centric_v1.schema.json",
        "payload": {
            "workout_id": f"w_{date}",
            "type": "set-centric",
            "date": f"{date}T18:00:00Z",
            "exercises": [
                {
                    "name": name,
                    "sets": [
                        {"setNumber": n, "repetitions": reps, "weight": {"amount": kg, "unit": "kg"}}
                        for n, (reps, kg) in enumerate(sets, start=1)
                    ],
                }
                for name, sets in exercises
            ],
        },
    }


def write_workouts(directory: Path, workouts: dict[str, Any]) -> None:
    """Write each workout as a JSON file (relative path -> content)."""
    for name, content in workouts.items():
        path = directory / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(content))


class TestSetCentricInput(unittest.TestCase):
    """Test reading sessions from set-centric JSON files."""

    def test_enveloped_workout(self) -> None:
        workout = set_centric("2023-04-14", ("Deadlift", [(6, 80), (6, 80)]))
        result = session_from_set_centric(workout)
        self.assertEqual(result.date, d("2023-04-14"))
        self.assertEqual(result.sets, (TrainingSet("Deadlift", 6, 80.0, "kg"),) * 2)

    def test_bare_workout(self) -> None:
        workout = set_centric("2023-04-14", ("Squat", [(5, 100)]))["payload"]
        self.assertEqual(
            session_from_set_centric(workout).sets, (TrainingSet("Squat", 5, 100.0, "kg"),)
        )

    def test_repository_example(self) -> None:
        data = json.loads(Path("data/set-centric-example.json").read_text())
        result = session_from_set_centric(data)
        self.assertEqual(result.date, d("2026-01-23"))
        self.assertIn(TrainingSet("Bench Press", 8, 65.0, "kg"), result.sets)

    def test_rejects_other_formats(self) -> None:
        with self.assertRaises(ValueError):
            session_from_set_centric({"type": "bench-centric.v1", "payload": {"date": "2023-01-01"}})
        with self.assertRaises(ValueError):
            session_from_set_centric({"type": "bench-centric", "date": "2023-01-01"})
        with self.assertRaises(ValueError):
            session_from_set_centric({"type": "set-centric", "exercises": []})
        with self.assertRaises(ValueError):
            session_from_set_centric(
                {"type": "set-centric", "date": "2023-01-01", "exercises": [{"name": "Squat"}]}
            )

    def test_directory_with_several_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            write_workouts(Path(tmp), {
                "2023-04-19.json": set_centric("2023-04-19", ("Squat", [(10, 40)])),
                "2023/2023-04-14.json": set_centric("2023-04-14", ("Deadlift", [(6, 80)])),
                "notes.md": "not a workout",
                "list.json": [set_centric("2023-05-01", ("Squat", [(5, 90)]))],
            })
            sessions = sessions_from_directory(Path(tmp))
        self.assertEqual(
            sorted(s.date for s in sessions), [d("2023-04-14"), d("2023-04-19"), d("2023-05-01")]
        )

    def test_directory_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                sessions_from_directory(Path(tmp))
            with self.assertRaises(NotADirectoryError):
                sessions_from_directory(Path(tmp) / "missing")


class TestCli(unittest.TestCase):
    """Test the detect_seasons command line tool."""

    def test_directory_json_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workouts = Path(tmp) / "workouts"
            write_workouts(workouts, {
                "a.json": set_centric("2023-01-01", ("Deadlift", [(10, 60)])),
                "b.json": set_centric("2023-01-05", ("Deadlift", [(2, 120), (10, 60)])),
                "c.json": set_centric("2023-03-01", ("Deadlift", [(1, 100), (5, 50)])),
            })
            config = Path(tmp) / "seasons.yaml"
            config.write_text("min_break_days: 21\n")
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                code = main([str(workouts), "--config", str(config), "--format", "json"])
        result = json.loads(buffer.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(result["config"]["min_break_days"], 21)
        self.assertEqual(
            [(s["start"], s["end"]) for s in result["seasons"]],
            [("2023-01-01", "2023-01-05"), ("2023-03-01", "2023-03-01")],
        )
        first, second = (s["exercises"][0] for s in result["seasons"])
        # Best set: 120 kg x 2 -> 120 * 36 / 35
        self.assertAlmostEqual(first["one_rep_max"], 123.4)
        self.assertEqual(first["best_set"]["weight"], 120)
        self.assertAlmostEqual(second["one_rep_max"], 100.0)
        self.assertEqual([s["percentage_1rm"] for s in second["sets"]], [100.0, 50.0])
        validate_report_dict(result)

    def test_directory_text_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workouts = Path(tmp) / "workouts"
            write_workouts(workouts, {
                "a.json": set_centric("2023-01-01", ("Squat", [(1, 100), (5, 50)])),
                "b.json": set_centric("2023-03-01", ("Squat", [(5, 50)])),
            })
            config = Path(tmp) / "seasons.yaml"
            config.write_text("min_break_days: 7\n")
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                code = main([str(workouts), "--config", str(config), "--format", "text"])
        text = buffer.getvalue()

        self.assertEqual(code, 0)
        self.assertIn("TRAINING SEASONS", text)
        self.assertIn("Season 1: 2023-01-01 -> 2023-01-01", text)
        self.assertIn("Season 2: 2023-03-01 -> 2023-03-01", text)
        self.assertIn("Squat: 1RM=100.0kg", text)

    def test_missing_input(self) -> None:
        self.assertEqual(main(["does-not-exist"]), 1)

    def test_file_instead_of_directory(self) -> None:
        self.assertEqual(main(["data/set-centric-example.json"]), 1)

    def test_format_report(self) -> None:
        sessions = [
            session("2023-01-01", ("Squat", 1, 100), ("Squat", 5, 50), ("Squat", 5, 50)),
            session("2023-03-01"),
        ]
        text = format_report(analyse_seasons(sessions, SeasonConfig(min_break_days=7)))
        self.assertIn("Season 1: 2023-01-01 -> 2023-01-01", text)
        self.assertIn("58 days without training", text)
        self.assertIn("Season 2: 2023-03-01 -> 2023-03-01", text)
        self.assertIn("Squat: 1RM=100.0kg", text)
        self.assertIn("2023-01-01: 1x1x100kg 100%, 2x5x50kg 50%", text)

    def test_format_output_dispatches_by_format(self) -> None:
        sessions = [session("2023-01-01", ("Squat", 1, 100))]
        report = analyse_seasons(sessions, SeasonConfig(min_break_days=7))
        data = report.to_dict()

        json_text = format_output(report, data, "json")
        self.assertEqual(json.loads(json_text), data)

        plain_text = format_output(report, data, "text")
        self.assertEqual(plain_text, format_report(report))
