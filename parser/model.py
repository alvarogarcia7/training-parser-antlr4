import copy
from dataclasses import dataclass, field
from itertools import groupby
from typing import Any


def _validate_weight(amount: float, unit: str) -> None:
    if amount < 0:
        raise ValueError(f"Weight amount must be non-negative, got {amount}")
    if not unit:
        raise ValueError("Weight unit cannot be empty")


def _validate_set(repetitions: int, weight: Any) -> None:
    if repetitions <= 0:
        raise ValueError(f"Repetitions must be positive, got {repetitions}")
    if not isinstance(weight, Weight):
        raise TypeError(f"Weight must be a Weight instance, got {type(weight)}")
    weight.validate()


@dataclass(frozen=True, order=True)
class Weight:
    amount: float
    unit: str

    def __post_init__(self) -> None:
        _validate_weight(self.amount, self.unit)

    def validate(self) -> None:
        _validate_weight(self.amount, self.unit)


@dataclass(frozen=True, order=True)
class Set_:
    repetitions: int
    weight: Weight

    def __post_init__(self) -> None:
        _validate_set(self.repetitions, self.weight)

    def validate(self) -> None:
        _validate_set(self.repetitions, self.weight)


class Units:
    KILOGRAM: str = 'kg'


@dataclass(eq=True, unsafe_hash=True)
class Exercise:
    name: str
    sets_: list[Set_] = field(default_factory=list)

    def __post_init__(self) -> None:
        all_units = set(s.weight.unit for s in self.sets_)
        if len(all_units) > 1:
            raise ValueError(f"Detected multiple units in the Exercise: {all_units}")

    def __repr__(self) -> str:
        flattened = self.flatten()
        repetitions_repr = []
        for exercise in flattened:
            repetition = exercise.sets_[0]
            weight = repetition.weight
            repetitions_repr.append(f"{len(exercise.sets_)}x{repetition.repetitions}@{weight.amount}{weight.unit}")
        repetitions = ', '.join(repetitions_repr)
        return f"{self.name}: {repetitions}"

    def flatten(self) -> list[Any]:
        result = []
        for group in groupby(self.sets_, lambda x: (x.weight, x.repetitions)):
            c = copy.deepcopy(self)
            c.sets_ = list(group[1])
            result.append(c)
        return result

    def total_volume(self) -> float:
        total_volume: float = 0
        group: Set_
        for group in self.sets_:
            total_volume += group.repetitions * group.weight.amount
        return total_volume

    def validate(self) -> None:
        if not self.name:
            raise ValueError("Exercise name cannot be empty")
        all_units = set(s.weight.unit for s in self.sets_)
        if len(all_units) > 1:
            raise ValueError(f"Detected multiple units in the Exercise: {all_units}")
        for set_ in self.sets_:
            set_.validate()

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Exercise):
            return NotImplemented
        return (self.name, tuple(self.sets_)) < (other.name, tuple(other.sets_))

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Exercise):
            return NotImplemented
        return (self.name, tuple(self.sets_)) <= (other.name, tuple(other.sets_))

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Exercise):
            return NotImplemented
        return (self.name, tuple(self.sets_)) > (other.name, tuple(other.sets_))

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, Exercise):
            return NotImplemented
        return (self.name, tuple(self.sets_)) >= (other.name, tuple(other.sets_))
