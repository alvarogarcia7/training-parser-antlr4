from typing import Any

from antlr4 import CommonTokenStream, InputStream, ErrorNode

from dist.trainingLexer import trainingLexer
from dist.trainingParser import trainingParser
from dist.trainingVisitor import trainingVisitor
from . import Exercise, Units


class Formatter(trainingVisitor):
    def __init__(self) -> None:
        super().__init__()
        self.result: list[Exercise] = []
        self.current: dict[str, Any] = {}

    def visitExercise(self, ctx: trainingParser.ExerciseContext) -> None:
        self.current = {'name': "", 'repetitions': [], 'weights': [], 'repetitions_val': []}
        super().visitExercise(ctx)
        self.result.append(Exercise(self.current['name'], self.current['repetitions']))

    def visitExercise_name(self, ctx: trainingParser.Exercise_nameContext) -> Any:
        super().visitExercise_name(ctx)
        self.current['name'] = ctx.EXERCISE_NAME().getText()

    def visitWeight(self, ctx: trainingParser.WeightContext) -> Any:
        super().visitWeight(ctx)
        self.current['weights'].append(float(ctx.getText().removesuffix('k')))

    def visitWhole_set_(self, ctx: trainingParser.Whole_set_Context) -> Any:
        super().visitWhole_set_(ctx)
        text: str = ctx.getText()
        chunks = text.split('x')
        number_of_series: int = int(chunks[0])
        number_of_repetitions: int = int(chunks[1])
        weight: float = float(chunks[2].removesuffix('k'))
        for i in range(int(number_of_series)):
            self.append_serie(number_of_repetitions, weight)
        self.current['weights'] = []

    def visitGroup_of_rep_set_(self, ctx: trainingParser.Group_of_rep_setContext) -> Any:
        super().visitGroup_of_rep_set(ctx)
        chunks: list[str] = ctx.getText().split('x')
        number_of_series: int = int(chunks[0])
        number_of_repetitions: int = int(chunks[1])
        weights_ = self.current['weights']
        assert len(weights_) == 1, f"{weights_} is longer than 1"
        for i in range(number_of_series):
            self.append_serie(number_of_repetitions, weights_[0])

    def visitSingle_rep_set_(self, ctx: trainingParser.Single_rep_set_Context) -> Any:
        super().visitSingle_rep_set_(ctx)
        number_of_repetitions = int(ctx.getText())
        for weight in self.current['weights']:
            self.append_serie(number_of_repetitions, weight)
    def visitSingle_rep_set2_(self, ctx: trainingParser.Single_rep_set2_Context) -> Any:
        super().visitSingle_rep_set2_(ctx)
        repetitions = int(ctx.getChild(0).getText())
        for weight in self.current['weights']:
            self.append_serie(repetitions, weight)
        # del self.current['visitSingle_rep_set2']
        self.current['weights'] = []
        self.current['repetitions_val'] = []

    def append_serie(self, number_of_repetitions: int, weight: float) -> None:
        self.current['repetitions'].append(
            {'repetitions': number_of_repetitions, 'weight': {'amount': weight, 'unit': Units.KILOGRAM}})

    def visitErrorNode(self, node: ErrorNode) -> None:
        print(type(node))
        super().visitErrorNode(node)
        raise ValueError(node)


class Parser:
    def __init__(self, input_stream: InputStream):
        self.input_stream = input_stream

    @classmethod
    def from_string(cls, string: str) -> Any:
        input_stream = InputStream(string)
        return Parser(input_stream)

    def parse_sessions(self) -> list[Exercise]:
        lexer = trainingLexer(self.input_stream)
        token_stream = CommonTokenStream(lexer)
        token_stream.fill()
        parser = trainingParser(token_stream)
        tree = parser.workout()

        formatter = Formatter()
        formatter.visit(tree)
        return formatter.result
