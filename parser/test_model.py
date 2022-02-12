import unittest

from parser import Exercise, Units


class TestModel(unittest.TestCase):
    def test_exercise_is_different_when_name_is_different(self) -> None:
        self.assertNotEqual(Exercise('a', []), Exercise('b', []))

    def test_exercise_is_different_when_repetitions_are_different(self) -> None:
        repetition = 1
        amount = 10
        self.assertNotEqual(
            Exercise('b', [{'repetitions': repetition, 'weight': {'amount': amount, 'unit': Units.KILOGRAM}}]),
            Exercise('b', []))
