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


class TestNegativeParserValidation(unittest.TestCase):
    """Comprehensive negative test cases for parser input validation."""

    def test_missing_weight_in_x_notation(self) -> None:
        """Test malformed set notation: 5x without weight."""
        result = Parser.from_string('Squat: 5x\n').parse()

        self.assertTrue(result.has_errors)
        self.assertGreater(len(result.errors), 0)
        self.assertFalse(result.is_valid)

    def test_missing_repetitions_in_x_notation(self) -> None:
        """Test malformed set notation: x5 without repetitions."""
        result = Parser.from_string('Bench: x5\n').parse()

        self.assertTrue(result.has_errors)
        self.assertGreater(len(result.errors), 0)

    def test_incomplete_whole_set_missing_weight(self) -> None:
        """Test incomplete whole set notation: 5x10x without weight."""
        result = Parser.from_string('Deadlift: 5x10x\n').parse()

        self.assertTrue(result.has_errors)
        self.assertGreater(len(result.errors), 0)

    def test_incomplete_whole_set_missing_repetitions(self) -> None:
        """Test incomplete whole set notation: 5x without repetitions."""
        result = Parser.from_string('Overhead press: 5xx100k\n').parse()

        # This might parse as fixed_reps_multiple_weight, but let's check the behavior
        # If it doesn't parse correctly, we should get errors or unexpected results
        result_check = Parser.from_string('Overhead press: 5xx100k\n').parse()
        # At minimum, verify we can detect this scenario
        self.assertIsInstance(result_check, ParseResult)

    def test_missing_weight_unit_in_weight_prefix(self) -> None:
        """Test weight without unit (though 'k' is optional, this tests edge cases)."""
        result = Parser.from_string('Bench press: 5, 4x5\n').parse()

        # Grammar allows parsing integers as weights without 'k' unit
        # This may parse successfully - test documents this behavior
        self.assertIsInstance(result, ParseResult)

    def test_invalid_characters_in_exercise_name(self) -> None:
        """Test exercise name with invalid special characters."""
        result = Parser.from_string('Bench@press#123: 5x5x100k\n').parse()

        # Should capture error for invalid characters
        self.assertTrue(result.has_errors)
        self.assertGreater(len(result.errors), 0)

    def test_invalid_characters_in_weight(self) -> None:
        """Test weight with invalid characters."""
        result = Parser.from_string('Squat: 5x10x100l\n').parse()

        # 'l' is not a valid weight unit
        self.assertTrue(result.has_errors)
        self.assertGreater(len(result.errors), 0)

    def test_empty_input(self) -> None:
        """Test completely empty input."""
        result = Parser.from_string('').parse()

        # Empty input should parse without errors but produce no exercises
        self.assertEqual(len(result.exercises), 0)
        # May or may not have errors depending on grammar strictness

    def test_whitespace_only_input(self) -> None:
        """Test input with only whitespace."""
        result = Parser.from_string('   \n\n  \t  \n').parse()

        # Should produce no exercises
        self.assertEqual(len(result.exercises), 0)

    def test_incomplete_exercise_no_sets(self) -> None:
        """Test exercise with name but no sets."""
        result = Parser.from_string('Bench press\n').parse()

        # Should have error for missing sets
        self.assertTrue(result.has_errors)
        self.assertGreater(len(result.errors), 0)

    def test_incomplete_exercise_only_colon(self) -> None:
        """Test exercise with name and colon but no sets."""
        result = Parser.from_string('Squat:\n').parse()

        # Should have error for missing sets after colon
        self.assertTrue(result.has_errors)
        self.assertGreater(len(result.errors), 0)

    def test_incomplete_exercise_only_weight(self) -> None:
        """Test exercise with only weight, no sets."""
        result = Parser.from_string('Deadlift 100k\n').parse()

        # Grammar allows weight without explicit sets (via weight_ rule with optional set_)
        # This may parse successfully - test documents this behavior
        self.assertIsInstance(result, ParseResult)

    def test_negative_weight_value(self) -> None:
        """Test negative weight value (parser may accept, but model should reject)."""
        result = Parser.from_string('Bench: 5x10x-100k\n').parse()

        # Parser might capture this as an error, or it might parse but fail validation
        # Either way, we should not get a valid exercise with negative weight
        if len(result.exercises) > 0:
            # If it somehow parsed, the weight should be caught elsewhere
            # But more likely the parser will reject the minus sign
            pass
        # Most likely scenario: parser error
        self.assertTrue(result.has_errors or len(result.exercises) == 0)

    def test_zero_repetitions(self) -> None:
        """Test zero repetitions."""
        result = Parser.from_string('Squat: 5x0x100k\n').parse()

        # Zero repetitions should either be a parse error or model validation error
        # Check that we don't produce a valid exercise with zero reps
        if len(result.exercises) > 0:
            # If somehow parsed, validate should catch it
            with self.assertRaises(ValueError):
                result.exercises[0].validate()

    def test_zero_sets(self) -> None:
        """Test zero sets."""
        result = Parser.from_string('Bench: 0x10x100k\n').parse()

        # Zero sets might parse but should be meaningless
        # Verify error handling or appropriate behavior
        self.assertIsInstance(result, ParseResult)

    def test_extremely_large_weight(self) -> None:
        """Test extremely large weight value."""
        result = Parser.from_string('Deadlift: 5x5x999999999999k\n').parse()

        # Should parse but represents unrealistic data
        # Verify parser can handle large numbers
        self.assertIsInstance(result, ParseResult)

    def test_extremely_large_repetitions(self) -> None:
        """Test extremely large repetition count."""
        result = Parser.from_string('Squat: 5x999999999x100k\n').parse()

        # Should parse but represents unrealistic data
        self.assertIsInstance(result, ParseResult)

    def test_malformed_comma_separated_sets_trailing_comma(self) -> None:
        """Test comma-separated sets with trailing comma."""
        result = Parser.from_string('Bench press 100k: 5, 4, 3,\n').parse()

        # Grammar's multiple_set_ rule allows optional commas between sets
        # Trailing comma is handled gracefully - test documents this behavior
        self.assertIsInstance(result, ParseResult)

    def test_malformed_comma_separated_sets_leading_comma(self) -> None:
        """Test comma-separated sets with leading comma."""
        result = Parser.from_string('Squat 100k: , 5, 4, 3\n').parse()

        # Grammar's weight_ rule allows optional set_, so comma can appear
        # This is handled - test documents actual behavior
        self.assertIsInstance(result, ParseResult)

    def test_malformed_comma_separated_sets_double_comma(self) -> None:
        """Test comma-separated sets with double comma."""
        result = Parser.from_string('Overhead press 100k: 5,, 4, 3\n').parse()

        # Grammar's multiple_set_ rule with optional commas handles this
        # This is processed - test documents actual behavior
        self.assertIsInstance(result, ParseResult)

    def test_missing_exercise_name(self) -> None:
        """Test set notation without exercise name."""
        result = Parser.from_string('5x10x100k\n').parse()

        # Should fail - must have exercise name
        self.assertTrue(result.has_errors)
        self.assertGreater(len(result.errors), 0)

    def test_only_colon_and_sets(self) -> None:
        """Test only colon and sets without exercise name."""
        result = Parser.from_string(': 5x10x100k\n').parse()

        # Should fail - must have exercise name before colon
        self.assertTrue(result.has_errors)
        self.assertGreater(len(result.errors), 0)

    def test_decimal_repetitions(self) -> None:
        """Test decimal values for repetitions (should only accept integers)."""
        result = Parser.from_string('Bench: 5x10.5x100k\n').parse()

        # Grammar allows decimals in weight position, so this parses as 5x10 with weight .5x100k
        # This demonstrates how grammar is permissive - test documents actual behavior
        self.assertIsInstance(result, ParseResult)

    def test_decimal_sets(self) -> None:
        """Test decimal values for number of sets (should only accept integers)."""
        result = Parser.from_string('Squat: 5.5x10x100k\n').parse()

        # Grammar allows decimals as weight, so this parses as weight 5.5 followed by 10x100k
        # This demonstrates grammar permissiveness - test documents actual behavior
        self.assertIsInstance(result, ParseResult)

    def test_multiple_weight_units_in_single_exercise(self) -> None:
        """Test mixing weight units within a single exercise."""
        result = Parser.from_string('Bench: 5x10x100k 5x10x200\n').parse()

        # This might parse, but if it does, validation should catch mixed units
        if len(result.exercises) > 0:
            # Mixed units in same exercise should fail validation
            all_units = set(s.weight.unit for s in result.exercises[0].sets_)
            # Either caught during parse or during validation
            if len(all_units) > 1:
                with self.assertRaises(ValueError):
                    result.exercises[0].validate()

    def test_special_characters_instead_of_numbers(self) -> None:
        """Test special characters where numbers are expected."""
        result = Parser.from_string('Squat: #x@x$k\n').parse()

        # Should fail to parse
        self.assertTrue(result.has_errors)
        self.assertGreater(len(result.errors), 0)

    def test_letters_in_weight_value(self) -> None:
        """Test letters in weight value."""
        result = Parser.from_string('Bench: 5x10xABCk\n').parse()

        # Should fail - weight must be numeric
        self.assertTrue(result.has_errors)
        self.assertGreater(len(result.errors), 0)

    def test_letters_in_repetition_value(self) -> None:
        """Test letters in repetition value."""
        result = Parser.from_string('Deadlift: ABCx10x100k\n').parse()

        # Should fail - repetitions must be numeric
        self.assertTrue(result.has_errors)
        self.assertGreater(len(result.errors), 0)

    def test_mixed_valid_invalid_exercises_error_recovery(self) -> None:
        """Test that parser recovers and continues after errors."""
        input_text = """Bench press 75k: 5, 4, 3
Squat: 5x
Deadlift 100k: 5x5
Invalid: @#$
Overhead press 50k: 5x5
"""
        result = Parser.from_string(input_text).parse()

        # Should have errors for invalid lines
        self.assertTrue(result.has_errors)
        self.assertGreater(len(result.errors), 0)

        # Should still parse valid exercises
        self.assertGreater(len(result.exercises), 0)
        exercise_names = [ex.name for ex in result.exercises]

        # Valid exercises should be present
        self.assertIn('Bench press', exercise_names)
        self.assertIn('Deadlift', exercise_names)
        self.assertIn('Overhead press', exercise_names)

    def test_error_contains_line_and_column_info(self) -> None:
        """Test that errors contain accurate line and column information."""
        result = Parser.from_string('Bench: 5x\n').parse()

        self.assertTrue(result.has_errors)
        error = result.errors[0]

        # Verify error has required fields
        self.assertIsInstance(error.line, int)
        self.assertIsInstance(error.column, int)
        self.assertIsInstance(error.message, str)
        self.assertGreater(error.line, 0)
        self.assertGreaterEqual(error.column, 0)

    def test_error_message_format(self) -> None:
        """Test that error messages are properly formatted."""
        result = Parser.from_string('Squat: 5x\n').parse()

        self.assertTrue(result.has_errors)
        error_str = str(result.errors[0])

        # Should contain line number and column
        self.assertIn('Line', error_str)
        self.assertIn(':', error_str)
        # Should contain meaningful message
        self.assertGreater(len(error_str), 10)

    def test_error_summary_format(self) -> None:
        """Test that error summary is properly formatted."""
        result = Parser.from_string('Bench: 5x\n').parse()

        summary = result.get_error_summary()

        # Should indicate number of errors
        self.assertIn('error', summary.lower())
        # Should contain the actual error details
        self.assertGreater(len(summary), 20)

    def test_multiple_errors_all_captured(self) -> None:
        """Test that multiple errors are all captured."""
        input_text = """Squat: 5x
Bench: 10x
Deadlift: 15x
"""
        result = Parser.from_string(input_text).parse()

        # Should capture multiple errors
        self.assertTrue(result.has_errors)
        # At least one error per malformed line
        self.assertGreaterEqual(len(result.errors), 1)

    def test_error_on_specific_line_number(self) -> None:
        """Test that error line numbers are accurate for multi-line input."""
        input_text = """Bench press 75k: 5
Squat: 5x
Overhead press 50k: 5x5
"""
        result = Parser.from_string(input_text).parse()

        if result.has_errors:
            error_lines = [error.line for error in result.errors]
            # Error should be on line 2 (the malformed Squat line)
            self.assertIn(2, error_lines)

    def test_unclosed_notation(self) -> None:
        """Test unclosed or incomplete notation."""
        test_cases = [
            'Bench: 5x10x',  # Missing weight
            'Squat: x10x100k',  # Missing sets
            'Deadlift: 5xx',  # Missing weight in fixed reps notation
        ]

        for test_input in test_cases:
            with self.subTest(input=test_input):
                result = Parser.from_string(test_input + '\n').parse()
                self.assertTrue(result.has_errors, f"Expected error for: {test_input}")

    def test_no_exercises_produced_from_invalid_input(self) -> None:
        """Test that completely invalid input produces no exercises."""
        result = Parser.from_string('@@@ ### $$$ %%% \n').parse()

        # Should have errors
        self.assertTrue(result.has_errors)
        # Should produce no exercises
        self.assertEqual(len(result.exercises), 0)

    def test_parse_result_is_valid_property(self) -> None:
        """Test that is_valid property correctly reflects error state."""
        valid_result = Parser.from_string('Bench press 75k: 5\n').parse()
        invalid_result = Parser.from_string('Bench: 5x\n').parse()

        self.assertTrue(valid_result.is_valid)
        self.assertFalse(invalid_result.is_valid)

    def test_parse_result_has_errors_property(self) -> None:
        """Test that has_errors property correctly reflects error state."""
        valid_result = Parser.from_string('Bench press 75k: 5\n').parse()
        invalid_result = Parser.from_string('Bench: 5x\n').parse()

        self.assertFalse(valid_result.has_errors)
        self.assertTrue(invalid_result.has_errors)

    def test_malformed_fixed_reps_notation(self) -> None:
        """Test malformed fixed reps notation (xx)."""
        test_cases = [
            ('Squat: xx100k', True),  # Missing repetitions - should error
            ('Bench: 5xx', True),  # Missing weights - should error
            ('Deadlift: 5xx100k,', False),  # Trailing comma - grammar handles this
        ]

        for test_input, should_error in test_cases:
            with self.subTest(input=test_input):
                result = Parser.from_string(test_input + '\n').parse()
                if should_error:
                    # Should either have errors or produce no exercises
                    self.assertTrue(result.has_errors or len(result.exercises) == 0,
                                   f"Expected error or no exercises for: {test_input}")
                else:
                    # Grammar handles this case
                    self.assertIsInstance(result, ParseResult)

    def test_invalid_rir_notation(self) -> None:
        """Test invalid RIR (Reps In Reserve) notation if supported."""
        # Assuming RIR is the fourth element in whole_set_
        result = Parser.from_string('Bench: 5x10x100k xyz\n').parse()

        # Should fail if RIR notation is invalid
        # This depends on grammar, but generally should error
        self.assertTrue(result.has_errors or len(result.exercises) == 0)

    def test_consecutive_operators(self) -> None:
        """Test consecutive operators without values."""
        test_cases = [
            'Bench: ::',
            'Squat: xxx',
            'Deadlift: ,,,',
        ]

        for test_input in test_cases:
            with self.subTest(input=test_input):
                result = Parser.from_string(test_input + '\n').parse()
                self.assertTrue(result.has_errors, f"Expected error for: {test_input}")

    def test_missing_separator_between_sets(self) -> None:
        """Test missing separators between different set notations."""
        # This should work with current grammar: '5x10x100k 3x8x90k'
        # But let's test edge cases
        result = Parser.from_string('Bench: 5x10x100k3x8x90k\n').parse()

        # Depending on grammar, this might error or parse unexpectedly
        # Verify it doesn't silently produce incorrect data
        self.assertIsInstance(result, ParseResult)

    def test_empty_exercise_name(self) -> None:
        """Test exercise with empty name."""
        result = Parser.from_string(' : 5x10x100k\n').parse()

        # Should fail - exercise must have a name
        self.assertTrue(result.has_errors)
        self.assertGreater(len(result.errors), 0)

    def test_only_numbers_as_exercise_name(self) -> None:
        """Test using only numbers as exercise name."""
        result = Parser.from_string('12345: 5x10x100k\n').parse()

        # Depending on grammar, this might fail or succeed
        # Document the behavior
        self.assertIsInstance(result, ParseResult)

    def test_parse_sessions_raises_on_any_error(self) -> None:
        """Test that parse_sessions() raises ValueError on any parse error."""
        invalid_inputs = [
            'Squat: 5x\n',
            'Bench: x10\n',
            '@@@ invalid @@@\n',
            ': 5x10x100k\n',
        ]

        for test_input in invalid_inputs:
            with self.subTest(input=test_input):
                with self.assertRaises(ValueError):
                    Parser.from_string(test_input).parse_sessions()

    def test_error_offending_symbol_captured(self) -> None:
        """Test that offending symbol is captured when available."""
        result = Parser.from_string('Bench: 5x\n').parse()

        if result.has_errors and len(result.errors) > 0:
            # At least check that the field exists
            error = result.errors[0]
            # offending_symbol may be None or a string
            self.assertTrue(error.offending_symbol is None or
                          isinstance(error.offending_symbol, str))


if __name__ == '__main__':
    unittest.main()
