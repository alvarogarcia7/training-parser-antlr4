from typing import Any

from dist.trainingParser import trainingParser
from dist.trainingVisitor import trainingVisitor
from . import Exercise, Units


class Formatter(trainingVisitor):
    def __init__(self) -> None:
        super().__init__()
        self.result: list[Exercise] = []
        self.current: dict[str, Any] = {}

    def visitSession(self, ctx: trainingParser.SessionContext) -> Any:
        self.current = {'name': "", 'repetitions': [], 'weight': 0}
        super().visitSession(ctx)
        self.result.append(Exercise(
            self.current['name'], self.current['repetitions']))

    def visitExercise_name(self, ctx: trainingParser.Exercise_nameContext) -> Any:
        super().visitExercise_name(ctx)
        self.current['name'] = ctx.EXERCISE_NAME().getText()

    def visitWeight(self, ctx: trainingParser.WeightContext) -> Any:
        super().visitWeight(ctx)
        self.current['weight'] = ctx.getText().removesuffix('k')

    def visitWhole_reps(self, ctx: trainingParser.Whole_repsContext) -> Any:
        super().visitWhole_reps(ctx)
        text: str = ctx.getText()
        chunks = text.split('x')
        number_of_series: int = int(chunks[0])
        number_of_repetitions: int = int(chunks[1])
        weight: int = int(chunks[2].removesuffix('k'))
        for i in range(int(number_of_series) + 1):
            self.current['repetitions'].append(
                {'repetitions': number_of_repetitions, 'weight': {'amount': weight, 'unit': Units.KILOGRAM}})

    def visitGroup_of_reps(self, ctx: trainingParser.Group_of_repsContext) -> Any:
        super().visitGroup_of_reps(ctx)
        number_of_series, number_of_repetitions = ctx.getText().split('x')
        for i in range(int(number_of_series) + 1):
            self.current['repetitions'].append({'repetitions': number_of_repetitions,
                                                'weight': {'amount': self.current['weight'], 'unit': Units.KILOGRAM}})

    def visitRep1(self, ctx: trainingParser.Rep1Context) -> Any:
        super().visitRep1(ctx)
        number_of_repetitions = int(ctx.getText())
        self.current['repetitions'].append({'repetitions': number_of_repetitions,
                                            'weight': {'amount': self.current['weight'], 'unit': Units.KILOGRAM}})
