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

    def test_exercise_group_by_weight_and_repetitions__should_flatten_when_all_match(self) -> None:
        unflattened = Exercise('name',
                               [{'repetitions': 10, 'weight': {'amount': 40.0, 'unit': 'kg'}},
                                {'repetitions': 10, 'weight': {'amount': 40.0, 'unit': 'kg'}},
                                {'repetitions': 6, 'weight': {'amount': 40.0, 'unit': 'kg'}}])
        flattened_list_by_weight_and_repetitions = [
            Exercise('name', [
                {'repetitions': 10, 'weight': {'amount': 40.0, 'unit': 'kg'}},
                {'repetitions': 10, 'weight': {'amount': 40.0, 'unit': 'kg'}}
            ]),
            Exercise('name', [{'repetitions': 6, 'weight': {'amount': 40.0, 'unit': 'kg'}}])
        ]

        self.assertEqual(unflattened.flatten(), flattened_list_by_weight_and_repetitions)

    def test_exercise_group_by_weight_requires_exact_repetitions_and_weight(self) -> None:
        unflattened = Exercise('name',
                               [{'repetitions': 50, 'weight': {'amount': 20.0, 'unit': 'kg'}},
                                {'repetitions': 15, 'weight': {'amount': 40.0, 'unit': 'kg'}},
                                {'repetitions': 6, 'weight': {'amount': 60.0, 'unit': 'kg'}}])
        flattened_list_by_weight_and_repetitions = [
            Exercise('name', [{'repetitions': 50, 'weight': {'amount': 20.0, 'unit': 'kg'}}]),
            Exercise('name', [{'repetitions': 15, 'weight': {'amount': 40.0, 'unit': 'kg'}}]),
            Exercise('name', [{'repetitions': 6, 'weight': {'amount': 60.0, 'unit': 'kg'}}])
        ]

        self.assertEqual(unflattened.flatten(), flattened_list_by_weight_and_repetitions)

    def test_exercise_group_by_weight_and_repetitions_requires_exact_repetitions(self) -> None:
        unflattened = Exercise('name',
                               [{'repetitions': 10, 'weight': {'amount': 40.0, 'unit': 'kg'}},
                                {'repetitions': 6, 'weight': {'amount': 40.0, 'unit': 'kg'}}])
        flattened_list_by_weight_and_repetitions = [
            Exercise('name', [{'repetitions': 10, 'weight': {'amount': 40.0, 'unit': 'kg'}}]),
            Exercise('name', [{'repetitions': 6, 'weight': {'amount': 40.0, 'unit': 'kg'}}])
        ]
        self.assertEqual(unflattened.flatten(), flattened_list_by_weight_and_repetitions)

    def test_exercise_group_by_weight_and_repetitions_requires_exact_weight(self) -> None:
        unflattened = Exercise('name',
                               [{'repetitions': 10, 'weight': {'amount': 40.0, 'unit': 'kg'}},
                                {'repetitions': 10, 'weight': {'amount': 50.0, 'unit': 'kg'}}])
        flattened_list_by_weight = [
            Exercise('name', [{'repetitions': 10, 'weight': {'amount': 40.0, 'unit': 'kg'}}]),
            Exercise('name', [{'repetitions': 10, 'weight': {'amount': 50.0, 'unit': 'kg'}}])
        ]

        self.assertEqual(unflattened.flatten(), flattened_list_by_weight)

    def test_flattened_exercise__should_repr_for_object(self) -> None:
        exercise = Exercise('name',
                            [{'repetitions': 10, 'weight': {'amount': 40.0, 'unit': 'kg'}},
                             {'repetitions': 6, 'weight': {'amount': 40.0, 'unit': 'kg'}}])
        self.assertEqual(exercise.__repr__(), "name: 1x10@40.0kg, 1x6@40.0kg")

    def test_unflattened_exercise__should_repr_for_object(self) -> None:
        exercise = Exercise('name',
                            [{'repetitions': 10, 'weight': {'amount': 40.0, 'unit': 'kg'}},
                             {'repetitions': 10, 'weight': {'amount': 40.0, 'unit': 'kg'}},
                             {'repetitions': 6, 'weight': {'amount': 40.0, 'unit': 'kg'}}])
        self.assertEqual("name: 2x10@40.0kg, 1x6@40.0kg", exercise.__repr__())
