import copy
from itertools import groupby
from operator import itemgetter
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

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Exercise):
            return self.name == o.name and \
                   self.sets_ == o.sets_

        return False

    def __repr__(self) -> str:
        repetitions_repr = []
        for repetition in self.sets_:
            weight = repetition['weight']
            repetitions_repr.append(f"{repetition['repetitions']} - {weight['amount']}{weight['unit']}")
        repetitions = ', '.join(repetitions_repr)
        return f"{self.name}: {repetitions}"

    def flatten(self) -> list[Any]:
        result = []
        for group in groupby(self.sets_, lambda x:(x['weight'], x['repetitions'])):
            c = copy.deepcopy(self)
            c.sets_ = list(group[1])
            result.append(c)
        return result
