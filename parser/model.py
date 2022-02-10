from typing import TypedDict

Weight = TypedDict('Weight', {
    'amount': int,
    'unit': str})
Repetition = TypedDict('Repetition', {
    'repetitions': int,
    'weight': Weight})


class Units:
    KILOGRAM: str = 'kg'


class Exercise:

    def __init__(self, name: str, repetitions: list[Repetition]) -> None:
        self.name = name
        self.repetitions = repetitions

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Exercise):
            return self.name == o.name

        return False

    def __repr__(self) -> str:
        repetitions_repr = []
        for repetition in self.repetitions:
            weight = repetition['weight']
            repetitions_repr.append(f"{repetition['repetitions']} - {weight['amount']}{weight['unit']}")
        return "".join([self.name, ": ",
                        ', '.join(repetitions_repr)])
