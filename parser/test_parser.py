import unittest

from parser import Exercise, Units, Repetition, Parser


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

    def test_visit_sessions_can_parse_accents(self) -> None:
        result = Parser.from_string('Row en máquina 41k: 1\n').parse_sessions()

        self.assertListEqual(result, [Exercise('Row en máquina', [self.serie(1, 41)])])

    def serie(self, repetition: int, weight: float) -> Repetition:
        return {'repetitions': repetition, 'weight': {'amount': weight, 'unit': Units.KILOGRAM}}
