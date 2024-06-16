import copy
from itertools import groupby
from typing import TypedDict, Any

Weight = TypedDict('Weight', {
    'amount': float,
    'unit': str})
Set_ = TypedDict('Set_', {
    'repetitions': int,
    'weight': Weight})


class Units:
    KILOGRAM: str = 'kg'


class Exercise:

    def __init__(self, name: str, sets_: list[Set_]) -> None:
        self.name = name
        self.sets_ = sets_
        all_units = set(map(lambda set_: set_['weight']['unit'], sets_))
        assert len(all_units) <= 1, f"Detected multiple units in the Exercise: {all_units}"

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Exercise):
            return self.name == o.name and \
                   self.sets_ == o.sets_

        return False

    def __repr__(self) -> str:
        flattened = self.flatten()
        repetitions_repr = []
        for exercise in flattened:
            repetition = exercise.sets_[0]
            weight = repetition['weight']
            repetitions_repr.append(f"{len(exercise.sets_)}x{repetition['repetitions']}@{weight['amount']}{weight['unit']}")
        repetitions = ', '.join(repetitions_repr)
        return f"{self.name}: {repetitions}"

    def flatten(self) -> list[Any]:
        result = []
        for group in groupby(self.sets_, lambda x:(x['weight'], x['repetitions'])):
            c = copy.deepcopy(self)
            c.sets_ = list(group[1])
            result.append(c)
        return result

    def total_volume(self) -> float:
        total_volume: float = 0
        group: Set_
        for group in self.sets_:
            total_volume += group['repetitions'] * group['weight']['amount']
        return total_volume
