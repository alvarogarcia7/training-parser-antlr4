import unittest

from parser import Exercise, Units, Set_, Parser, Weight


class TestParser(unittest.TestCase):
    def test_canary(self) -> None:
        self.assertTrue(True)

    def test_visit_sessions_mixing_single_and_multiple(self) -> None:
        result = Parser.from_string('Bench press 10k: 4, 4x5\n').parse_sessions()

        self.assertListEqual(result, [(Exercise('Bench press', [self.serie(i, 10) for i in [4] + 4 * [5]]))])

    def test_visit_sessions_mixing_single_and_multiple_no_colon(self) -> None:
        result = Parser.from_string('Bench press 10k 4, 4x5\n').parse_sessions()

        self.assertListEqual(result, [(Exercise('Bench press', [self.serie(i, 10) for i in [4] + 4 * [5]]))])

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

    def disabled_test_dots_visit_sessions_support_mixed_formats__singles_then_multi_series(self) -> None:
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
        with self.assertRaises(ValueError):
            Parser.from_string(wrong_input + "\n").parse_sessions()

    def serie(self, repetition: int, weight: float) -> Set_:
        return Set_(repetitions=repetition, weight=Weight(amount=weight, unit=Units.KILOGRAM))
