import copy
from dataclasses import dataclass, field
from itertools import groupby
from typing import Any


@dataclass
class ParseError:
    line: int
    column: int
    message: str
    offending_symbol: str | None = None

    def __str__(self) -> str:
        if self.offending_symbol:
            return f"Line {self.line}:{self.column} - {self.message} (at '{self.offending_symbol}')"
        return f"Line {self.line}:{self.column} - {self.message}"


@dataclass
class ParseResult:
    exercises: list['Exercise']
    errors: list[ParseError] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0

    @property
    def is_valid(self) -> bool:
        return not self.has_errors

    def get_error_summary(self) -> str:
        """Get a formatted summary of all errors."""
        if not self.has_errors:
            return "No errors"

        lines = [f"Found {len(self.errors)} error(s):"]
        for error in self.errors:
            lines.append(f"  - {error}")
        return "\n".join(lines)

    def print_errors(self) -> None:
        """Print all errors to stdout."""
        if self.has_errors:
            print(self.get_error_summary())
        else:
            print("✓ No parsing errors")


def _validate_weight(amount: float, unit: str) -> None:
    if amount < 0:
        raise ValueError(f"Weight amount must be non-negative, got {amount}")
    if not unit:
        raise ValueError("Weight unit cannot be empty")


def _validate_set(repetitions: int, weight: Any, rir: int | None) -> None:
    if repetitions <= 0:
        raise ValueError(f"Repetitions must be positive, got {repetitions}")
    if not isinstance(weight, Weight):
        raise TypeError(f"Weight must be a Weight instance, got {type(weight)}")
    if rir is not None and rir < 0:
        raise ValueError(f"RIR must be non-negative, got {rir}")
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
    rir: int | None = None

    def __post_init__(self) -> None:
        _validate_set(self.repetitions, self.weight, self.rir)

    def validate(self) -> None:
        _validate_set(self.repetitions, self.weight, self.rir)

    def to_dict(self, set_number: int = 1) -> dict[str, Any]:
        """
        Convert Set_ to a dictionary representation.

        Args:
            set_number: The sequential number of the set (default: 1)

        Returns:
            Dictionary representation of the set
        """
        result: dict[str, Any] = {
            "setNumber": set_number,
            "repetitions": self.repetitions,
            "weight": {
                "amount": self.weight.amount,
                "unit": self.weight.unit
            }
        }

        if self.rir is not None:
            result["rir"] = self.rir

        return result


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
