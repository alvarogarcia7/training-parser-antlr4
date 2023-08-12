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

    def visitExercise(self, ctx:trainingParser.ExerciseContext) -> None:
        self.current = {'name': "", 'repetitions': [], 'weight': float(0)}
        super().visitExercise(ctx)
        self.result.append(Exercise(
            self.current['name'], self.current['repetitions']))

    def visitExercise_name(self, ctx: trainingParser.Exercise_nameContext) -> Any:
        super().visitExercise_name(ctx)
        self.current['name'] = ctx.EXERCISE_NAME().getText()

    def visitWeight(self, ctx: trainingParser.WeightContext) -> Any:
        super().visitWeight(ctx)
        self.current['weight'] = float(ctx.getText().removesuffix('k'))

    def visitWhole_set_(self, ctx: trainingParser.Whole_set_Context) -> Any:
        super().visitWhole_set_(ctx)
        text: str = ctx.getText()
        chunks = text.split('x')
        number_of_series: int = int(chunks[0])
        number_of_repetitions: int = int(chunks[1])
        weight: float = float(chunks[2].removesuffix('k'))
        for i in range(int(number_of_series)):
            self.append_serie(number_of_repetitions, weight)

    def visitGroup_of_rep_set(self, ctx:trainingParser.Group_of_rep_setContext) -> Any:
        super().visitGroup_of_rep_set(ctx)
        chunks: list[str] = ctx.getText().split('x')
        number_of_series: int = int(chunks[0])
        number_of_repetitions: int = int(chunks[1])
        for i in range(number_of_series):
            self.append_serie(number_of_repetitions, self.current['weight'])

    def visitSingle_rep_set(self, ctx:trainingParser.Single_rep_setContext) -> Any:
        super().visitSingle_rep_set(ctx)
        number_of_repetitions = int(ctx.getText())
        self.append_serie(number_of_repetitions, self.current['weight'])

    def visitSingle_rep_set2(self, ctx:trainingParser.Single_rep_set2Context) -> Any:
        self.current['visitSingle_rep_set2'] = True
        super().visitSingle_rep_set2(ctx)
        self.current['repet'] = int(ctx.getText())

    def visitSet_(self, ctx:trainingParser.Set_Context) -> Any:
        super().visitSet_(ctx)
        if 'visitSingle_rep_set2' in self.current and self.current['visitSingle_rep_set2']:
            self.append_serie(self.current['repet'], self.current['weight'])
            del self.current['visitSingle_rep_set2']

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
