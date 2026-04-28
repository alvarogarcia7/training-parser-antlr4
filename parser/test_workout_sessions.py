import unittest

from parser import Parser, ParseResult, Exercise, Units, Set_, Weight


class TestWorkoutSessions(unittest.TestCase):
    """Test complete workout sessions with multiple exercises."""

    def test_complete_valid_workout_session(self) -> None:
        """Test parsing a complete valid workout session with multiple exercises."""
        workout = """Bench press 75k: 4, 4x5
Squat 70k: 5x10
Overhead press: 5x5x40k
Deadlift 60k: 20, 15, 8, 8
Row en maquina 41k: 15, 8
"""
        result = Parser.from_string(workout).parse()

        self.assertFalse(result.has_errors)
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.exercises), 5)

        # Verify exercise names
        exercise_names = [ex.name for ex in result.exercises]
        self.assertEqual(exercise_names, [
            'Bench press',
            'Squat',
            'Overhead press',
            'Deadlift',
            'Row en maquina'
        ])

    def test_workout_session_with_partial_errors(self) -> None:
        """Test workout session where some exercises have errors but others are valid."""
        workout = """Bench press 75k: 4, 4x5
Squat: 5x
Overhead press: 5x5x40k
Deadlift: 10x
Row en maquina 41k: 15, 8
"""
        result = Parser.from_string(workout).parse()

        # Should have errors from incomplete exercises
        self.assertTrue(result.has_errors)
        self.assertFalse(result.is_valid)

        # But should still parse valid exercises
        self.assertEqual(len(result.exercises), 3)

        exercise_names = [ex.name for ex in result.exercises]
        self.assertIn('Bench press', exercise_names)
        self.assertIn('Overhead press', exercise_names)
        self.assertIn('Row en maquina', exercise_names)

        # Verify we have errors
        self.assertGreater(len(result.errors), 0)

    def test_workout_session_all_errors(self) -> None:
        """Test workout session where all exercises have errors."""
        workout = """Squat: 5x
Bench: 10x
Deadlift: 3x
"""
        result = Parser.from_string(workout).parse()

        self.assertTrue(result.has_errors)
        self.assertEqual(len(result.exercises), 0)
        self.assertGreater(len(result.errors), 0)

    def test_workout_session_mixed_formats(self) -> None:
        """Test workout session with various exercise formats."""
        workout = """Bench press 3x50x10k 60: 12, 11
Squat: 15xx40, 50
Deadlift 1x1x60k 1x2x40k
Overhead press 5x6x40k
"""
        result = Parser.from_string(workout).parse()

        self.assertFalse(result.has_errors)
        self.assertEqual(len(result.exercises), 4)

        # Verify bench press has mixed formats
        bench = result.exercises[0]
        self.assertEqual(bench.name, 'Bench press')
        # 3 sets of 50 reps + 2 sets (12 and 11 reps)
        self.assertEqual(len(bench.sets_), 5)

    def test_workout_session_with_accents_and_special_chars(self) -> None:
        """Test workout session with exercises containing accents and hyphens."""
        workout = """Row en máquina 41k: 15, 8
Pull-up 20k: 10, 8, 6
Press francés 30k: 12, 10
"""
        result = Parser.from_string(workout).parse()

        self.assertFalse(result.has_errors)
        self.assertEqual(len(result.exercises), 3)

        exercise_names = [ex.name for ex in result.exercises]
        self.assertIn('Row en máquina', exercise_names)
        self.assertIn('Pull-up', exercise_names)
        self.assertIn('Press francés', exercise_names)

    def test_workout_session_with_empty_lines(self) -> None:
        """Test workout session handling empty lines between exercises."""
        workout = """Bench press 75k: 4, 4x5

Squat 70k: 5x10

Overhead press: 5x5x40k
"""
        result = Parser.from_string(workout).parse()

        self.assertFalse(result.has_errors)
        self.assertEqual(len(result.exercises), 3)

    def test_workout_session_error_recovery(self) -> None:
        """Test that parser recovers from errors and continues parsing remaining exercises."""
        workout = """Bench press 75k: 4, 4x5
Squat: 5x
Overhead press: 5x5x40k
Deadlift: 10x
Row en maquina 41k: 15, 8
Pull-up 20k: 10
"""
        result = Parser.from_string(workout).parse()

        self.assertTrue(result.has_errors)

        # Should parse 4 valid exercises despite 2 errors
        self.assertEqual(len(result.exercises), 4)

        # Should have 2 errors
        self.assertEqual(len(result.errors), 2)

        # Verify error line numbers
        error_lines = [error.line for error in result.errors]
        self.assertIn(2, error_lines)  # Squat: 5x
        self.assertIn(4, error_lines)  # Deadlift: 10x

    def test_workout_session_with_rir(self) -> None:
        """Test workout session with RIR (Reps In Reserve) values."""
        workout = """Bench press 3x8x80k-2
Squat 4x5x100k-1
Deadlift 5x3x120k-0
"""
        result = Parser.from_string(workout).parse()

        self.assertFalse(result.has_errors)
        self.assertEqual(len(result.exercises), 3)

        # Verify RIR values are captured
        bench = result.exercises[0]
        self.assertEqual(bench.name, 'Bench press')
        self.assertIsNotNone(bench.sets_[0].rir)
        self.assertEqual(bench.sets_[0].rir, 2)

    def test_workout_session_complex_with_errors(self) -> None:
        """Test complex workout session with various formats and some errors."""
        workout = """Bench press 75k: 4, 4x5
Squat: 5x
Overhead press 5x6x40k
Deadlift 60k: 20, 15, 8
Bad format: 3x
Row en maquina: 15xx41, 50
Pull-up: 10x
Dips 20k: 12, 10, 8
"""
        result = Parser.from_string(workout).parse()

        self.assertTrue(result.has_errors)

        # Should have successfully parsed several exercises
        self.assertGreater(len(result.exercises), 3)

        # Should have multiple errors
        self.assertGreater(len(result.errors), 0)

        # Verify some valid exercises were parsed
        exercise_names = [ex.name for ex in result.exercises]
        self.assertIn('Bench press', exercise_names)
        self.assertIn('Overhead press', exercise_names)
        self.assertIn('Deadlift', exercise_names)
        self.assertIn('Dips', exercise_names)

    def test_workout_session_weight_variations(self) -> None:
        """Test workout session with various weight notations."""
        workout = """Bench press 75k: 4, 4x5
Squat 70: 5x10
Overhead press 40k: 5x5
Deadlift 60.5k: 10, 8
"""
        result = Parser.from_string(workout).parse()

        self.assertFalse(result.has_errors)
        self.assertEqual(len(result.exercises), 4)

        # Verify weights are parsed correctly
        bench = result.exercises[0]
        self.assertEqual(bench.sets_[0].weight.amount, 75.0)

        deadlift = result.exercises[3]
        self.assertEqual(deadlift.sets_[0].weight.amount, 60.5)

    def test_workout_session_get_total_volume(self) -> None:
        """Test calculating total volume for a workout session."""
        workout = """Bench press 3x10x50k
Squat 5x5x100k
"""
        result = Parser.from_string(workout).parse()

        self.assertFalse(result.has_errors)
        self.assertEqual(len(result.exercises), 2)

        # Calculate total volume
        total_volume = sum(ex.total_volume() for ex in result.exercises)
        # Bench: 3 * 10 * 50 = 1500
        # Squat: 5 * 5 * 100 = 2500
        # Total: 4000
        self.assertEqual(total_volume, 4000.0)

    def test_workout_session_with_standard_exercise_names(self) -> None:
        """Test workout session using standard exercise names from grammar."""
        workout = """Deadlift 3x5x100k
Squat 5x5x80k
Bench press 3x8x60k
Overhead press 4x6x40k
"""
        result = Parser.from_string(workout).parse()

        self.assertFalse(result.has_errors)
        self.assertEqual(len(result.exercises), 4)

        exercise_names = [ex.name for ex in result.exercises]
        self.assertIn('Deadlift', exercise_names)
        self.assertIn('Squat', exercise_names)
        self.assertIn('Bench press', exercise_names)
        self.assertIn('Overhead press', exercise_names)

    def test_workout_session_error_line_tracking(self) -> None:
        """Test that errors are correctly tracked to their line numbers in a workout."""
        workout = """Bench press 75k: 4, 4x5
Squat: 5x
Overhead press: 5x5x40k
Deadlift: 10x
Row en maquina 41k: 15
"""
        result = Parser.from_string(workout).parse()

        self.assertTrue(result.has_errors)

        # Check that error lines are correctly identified
        error_lines = sorted([error.line for error in result.errors])

        # Lines 2 and 4 should have errors
        self.assertIn(2, error_lines)
        self.assertIn(4, error_lines)

        # Verify error messages contain useful information
        for error in result.errors:
            self.assertIsInstance(error.message, str)
            self.assertGreater(len(error.message), 0)

    def test_workout_session_multiple_sets_same_weight(self) -> None:
        """Test workout session with multiple sets at the same weight."""
        workout = """Bench press 5x5x75k
Squat 3x10x100k
Deadlift 1x5x140k
"""
        result = Parser.from_string(workout).parse()

        self.assertFalse(result.has_errors)
        self.assertEqual(len(result.exercises), 3)

        # Verify bench press has 5 sets
        bench = result.exercises[0]
        self.assertEqual(len(bench.sets_), 5)
        # All sets should be 5 reps at 75kg
        for set_ in bench.sets_:
            self.assertEqual(set_.repetitions, 5)
            self.assertEqual(set_.weight.amount, 75.0)

    def test_workout_session_progressive_overload(self) -> None:
        """Test workout session with progressive weight increases."""
        workout = """Bench press: 15xx50, 60, 70
Squat: 10xx80, 90, 100
Deadlift: 5xx100, 110, 120
"""
        result = Parser.from_string(workout).parse()

        self.assertFalse(result.has_errors)
        self.assertEqual(len(result.exercises), 3)

        # Verify progressive weights
        bench = result.exercises[0]
        self.assertEqual(len(bench.sets_), 3)
        weights = [set_.weight.amount for set_ in bench.sets_]
        self.assertEqual(weights, [50.0, 60.0, 70.0])

    def test_workout_session_validate_all_exercises(self) -> None:
        """Test that all exercises in a workout can be validated."""
        workout = """Bench press 75k: 4, 4x5
Squat 70k: 5x10
Overhead press: 5x5x40k
"""
        result = Parser.from_string(workout).parse()

        self.assertFalse(result.has_errors)

        # All exercises should be valid
        for exercise in result.exercises:
            # This should not raise an exception
            exercise.validate()
            self.assertGreater(len(exercise.sets_), 0)
            self.assertIsInstance(exercise.name, str)
            self.assertGreater(len(exercise.name), 0)

    def serie(self, repetition: int, weight: float) -> Set_:
        return Set_(repetitions=repetition, weight=Weight(amount=weight, unit=Units.KILOGRAM))


if __name__ == '__main__':
    unittest.main()
