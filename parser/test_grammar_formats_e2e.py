"""
End-to-End Grammar Format Tests

This test suite provides comprehensive coverage of all possible input formats
supported by the training log grammar. Each test demonstrates a specific format
or combination of formats defined in the ANTLR4 grammar.

The tests serve as both validation and documentation of the grammar's capabilities.

Documentation:
- GRAMMAR_FORMATS.md - Complete format guide with test references
- SYNTAX.md - Detailed syntax documentation with use cases
- parser/test_grammar_formats_e2e_README.md - Information about this test file

Usage:
    make test-grammar-formats                   # Run these tests
    pytest parser/test_grammar_formats_e2e.py -v  # Run with pytest directly
"""
import unittest

from parser import Exercise, Units, Set_, Parser, Weight


class TestGrammarFormatsE2E(unittest.TestCase):
    """
    Comprehensive end-to-end tests for all grammar formats.

    Test organization:
    - Basic Exercise Names
    - Weight Specifications
    - Whole Set Notation (NxNxweight)
    - Group of Reps Notation (weight NxN)
    - Fixed Reps Multiple Weights (Nxxweight,weight,...)
    - Single Rep Notation (weight: N,N,N)
    - Combined/Mixed Formats
    - Edge Cases
    """

    # =============================================================================
    # Helper Methods
    # =============================================================================

    def serie(self, repetition: int, weight: float, rir: int | None = None) -> Set_:
        """Helper to create a Set_ with kilograms."""
        return Set_(repetitions=repetition, weight=Weight(amount=weight, unit=Units.KILOGRAM), rir=rir)

    def parse(self, text: str) -> list[Exercise]:
        """Helper to parse text into exercises."""
        if not text.endswith('\n'):
            text += '\n'
        parser = Parser.from_string(text)
        exercises: list[Exercise] = parser.parse_sessions()
        return exercises

    # =============================================================================
    # Exercise Names
    # =============================================================================

    def test_predefined_exercise_deadlift(self) -> None:
        """Test predefined exercise name: Deadlift"""
        result = self.parse('Deadlift 100k: 5')
        self.assertEqual(result, [Exercise('Deadlift', [self.serie(5, 100)])])

    def test_predefined_exercise_squat(self) -> None:
        """Test predefined exercise name: Squat"""
        result = self.parse('Squat 100k: 5')
        self.assertEqual(result, [Exercise('Squat', [self.serie(5, 100)])])

    def test_predefined_exercise_bench_press(self) -> None:
        """Test predefined exercise name: Bench press"""
        result = self.parse('Bench press 75k: 8')
        self.assertEqual(result, [Exercise('Bench press', [self.serie(8, 75)])])

    def test_predefined_exercise_overhead_press(self) -> None:
        """Test predefined exercise name: Overhead press"""
        result = self.parse('Overhead press 40k: 6')
        self.assertEqual(result, [Exercise('Overhead press', [self.serie(6, 40)])])

    def test_custom_exercise_simple_name(self) -> None:
        """Test custom exercise with simple name"""
        result = self.parse('Bench 60k: 10')
        self.assertEqual(result, [Exercise('Bench', [self.serie(10, 60)])])

    def test_custom_exercise_multi_word_name(self) -> None:
        """Test custom exercise with multiple words"""
        result = self.parse('Row en maquina 41k: 15')
        self.assertEqual(result, [Exercise('Row en maquina', [self.serie(15, 41)])])

    def test_custom_exercise_with_accents(self) -> None:
        """Test custom exercise with accented characters"""
        result = self.parse('Row en máquina 41k: 1')
        self.assertEqual(result, [Exercise('Row en máquina', [self.serie(1, 41)])])

    def test_custom_exercise_with_hyphen(self) -> None:
        """Test custom exercise with hyphen in name"""
        result = self.parse('Cable-fly 20k: 12')
        self.assertEqual(result, [Exercise('Cable-fly', [self.serie(12, 20)])])

    # =============================================================================
    # Weight Specifications
    # =============================================================================

    def test_weight_integer_with_k(self) -> None:
        """Test weight as integer with 'k' suffix"""
        result = self.parse('Squat 100k: 5')
        self.assertEqual(result, [Exercise('Squat', [self.serie(5, 100)])])

    def test_weight_integer_without_k(self) -> None:
        """Test weight as integer without 'k' suffix"""
        result = self.parse('Squat 100: 5')
        self.assertEqual(result, [Exercise('Squat', [self.serie(5, 100)])])

    def test_weight_decimal_with_k(self) -> None:
        """Test weight as decimal with 'k' suffix"""
        result = self.parse('Bench press 62.5k: 5')
        self.assertEqual(result, [Exercise('Bench press', [self.serie(5, 62.5)])])

    def test_weight_decimal_without_k(self) -> None:
        """Test weight as decimal without 'k' suffix"""
        result = self.parse('Bench press 62.5: 5')
        self.assertEqual(result, [Exercise('Bench press', [self.serie(5, 62.5)])])

    # =============================================================================
    # Whole Set Notation (NxNxweight)
    # =============================================================================

    def test_whole_set_basic(self) -> None:
        """Test basic whole set notation: NxNxweight"""
        result = self.parse('Overhead press: 5x6x40k')
        expected = [self.serie(6, 40) for _ in range(5)]
        self.assertEqual(result, [Exercise('Overhead press', expected)])

    def test_whole_set_single_set(self) -> None:
        """Test whole set notation with single set: 1xNxweight"""
        result = self.parse('Deadlift: 1x1x100k')
        self.assertEqual(result, [Exercise('Deadlift', [self.serie(1, 100)])])

    def test_whole_set_multiple_sets(self) -> None:
        """Test whole set notation with multiple sets"""
        result = self.parse('Bench press: 3x8x75k')
        expected = [self.serie(8, 75) for _ in range(3)]
        self.assertEqual(result, [Exercise('Bench press', expected)])

    def test_whole_set_decimal_weight(self) -> None:
        """Test whole set notation with decimal weight"""
        result = self.parse('Squat: 3x5x82.5k')
        expected = [self.serie(5, 82.5) for _ in range(3)]
        self.assertEqual(result, [Exercise('Squat', expected)])

    def test_whole_set_without_k_suffix(self) -> None:
        """Test whole set notation without 'k' suffix on weight"""
        result = self.parse('Squat: 3x5x100')
        expected = [self.serie(5, 100) for _ in range(3)]
        self.assertEqual(result, [Exercise('Squat', expected)])

    def test_whole_set_with_rir(self) -> None:
        """Test whole set notation with RIR (Reps in Reserve)"""
        result = self.parse('Squat: 3x5x100k-2')
        expected = [self.serie(5, 100, rir=2) for _ in range(3)]
        self.assertEqual(result, [Exercise('Squat', expected)])

    # =============================================================================
    # Group of Reps Notation (weight NxN)
    # =============================================================================

    def test_group_of_reps_with_colon(self) -> None:
        """Test group of reps notation with colon separator"""
        result = self.parse('Squat 70k: 5x10')
        expected = [self.serie(10, 70) for _ in range(5)]
        self.assertEqual(result, [Exercise('Squat', expected)])

    def test_group_of_reps_without_colon(self) -> None:
        """Test group of reps notation without colon separator"""
        result = self.parse('Squat 70k 5x10')
        expected = [self.serie(10, 70) for _ in range(5)]
        self.assertEqual(result, [Exercise('Squat', expected)])

    def test_group_of_reps_single_set(self) -> None:
        """Test group of reps notation with single set"""
        result = self.parse('Deadlift 100k: 1x5')
        self.assertEqual(result, [Exercise('Deadlift', [self.serie(5, 100)])])

    def test_group_of_reps_decimal_weight(self) -> None:
        """Test group of reps notation with decimal weight"""
        result = self.parse('Bench press 67.5k: 3x8')
        expected = [self.serie(8, 67.5) for _ in range(3)]
        self.assertEqual(result, [Exercise('Bench press', expected)])

    # =============================================================================
    # Fixed Reps Multiple Weights (Nxxweight,weight,...)
    # =============================================================================

    def test_fixed_reps_two_weights(self) -> None:
        """Test fixed reps with two different weights"""
        result = self.parse('Squat: 15xx40k,50k')
        expected = [self.serie(15, 40), self.serie(15, 50)]
        self.assertEqual(result, [Exercise('Squat', expected)])

    def test_fixed_reps_three_weights(self) -> None:
        """Test fixed reps with three different weights"""
        result = self.parse('Bench press: 8xx60k,70k,80k')
        expected = [self.serie(8, 60), self.serie(8, 70), self.serie(8, 80)]
        self.assertEqual(result, [Exercise('Bench press', expected)])

    def test_fixed_reps_four_weights(self) -> None:
        """Test fixed reps with four different weights (warmup progression)"""
        result = self.parse('Deadlift: 5xx100,110,120,130')
        expected = [self.serie(5, 100), self.serie(5, 110), self.serie(5, 120), self.serie(5, 130)]
        self.assertEqual(result, [Exercise('Deadlift', expected)])

    def test_fixed_reps_decimal_weights(self) -> None:
        """Test fixed reps with decimal weights"""
        result = self.parse('Squat: 8xx60.5,70.5,80.5')
        expected = [self.serie(8, 60.5), self.serie(8, 70.5), self.serie(8, 80.5)]
        self.assertEqual(result, [Exercise('Squat', expected)])

    def test_fixed_reps_progressive_overload(self) -> None:
        """Test fixed reps for progressive overload session"""
        result = self.parse('Squat: 5xx60k,70k,80k,90k,100k')
        expected = [self.serie(5, weight) for weight in [60, 70, 80, 90, 100]]
        self.assertEqual(result, [Exercise('Squat', expected)])

    # =============================================================================
    # Single Rep Notation (weight: N,N,N)
    # =============================================================================

    def test_single_rep_with_colon(self) -> None:
        """Test single rep notation with colon separator"""
        result = self.parse('Deadlift 60k: 20, 15, 8, 8')
        expected = [self.serie(i, 60) for i in [20, 15, 8, 8]]
        self.assertEqual(result, [Exercise('Deadlift', expected)])

    def test_single_rep_without_spaces(self) -> None:
        """Test single rep notation without spaces after commas"""
        result = self.parse('Deadlift 60k: 20,15,8,8')
        expected = [self.serie(i, 60) for i in [20, 15, 8, 8]]
        self.assertEqual(result, [Exercise('Deadlift', expected)])

    def test_single_rep_descending_reps(self) -> None:
        """Test single rep notation with descending reps (fatigue)"""
        result = self.parse('Bench press 75k: 4, 4, 3, 2')
        expected = [self.serie(i, 75) for i in [4, 4, 3, 2]]
        self.assertEqual(result, [Exercise('Bench press', expected)])

    def test_single_rep_two_sets(self) -> None:
        """Test single rep notation with just two sets"""
        result = self.parse('Row en maquina 41k: 15, 8')
        expected = [self.serie(15, 41), self.serie(8, 41)]
        self.assertEqual(result, [Exercise('Row en maquina', expected)])

    def test_single_rep_single_set(self) -> None:
        """Test single rep notation with single set"""
        result = self.parse('Deadlift 100k: 5')
        self.assertEqual(result, [Exercise('Deadlift', [self.serie(5, 100)])])

    # =============================================================================
    # Combined/Mixed Formats
    # =============================================================================

    def test_mixed_single_and_group_with_colon(self) -> None:
        """Test mixing single rep and group of reps with colon"""
        result = self.parse('Bench press 10k: 4, 4x5')
        expected = [self.serie(4, 10)] + [self.serie(5, 10) for _ in range(4)]
        self.assertEqual(result, [Exercise('Bench press', expected)])

    def test_mixed_single_and_group_without_colon(self) -> None:
        """Test mixing single rep and group of reps without colon"""
        result = self.parse('Bench press 10k 4, 4x5')
        expected = [self.serie(4, 10)] + [self.serie(5, 10) for _ in range(4)]
        self.assertEqual(result, [Exercise('Bench press', expected)])

    def test_mixed_whole_sets(self) -> None:
        """Test multiple whole set notations in sequence"""
        result = self.parse('Bench press 1x1x60k 1x2x40k')
        expected = [self.serie(1, 60), self.serie(2, 40)]
        self.assertEqual(result, [Exercise('Bench press', expected)])

    def test_mixed_three_whole_sets(self) -> None:
        """Test three different whole set notations (e.g., drop sets)"""
        result = self.parse('Bench press 3x50x10k 3x15x10k 3x6x10k')
        expected = (
            [self.serie(50, 10) for _ in range(3)] +
            [self.serie(15, 10) for _ in range(3)] +
            [self.serie(6, 10) for _ in range(3)]
        )
        self.assertEqual(result, [Exercise('Bench press', expected)])

    def test_mixed_whole_set_and_single_rep(self) -> None:
        """Test mixing whole set notation with single rep notation"""
        result = self.parse('Bench press 3x50x10k 60: 12,11')
        expected = (
            [self.serie(50, 10) for _ in range(3)] +
            [self.serie(12, 60), self.serie(11, 60)]
        )
        self.assertEqual(result, [Exercise('Bench press', expected)])

    def test_mixed_whole_set_and_single_rep_with_k(self) -> None:
        """Test mixing whole set notation with single rep notation (weight has 'k')"""
        result = self.parse('Bench press 3x50x10k 60k: 12,11')
        expected = (
            [self.serie(50, 10) for _ in range(3)] +
            [self.serie(12, 60), self.serie(11, 60)]
        )
        self.assertEqual(result, [Exercise('Bench press', expected)])

    def test_mixed_single_then_whole_sets(self) -> None:
        """Test single reps followed by whole set notations"""
        result = self.parse('Bench 60k: 2,3, 1x1x60k 1x2x40k')
        expected = [
            self.serie(2, 60),
            self.serie(3, 60),
            self.serie(1, 60),
            self.serie(2, 40)
        ]
        self.assertEqual(result, [Exercise('Bench', expected)])

    def test_mixed_fixed_reps_and_whole_set(self) -> None:
        """Test fixed reps multiple weights mixed with whole set notation"""
        result = self.parse('Squat: 15xx40,50 1x1x10k')
        expected = [
            self.serie(15, 40),
            self.serie(15, 50),
            self.serie(1, 10)
        ]
        self.assertEqual(result, [Exercise('Squat', expected)])

    def test_mixed_fixed_reps_and_single_rep(self) -> None:
        """Test fixed reps multiple weights mixed with single rep notation"""
        result = self.parse('Squat: 15xx40,50 60k: 12,11')
        expected = [
            self.serie(15, 40),
            self.serie(15, 50),
            self.serie(12, 60),
            self.serie(11, 60)
        ]
        self.assertEqual(result, [Exercise('Squat', expected)])

    def test_complex_mixed_format(self) -> None:
        """Test complex mixing of multiple formats"""
        result = self.parse('Squat 60k: 10, 3x8x80k, 5xx100k,110k,120k')
        expected = [
            self.serie(10, 60),
            self.serie(8, 80),
            self.serie(8, 80),
            self.serie(8, 80),
            self.serie(5, 100),
            self.serie(5, 110),
            self.serie(5, 120)
        ]
        self.assertEqual(result, [Exercise('Squat', expected)])

    # =============================================================================
    # Multiple Exercises
    # =============================================================================

    def test_multiple_exercises_simple(self) -> None:
        """Test multiple exercises in a workout"""
        result = self.parse(
            'Bench press 75k: 8\n'
            'Squat 100k: 5\n'
        )
        expected = [
            Exercise('Bench press', [self.serie(8, 75)]),
            Exercise('Squat', [self.serie(5, 100)])
        ]
        self.assertEqual(result, expected)

    def test_multiple_exercises_complex(self) -> None:
        """Test complete workout session with multiple exercises"""
        result = self.parse(
            'Bench press 75k: 4, 4x5\n'
            'Squat 70k: 5x10\n'
            'Overhead press: 5x5x40k\n'
            'Deadlift 60k: 20, 15,8,8\n'
            'Row en maquina 41k: 15, 8\n'
        )
        expected = [
            Exercise('Bench press', [self.serie(4, 75)] + [self.serie(5, 75) for _ in range(4)]),
            Exercise('Squat', [self.serie(10, 70) for _ in range(5)]),
            Exercise('Overhead press', [self.serie(5, 40) for _ in range(5)]),
            Exercise('Deadlift', [self.serie(i, 60) for i in [20, 15, 8, 8]]),
            Exercise('Row en maquina', [self.serie(15, 41), self.serie(8, 41)])
        ]
        self.assertEqual(result, expected)

    def test_multiple_exercises_progressive_overload(self) -> None:
        """Test progressive overload workout session"""
        result = self.parse(
            'Squat: 5xx60k,70k,80k,90k,100k\n'
            'Bench press: 5xx40k,50k,60k,70k\n'
            'Deadlift: 3xx100k,120k,140k\n'
        )
        expected = [
            Exercise('Squat', [self.serie(5, w) for w in [60, 70, 80, 90, 100]]),
            Exercise('Bench press', [self.serie(5, w) for w in [40, 50, 60, 70]]),
            Exercise('Deadlift', [self.serie(3, w) for w in [100, 120, 140]])
        ]
        self.assertEqual(result, expected)

    # =============================================================================
    # Edge Cases and Special Scenarios
    # =============================================================================

    def test_exercise_with_extra_newlines(self) -> None:
        """Test exercise with multiple trailing newlines"""
        result = self.parse('Squat 100k: 5\n\n\n')
        self.assertEqual(result, [Exercise('Squat', [self.serie(5, 100)])])

    def test_multiple_exercises_with_blank_lines(self) -> None:
        """Test multiple exercises separated by blank lines"""
        result = self.parse(
            'Bench press 75k: 8\n'
            '\n'
            'Squat 100k: 5\n'
        )
        expected = [
            Exercise('Bench press', [self.serie(8, 75)]),
            Exercise('Squat', [self.serie(5, 100)])
        ]
        self.assertEqual(result, expected)

    def test_weight_zero_integer(self) -> None:
        """Test with zero weight (bodyweight exercises)"""
        result = self.parse('Push-up 0k: 20')
        self.assertEqual(result, [Exercise('Push-up', [self.serie(20, 0)])])

    def test_weight_zero_decimal(self) -> None:
        """Test with zero decimal weight"""
        result = self.parse('Pull-up 0.0k: 10')
        self.assertEqual(result, [Exercise('Pull-up', [self.serie(10, 0.0)])])

    def test_single_digit_reps(self) -> None:
        """Test with single digit reps"""
        result = self.parse('Squat 100k: 1')
        self.assertEqual(result, [Exercise('Squat', [self.serie(1, 100)])])

    def test_double_digit_reps(self) -> None:
        """Test with double digit reps"""
        result = self.parse('Squat 60k: 50')
        self.assertEqual(result, [Exercise('Squat', [self.serie(50, 60)])])

    def test_triple_digit_reps(self) -> None:
        """Test with triple digit reps (endurance training)"""
        result = self.parse('Squat 20k: 100')
        self.assertEqual(result, [Exercise('Squat', [self.serie(100, 20)])])

    def test_many_sets_whole_notation(self) -> None:
        """Test with many sets using whole set notation"""
        result = self.parse('Bench press: 10x5x60k')
        expected = [self.serie(5, 60) for _ in range(10)]
        self.assertEqual(result, [Exercise('Bench press', expected)])

    def test_pyramid_training_session(self) -> None:
        """Test pyramid training (up and down)"""
        result = self.parse('Bench press: 12xx40k,50k,60k,70k 10xx80k 12xx70k,60k,50k,40k')
        expected = (
            [self.serie(12, w) for w in [40, 50, 60, 70]] +
            [self.serie(10, 80)] +
            [self.serie(12, w) for w in [70, 60, 50, 40]]
        )
        self.assertEqual(result, [Exercise('Bench press', expected)])

    def test_drop_set_pattern(self) -> None:
        """Test drop set pattern (same reps, decreasing weight)"""
        result = self.parse('Bench press: 8xx80k,60k,40k,20k')
        expected = [self.serie(8, w) for w in [80, 60, 40, 20]]
        self.assertEqual(result, [Exercise('Bench press', expected)])

    # =============================================================================
    # Dot Notation for Whole Sets (N.N.weight)
    # =============================================================================

    def test_dot_notation_basic(self) -> None:
        """Test basic dot notation: 1.10.23"""
        result = self.parse('Bench press: 1.10.23')
        self.assertEqual(result, [Exercise('Bench press', [self.serie(10, 23)])])

    def test_dot_notation_with_k_suffix(self) -> None:
        """Test dot notation with k suffix: 1.10.23k"""
        result = self.parse('Bench press: 1.10.23k')
        self.assertEqual(result, [Exercise('Bench press', [self.serie(10, 23)])])

    def test_dot_notation_multiple_sets(self) -> None:
        """Test dot notation with multiple sets: 3.8.100k"""
        result = self.parse('Squat: 3.8.100k')
        expected = [self.serie(8, 100) for _ in range(3)]
        self.assertEqual(result, [Exercise('Squat', expected)])

    def test_dot_notation_decimal_weight(self) -> None:
        """Test dot notation with decimal weight: 1.5.62.5k"""
        result = self.parse('Deadlift: 1.5.62.5k')
        self.assertEqual(result, [Exercise('Deadlift', [self.serie(5, 62.5)])])

    def test_dot_notation_decimal_weight_no_k(self) -> None:
        """Test dot notation with decimal weight without k suffix"""
        result = self.parse('Bench: 2.8.75.5')
        expected = [self.serie(8, 75.5) for _ in range(2)]
        self.assertEqual(result, [Exercise('Bench', expected)])

    def test_dot_notation_with_rir(self) -> None:
        """Test dot notation with RIR: 3.8.100k 2"""
        result = self.parse('Squat: 3.8.100k 2')
        expected = [self.serie(8, 100, rir=2) for _ in range(3)]
        self.assertEqual(result, [Exercise('Squat', expected)])

    def test_dot_notation_five_sets(self) -> None:
        """Test dot notation with five sets"""
        result = self.parse('Bench press: 5.6.80k')
        expected = [self.serie(6, 80) for _ in range(5)]
        self.assertEqual(result, [Exercise('Bench press', expected)])

    # =============================================================================
    # Range Notation for Fixed Reps (N..weight/weight)
    # =============================================================================

    def test_range_notation_basic(self) -> None:
        """Test basic range notation: 10..23/24"""
        result = self.parse('Squat: 10..23/24')
        expected = [self.serie(10, 23), self.serie(10, 24)]
        self.assertEqual(result, [Exercise('Squat', expected)])

    def test_range_notation_three_weights(self) -> None:
        """Test range notation with three weights: 8..60/70/80"""
        result = self.parse('Bench: 8..60/70/80')
        expected = [self.serie(8, w) for w in [60, 70, 80]]
        self.assertEqual(result, [Exercise('Bench', expected)])

    def test_range_notation_with_k_suffix(self) -> None:
        """Test range notation with k suffix on weights"""
        result = self.parse('Press: 10..23k/24k')
        expected = [self.serie(10, 23), self.serie(10, 24)]
        self.assertEqual(result, [Exercise('Press', expected)])

    def test_range_notation_decimal_weights(self) -> None:
        """Test range notation with decimal weights: 5..40.5/42.5/45"""
        result = self.parse('Squat: 5..40.5/42.5/45')
        expected = [self.serie(5, w) for w in [40.5, 42.5, 45]]
        self.assertEqual(result, [Exercise('Squat', expected)])

    def test_range_notation_single_weight(self) -> None:
        """Test range notation with single weight: 10..50"""
        result = self.parse('Bench: 10..50')
        self.assertEqual(result, [Exercise('Bench', [self.serie(10, 50)])])

    def test_range_notation_four_weights(self) -> None:
        """Test range notation with four weights (progressive overload)"""
        result = self.parse('Squat: 5..60/70/80/90')
        expected = [self.serie(5, w) for w in [60, 70, 80, 90]]
        self.assertEqual(result, [Exercise('Squat', expected)])

    def test_range_notation_warmup_progression(self) -> None:
        """Test range notation for warmup progression"""
        result = self.parse('Deadlift: 5..100/110/120/130/140')
        expected = [self.serie(5, w) for w in [100, 110, 120, 130, 140]]
        self.assertEqual(result, [Exercise('Deadlift', expected)])

    # =============================================================================
    # Mixed Dot and Range Notation
    # =============================================================================

    def test_mixed_dot_and_x_notation(self) -> None:
        """Test mixing dot notation with x notation"""
        result = self.parse('Squat: 5xx60k,70k,80k 1.8.100k')
        expected = [self.serie(5, 60), self.serie(5, 70), self.serie(5, 80), self.serie(8, 100)]
        self.assertEqual(result, [Exercise('Squat', expected)])

    def test_mixed_range_and_whole_set(self) -> None:
        """Test mixing range notation with whole set notation"""
        result = self.parse('Bench: 3x8x75k 10..80/85/90')
        expected = [self.serie(8, 75) for _ in range(3)] + [self.serie(10, w) for w in [80, 85, 90]]
        self.assertEqual(result, [Exercise('Bench', expected)])

    def test_mixed_dot_and_range_notation(self) -> None:
        """Test mixing dot notation with range notation"""
        result = self.parse('Squat: 1.10.23 1.10.23.5 10..25/27.5/30')
        expected = [self.serie(10, 23), self.serie(10, 23.5)] + [self.serie(10, w) for w in [25, 27.5, 30]]
        self.assertEqual(result, [Exercise('Squat', expected)])

    def test_mixed_all_notations(self) -> None:
        """Test complex mixing of all notation types"""
        result = self.parse('Squat: 60k: 10, 3.8.80k, 5xx100k,110k, 8..120/130')
        expected = [
            self.serie(10, 60),
            self.serie(8, 80),
            self.serie(8, 80),
            self.serie(8, 80),
            self.serie(5, 100),
            self.serie(5, 110),
            self.serie(8, 120),
            self.serie(8, 130)
        ]
        self.assertEqual(result, [Exercise('Squat', expected)])

    def test_dot_notation_multiple_sequences(self) -> None:
        """Test multiple dot notation sequences in one exercise"""
        result = self.parse('Bench press: 1.10.60k 1.8.70k 1.6.80k')
        expected = [self.serie(10, 60), self.serie(8, 70), self.serie(6, 80)]
        self.assertEqual(result, [Exercise('Bench press', expected)])

    def test_range_notation_multiple_sequences(self) -> None:
        """Test multiple range notation sequences in one exercise"""
        result = self.parse('Squat: 10..60/70 8..80/90 5..100/110')
        expected = [
            self.serie(10, 60),
            self.serie(10, 70),
            self.serie(8, 80),
            self.serie(8, 90),
            self.serie(5, 100),
            self.serie(5, 110)
        ]
        self.assertEqual(result, [Exercise('Squat', expected)])

    # =============================================================================
    # Error Cases
    # =============================================================================

    def test_invalid_syntax_raises_error(self) -> None:
        """Test that invalid syntax raises ValueError"""
        valid_input = 'Deadlift: 1x20x20k'
        wrong_input = valid_input.removesuffix("k") + "l"
        with self.assertRaises(ValueError):
            self.parse(wrong_input)

    def test_missing_newline_handled(self) -> None:
        """Test that parser handles missing newline (helper adds it)"""
        # Our helper adds newline, so this should work
        result = Parser.from_string('Squat 100k: 5\n').parse_sessions()
        self.assertEqual(result, [Exercise('Squat', [self.serie(5, 100)])])


if __name__ == '__main__':
    unittest.main()
