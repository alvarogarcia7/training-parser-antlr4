"""End-to-end tests for bulk training file parser pipeline."""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Any, cast


class TestBulkParserPipeline(unittest.TestCase):
    """Test the bulk parser script and JSON database pipeline."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_dir = Path(self.temp_dir.name) / "parsed"
        self.script_path = Path("bin/parse_bulk.sh")

        # Sample training data
        self.training_sample_1 = """2025-01-01
Bench press 75k: 4, 5x3
Squat 70k: 5x10
"""

        self.training_sample_2 = """2025-01-02
Overhead press: 5x5x40k
Deadlift 60k: 20, 15,8,8
"""

        self.training_sample_3 = """2025-01-03
Row en maquina 41k: 15, 8
"""

    def tearDown(self) -> None:
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def create_training_file(self, content: str, filename: str) -> Path:
        """Create a temporary training file."""
        file_path = Path(self.temp_dir.name) / filename
        file_path.write_text(content)
        return file_path

    def run_bulk_parser(self, *files: Path) -> int:
        """Run the bulk parser script."""
        cmd = [
            "bash",
            str(self.script_path),
            "-o", str(self.output_dir),
            *[str(f) for f in files]
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode

    def produced_files(self) -> list[str]:
        """Every JSON file under the output directory, relative and sorted."""
        return sorted(p.relative_to(self.output_dir).as_posix() for p in self.output_dir.rglob("*.json"))

    def exercise_names(self, file_path: Path) -> list[str]:
        """Exercise names in a set-centric or bench-centric file."""
        data = self.assert_json_valid(file_path)
        return [e["name"] for e in data["exercises"]]

    def assert_json_valid(self, file_path: Path) -> dict[str, Any]:
        """Assert file is valid JSON and return parsed content."""
        self.assertTrue(file_path.exists(), f"File not found: {file_path}")
        try:
            with open(file_path) as f:
                return cast(dict[str, Any], json.load(f))
        except json.JSONDecodeError as e:
            self.fail(f"Invalid JSON in {file_path}: {e}")

    def assert_json_sorted(self, obj: Any) -> None:
        """Assert JSON object keys are sorted."""
        if isinstance(obj, dict):
            keys = list(obj.keys())
            sorted_keys = sorted(keys)
            self.assertEqual(
                keys, sorted_keys,
                f"Keys not sorted: {keys} != {sorted_keys}"
            )
            for value in obj.values():
                self.assert_json_sorted(value)
        elif isinstance(obj, list):
            for item in obj:
                self.assert_json_sorted(item)

    def test_single_file_parsing(self) -> None:
        """Test parsing a single training file."""
        file1 = self.create_training_file(
            self.training_sample_1,
            "workout_day1.txt"
        )

        returncode = self.run_bulk_parser(file1)
        self.assertEqual(returncode, 0, "Parser script should succeed")

        # Check output files exist
        set_file = self.output_dir / "set" / "workout_day1_set.json"
        bench_file = self.output_dir / "bench" / "workout_day1_bench.json"
        db_file = self.output_dir / "database.json"

        self.assertTrue(set_file.exists(), "Set-centric file should exist")
        self.assertTrue(bench_file.exists(), "Bench-centric file should exist")
        self.assertTrue(db_file.exists(), "Database file should exist")

    def test_multiple_files_parsing(self) -> None:
        """Test parsing multiple training files."""
        file1 = self.create_training_file(
            self.training_sample_1,
            "day1.txt"
        )
        file2 = self.create_training_file(
            self.training_sample_2,
            "day2.txt"
        )
        file3 = self.create_training_file(
            self.training_sample_3,
            "day3.txt"
        )

        returncode = self.run_bulk_parser(file1, file2, file3)
        self.assertEqual(returncode, 0, "Parser should process all files")

        # Check all output files exist
        for prefix in ["day1", "day2", "day3"]:
            set_file = self.output_dir / "set" / f"{prefix}_set.json"
            bench_file = self.output_dir / "bench" / f"{prefix}_bench.json"
            self.assertTrue(set_file.exists(), f"{prefix} set file missing")
            self.assertTrue(bench_file.exists(), f"{prefix} bench file missing")

    def test_set_centric_format(self) -> None:
        """Test that set-centric JSON has correct structure."""
        file1 = self.create_training_file(
            self.training_sample_1,
            "test.txt"
        )

        self.run_bulk_parser(file1)

        set_file = self.output_dir / "set" / "test_set.json"
        data = self.assert_json_valid(set_file)

        # Check required fields
        self.assertIn("type", data, "Should have type field")
        self.assertEqual(data["type"], "set-centric")
        self.assertIn("exercises", data, "Should have exercises")
        self.assertGreater(len(data["exercises"]), 0, "Should have parsed exercises")

        # Check exercise structure
        exercise = data["exercises"][0]
        self.assertIn("name", exercise)
        self.assertIn("sets", exercise)
        self.assertGreater(len(exercise["sets"]), 0)

        # Check set structure
        set_ = exercise["sets"][0]
        self.assertIn("setNumber", set_)
        self.assertIn("repetitions", set_)
        self.assertIn("weight", set_)
        self.assertIn("amount", set_["weight"])
        self.assertIn("unit", set_["weight"])

    def test_bench_centric_format(self) -> None:
        """Test that bench-centric JSON has correct structure."""
        file1 = self.create_training_file(
            self.training_sample_1,
            "test.txt"
        )

        self.run_bulk_parser(file1)

        bench_file = self.output_dir / "bench" / "test_bench.json"
        data = self.assert_json_valid(bench_file)

        # Check required fields
        self.assertIn("type", data, "Should have type field")
        self.assertEqual(data["type"], "bench-centric")
        self.assertGreater(len(data["exercises"]), 0)

        # Check exercise structure
        exercise = data["exercises"][0]
        self.assertIn("name", exercise)
        self.assertGreater(len(exercise["sets"]), 0)

        # Check set structure (weight and unit are flat in bench-centric)
        set_ = exercise["sets"][0]
        self.assertEqual(set_["reps"], 4)
        self.assertEqual(set_["weight"], 75)
        self.assertEqual(set_["unit"], "kg")

    def test_database_append(self) -> None:
        """Test that results are appended to database."""
        file1 = self.create_training_file(
            self.training_sample_1,
            "day1.txt"
        )
        file2 = self.create_training_file(
            self.training_sample_2,
            "day2.txt"
        )

        self.run_bulk_parser(file1)
        db_content_1 = self.assert_json_valid(self.output_dir / "database.json")
        count_1 = len(db_content_1.get("workouts", []))

        self.run_bulk_parser(file2)
        db_content_2 = self.assert_json_valid(self.output_dir / "database.json")
        count_2 = len(db_content_2.get("workouts", []))

        self.assertGreater(count_2, count_1, "Database should grow with new files")
        self.assertEqual(count_2, count_1 + 1, "Should add exactly one workout")

    def test_json_sorted(self) -> None:
        """Test that all JSON files are properly sorted."""
        file1 = self.create_training_file(
            self.training_sample_1,
            "test.txt"
        )

        self.run_bulk_parser(file1)

        # Check all JSON files are sorted
        for json_file in self.output_dir.rglob("*.json"):
            data = self.assert_json_valid(json_file)
            self.assert_json_sorted(data)

    def test_database_structure(self) -> None:
        """Test database structure and content."""
        file1 = self.create_training_file(
            self.training_sample_1,
            "day1.txt"
        )

        self.run_bulk_parser(file1)

        db_file = self.output_dir / "database.json"
        data = self.assert_json_valid(db_file)

        self.assertIn("workouts", data)
        self.assertIsInstance(data["workouts"], list)
        self.assertEqual(len(data["workouts"]), 1)

        workout = data["workouts"][0]
        self.assertIn("source_file", workout)
        self.assertIn("exercises", workout)
        self.assertGreater(len(workout["exercises"]), 0)

    def test_exercises_parsed_correctly(self) -> None:
        """Test that exercises are parsed with correct data."""
        file1 = self.create_training_file(
            self.training_sample_1,
            "test.txt"
        )

        self.run_bulk_parser(file1)

        set_file = self.output_dir / "set" / "test_set.json"
        data = self.assert_json_valid(set_file)
        exercises = data["exercises"]

        # Check exercises are present
        self.assertGreater(len(exercises), 0, "Should have parsed exercises")

        # Check bench press is present
        bench_press_exercises = [
            e for e in exercises if "bench" in e["name"].lower()
        ]
        self.assertGreater(len(bench_press_exercises), 0, "Should have bench press")

        # Check bench press has sets
        for exercise in bench_press_exercises:
            self.assertGreater(
                len(exercise["sets"]), 0,
                f"Exercise {exercise['name']} should have sets"
            )

        # Check squat is present
        squat_exercises = [
            e for e in exercises if "squat" in e["name"].lower()
        ]
        self.assertGreater(len(squat_exercises), 0, "Should have squat")

    def test_output_directory_creation(self) -> None:
        """Test that output directory is created if it doesn't exist."""
        file1 = self.create_training_file(
            self.training_sample_1,
            "test.txt"
        )

        self.assertFalse(self.output_dir.exists())
        self.run_bulk_parser(file1)
        self.assertTrue(self.output_dir.exists())

    def test_custom_database_file(self) -> None:
        """Test using a custom database file path."""
        file1 = self.create_training_file(
            self.training_sample_1,
            "test.txt"
        )
        custom_db = self.temp_dir.name + "/custom_db.json"

        cmd = [
            "bash", str(self.script_path),
            "-o", str(self.output_dir),
            "-d", custom_db,
            str(file1)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)

        self.assertTrue(Path(custom_db).exists())
        data = self.assert_json_valid(Path(custom_db))
        self.assertIn("workouts", data)

    def test_set_and_bench_files_describe_same_input(self) -> None:
        """The set-centric and bench-centric files come from the same parse."""
        file1 = self.create_training_file(self.training_sample_1, "day1.txt")
        self.run_bulk_parser(file1)

        set_data = self.assert_json_valid(self.output_dir / "set" / "day1_set.json")
        bench_data = self.assert_json_valid(self.output_dir / "bench" / "day1_bench.json")

        self.assertEqual(set_data["workout_id"], bench_data["workout_id"])
        self.assertEqual(set_data["date"], bench_data["date"])
        self.assertEqual(set_data["date"], "2025-01-01T00:00:00+00:00")
        set_reps = [[s["repetitions"] for s in e["sets"]] for e in set_data["exercises"]]
        bench_reps = [[s["reps"] for s in e["sets"]] for e in bench_data["exercises"]]
        self.assertEqual(set_reps, bench_reps)

    def test_each_input_maps_to_its_own_files(self) -> None:
        """Files do not leak exercises into each other's output."""
        file1 = self.create_training_file(self.training_sample_1, "day1.txt")
        file2 = self.create_training_file(self.training_sample_2, "day2.txt")
        self.run_bulk_parser(file1, file2)

        for kind in ("set", "bench"):
            names_1 = self.exercise_names(self.output_dir / kind / f"day1_{kind}.json")
            names_2 = self.exercise_names(self.output_dir / kind / f"day2_{kind}.json")
            self.assertEqual(len(names_1), 2)
            self.assertEqual(len(names_2), 2)
            self.assertFalse(set(names_1) & set(names_2))
            self.assertTrue(any("Squat" in n for n in names_1))
            self.assertTrue(any("Deadlift" in n for n in names_2))

        db = self.assert_json_valid(self.output_dir / "database.json")
        by_source = {
            Path(w["source_file"]).name: [e["name"] for e in w["exercises"]]
            for w in db["workouts"]
        }
        self.assertEqual(by_source["day1.txt"], self.exercise_names(self.output_dir / "set" / "day1_set.json"))
        self.assertEqual(by_source["day2.txt"], self.exercise_names(self.output_dir / "set" / "day2_set.json"))

    def test_set_and_bench_files_go_to_separate_folders(self) -> None:
        """Set-centric files live in set/, bench-centric files in bench/, nothing else."""
        file1 = self.create_training_file(self.training_sample_1, "day1.txt")
        file2 = self.create_training_file(self.training_sample_2, "day2.txt")
        self.assertEqual(self.run_bulk_parser(file1, file2), 0)

        self.assertEqual(
            sorted(p.name for p in self.output_dir.iterdir()), ["bench", "database.json", "set"]
        )
        self.assertEqual(
            sorted(p.name for p in (self.output_dir / "set").iterdir()),
            ["day1_set.json", "day2_set.json"]
        )
        self.assertEqual(
            sorted(p.name for p in (self.output_dir / "bench").iterdir()),
            ["day1_bench.json", "day2_bench.json"]
        )
        for path in (self.output_dir / "set").iterdir():
            self.assertEqual(self.assert_json_valid(path)["type"], "set-centric")
        for path in (self.output_dir / "bench").iterdir():
            self.assertEqual(self.assert_json_valid(path)["type"], "bench-centric")

    def test_two_sessions_yield_two_files_per_input(self) -> None:
        """N input files produce exactly 2N files (set + bench) plus the database."""
        jan = self.create_training_file(
            "2020-01-01\n" + self.training_sample_1.split("\n", 1)[1], "2020-01-01.txt"
        )
        feb = self.create_training_file(
            "2020-02-01\n" + self.training_sample_2.split("\n", 1)[1], "2020-02-01.txt"
        )
        self.assertEqual(self.run_bulk_parser(jan, feb), 0)

        produced = self.produced_files()
        self.assertEqual(produced, [
            "bench/2020-01-01_bench.json", "bench/2020-02-01_bench.json",
            "database.json",
            "set/2020-01-01_set.json", "set/2020-02-01_set.json",
        ])
        for stem, date in (("2020-01-01", "2020-01-01"), ("2020-02-01", "2020-02-01")):
            for kind in ("set", "bench"):
                data = self.assert_json_valid(self.output_dir / kind / f"{stem}_{kind}.json")
                self.assertTrue(data["date"].startswith(date))

    def test_multiple_sessions_in_one_file_are_split(self) -> None:
        """A file with N dated sessions yields N set-centric and N bench-centric files."""
        multi = self.create_training_file(
            "2020-01-01\nSquat 70k: 5x10\n\n2020-02-01\nDeadlift 60k: 20, 15\n",
            "multi.txt"
        )
        other = self.create_training_file(self.training_sample_3, "single.txt")
        self.assertEqual(self.run_bulk_parser(multi, other), 0)

        produced = self.produced_files()
        self.assertEqual(produced, [
            "bench/multi_2020-01-01_bench.json", "bench/multi_2020-02-01_bench.json",
            "bench/single_bench.json",
            "database.json",
            "set/multi_2020-01-01_set.json", "set/multi_2020-02-01_set.json",
            "set/single_set.json",
        ])

        for kind in ("set", "bench"):
            jan = self.assert_json_valid(self.output_dir / kind / f"multi_2020-01-01_{kind}.json")
            feb = self.assert_json_valid(self.output_dir / kind / f"multi_2020-02-01_{kind}.json")
            self.assertEqual([e["name"] for e in jan["exercises"]], ["Squat"])
            self.assertEqual([e["name"] for e in feb["exercises"]], ["Deadlift"])
            self.assertTrue(jan["date"].startswith("2020-01-01"))
            self.assertTrue(feb["date"].startswith("2020-02-01"))
            self.assertNotEqual(jan["workout_id"], feb["workout_id"])

        db = self.assert_json_valid(self.output_dir / "database.json")
        self.assertEqual(len(db["workouts"]), 3)
        self.assertEqual(
            [w["date"][:10] for w in db["workouts"]],
            ["2020-01-01", "2020-02-01", "2025-01-03"]
        )
        from_multi = [w for w in db["workouts"] if w["source_file"] == str(multi)]
        self.assertEqual(
            [(w["date"][:10], w["exercises"][0]["name"]) for w in from_multi],
            [("2020-01-01", "Squat"), ("2020-02-01", "Deadlift")],
        )

    def test_same_date_twice_in_one_file_does_not_collide(self) -> None:
        """Two sessions with the same date get distinct files and ids."""
        multi = self.create_training_file(
            "2020-01-01\nSquat 70k: 5x10\n\n2020-01-01\nDeadlift 60k: 20, 15\n",
            "twice.txt"
        )
        self.assertEqual(self.run_bulk_parser(multi), 0)

        set_files = sorted((self.output_dir / "set").glob("twice_*_set.json"))
        self.assertEqual(len(set_files), 2)
        self.assertEqual(
            sorted(self.exercise_names(f)[0] for f in set_files), ["Deadlift", "Squat"]
        )
        db = self.assert_json_valid(self.output_dir / "database.json")
        self.assertEqual(len({w["workout_id"] for w in db["workouts"]}), 2)

    def test_session_without_exercises_is_skipped(self) -> None:
        """A date line with nothing under it does not fail the whole file."""
        multi = self.create_training_file(
            "2020-01-01\n\n2020-02-01\nDeadlift 60k: 20, 15\n", "gap.txt"
        )
        self.assertEqual(self.run_bulk_parser(multi), 0)
        # Only one session is left, so it keeps the plain file name
        self.assertEqual(self.exercise_names(self.output_dir / "set" / "gap_set.json"), ["Deadlift"])
        db = self.assert_json_valid(self.output_dir / "database.json")
        self.assertEqual(db["workouts"][0]["date"][:10], "2020-02-01")

    def test_unparseable_session_fails_the_file(self) -> None:
        """A session with content that yields no exercise is an error, not a silent drop."""
        bad = self.create_training_file(
            "2020-01-01\nSquat 70k: 5x10\n\n2020-02-01\nthis is !!! not valid\n", "bad.txt"
        )
        good = self.create_training_file(self.training_sample_3, "good.txt")
        result = subprocess.run(
            ["bash", str(self.script_path), "-o", str(self.output_dir), str(bad), str(good)],
            capture_output=True, text=True
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no exercise could be parsed", result.stderr)
        self.assertEqual(list(self.output_dir.rglob("bad*")), [], "no partial output for a failed file")
        self.assertTrue((self.output_dir / "set" / "good_set.json").exists())

    def test_runs_from_any_working_directory(self) -> None:
        """The script resolves its own dependencies and does not rely on the cwd."""
        file1 = self.create_training_file(self.training_sample_1, "day1.txt")
        result = subprocess.run(
            ["bash", str(self.script_path.resolve()), "-o", str(self.output_dir), str(file1)],
            capture_output=True, text=True, cwd=self.temp_dir.name
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.output_dir / "set" / "day1_set.json").exists())

    def test_same_basename_in_different_directories(self) -> None:
        """Two inputs named alike must not overwrite each other's output."""
        (Path(self.temp_dir.name) / "a").mkdir()
        (Path(self.temp_dir.name) / "b").mkdir()
        file_a = self.create_training_file(self.training_sample_1, "a/day.txt")
        file_b = self.create_training_file(self.training_sample_2, "b/day.txt")

        self.assertEqual(self.run_bulk_parser(file_a, file_b), 0)

        set_files = sorted((self.output_dir / "set").glob("*_set.json"))
        bench_files = sorted((self.output_dir / "bench").glob("*_bench.json"))
        self.assertEqual(len(set_files), 2)
        self.assertEqual(len(bench_files), 2)

        seen = {tuple(self.exercise_names(f)) for f in set_files}
        self.assertEqual(len(seen), 2, "Each input needs its own set-centric file")

        db = self.assert_json_valid(self.output_dir / "database.json")
        self.assertEqual(len(db["workouts"]), 2)
        sources = {w["source_file"] for w in db["workouts"]}
        self.assertEqual(sources, {str(file_a), str(file_b)})

    def test_workout_ids_are_unique_within_one_second(self) -> None:
        """Files without a date, parsed together, still get distinct ids."""
        file1 = self.create_training_file("Squat 70k: 5x10\n", "x.txt")
        file2 = self.create_training_file("Squat 70k: 5x10\n", "y.txt")
        self.run_bulk_parser(file1, file2)

        db = self.assert_json_valid(self.output_dir / "database.json")
        ids = [w["workout_id"] for w in db["workouts"]]
        self.assertEqual(len(ids), 2)
        self.assertEqual(len(set(ids)), 2)

    def test_rerun_does_not_duplicate_database_entry(self) -> None:
        """Parsing the same file again updates its entry instead of adding one."""
        file1 = self.create_training_file(self.training_sample_1, "day1.txt")
        self.run_bulk_parser(file1)
        self.run_bulk_parser(file1)

        db = self.assert_json_valid(self.output_dir / "database.json")
        self.assertEqual(len(db["workouts"]), 1)

    def test_database_sorted_by_date(self) -> None:
        """Database workouts are ordered by workout date, not input order."""
        file1 = self.create_training_file(self.training_sample_1, "day1.txt")
        file2 = self.create_training_file(self.training_sample_2, "day2.txt")
        file3 = self.create_training_file(self.training_sample_3, "day3.txt")
        self.run_bulk_parser(file3, file1, file2)

        db = self.assert_json_valid(self.output_dir / "database.json")
        dates = [w["date"] for w in db["workouts"]]
        self.assertEqual(dates, sorted(dates))
        self.assertEqual(len(dates), 3)

    def test_unrelated_json_in_output_dir_untouched(self) -> None:
        """Only files produced by the run are rewritten."""
        self.output_dir.mkdir()
        unrelated = self.output_dir / "unrelated.json"
        unrelated.write_text('{"b":1,   "a":2}')

        file1 = self.create_training_file(self.training_sample_1, "day1.txt")
        self.run_bulk_parser(file1)

        self.assertEqual(unrelated.read_text(), '{"b":1,   "a":2}')

    def test_failing_file_does_not_stop_others(self) -> None:
        """One bad input is reported and the rest are still exported."""
        bad = Path(self.temp_dir.name) / "missing.txt"
        good = self.create_training_file(self.training_sample_1, "good.txt")

        result = subprocess.run(
            ["bash", str(self.script_path), "-o", str(self.output_dir), str(bad), str(good)],
            capture_output=True, text=True
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((self.output_dir / "set" / "good_set.json").exists())
        self.assertTrue((self.output_dir / "bench" / "good_bench.json").exists())

    def test_missing_file_handling(self) -> None:
        """Test that script handles missing input files gracefully."""
        nonexistent = Path(self.temp_dir.name) / "nonexistent.txt"

        cmd = [
            "bash", str(self.script_path),
            "-o", str(self.output_dir),
            str(nonexistent)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        # Should still run but report error for the file
        self.assertIn("not found", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()
