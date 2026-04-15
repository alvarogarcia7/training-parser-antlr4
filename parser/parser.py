from typing import Any

from antlr4 import CommonTokenStream, InputStream, ErrorNode
from antlr4.error.ErrorListener import ErrorListener

from dist.trainingLexer import trainingLexer
from dist.trainingParser import trainingParser
from dist.trainingVisitor import trainingVisitor
from . import Exercise
from .model import ParseError, ParseResult
from .series_builder import SeriesBuilder


class TrainingErrorListener(ErrorListener):
    def __init__(self) -> None:
        super().__init__()
        self.errors: list[ParseError] = []

    def syntaxError(self, recognizer: Any, offendingSymbol: Any, line: int, column: int, msg: str, e: Any) -> None:
        symbol_text = None
        if offendingSymbol is not None:
            try:
                symbol_text = str(offendingSymbol.text)
            except AttributeError:
                symbol_text = str(offendingSymbol) if offendingSymbol else None

        error = ParseError(
            line=line,
            column=column,
            message=msg,
            offending_symbol=symbol_text
        )
        self.errors.append(error)


class Formatter(trainingVisitor):
    def __init__(self) -> None:
        super().__init__()
        self.result: list[Exercise] = []
        self.builder = SeriesBuilder()

    def visitExercise(self, ctx: trainingParser.ExerciseContext) -> None:
        self.builder.reset()
        try:
            super().visitExercise(ctx)
            exercise = self.builder.addSeriesIfComplete()
            if exercise is not None:
                self.result.append(exercise)
        except Exception:
            # If an error occurs while processing this exercise, skip it
            # The error will have been captured by the error listener
            pass

    def visitExercise_name(self, ctx: trainingParser.Exercise_nameContext) -> Any:
        try:
            super().visitExercise_name(ctx)
            exercise_name_token = ctx.EXERCISE_NAME()
            if exercise_name_token is not None:
                self.builder.set_exercise_name(exercise_name_token.getText())
        except Exception:
            # Skip if we can't get the exercise name
            pass

    def visitWeight(self, ctx: trainingParser.WeightContext) -> Any:
        try:
            super().visitWeight(ctx)
            weight_text = ctx.getText()
            if weight_text:
                self.builder.add_weight(float(weight_text.removesuffix('k')))
        except (ValueError, AttributeError):
            # Skip invalid weights
            pass

    def visitWhole_set_(self, ctx: trainingParser.Whole_set_Context) -> Any:
        try:
            super().visitWhole_set_(ctx)

            # Get the INT tokens which are number_of_series and number_of_repetitions
            int_tokens = ctx.INT()
            if len(int_tokens) < 2:
                return

            number_of_series: int = int(int_tokens[0].getText())
            number_of_repetitions: int = int(int_tokens[1].getText())

            # Get weight from the weight context
            weight_ctx = ctx.weight()
            if weight_ctx is None:
                return

            weight: float = float(weight_ctx.getText().removesuffix('k'))

            # Check if there's a RIR value
            rir: int | None = None
            rir_ctx = ctx.rir()
            if rir_ctx is not None:
                rir = int(rir_ctx.getText())

            self.builder.add_whole_set(number_of_series, number_of_repetitions, weight, rir)
        except (ValueError, AttributeError, IndexError):
            # Skip malformed sets
            pass

    def visitGroup_of_rep_set(self, ctx: trainingParser.Group_of_rep_setContext) -> Any:
        try:
            super().visitGroup_of_rep_set(ctx)
            chunks: list[str] = ctx.getText().split('x')
            if len(chunks) < 2:
                return
            number_of_series: int = int(chunks[0])
            number_of_repetitions: int = int(chunks[1])
            self.builder.add_group_of_reps(number_of_series, number_of_repetitions)
        except (ValueError, IndexError, AssertionError):
            # Skip malformed group sets
            pass

    def visitSingle_rep_set_(self, ctx: trainingParser.Single_rep_set_Context) -> Any:
        try:
            super().visitSingle_rep_set_(ctx)
            number_of_repetitions = int(ctx.getText())
            self.builder.add_single_rep_set(number_of_repetitions)
        except (ValueError, AttributeError):
            # Skip malformed single rep sets
            pass

    def visitFixed_reps_multiple_weight(self, ctx: trainingParser.Fixed_reps_multiple_weightContext) -> Any:
        try:
            super().visitFixed_reps_multiple_weight(ctx)
            first_child = ctx.getChild(0)
            if first_child is not None:
                repetitions = int(first_child.getText())
                self.builder.add_fixed_reps_multiple_weights(repetitions)
        except (ValueError, AttributeError):
            # Skip malformed fixed reps sets
            pass

    def visitErrorNode(self, node: ErrorNode) -> None:
        # Don't raise exception, just skip the error node to continue parsing
        super().visitErrorNode(node)


class Parser:
    def __init__(self, input_stream: InputStream):
        self.input_stream = input_stream

    @classmethod
    def from_string(cls, string: str) -> Any:
        input_stream = InputStream(string)
        return Parser(input_stream)

    def parse_sessions(self) -> list[Exercise]:
        """
        Legacy method that returns only exercises, raises on errors.
        Kept for backward compatibility.
        """
        result = self.parse()
        if result.has_errors:
            # Raise the first error for backward compatibility
            first_error = result.errors[0]
            raise ValueError(str(first_error))
        return result.exercises

    def parse(self) -> ParseResult:
        """
        Parse the input and return a ParseResult containing both exercises and errors.
        This method continues parsing after encountering errors.
        """
        lexer = trainingLexer(self.input_stream)
        token_stream = CommonTokenStream(lexer)
        token_stream.fill()

        parser = trainingParser(token_stream)

        # Remove default error listeners and add our custom one
        error_listener = TrainingErrorListener()
        lexer.removeErrorListeners()
        lexer.addErrorListener(error_listener)
        parser.removeErrorListeners()
        parser.addErrorListener(error_listener)

        # Parse the tree
        tree = parser.workout()

        # Visit the tree to extract exercises
        formatter = Formatter()
        formatter.visit(tree)

        return ParseResult(
            exercises=formatter.result,
            errors=error_listener.errors
        )
