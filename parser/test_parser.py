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

    def test_dots_visit_sessions_support_mixed_formats__singles_then_multi_series(self) -> None:
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
