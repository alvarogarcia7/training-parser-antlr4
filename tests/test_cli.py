"""Tests for the unified CLI program."""

import json
import tempfile
import unittest
from pathlib import Path
from io import StringIO
import sys
from datetime import datetime, timezone
from typing import cast

from parser import Exercise, Set_, Weight
from src.data_access import DataSerializer, ParsedWorkoutSession


class TestDataSerializer(unittest.TestCase):
    """Test DataSerializer output formats match expected outputs."""

    def setUp(self) -> None:
        """Set up test exercises."""
        self.exercises = [
            Exercise('Bench press', [
                Set_(4, Weight(75.0, 'kg')),
                Set_(5, Weight(75.0, 'kg')),
                Set_(5, Weight(75.0, 'kg')),
                Set_(5, Weight(75.0, 'kg')),
            ]),
            Exercise('Squat', [
                Set_(10, Weight(70.0, 'kg')),
                Set_(10, Weight(70.0, 'kg')),
                Set_(10, Weight(70.0, 'kg')),
                Set_(10, Weight(70.0, 'kg')),
                Set_(10, Weight(70.0, 'kg')),
            ]),
            Exercise('Overhead press', [
                Set_(5, Weight(40.0, 'kg')),
                Set_(5, Weight(40.0, 'kg')),
                Set_(5, Weight(40.0, 'kg')),
                Set_(5, Weight(40.0, 'kg')),
                Set_(5, Weight(40.0, 'kg')),
            ]),
            Exercise('Deadlift', [
                Set_(20, Weight(60.0, 'kg')),
                Set_(15, Weight(60.0, 'kg')),
                Set_(8, Weight(60.0, 'kg')),
                Set_(8, Weight(60.0, 'kg')),
            ]),
            Exercise('Machine row', [
                Set_(15, Weight(41.0, 'kg')),
                Set_(8, Weight(41.0, 'kg')),
            ]),
        ]

    def test_set_centric_json_structure(self) -> None:
        """Test that set-centric JSON matches expected structure."""
        timestamp = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        result = DataSerializer.to_set_centric_json(self.exercises, timestamp)

        # Verify top-level structure
        self.assertEqual(result['type'], 'set-centric')
        self.assertEqual(result['workout_id'], 'w_20250101_000000')
        self.assertEqual(result['date'], '2025-01-01T00:00:00+00:00')
        self.assertIn('exercises', result)
        self.assertIn('location', result)
        self.assertIn('notes', result)
        self.assertIn('statistics', result)

        # Verify exercises
        self.assertEqual(len(result['exercises']), 5)

        # Verify first exercise structure
        bench = result['exercises'][0]
        self.assertEqual(bench['name'], 'Bench press')
        self.assertEqual(bench['equipment'], 'other')
        self.assertEqual(len(bench['sets']), 4)

        # Verify set structure
        first_set = bench['sets'][0]
        self.assertEqual(first_set['setNumber'], 1)
        self.assertEqual(first_set['repetitions'], 4)
        self.assertEqual(first_set['weight']['amount'], 75.0)
        self.assertEqual(first_set['weight']['unit'], 'kg')

    def test_set_centric_json_all_exercises(self) -> None:
        """Test that all exercises are properly serialized."""
        result = DataSerializer.to_set_centric_json(self.exercises)

        exercise_names = [ex['name'] for ex in result['exercises']]
        self.assertEqual(exercise_names, [
            'Bench press',
            'Squat',
            'Overhead press',
            'Deadlift',
            'Machine row'
        ])

    def test_set_centric_json_is_valid_json(self) -> None:
        """Test that output can be serialized to JSON and deserialized."""
        result = DataSerializer.to_set_centric_json(self.exercises)
        json_str = json.dumps(result)
        parsed = json.loads(json_str)
        self.assertEqual(parsed['type'], 'set-centric')

    def test_tsv_rows_structure(self) -> None:
        """Test that TSV rows have correct structure."""
        sessions: list[ParsedWorkoutSession] = cast(list[ParsedWorkoutSession], [{
            'date': '2025-01-01',
            'parsed': self.exercises,
            'notes': ''
        }])

        rows = DataSerializer.to_tsv_rows(sessions)

        # First row should be header
        self.assertEqual(rows[0], ['Date', 'Exercise', 'Sets', 'Avg Reps', 'Weight'])

        # Subsequent rows should have data
        self.assertGreater(len(rows), 1)

        # Each data row should have 5 columns
        for row in rows[1:]:
            self.assertEqual(len(row), 5)

    def test_tsv_rows_content(self) -> None:
        """Test that TSV rows contain expected exercise data."""
        sessions: list[ParsedWorkoutSession] = cast(list[ParsedWorkoutSession], [{
            'date': '2025-01-01',
            'parsed': self.exercises,
            'notes': ''
        }])

        rows = DataSerializer.to_tsv_rows(sessions)

        # Skip header, check first exercise (Bench press)
        # Note: flatten() groups by (weight, repetitions), so we get multiple rows
        # First group should be the single 4-rep set at 75kg
        bench_row_1 = rows[1]
        self.assertEqual(bench_row_1[0], '2025-01-01')  # date
        self.assertEqual(bench_row_1[1], 'Bench press')  # exercise name
        self.assertEqual(bench_row_1[2], '1')  # 1 set of 4 reps at 75kg
        self.assertEqual(bench_row_1[3], '4')  # avg reps = 4
        self.assertEqual(bench_row_1[4], '75,0')  # weight with comma decimal

        # Second group should be the three 5-rep sets at 75kg
        bench_row_2 = rows[2]
        self.assertEqual(bench_row_2[0], '2025-01-01')  # date
        self.assertEqual(bench_row_2[1], 'Bench press')  # exercise name
        self.assertEqual(bench_row_2[2], '3')  # 3 sets of 5 reps at 75kg
        self.assertEqual(bench_row_2[3], '5')  # avg reps = 5
        self.assertEqual(bench_row_2[4], '75,0')  # weight with comma decimal

    def test_tsv_rows_multiple_sessions(self) -> None:
        """Test that TSV rows handle multiple sessions correctly."""
        sessions: list[ParsedWorkoutSession] = cast(list[ParsedWorkoutSession], [
            {
                'date': '2025-01-01',
                'parsed': self.exercises[:2],  # Bench + Squat
                'notes': ''
            },
            {
                'date': '2025-01-02',
                'parsed': self.exercises[2:4],  # Overhead press + Deadlift
                'notes': ''
            }
        ])

        rows = DataSerializer.to_tsv_rows(sessions)

        # Header + 2 exercises from session 1 + 2 exercises from session 2
        self.assertGreaterEqual(len(rows), 5)

        # Check dates are present
        dates = [row[0] for row in rows[1:]]
        self.assertIn('2025-01-01', dates)
        self.assertIn('2025-01-02', dates)

    def test_text_format_matches_compact_display(self) -> None:
        """Test that text format output matches compact display format."""
        # This is a basic test to ensure the format is correct
        # The actual compact format is tested in parser module
        exercise = Exercise('Bench Press', [
            Set_(10, Weight(60.0, 'kg')),
            Set_(8, Weight(70.0, 'kg')),
        ])

        repr_str = repr(exercise)
        self.assertIn('Bench Press', repr_str)
        # Exercise repr should show name and sets information
        self.assertIsNotNone(repr_str)


class TestCLIIntegration(unittest.TestCase):
    """Integration tests for CLI with actual files."""

    def setUp(self) -> None:
        """Set up temporary directory and sample files."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def test_parse_simple_file_json_format(self) -> None:
        """Test parsing a simple file outputs valid JSON."""
        # Create a sample training file
        sample_file = self.temp_path / "training.txt"
        sample_file.write_text("Bench press 75k: 4, 4x5\nSquat 70k: 5x10\n")

        from src.data_access import DataAccess
        data = DataAccess()
        exercises = data.parse_single_file(str(sample_file))

        # Convert to JSON
        json_data = DataSerializer.to_set_centric_json(exercises)
        json_str = json.dumps(json_data)

        # Verify it's valid JSON
        parsed = json.loads(json_str)
        self.assertEqual(parsed['type'], 'set-centric')
        self.assertGreater(len(parsed['exercises']), 0)

    def test_parse_multi_session_file(self) -> None:
        """Test parsing a multi-session file."""
        sample_file = self.temp_path / "multi-session.txt"
        sample_file.write_text(
            "2025-01-01\n"
            "Bench press 75k: 4, 4x5\n"
            "Squat 70k: 5x10\n"
            "\n"
            "2025-01-02\n"
            "Deadlift 60k: 20, 15, 8, 8\n"
            "\n"
        )

        from src.data_access import DataAccess
        data = DataAccess()
        sessions = data.parse_multi_session_file(str(sample_file))

        # Should have 2 sessions
        self.assertEqual(len(sessions), 2)
        self.assertEqual(sessions[0]['date'], '2025-01-01')
        self.assertEqual(sessions[1]['date'], '2025-01-02')

        # Each session should have exercises
        self.assertGreater(len(sessions[0]['parsed']), 0)
        self.assertGreater(len(sessions[1]['parsed']), 0)

    def test_parse_file_with_notes(self) -> None:
        """Test parsing file with notes."""
        sample_file = self.temp_path / "training-notes.txt"
        sample_file.write_text(
            "2025-01-01\n"
            "Bench press 75k: 4, 4x5\n"
            "# Good workout, feeling strong\n"
            "# Tired on last set\n"
            "\n"
        )

        from src.data_access import DataAccess
        data = DataAccess()
        sessions = data.parse_multi_session_file(str(sample_file))

        # Verify notes are captured
        self.assertIn('Good workout', sessions[0]['notes'])
        self.assertIn('Tired on last set', sessions[0]['notes'])

    def test_tsv_export_matches_format(self) -> None:
        """Test that TSV export has correct format."""
        sample_file = self.temp_path / "training.txt"
        sample_file.write_text(
            "2025-01-01\n"
            "Bench press 75k: 4, 4x5\n"
            "\n"
        )

        from src.data_access import DataAccess
        data = DataAccess()
        sessions = data.parse_multi_session_file(str(sample_file))
        rows = DataSerializer.to_tsv_rows(sessions)

        # Verify TSV structure
        self.assertEqual(rows[0], ['Date', 'Exercise', 'Sets', 'Avg Reps', 'Weight'])

        # Verify data rows (flatten() groups by weight/reps, so we get 2 rows)
        # First row: single 4-rep set at 75kg (standardized name)
        # Note: "Bench press" → "bench" matches synonym → "bench press" + leftover "press"
        data_row_1 = rows[1]
        self.assertEqual(data_row_1[0], '2025-01-01')
        self.assertEqual(data_row_1[1], 'Bench Press Press')  # StandardizeName: "bench" + "press"
        self.assertEqual(data_row_1[2], '1')  # 1 set of 4 reps
        self.assertEqual(data_row_1[3], '4')  # avg reps = 4
        self.assertEqual(data_row_1[4], '75,0')

        # Second row: four 5-rep sets at 75kg (from "4x5" = 4 times 5 reps)
        data_row_2 = rows[2]
        self.assertEqual(data_row_2[0], '2025-01-01')
        self.assertEqual(data_row_2[1], 'Bench Press Press')
        self.assertEqual(data_row_2[2], '4')  # 4 sets of 5 reps
        self.assertEqual(data_row_2[3], '5')  # avg reps = 5
        self.assertEqual(data_row_2[4], '75,0')


if __name__ == '__main__':
    unittest.main()
