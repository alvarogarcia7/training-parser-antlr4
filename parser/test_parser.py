import unittest

from parser import Exercise, Units, Repetition, Parser


class TestParser(unittest.TestCase):
    def test_canary(self) -> None:
        self.assertTrue(True)

    def test_visit_sessions_mixing_single_and_multiple(self) -> None:
        result = Parser.from_string('Bench press 10k: 4, 4x5\n').parse_sessions()

        self.assertListEqual(result,
                             [Exercise('Bench press', [self.serie(10, 4)] + [self.serie(10, 5) for _ in range(5)])])

    def test_visit_sessions_only_multiple(self) -> None:
        result = Parser.from_string('Squat 70k: 5x10').parse_sessions()

        self.assertListEqual(result, [Exercise('Squat', [self.serie(10, 5) for _ in range(5)])])

    def test_visit_sessions_multi_series_format(self) -> None:
        result = Parser.from_string('Overhead press 5x6x40k\n').parse_sessions()

        self.assertListEqual(result, [Exercise('Overhead press', [self.serie(40, 6) for _ in range(5)])])

    def test_visit_sessions_multi_singles_format(self) -> None:
        result = Parser.from_string('Deadlift 60k: 20, 15,8,8\n').parse_sessions()

        self.assertListEqual(result, [Exercise('Deadlift', [self.serie(60, i) for i in [20, 15, 8, 8]])])

    def serie(self, amount: int, repetition: int) -> Repetition:
        return {'repetitions': repetition, 'weight': {'amount': amount, 'unit': Units.KILOGRAM}}
