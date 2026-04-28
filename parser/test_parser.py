import unittest

from parser import Exercise, Units, Set_, Parser, Weight
from parser.parser import ParsingException


class TestParser(unittest.TestCase):
    def test_canary(self) -> None:
        self.assertTrue(True)

    def test_visit_sessions_mixing_single_and_multiple(self) -> None:
        result = Parser.from_string('Bench press 10k: 4, 4x5\n').parse_sessions()

        self.assertListEqual(result, [Exercise('Bench press', [self.serie(i, 10) for i in [4] + 4 * [5]])])

    def test_visit_sessions_mixing_single_and_multiple_no_colon(self) -> None:
        result = Parser.from_string('Bench press 10k 4, 4x5\n').parse_sessions()

        self.assertListEqual(result, [Exercise('Bench press', [self.serie(i, 10) for i in [4] + 4 * [5]])])

    def test_visit_sessions_only_multiple(self) -> None:
        result = Parser.from_string('Squat 70k: 5x10\n').parse_sessions()

        self.assertListEqual(result, [Exercise('Squat', [self.serie(10, 70) for _ in range(5)])])

    def test_visit_sessions_only_multiple_no_colon(self) -> None:
        result = Parser.from_string('Squat 70k 5x10\n').parse_sessions()

        self.assertListEqual(result, [Exercise('Squat', [self.serie(10, 70) for _ in range(5)])])

    def test_visit_sessions_multi_series_format(self) -> None:
        result = Parser.from_string('Overhead press 5x6x40k\n').parse_sessions()

        self.assertListEqual(result, [Exercise('Overhead press', [self.serie(6, 40) for _ in range(5)])])

    def test_visit_sessions_multi_singles_format(self) -> None:
        result = Parser.from_string('Deadlift 60k: 20, 15,8,8\n').parse_sessions()

        self.assertListEqual(result, [Exercise('Deadlift', [self.serie(i, 60) for i in [20, 15, 8, 8]])])

    def test_visit_sessions_another_exercise(self) -> None:
        result = Parser.from_string('Row en maquina 41k: 15, 8\n').parse_sessions()

        self.assertListEqual(result, [Exercise('Row en maquina', [self.serie(i, 41) for i in [15, 8]])])

    def test_visit_sessions_support_multiple_multi_series_format(self) -> None:
        result = Parser.from_string('Bench 1x1x60k 1x2x40k\n').parse_sessions()

        self.assertListEqual(result, [Exercise('Bench', [self.serie(1, 60)] + [self.serie(2, 40)])])

    def test_visit_sessions_support_three_multi_series_format(self) -> None:
        result = Parser.from_string('Bench press 3x50x10k 3x15x10k 3x6x10k\n').parse_sessions()

        self.assertListEqual(result, [Exercise('Bench press',
                                               [self.serie(50, 10) for _ in range(3)]
                                               + [self.serie(15, 10) for _ in range(3)]
                                               + [self.serie(6, 10) for _ in range(3)]
                                               )])

    def test_visit_sessions_support_mixing_straight_series_and_variable_repetitions(self) -> None:
        result = Parser.from_string('Bench press 3x50x10k 60: 12,11\n').parse_sessions()

        self.assertListEqual(result, [Exercise('Bench press',
                                               [self.serie(50, 10) for _ in range(3)]
                                               + [self.serie(i, 60) for i in [12, 11]]
                                               )])

    def test_visit_sessions_support_mixing_straight_series_and_variable_repetitions_with_kg(self) -> None:
        result = Parser.from_string('Bench press 3x50x10k 60k: 12,11\n').parse_sessions()

        self.assertListEqual(result, [Exercise('Bench press',
                                               [self.serie(50, 10) for _ in range(3)]
                                               + [self.serie(i, 60) for i in [12, 11]]
                                               )])

    def test_visit_sessions_support_mixed_formats__singles_then_multi_series(self) -> None:
        result = Parser.from_string('Bench 60k: 2,3, 1x1x60k 1x2x40k\n').parse_sessions()

        self.assertListEqual(result, [Exercise('Bench',
                                               [self.serie(i, 60) for i in [2, 3]]
                                               + [self.serie(1, 60)]
                                               + [self.serie(2, 40)])])

    # ===== Phase 2: iOS-friendly keyboard syntax =====

    def test_phase2_dot_separator_whole_set(self) -> None:
        """Dot (.) as single separator equivalent to x"""
        result = Parser.from_string('Ms: 1.20.24\n').parse_sessions()
        self.assertListEqual(result, [Exercise('Ms', [self.serie(20, 24) for _ in range(1)])])

    def test_phase2_dot_separator_three_components(self) -> None:
        """Dot (.) with three components"""
        result = Parser.from_string('Ms: 5.5.39\n').parse_sessions()
        self.assertListEqual(result, [Exercise('Ms', [self.serie(5, 39) for _ in range(5)])])

    def test_phase2_double_dot_separator(self) -> None:
        """Double dot (..) as equivalent to xx"""
        result = Parser.from_string('Ms: 5..80,90,100\n').parse_sessions()
        self.assertListEqual(result, [Exercise('Ms', [self.serie(5, weight) for weight in [80, 90, 100]])])

    def test_phase2_slash_delimited_weights_integers(self) -> None:
        """Slash (/) as weight separator with integer weights"""
        result = Parser.from_string('Ms: 20xx40/50/60\n').parse_sessions()
        self.assertListEqual(result, [Exercise('Ms', [self.serie(20, weight) for weight in [40, 50, 60]])])

    def test_phase2_slash_delimited_with_comma_decimals(self) -> None:
        """Slash (/) with comma as decimal point"""
        result = Parser.from_string('Ms: 1.20.24/27,5/28,1\n').parse_sessions()
        expected = ([self.serie(20, 24) for _ in range(1)]
                   + [self.serie(20, 27.5)]
                   + [self.serie(20, 28.1)])
        self.assertListEqual(result, [Exercise('Ms', expected)])

    def test_phase2_bare_comma_decimal_weight(self) -> None:
        """Standalone comma-decimal weight (e.g. 62,5 as 62.5)"""
        result = Parser.from_string('Ms: 62,5\n').parse_sessions()
        # This should parse as a weight, with no nested set
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'Ms')

    def test_phase2_rir_single_rep(self) -> None:
        """RIR (Reps In Reserve) dash notation on single rep"""
        result = Parser.from_string('Ms: 39-4\n').parse_sessions()
        self.assertListEqual(result, [Exercise('Ms', [self.serie(39, 0, rir=4)])])

    def test_phase2_rir_group_of_reps(self) -> None:
        """RIR dash notation on group of reps (Note: 15.18-3 now parsed as Point 4: 15 reps@18kg RIR3, not group_of_rep_set)"""
        result = Parser.from_string('Ms: 15.18-3\n').parse_sessions()
        self.assertListEqual(result, [Exercise('Ms', [self.serie(15, 18, rir=3)])])

    def test_phase2_rir_whole_set(self) -> None:
        """RIR dash notation on whole set"""
        result = Parser.from_string('Ms: 5.5.39-8\n').parse_sessions()
        self.assertListEqual(result, [Exercise('Ms', [self.serie(5, 39, rir=8) for _ in range(5)])])

    def test_phase2_rir_whole_set_v1_style(self) -> None:
        """RIR dash notation with v1 whole set syntax"""
        result = Parser.from_string('Ms: 3x5x100k-2\n').parse_sessions()
        self.assertListEqual(result, [Exercise('Ms', [self.serie(5, 100, rir=2) for _ in range(3)])])

    def test_phase2_rir_fixed_reps_multi_weight(self) -> None:
        """RIR dash notation on fixed reps with multiple weights"""
        result = Parser.from_string('Ms: 5xx80,90,100-3\n').parse_sessions()
        self.assertListEqual(result, [Exercise('Ms', [self.serie(5, weight, rir=3) for weight in [80, 90, 100]])])

    def test_phase2_rir_v2_multi_weight_whole_set(self) -> None:
        """RIR dash notation on v2 multi-weight whole set"""
        result = Parser.from_string('Ms: 1.20.24/27,5/28,1-3\n').parse_sessions()
        expected = ([self.serie(20, 24, rir=3) for _ in range(1)]
                   + [self.serie(20, 27.5, rir=3)]
                   + [self.serie(20, 28.1, rir=3)])
        self.assertListEqual(result, [Exercise('Ms', expected)])

    def test_phase2_multiple_single_reps_with_rir(self) -> None:
        """Multiple single reps, each with its own RIR"""
        result = Parser.from_string('Ms: 5-2, 3-1\n').parse_sessions()
        self.assertListEqual(result, [Exercise('Ms', [self.serie(5, 0, rir=2), self.serie(3, 0, rir=1)])])

    def test_phase2_mixed_rir_in_compound(self) -> None:
        """RIR attaches to inner set in compound"""
        result = Parser.from_string('Ms: 5, 3-2\n').parse_sessions()
        self.assertListEqual(result, [Exercise('Ms', [self.serie(5, 0), self.serie(3, 0, rir=2)])])

    # ===== Regression tests: backwards compatibility =====

    def test_regression_whole_set(self) -> None:
        """Backwards compatibility: whole set syntax"""
        result = Parser.from_string('Squat: 5x5x100\n').parse_sessions()
        self.assertListEqual(result, [Exercise('Squat', [self.serie(5, 100) for _ in range(5)])])

    def test_regression_deadlift(self) -> None:
        """Backwards compatibility: deadlift example"""
        result = Parser.from_string('Deadlift: 1x5x140\n').parse_sessions()
        self.assertListEqual(result, [Exercise('Deadlift', [self.serie(5, 140)])])

    def test_regression_fixed_reps_multi_weight(self) -> None:
        """Backwards compatibility: fixed reps with multiple weights"""
        result = Parser.from_string('Bench press: 5xx80,90,100\n').parse_sessions()
        self.assertListEqual(result, [Exercise('Bench press', [self.serie(5, weight) for weight in [80, 90, 100]])])

    def test_regression_group_of_reps(self) -> None:
        """Backwards compatibility: group of reps"""
        result = Parser.from_string('Overhead press: 3x10\n').parse_sessions()
        self.assertListEqual(result, [Exercise('Overhead press', [self.serie(10, 0) for _ in range(3)])])

    def test_regression_weight_with_nested_set(self) -> None:
        """Backwards compatibility: weight with nested set"""
        result = Parser.from_string('Squat: 80.5: 5x5\n').parse_sessions()
        self.assertListEqual(result, [Exercise('Squat', [self.serie(5, 80.5) for _ in range(5)])])

    def test_regression_bare_weight(self) -> None:
        """Backwards compatibility: bare weight (no nested set)"""
        result = Parser.from_string('Squat: 80.5\n').parse_sessions()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'Squat')

    def test_regression_single_rep(self) -> None:
        """Backwards compatibility: single rep"""
        result = Parser.from_string('Deadlift: 5\n').parse_sessions()
        self.assertListEqual(result, [Exercise('Deadlift', [self.serie(5, 0)])])

    def test_disabled_test_dots_visit_sessions_support_mixed_formats__singles_then_multi_series(self) -> None:
        result = Parser.from_string('Bench 60k: 2,3, 1.1.60k, 1.2.40k\n').parse_sessions()

        self.assertListEqual(result, [Exercise('Bench',
                                               [self.serie(i, 60) for i in [2, 3]]
                                               + [self.serie(1, 60)]
                                               + [self.serie(2, 40)])])

    def test_visit_sessions_can_parse_accents(self) -> None:
        result = Parser.from_string('Row en máquina 41k: 1\n').parse_sessions()

        self.assertListEqual(result, [Exercise('Row en máquina', [self.serie(1, 41)])])

    def test_parse_format_of_fixed_repetitions(self) -> None:
        result = Parser.from_string('Squat: 15xx40k\n').parse_sessions()

        print(result)

        self.assertListEqual(result, [Exercise('Squat', [self.serie(15, 40)])])

    def test_parse_format_of_multiple_fixed_repetitions(self) -> None:
        result = Parser.from_string('Squat: 15xx40,50\n').parse_sessions()

        print(result)

        self.assertListEqual(result, [Exercise('Squat', [self.serie(15, weight) for weight in [40, 50]])])

    def test_parse_format_of_multiple_fixed_repetitions_mixed_with_multi_series_format(self) -> None:
        result = Parser.from_string('Squat: 15xx40,50 1x1x10k\n').parse_sessions()

        self.assertListEqual(result,
                             [Exercise('Squat', [self.serie(15, weight) for weight in [40, 50]] + [self.serie(1, 10)])])

    def test_parse_format_of_multiple_fixed_repetitions_mixed_with_fixed_weight(self) -> None:
        result = Parser.from_string('Squat: 15xx40,50 60k: 12,11\n').parse_sessions()

        expected_series = [self.serie(15, weight) for weight in [40, 50]] + [self.serie(i, 60) for i in [12, 11]]
        assert len(expected_series) == 4
        self.assertListEqual(result, [Exercise('Squat', expected_series)])

    # ===== PRD Point 4: Single Series N.weight format =====

    def test_prd_point4_reps_weight_basic(self) -> None:
        """Point 4: Basic N.weight with k suffix - 10 reps at 23kg"""
        result = Parser.from_string('Bench: 10.23k\n').parse_sessions()
        self.assertListEqual(result, [Exercise('Bench', [self.serie(10, 23)])])

    def test_prd_point4_reps_weight_larger_weight(self) -> None:
        """Point 4: N.weight with larger weight value"""
        result = Parser.from_string('Squat: 5.100k\n').parse_sessions()
        self.assertListEqual(result, [Exercise('Squat', [self.serie(5, 100)])])

    def test_prd_point4_reps_weight_small_reps(self) -> None:
        """Point 4: N.weight with 1 rep"""
        result = Parser.from_string('Deadlift: 1.140k\n').parse_sessions()
        self.assertListEqual(result, [Exercise('Deadlift', [self.serie(1, 140)])])

    def test_prd_point4_reps_weight_with_rir(self) -> None:
        """Point 4: N.weight with RIR dash notation"""
        result = Parser.from_string('Squat: 5.100k-2\n').parse_sessions()
        self.assertListEqual(result, [Exercise('Squat', [self.serie(5, 100, rir=2)])])

    def test_prd_point4_reps_weight_multiple_reps_with_rir(self) -> None:
        """Point 4: N.weight with more reps and RIR"""
        result = Parser.from_string('Bench: 10.75k-3\n').parse_sessions()
        self.assertListEqual(result, [Exercise('Bench', [self.serie(10, 75, rir=3)])])

    def test_prd_point4_reps_weight_colon_context(self) -> None:
        """Point 4: weight with colon still works as weight_ context (not N.weight)"""
        result = Parser.from_string('Squat: 80.5k: 5x3\n').parse_sessions()
        self.assertListEqual(result, [Exercise('Squat', [self.serie(3, 80.5) for _ in range(5)])])

    def test_prd_point4_mixed_with_other_formats(self) -> None:
        """Point 4: N.weight mixed with x notation"""
        result = Parser.from_string('Bench: 3x5x60k 10.50k\n').parse_sessions()
        expected = [self.serie(5, 60) for _ in range(3)] + [self.serie(10, 50)]
        self.assertListEqual(result, [Exercise('Bench', expected)])

    # ===== RIR Support: Verify both x and dot notation modes =====

    def test_rir_x_notation_single_rep(self) -> None:
        """RIR with x notation: single rep with RIR"""
        result = Parser.from_string('Ms: 20-3\n').parse_sessions()
        self.assertListEqual(result, [Exercise('Ms', [self.serie(20, 0, rir=3)])])

    def test_rir_x_notation_group_of_reps(self) -> None:
        """RIR with x notation: group of reps (NxN-RIR)"""
        result = Parser.from_string('Ms: 3x10-2\n').parse_sessions()
        self.assertListEqual(result, [Exercise('Ms', [self.serie(10, 0, rir=2) for _ in range(3)])])

    def test_rir_x_notation_whole_set(self) -> None:
        """RIR with x notation: whole set (NxNxweight-RIR)"""
        result = Parser.from_string('Ms: 3x5x100-2\n').parse_sessions()
        self.assertListEqual(result, [Exercise('Ms', [self.serie(5, 100, rir=2) for _ in range(3)])])

    def test_rir_dot_notation_single_rep(self) -> None:
        """RIR with dot notation: single rep with RIR"""
        result = Parser.from_string('Ms: 20-3\n').parse_sessions()  # Same as x, no dot in single rep
        self.assertListEqual(result, [Exercise('Ms', [self.serie(20, 0, rir=3)])])

    def test_rir_dot_notation_group_of_reps(self) -> None:
        """RIR with dot notation: Point 4 (N.weight-RIR) takes priority over group_of_rep_set"""
        result = Parser.from_string('Ms: 3.10-2\n').parse_sessions()
        self.assertListEqual(result, [Exercise('Ms', [self.serie(3, 10, rir=2)])])

    def test_rir_dot_notation_whole_set(self) -> None:
        """RIR with dot notation: whole set (N.N.weight-RIR)"""
        result = Parser.from_string('Ms: 3.5.100-2\n').parse_sessions()
        self.assertListEqual(result, [Exercise('Ms', [self.serie(5, 100, rir=2) for _ in range(3)])])

    def test_rir_point4_n_weight_notation(self) -> None:
        """RIR with Point 4: N.weight format (N.weightk-RIR)"""
        result = Parser.from_string('Ms: 5.100k-2\n').parse_sessions()
        self.assertListEqual(result, [Exercise('Ms', [self.serie(5, 100, rir=2)])])

    def test_raise_error_on_wrong_input(self) -> None:
        valid_input = 'Deadlift: 1x20x20k'
        wrong_input = valid_input.removesuffix("k") + "l"
        with self.assertRaises(ParsingException):
            Parser.from_string(wrong_input + "\n").parse_sessions()

    def test_dot_notation_basic(self) -> None:
        result = Parser.from_string('Bench press: 1.10.23\n').parse_sessions()

        self.assertListEqual(result, [Exercise('Bench press', [self.serie(10, 23)])])

    def test_dot_notation_with_k_suffix(self) -> None:
        result = Parser.from_string('Bench press: 1.10.23k\n').parse_sessions()

        self.assertListEqual(result, [Exercise('Bench press', [self.serie(10, 23)])])

    def test_dot_notation_multiple_sets(self) -> None:
        result = Parser.from_string('Squat: 3.8.100k\n').parse_sessions()

        self.assertListEqual(result, [Exercise('Squat', [self.serie(8, 100) for _ in range(3)])])

    def test_dot_notation_decimal_weight(self) -> None:
        result = Parser.from_string('Deadlift: 1.5.62.5k\n').parse_sessions()

        self.assertListEqual(result, [Exercise('Deadlift', [self.serie(5, 62.5)])])

    def test_dot_notation_decimal_weight_no_k(self) -> None:
        result = Parser.from_string('Bench: 2.8.75.5\n').parse_sessions()

        self.assertListEqual(result, [Exercise('Bench', [self.serie(8, 75.5) for _ in range(2)])])

    def test_dot_notation_with_rir(self) -> None:
        result = Parser.from_string('Squat: 3.8.100k 2\n').parse_sessions()

        self.assertListEqual(result, [Exercise('Squat', [Set_(repetitions=8, weight=Weight(amount=100, unit=Units.KILOGRAM), rir=2) for _ in range(3)])])

    def test_range_notation_basic(self) -> None:
        result = Parser.from_string('Squat: 10..23/24\n').parse_sessions()

        self.assertListEqual(result, [Exercise('Squat', [self.serie(10, 23), self.serie(10, 24)])])

    def test_range_notation_three_weights(self) -> None:
        result = Parser.from_string('Bench: 8..60/70/80\n').parse_sessions()

        self.assertListEqual(result, [Exercise('Bench', [self.serie(8, weight) for weight in [60, 70, 80]])])

    def test_range_notation_with_k_suffix(self) -> None:
        result = Parser.from_string('Press: 10..23k/24k\n').parse_sessions()

        self.assertListEqual(result, [Exercise('Press', [self.serie(10, 23), self.serie(10, 24)])])

    def test_range_notation_decimal_weights(self) -> None:
        result = Parser.from_string('Squat: 5..40.5/42.5/45\n').parse_sessions()

        self.assertListEqual(result, [Exercise('Squat', [self.serie(5, weight) for weight in [40.5, 42.5, 45]])])

    def test_range_notation_single_weight(self) -> None:
        result = Parser.from_string('Bench: 10..50\n').parse_sessions()

        self.assertListEqual(result, [Exercise('Bench', [self.serie(10, 50)])])

    def test_mixed_dot_and_x_notation(self) -> None:
        result = Parser.from_string('Squat: 5xx60k,70k,80k 1.8.100k\n').parse_sessions()

        self.assertListEqual(result, [Exercise('Squat', [self.serie(5, 60), self.serie(5, 70), self.serie(5, 80), self.serie(8, 100)])])

    def test_mixed_range_and_whole_set(self) -> None:
        result = Parser.from_string('Bench: 3x8x75k 10..80/85/90\n').parse_sessions()

        expected = [self.serie(8, 75) for _ in range(3)] + [self.serie(10, weight) for weight in [80, 85, 90]]
        self.assertListEqual(result, [Exercise('Bench', expected)])

    def test_mixed_dot_and_range_notation(self) -> None:
        result = Parser.from_string('Squat: 1.10.23 1.10.23.5 10..25/27.5/30\n').parse_sessions()

        expected = [self.serie(10, 23), self.serie(10, 23.5)] + [self.serie(10, weight) for weight in [25, 27.5, 30]]
        self.assertListEqual(result, [Exercise('Squat', expected)])

    def serie(self, repetition: int, weight: float, rir: int | None = None) -> Set_:
        return Set_(repetitions=repetition, weight=Weight(amount=weight, unit=Units.KILOGRAM), rir=rir)
