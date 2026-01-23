from typing import Any

from antlr4 import CommonTokenStream, InputStream, ErrorNode

from dist.trainingLexer import trainingLexer
from dist.trainingParser import trainingParser
from dist.trainingVisitor import trainingVisitor
from . import Exercise
from .series_builder import SeriesBuilder


class Formatter(trainingVisitor):
    def __init__(self) -> None:
        super().__init__()
        self.result: list[Exercise] = []
        self.builder = SeriesBuilder()

    def visitExercise(self, ctx: trainingParser.ExerciseContext) -> None:
        self.builder.reset()
        super().visitExercise(ctx)
        exercise = self.builder.addSeriesIfComplete()
        if exercise is not None:
            self.result.append(exercise)

    def visitExercise_name(self, ctx: trainingParser.Exercise_nameContext) -> Any:
        super().visitExercise_name(ctx)
        self.builder.set_exercise_name(ctx.EXERCISE_NAME().getText())

    def visitWeight(self, ctx: trainingParser.WeightContext) -> Any:
        super().visitWeight(ctx)
        self.builder.add_weight(float(ctx.getText().removesuffix('k')))

    def visitWhole_set_(self, ctx: trainingParser.Whole_set_Context) -> Any:
        super().visitWhole_set_(ctx)
        text: str = ctx.getText()
        chunks = text.split('x')
        number_of_series: int = int(chunks[0])
        number_of_repetitions: int = int(chunks[1])
        weight: float = float(chunks[2].removesuffix('k'))
        self.builder.add_whole_set(number_of_series, number_of_repetitions, weight)

    def visitGroup_of_rep_set(self, ctx: trainingParser.Group_of_rep_setContext) -> Any:
        super().visitGroup_of_rep_set(ctx)
        chunks: list[str] = ctx.getText().split('x')
        number_of_series: int = int(chunks[0])
        number_of_repetitions: int = int(chunks[1])
        self.builder.add_group_of_reps(number_of_series, number_of_repetitions)

    def visitSingle_rep_set_(self, ctx: trainingParser.Single_rep_set_Context) -> Any:
        super().visitSingle_rep_set_(ctx)
        number_of_repetitions = int(ctx.getText())
        self.builder.add_single_rep_set(number_of_repetitions)

    def visitFixed_reps_multiple_weight(self, ctx: trainingParser.Fixed_reps_multiple_weightContext) -> Any:
        super().visitFixed_reps_multiple_weight(ctx)
        repetitions = int(ctx.getChild(0).getText())
        self.builder.add_fixed_reps_multiple_weights(repetitions)

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
