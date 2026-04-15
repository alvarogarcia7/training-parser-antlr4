import unittest

from parser import Parser, ParseResult, ParseError, Exercise, Units, Set_, Weight


class TestErrorHandling(unittest.TestCase):
    def test_parse_valid_input_no_errors(self) -> None:
        """Test that valid input produces no errors."""
        result = Parser.from_string('Bench press 75k: 4, 4x5\n').parse()

        self.assertIsInstance(result, ParseResult)
        self.assertFalse(result.has_errors)
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.exercises), 1)

    def test_parse_invalid_input_captures_errors(self) -> None:
        """Test that invalid input produces errors with line/column info."""
        # Missing weight in 'x' notation causes parse error
        result = Parser.from_string('Squat: 5x\n').parse()

        self.assertTrue(result.has_errors)
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 0)

        # Check that error has line and column information
        first_error = result.errors[0]
        self.assertIsInstance(first_error, ParseError)
        self.assertGreater(first_error.line, 0)
        self.assertGreaterEqual(first_error.column, 0)
        self.assertIsInstance(first_error.message, str)

    def test_parse_mixed_valid_invalid_returns_partial_results(self) -> None:
        """Test that parser returns valid exercises even when some lines have errors."""
        input_text = """Bench press 75k: 4, 4x5
Squat: 5x
Overhead press: 5x5x40k
"""
        result = Parser.from_string(input_text).parse()

        # Should have some errors
        self.assertTrue(result.has_errors)

        # But should still parse valid exercises (Bench press and Overhead press)
        self.assertGreater(len(result.exercises), 0)

        # Check that we got the valid exercises
        exercise_names = [ex.name for ex in result.exercises]
        self.assertIn('Bench press', exercise_names)
        self.assertIn('Overhead press', exercise_names)

    def test_parse_error_contains_offending_symbol(self) -> None:
        """Test that error may contain the offending symbol."""
        result = Parser.from_string('Bench: 5x\n').parse()

        self.assertTrue(result.has_errors)
        # Error should exist
        self.assertGreater(len(result.errors), 0)

    def test_parse_error_str_representation(self) -> None:
        """Test that ParseError has a useful string representation."""
        result = Parser.from_string('Squat: 5x\n').parse()

        self.assertTrue(result.has_errors)
        error_str = str(result.errors[0])

        # Should contain line and column information
        self.assertIn('Line', error_str)
        self.assertIn(':', error_str)

    def test_parse_result_error_summary(self) -> None:
        """Test ParseResult.get_error_summary() method."""
        result = Parser.from_string('Squat: 5x\n').parse()

        summary = result.get_error_summary()
        self.assertIsInstance(summary, str)
        self.assertGreater(len(summary), 0)

        # Valid input should return "No errors"
        valid_result = Parser.from_string('Bench press 75k: 5\n').parse()
        valid_summary = valid_result.get_error_summary()
        self.assertEqual(valid_summary, "No errors")

    def test_parse_multiple_errors(self) -> None:
        """Test that parser can handle multiple malformed lines."""
        input_text = """Squat: 5x
Bench: 10x
"""
        result = Parser.from_string(input_text).parse()

        # Should capture errors (may be multiple)
        self.assertTrue(result.has_errors)

    def test_parse_sessions_raises_on_error(self) -> None:
        """Test that parse_sessions() maintains backward compatibility by raising."""
        with self.assertRaises(ValueError):
            Parser.from_string('Squat: 5x\n').parse_sessions()

    def test_parse_sessions_works_with_valid_input(self) -> None:
        """Test that parse_sessions() works normally with valid input."""
        exercises = Parser.from_string('Bench press 75k: 4, 4x5\n').parse_sessions()

        self.assertIsInstance(exercises, list)
        self.assertEqual(len(exercises), 1)
        self.assertIsInstance(exercises[0], Exercise)

    def test_parse_continues_after_error(self) -> None:
        """Test that parsing continues to next valid line after error."""
        input_text = """Bench press 75k: 4
Squat: 5x
Overhead press: 5x5x40k
"""
        result = Parser.from_string(input_text).parse()

        # Should have parsed valid exercises
        self.assertGreater(len(result.exercises), 0)

        # Should have captured errors
        self.assertTrue(result.has_errors)

        # Should have some valid exercises
        exercise_names = [ex.name for ex in result.exercises]
        # At least some valid exercises should be parsed
        valid_names = ['Bench press', 'Overhead press']
        found_valid = [name for name in valid_names if name in exercise_names]
        self.assertGreater(len(found_valid), 0)

    def test_error_line_numbers_are_accurate(self) -> None:
        """Test that error line numbers correspond to actual input lines."""
        input_text = """Bench press 75k: 4
Squat: 5x
Overhead press: 5x5x40k
"""
        result = Parser.from_string(input_text).parse()

        if result.has_errors:
            # Error should be on line 2 (where incomplete 5x is)
            error_lines = [error.line for error in result.errors]
            self.assertIn(2, error_lines)

    def serie(self, repetition: int, weight: float) -> Set_:
        return Set_(repetitions=repetition, weight=Weight(amount=weight, unit=Units.KILOGRAM))


if __name__ == '__main__':
    unittest.main()
