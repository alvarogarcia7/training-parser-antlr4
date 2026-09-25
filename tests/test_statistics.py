"""Tests for workout statistics calculation."""

import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

from parser.model import Exercise, Set_, Weight
from src.statistics import StatisticsCalculator, WorkoutStats


class TestWorkoutStats(unittest.TestCase):
    """Test WorkoutStats dataclass and properties."""

    def test_initialization(self) -> None:
        """Test basic initialization."""
        stats = WorkoutStats(
            total_exercises=10,
            total_sets=50,
            total_weight=2500.0,
            time_minutes=60.0,
        )
        self.assertEqual(stats.total_exercises, 10)
        self.assertEqual(stats.total_sets, 50)
        self.assertEqual(stats.total_weight, 2500.0)
        self.assertEqual(stats.time_minutes, 60.0)

    def test_exercises_per_hour(self) -> None:
        """Test exercises per hour calculation."""
        stats = WorkoutStats(
            total_exercises=10,
            total_sets=50,
            total_weight=2500.0,
            time_minutes=60.0,
        )
        self.assertEqual(stats.exercises_per_hour, 10.0)

    def test_exercises_per_minute(self) -> None:
        """Test exercises per minute calculation."""
        stats = WorkoutStats(
            total_exercises=10,
            total_sets=50,
            total_weight=2500.0,
            time_minutes=60.0,
        )
        self.assertAlmostEqual(stats.exercises_per_minute, 10 / 60, places=4)

    def test_sets_per_hour(self) -> None:
        """Test sets per hour calculation."""
        stats = WorkoutStats(
            total_exercises=10,
            total_sets=60,
            total_weight=3000.0,
            time_minutes=120.0,
        )
        self.assertEqual(stats.sets_per_hour, 30.0)

    def test_sets_per_minute(self) -> None:
        """Test sets per minute calculation."""
        stats = WorkoutStats(
            total_exercises=10,
            total_sets=60,
            total_weight=3000.0,
            time_minutes=120.0,
        )
        self.assertEqual(stats.sets_per_minute, 0.5)

    def test_weight_per_hour(self) -> None:
        """Test weight per hour calculation."""
        stats = WorkoutStats(
            total_exercises=10,
            total_sets=50,
            total_weight=2000.0,
            time_minutes=120.0,
        )
        self.assertAlmostEqual(stats.weight_per_hour, 1000.0, places=5)

    def test_weight_per_minute(self) -> None:
        """Test weight per minute calculation."""
        stats = WorkoutStats(
            total_exercises=10,
            total_sets=50,
            total_weight=2000.0,
            time_minutes=120.0,
        )
        self.assertAlmostEqual(stats.weight_per_minute, 2000.0 / 120, places=4)

    def test_avg_weight_per_set(self) -> None:
        """Test average weight per set."""
        stats = WorkoutStats(
            total_exercises=10,
            total_sets=50,
            total_weight=2500.0,
            time_minutes=60.0,
        )
        self.assertEqual(stats.avg_weight_per_set, 50.0)

    def test_avg_sets_per_exercise(self) -> None:
        """Test average sets per exercise."""
        stats = WorkoutStats(
            total_exercises=10,
            total_sets=50,
            total_weight=2500.0,
            time_minutes=60.0,
        )
        self.assertEqual(stats.avg_sets_per_exercise, 5.0)

    def test_zero_time_handling(self) -> None:
        """Test handling of zero time duration."""
        stats = WorkoutStats(
            total_exercises=10,
            total_sets=50,
            total_weight=2500.0,
            time_minutes=0.0,
        )
        self.assertEqual(stats.exercises_per_hour, 0.0)
        self.assertEqual(stats.exercises_per_minute, 0.0)
        self.assertEqual(stats.sets_per_hour, 0.0)
        self.assertEqual(stats.weight_per_hour, 0.0)

    def test_zero_exercises_handling(self) -> None:
        """Test handling of zero exercises."""
        stats = WorkoutStats(
            total_exercises=0,
            total_sets=0,
            total_weight=0.0,
            time_minutes=60.0,
        )
        self.assertEqual(stats.avg_sets_per_exercise, 0.0)

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        stats = WorkoutStats(
            total_exercises=10,
            total_sets=50,
            total_weight=2500.0,
            time_minutes=60.0,
        )
        data = stats.to_dict()

        self.assertIn("totals", data)
        self.assertIn("rates", data)
        self.assertIn("averages", data)
        self.assertIn("time", data)

        self.assertEqual(data["totals"]["exercises"], 10)
        self.assertEqual(data["totals"]["sets"], 50)
        self.assertEqual(data["totals"]["weight_kg"], 2500.0)


class TestStatisticsCalculator(unittest.TestCase):
    """Test StatisticsCalculator."""

    def test_from_exercises(self) -> None:
        """Test calculation from Exercise objects."""
        exercises = [
            Exercise(
                "Bench press",
                [
                    Set_(4, Weight(75.0, "kg")),
                    Set_(5, Weight(75.0, "kg")),
                ],
            ),
            Exercise(
                "Squat",
                [
                    Set_(10, Weight(70.0, "kg")),
                    Set_(10, Weight(70.0, "kg")),
                ],
            ),
        ]

        stats = StatisticsCalculator.from_exercises(exercises, time_minutes=30.0)

        self.assertEqual(stats.total_exercises, 2)
        self.assertEqual(stats.total_sets, 4)
        # Bench: 4*75 + 5*75 = 675, Squat: 10*70 + 10*70 = 1400
        self.assertEqual(stats.total_weight, 2075.0)
        self.assertEqual(stats.time_minutes, 30.0)

    def test_from_json_workouts(self) -> None:
        """Test calculation from JSON workout data."""
        workouts = [
            {
                "exercises": [
                    {
                        "name": "Bench press",
                        "sets": [
                            {
                                "repetitions": 4,
                                "weight": {"amount": 75.0, "unit": "kg"},
                            },
                            {
                                "repetitions": 5,
                                "weight": {"amount": 75.0, "unit": "kg"},
                            },
                        ],
                    },
                    {
                        "name": "Squat",
                        "sets": [
                            {
                                "repetitions": 10,
                                "weight": {"amount": 70.0, "unit": "kg"},
                            },
                        ],
                    },
                ],
            },
        ]

        stats = StatisticsCalculator.from_json_workouts(workouts, time_minutes=45.0)

        self.assertEqual(stats.total_exercises, 2)
        self.assertEqual(stats.total_sets, 3)
        # Bench: 4*75 + 5*75 = 675, Squat: 10*70 = 700
        self.assertEqual(stats.total_weight, 1375.0)

    def test_from_multiple_workouts(self) -> None:
        """Test calculation from multiple workouts."""
        workouts = [
            {
                "exercises": [
                    {
                        "name": "Exercise 1",
                        "sets": [
                            {
                                "repetitions": 10,
                                "weight": {"amount": 50.0, "unit": "kg"},
                            },
                        ],
                    },
                ],
            },
            {
                "exercises": [
                    {
                        "name": "Exercise 2",
                        "sets": [
                            {
                                "repetitions": 10,
                                "weight": {"amount": 60.0, "unit": "kg"},
                            },
                        ],
                    },
                ],
            },
        ]

        stats = StatisticsCalculator.from_json_workouts(workouts, time_minutes=60.0)

        self.assertEqual(stats.total_exercises, 2)
        self.assertEqual(stats.total_sets, 2)
        self.assertEqual(stats.total_weight, 1100.0)

    def test_format_stats(self) -> None:
        """Test formatting stats for output."""
        stats = WorkoutStats(
            total_exercises=10,
            total_sets=50,
            total_weight=2500.0,
            time_minutes=60.0,
        )

        output = StatisticsCalculator.format_stats(stats)

        self.assertIn("WORKOUT STATISTICS", output)
        self.assertIn("Total Exercises", output)
        self.assertIn("Total Sets", output)
        self.assertIn("Total Weight", output)
        self.assertIn("RATES", output)
        self.assertIn("AVERAGES", output)


class TestStatisticsIntegration(unittest.TestCase):
    """Integration tests for statistics with real data."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        """Clean up."""
        self.temp_dir.cleanup()

    def test_stats_from_real_json_file(self) -> None:
        """Test loading stats from real JSON file."""
        json_data = {
            "type": "set-centric",
            "exercises": [
                {
                    "name": "Bench press",
                    "sets": [
                        {
                            "setNumber": 1,
                            "repetitions": 4,
                            "weight": {"amount": 75.0, "unit": "kg"},
                        },
                    ],
                },
            ],
        }

        json_file = Path(self.temp_dir.name) / "test.json"
        json_file.write_text(json.dumps(json_data))

        with open(json_file) as f:
            data = json.load(f)

        exercises = data.get("exercises", [])
        stats = StatisticsCalculator.from_json_workouts(
            [{"exercises": exercises}],
            time_minutes=30.0,
        )

        self.assertEqual(stats.total_exercises, 1)
        self.assertEqual(stats.total_sets, 1)
        self.assertEqual(stats.total_weight, 300.0)


if __name__ == "__main__":
    unittest.main()
