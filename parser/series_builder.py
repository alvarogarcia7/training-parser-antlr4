from typing import Optional

from . import Exercise, Units, Weight, Set_


class SeriesBuilder:
    def __init__(self) -> None:
        self.name: str = ""
        self.sets: list[Set_] = []
        self.pending_weights: list[float] = []
        self.pending_repetitions: list[int] = []

    def set_exercise_name(self, name: str) -> None:
        self.name = name

    def add_weight(self, weight: float) -> None:
        self.pending_weights.append(weight)

    def add_series(self, repetitions: int, weight: float, rir: int | None = None) -> None:
        self.sets.append(Set_(repetitions=repetitions, weight=Weight(amount=weight, unit=Units.KILOGRAM), rir=rir))

    def add_whole_set(self, number_of_series: int, number_of_repetitions: int, weight: float, rir: int | None = None) -> None:
        for _ in range(number_of_series):
            self.add_series(number_of_repetitions, weight, rir)
        self.pending_weights.clear()

    def add_group_of_reps(self, number_of_series: int, number_of_repetitions: int, rir: int | None = None) -> None:
        if self.pending_weights:
            assert len(self.pending_weights) == 1, f"{self.pending_weights} is longer than 1"
            weight = self.pending_weights[0]
        else:
            weight = 0  # Default weight when not specified
        for _ in range(number_of_series):
            self.add_series(number_of_repetitions, weight, rir)

    def add_single_rep_set(self, number_of_repetitions: int, rir: int | None = None) -> None:
        if self.pending_weights:
            for weight in self.pending_weights:
                self.add_series(number_of_repetitions, weight, rir)
        else:
            # If no weight is specified, use 0 (bodyweight or unspecified)
            self.add_series(number_of_repetitions, 0, rir)

    def add_fixed_reps_multiple_weights(self, repetitions: int, rir: int | None = None) -> None:
        for weight in self.pending_weights:
            self.add_series(repetitions, weight, rir)
        self.pending_weights.clear()
        self.pending_repetitions.clear()

    def addSeriesIfComplete(self) -> Optional[Exercise]:
        if self.name and self.sets:
            exercise = Exercise(self.name, self.sets)
            self.reset()
            return exercise
        return None

    def reset(self) -> None:
        self.name = ""
        self.sets = []
        self.pending_weights = []
        self.pending_repetitions = []

    def build(self) -> Exercise:
        if not self.name:
            raise ValueError("Exercise name not set")
        return Exercise(self.name, self.sets)
