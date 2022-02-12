import unittest

from parser import Exercise, Units, Repetition, Parser


class TestParser(unittest.TestCase):
    def test_canary(self) -> None:
        self.assertTrue(True)

    def test_visit_sessions(self) -> None:
        result = Parser.from_string('Bench press 10k: 4, 4x5\n').parse_sessions()

        self.assertListEqual(result,
                             [Exercise('Bench press', [self.serie(10, 4)] + [self.serie(10, 5) for _ in range(5)])])
        self.assertEqual(True, True)

    def serie(self, amount: int, repetition: int) -> Repetition:
        return {'repetitions': repetition, 'weight': {'amount': amount, 'unit': Units.KILOGRAM}}
