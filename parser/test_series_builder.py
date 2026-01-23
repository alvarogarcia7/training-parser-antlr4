import unittest

from parser import SeriesBuilder, Exercise, Set_, Weight, Units


class TestSeriesBuilder(unittest.TestCase):
    def setUp(self) -> None:
        self.builder = SeriesBuilder()

    def test_set_exercise_name(self) -> None:
        self.builder.set_exercise_name("Squat")
        self.assertEqual(self.builder.name, "Squat")

    def test_add_weight(self) -> None:
        self.builder.add_weight(100.0)
        self.assertEqual(self.builder.pending_weights, [100.0])

    def test_add_series(self) -> None:
        self.builder.add_series(10, 100.0)
        self.assertEqual(len(self.builder.sets), 1)
        self.assertEqual(self.builder.sets[0].repetitions, 10)
        self.assertEqual(self.builder.sets[0].weight.amount, 100.0)

    def test_add_whole_set(self) -> None:
        self.builder.add_whole_set(3, 5, 50.0)
        self.assertEqual(len(self.builder.sets), 3)
        for set_ in self.builder.sets:
            self.assertEqual(set_.repetitions, 5)
            self.assertEqual(set_.weight.amount, 50.0)
        self.assertEqual(self.builder.pending_weights, [])

    def test_add_group_of_reps(self) -> None:
        self.builder.add_weight(75.0)
        self.builder.add_group_of_reps(4, 8)
        self.assertEqual(len(self.builder.sets), 4)
        for set_ in self.builder.sets:
            self.assertEqual(set_.repetitions, 8)
            self.assertEqual(set_.weight.amount, 75.0)
        self.assertEqual(self.builder.pending_weights, [75.0])

    def test_add_single_rep_set(self) -> None:
        self.builder.add_weight(60.0)
        self.builder.add_weight(70.0)
        self.builder.add_single_rep_set(10)
        self.assertEqual(len(self.builder.sets), 2)
        self.assertEqual(self.builder.sets[0].repetitions, 10)
        self.assertEqual(self.builder.sets[0].weight.amount, 60.0)
        self.assertEqual(self.builder.sets[1].repetitions, 10)
        self.assertEqual(self.builder.sets[1].weight.amount, 70.0)
        self.assertEqual(self.builder.pending_weights, [60.0, 70.0])

    def test_add_fixed_reps_multiple_weights(self) -> None:
        self.builder.add_weight(40.0)
        self.builder.add_weight(50.0)
        self.builder.add_fixed_reps_multiple_weights(15)
        self.assertEqual(len(self.builder.sets), 2)
        self.assertEqual(self.builder.sets[0].repetitions, 15)
        self.assertEqual(self.builder.sets[0].weight.amount, 40.0)
        self.assertEqual(self.builder.sets[1].repetitions, 15)
        self.assertEqual(self.builder.sets[1].weight.amount, 50.0)
        self.assertEqual(self.builder.pending_weights, [])
        self.assertEqual(self.builder.pending_repetitions, [])

    def test_addSeriesIfComplete_with_complete_data(self) -> None:
        self.builder.set_exercise_name("Bench press")
        self.builder.add_series(10, 60.0)
        exercise = self.builder.addSeriesIfComplete()
        self.assertIsNotNone(exercise)
        assert exercise is not None
        self.assertEqual(exercise.name, "Bench press")
        self.assertEqual(len(exercise.sets_), 1)
        self.assertEqual(self.builder.name, "")
        self.assertEqual(self.builder.sets, [])

    def test_addSeriesIfComplete_without_name(self) -> None:
        self.builder.add_series(10, 60.0)
        exercise = self.builder.addSeriesIfComplete()
        self.assertIsNone(exercise)

    def test_addSeriesIfComplete_without_sets(self) -> None:
        self.builder.set_exercise_name("Squat")
        exercise = self.builder.addSeriesIfComplete()
        self.assertIsNone(exercise)

    def test_reset(self) -> None:
        self.builder.set_exercise_name("Deadlift")
        self.builder.add_weight(100.0)
        self.builder.add_series(5, 100.0)
        self.builder.reset()
        self.assertEqual(self.builder.name, "")
        self.assertEqual(self.builder.sets, [])
        self.assertEqual(self.builder.pending_weights, [])
        self.assertEqual(self.builder.pending_repetitions, [])

    def test_build_with_complete_data(self) -> None:
        self.builder.set_exercise_name("Overhead press")
        self.builder.add_series(8, 40.0)
        exercise = self.builder.build()
        self.assertEqual(exercise.name, "Overhead press")
        self.assertEqual(len(exercise.sets_), 1)

    def test_build_without_name_raises_error(self) -> None:
        self.builder.add_series(10, 60.0)
        with self.assertRaises(ValueError) as context:
            self.builder.build()
        self.assertIn("Exercise name not set", str(context.exception))

    def test_complex_workout_scenario(self) -> None:
        self.builder.set_exercise_name("Squat")
        self.builder.add_whole_set(3, 5, 100.0)
        self.builder.add_weight(80.0)
        self.builder.add_single_rep_set(10)
        exercise = self.builder.build()
        self.assertEqual(exercise.name, "Squat")
        self.assertEqual(len(exercise.sets_), 4)
        for i in range(3):
            self.assertEqual(exercise.sets_[i].repetitions, 5)
            self.assertEqual(exercise.sets_[i].weight.amount, 100.0)
        self.assertEqual(exercise.sets_[3].repetitions, 10)
        self.assertEqual(exercise.sets_[3].weight.amount, 80.0)


if __name__ == '__main__':
    unittest.main()
