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
        self.script_path = Path("scripts/parse_bulk.sh")

        # Sample training data
        self.training_sample_1 = """bench press
4x75, 5x75, 5x75, 5x75

squat
10x70, 10x70, 10x70, 10x70, 10x70
"""

        self.training_sample_2 = """overhead press
5x40, 5x40, 5x40, 5x40, 5x40

deadlift
20x60, 15x60, 8x60, 8x60
"""

        self.training_sample_3 = """machine row
15x41, 8x41
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
        set_file = self.output_dir / "workout_day1_set.json"
        bench_file = self.output_dir / "workout_day1_bench.json"
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
            set_file = self.output_dir / f"{prefix}_set.json"
            bench_file = self.output_dir / f"{prefix}_bench.json"
            self.assertTrue(set_file.exists(), f"{prefix} set file missing")
            self.assertTrue(bench_file.exists(), f"{prefix} bench file missing")

    def test_set_centric_format(self) -> None:
        """Test that set-centric JSON has correct structure."""
        file1 = self.create_training_file(
            self.training_sample_1,
            "test.txt"
        )

        self.run_bulk_parser(file1)

        set_file = self.output_dir / "test_set.json"
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

        bench_file = self.output_dir / "test_bench.json"
        data = self.assert_json_valid(bench_file)

        # Check required fields
        self.assertIn("type", data, "Should have type field")
        self.assertEqual(data["type"], "bench-centric.v1")
        self.assertIn("benches", data, "Should have benches")
        self.assertGreater(len(data["benches"]), 0)

        # Check bench structure
        bench = data["benches"][0]
        self.assertIn("name", bench)
        self.assertIn("exercises", bench)
        self.assertGreater(len(bench["exercises"]), 0)

        # Check exercise structure in bench
        exercise = bench["exercises"][0]
        self.assertIn("name", exercise)
        self.assertIn("sets", exercise)

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
        for json_file in self.output_dir.glob("*.json"):
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

        set_file = self.output_dir / "test_set.json"
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
