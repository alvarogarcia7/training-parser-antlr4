from typing import Any

from antlr4 import CommonTokenStream, InputStream, ErrorNode

from dist.trainingLexer import trainingLexer
from dist.trainingParser import trainingParser
from dist.trainingVisitor import trainingVisitor
from . import Exercise
from .model import ParseError, ParseResult, Set_
from .series_builder import SeriesBuilder
from .error_listener import TrainingErrorListener, format_error_message, SyntaxError


class Formatter(trainingVisitor):
    def __init__(self) -> None:
        super().__init__()
        self.result: list[Exercise] = []
        self.builder = SeriesBuilder()

    def visitExercise(self, ctx: trainingParser.ExerciseContext) -> None:
        self.builder.reset()
        try:
            super().visitExercise(ctx)

            # Handle pending weights that weren't consumed by a set_ rule
            # This handles bare weights like "80.5" with no nested set
            if self.builder.pending_weights and not self.builder.sets:
                for weight in self.builder.pending_weights:
                    self.builder.add_series(1, weight, None)
                self.builder.pending_weights.clear()

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
            # Get the exercise name from either a NAME token or a string literal
            name_token = ctx.NAME()
            if name_token is not None:
                self.builder.set_exercise_name(name_token.getText())
            else:
                # Handle string literals ('Deadlift', 'Squat', etc.)
                self.builder.set_exercise_name(ctx.getText())
        except Exception:
            # Skip if we can't get the exercise name
            pass

    def visitWeight(self, ctx: trainingParser.WeightContext) -> Any:
        # Don't add weight here - let the specific weight type visitors handle it
        # super().visitWeight(ctx) will be called by visitChildren
        try:
            super().visitWeight(ctx)
        except (ValueError, AttributeError):
            # Skip invalid weights
            pass

    def visitWeight_dot(self, ctx: trainingParser.Weight_dotContext) -> Any:
        """Handle dot-decimal weights"""
        try:
            weight_text = ctx.getText()
            if weight_text:
                weight_normalized = weight_text.removesuffix('k')
                self.builder.add_weight(float(weight_normalized))
        except (ValueError, AttributeError):
            # Skip invalid weights
            pass

    def visitWeight_com(self, ctx: trainingParser.Weight_comContext) -> Any:
        """Handle comma-decimal weights"""
        try:
            weight_text = ctx.getText()
            if weight_text:
                weight_normalized = weight_text.removesuffix('k').replace(',', '.')
                self.builder.add_weight(float(weight_normalized))
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

            weight: float = float(weight_ctx.getText().removesuffix('k').replace(',', '.'))

            # Check if there's a RIR value
            rir: int | None = None
            rir_ctx = ctx.rir_dash()
            if rir_ctx is not None:
                text = rir_ctx.getText()
                if text.startswith('-'):
                    text = text[1:]
                rir = int(text)

            self.builder.add_whole_set(number_of_series, number_of_repetitions, weight, rir)
        except (AttributeError, IndexError):
            # Skip malformed sets, but let ValueError from validation pass through
            pass

    def visitGroup_of_rep_set(self, ctx: trainingParser.Group_of_rep_setContext) -> Any:
        try:
            super().visitGroup_of_rep_set(ctx)
            # Get INT tokens
            int_tokens = ctx.INT()
            if len(int_tokens) < 2:
                return
            number_of_series: int = int(int_tokens[0].getText())
            number_of_repetitions: int = int(int_tokens[1].getText())

            # Check if there's a RIR value
            rir: int | None = None
            rir_ctx = ctx.rir_dash()
            if rir_ctx is not None:
                text = rir_ctx.getText()
                if text.startswith('-'):
                    text = text[1:]
                rir = int(text)

            self.builder.add_group_of_reps(number_of_series, number_of_repetitions, rir)
        except (IndexError, AssertionError, AttributeError):
            # Skip malformed group sets
            pass

    def visitSingle_rep_set_(self, ctx: trainingParser.Single_rep_set_Context) -> Any:
        try:
            super().visitSingle_rep_set_(ctx)
            int_token = ctx.INT()
            if int_token is None:
                return
            number_of_repetitions = int(int_token.getText())

            # Check if there's a RIR value
            rir: int | None = None
            rir_ctx = ctx.rir_dash()
            if rir_ctx is not None:
                text = rir_ctx.getText()
                if text.startswith('-'):
                    text = text[1:]
                rir = int(text)

            self.builder.add_single_rep_set(number_of_repetitions, rir)
        except (ValueError, AttributeError):
            # Skip malformed single rep sets
            pass

    def visitSingle_rep_with_weight_(self, ctx: trainingParser.Single_rep_with_weight_Context) -> Any:
        """Point 4: Handle N.weight format (e.g., '10.23k' or '10.23' = 10 reps at 23kg)"""
        try:
            super().visitSingle_rep_with_weight_(ctx)
            int_tokens = ctx.INT()
            if len(int_tokens) < 2:
                return
            number_of_repetitions = int(int_tokens[0].getText())
            weight_value = float(int_tokens[1].getText())

            # Check if there's a RIR value
            rir: int | None = None
            rir_ctx = ctx.rir_dash()
            if rir_ctx is not None:
                text = rir_ctx.getText()
                if text.startswith('-'):
                    text = text[1:]
                rir = int(text)

            self.builder.add_series(number_of_repetitions, weight_value, rir)
        except (ValueError, AttributeError, IndexError):
            # Skip malformed patterns
            pass

    def visitFixed_reps_multiple_weight_v1(self, ctx: trainingParser.Fixed_reps_multiple_weight_v1Context) -> Any:
        try:
            super().visitFixed_reps_multiple_weight_v1(ctx)
            int_tokens = ctx.INT()
            if int_tokens is None:
                return
            # Handle both single Token and list of Tokens
            if isinstance(int_tokens, list):
                if len(int_tokens) < 1:
                    return
                repetitions = int(int_tokens[0].getText())
            else:
                repetitions = int(int_tokens.getText())

            # Check if there's a RIR value
            rir: int | None = None
            rir_ctx = ctx.rir_dash()
            if rir_ctx is not None:
                text = rir_ctx.getText()
                if text.startswith('-'):
                    text = text[1:]
                rir = int(text)

            self.builder.add_fixed_reps_multiple_weights(repetitions, rir)
        except (ValueError, AttributeError, TypeError):
            # Skip malformed fixed reps sets
            pass

    def visitFixed_reps_multiple_weight_v2(self, ctx: trainingParser.Fixed_reps_multiple_weight_v2Context) -> Any:
        try:
            super().visitFixed_reps_multiple_weight_v2(ctx)

            int_tokens = ctx.INT()
            if int_tokens is None:
                return
            # Handle both single Token and list of Tokens
            if isinstance(int_tokens, list):
                if len(int_tokens) < 1:
                    return
                repetitions = int(int_tokens[0].getText())
            else:
                repetitions = int(int_tokens.getText())

            # Check if there's a RIR value
            rir: int | None = None
            rir_ctx = ctx.rir_dash()
            if rir_ctx is not None:
                text = rir_ctx.getText()
                if text.startswith('-'):
                    text = text[1:]
                rir = int(text)

            self.builder.add_fixed_reps_multiple_weights(repetitions, rir)
        except (ValueError, AttributeError, TypeError):
            # Skip malformed fixed reps sets
            pass

    def visitWhole_set_multi_weight_v2(self, ctx: trainingParser.Whole_set_multi_weight_v2Context) -> Any:
        """Handle v2 multi-weight whole set format (e.g. 1.20.24/27,5/28,1-3 or 20xx40/50/60)"""
        try:
            # Check if there's a RIR value
            rir: int | None = None
            rir_ctx = ctx.rir_dash()
            if rir_ctx is not None:
                text = rir_ctx.getText()
                if text.startswith('-'):
                    text = text[1:]
                rir = int(text)

            # Track the current series count before visiting set_
            initial_series_count = len(self.builder.sets)

            # Visit the set_ context first to create initial series
            set_ctx = ctx.set_()
            if set_ctx:
                self.visit(set_ctx)

            # Get series created from the initial set_
            current_series_count = len(self.builder.sets)
            created_series = self.builder.sets[initial_series_count:current_series_count]

            # If RIR was specified, update all created series with the RIR value
            if rir is not None and created_series:
                for i, series_idx in enumerate(range(initial_series_count, current_series_count)):
                    # Update the RIR for each created series
                    old_set = self.builder.sets[series_idx]
                    # Create a new Set_ with the updated RIR
                    self.builder.sets[series_idx] = Set_(
                        repetitions=old_set.repetitions,
                        weight=old_set.weight,
                        rir=rir
                    )

            # Get the repetitions from the first created series, or extract from set_ context
            repetitions = None
            if created_series:
                # Get repetitions from the first created series
                repetitions = created_series[0].repetitions
            else:
                # Fallback: try to extract from set_ context manually
                int_in_set = set_ctx.INT()
                if int_in_set:
                    if isinstance(int_in_set, list):
                        # For whole_set_ format (INT sep INT sep weight), repetitions is the second INT
                        if len(int_in_set) >= 2:
                            repetitions = int(int_in_set[1].getText())
                        # For fixed_reps formats (INT double_sep weight), repetitions is the first INT
                        elif len(int_in_set) >= 1:
                            repetitions = int(int_in_set[0].getText())
                    else:
                        repetitions = int(int_in_set.getText())

            # Get slash-delimited weights from ctx.weight()
            if repetitions is not None:
                for weight_ctx in ctx.weight():
                    if weight_ctx:
                        weight_text = weight_ctx.getText()
                        if weight_text:
                            weight_normalized = weight_text.removesuffix('k').replace(',', '.')
                            weight_value = float(weight_normalized)
                            self.builder.add_series(repetitions, weight_value, rir)

        except (ValueError, AttributeError, IndexError, TypeError):
            # Skip malformed multi-weight sets
            pass

    def visitErrorNode(self, node: ErrorNode) -> None:
        # Don't raise exception, just skip the error node to continue parsing
        super().visitErrorNode(node)


class ParsingException(ValueError):
    """Exception raised when parsing errors are detected."""
    pass


class Parser:
    def __init__(self, input_stream: InputStream, original_input: str = ""):
        self.input_stream = input_stream
        self.original_input = original_input

    @classmethod
    def from_string(cls, string: str) -> "Parser":
        input_stream = InputStream(string)
        return Parser(input_stream, string)

    def parse_sessions(self) -> list[Exercise]:
        """
        Legacy method that returns only exercises, raises on errors.
        Kept for backward compatibility.
        """
        result: ParseResult = self.parse()
        if result.has_errors:
            # Display formatted error messages with full context
            if self.original_input:
                print("Parsing errors detected:\n")
                # Convert ParseError objects back to SyntaxError-like objects for formatting
                from .error_listener import SyntaxError as SyntaxErrorType, format_error_message
                for error in result.errors:
                    # Create a temporary SyntaxError object for formatting
                    syntax_error = SyntaxErrorType(
                        line=error.line,
                        column=error.column,
                        offending_symbol=error.offending_symbol,
                        message=error.message,
                        expected_tokens=[]
                    )
                    formatted_message = format_error_message(syntax_error, self.original_input)
                    print(formatted_message)
                    print()

            # Raise exception to prevent invalid parse tree processing
            raise ParsingException(f"Found {len(result.errors)} parsing error(s)")
        exercises: list[Exercise] = result.exercises
        return exercises

    def parse(self) -> ParseResult:
        """
        Parse the input and return a ParseResult containing both exercises and errors.
        This method continues parsing after encountering errors.
        """
        lexer = trainingLexer(self.input_stream)

        # Instantiate error listener
        error_listener = TrainingErrorListener()

        # Remove default error listeners and attach custom error listener to lexer
        lexer.removeErrorListeners()
        lexer.addErrorListener(error_listener)

        token_stream = CommonTokenStream(lexer)
        token_stream.fill()

        parser = trainingParser(token_stream)

        # Remove default error listeners and attach custom error listener to parser
        parser.removeErrorListeners()
        parser.addErrorListener(error_listener)

        # Parse the tree
        tree = parser.workout()

        # Check if all tokens were consumed (detect leftover tokens that might indicate invalid syntax)
        # Get current token position
        current_index = token_stream.index
        # Get total number of tokens (excluding EOF)
        total_tokens = len(token_stream.tokens)

        # If we haven't consumed all tokens and there are no errors yet, check for unconsumed tokens
        if current_index < total_tokens - 1 and not error_listener.errors:
            # Get the first unconsumed token that's not EOF or NEWLINE
            for i in range(current_index, total_tokens):
                token = token_stream.tokens[i]
                # Skip EOF tokens (type -1 or 'EOF' text)
                if token.type == -1 or token.text == '<EOF>':
                    break
                # Skip NEWLINE tokens
                if token.type == trainingLexer.NEWLINE:
                    continue
                # Found an unconsumed token - add error
                error_listener.errors.append(
                    SyntaxError(
                        line=token.line,
                        column=token.column,
                        offending_symbol=token,
                        message=f"Unexpected token: '{token.text}'",
                        expected_tokens=[]
                    )
                )
                break

        # Visit the tree to extract exercises
        formatter = Formatter()
        formatter.visit(tree)

        # Convert SyntaxError objects from error_listener to ParseError objects
        parse_errors = [
            ParseError(
                line=err.line,
                column=err.column,
                message=err.message,
                offending_symbol=str(err.offending_symbol) if err.offending_symbol else None
            )
            for err in error_listener.errors
        ]

        return ParseResult(
            exercises=formatter.result,
            errors=parse_errors
        )
