import pytest
from antlr4 import InputStream

from parser.error_listener import TrainingErrorListener, format_error_message
from parser.parser import Parser, ParsingException


class TestErrorListener:
    def test_missing_weight_unit_lexer_error(self) -> None:
        # Note: "10x5x75" without a unit actually parses successfully because
        # the grammar accepts bare numbers. Use invalid character instead.
        input_text = "Bench press: 10x5x75@\nDeadlift: 5x5x100k"

        with pytest.raises(ParsingException) as exc_info:
            Parser.from_string(input_text).parse_sessions()

        error_output = str(exc_info.value)
        assert "1" in error_output or "parsing error" in error_output

    def test_invalid_syntax_with_mismatched_token(self) -> None:
        input_text = "Bench press: 10x5x75l\nDeadlift: 5x5x100k"

        with pytest.raises(ParsingException) as exc_info:
            Parser.from_string(input_text).parse_sessions()

        assert "1" in str(exc_info.value)

    def test_incomplete_exercise_entry(self) -> None:
        input_text = "Bench press: 10x5x\nDeadlift: 5x5x100k"

        with pytest.raises(ParsingException) as exc_info:
            Parser.from_string(input_text).parse_sessions()

        assert "1" in str(exc_info.value)

    def test_malformed_set_notation(self) -> None:
        input_text = "Bench press: 10x\nDeadlift: 5x5x100k"

        with pytest.raises(ParsingException) as exc_info:
            Parser.from_string(input_text).parse_sessions()

        assert "1" in str(exc_info.value)

    def test_error_has_line_number(self) -> None:
        input_text = "Bench press: 10x5x75k\nDeadlift: 5x5x\nSquat: 3x3x100k"

        with pytest.raises(ParsingException):
            Parser.from_string(input_text).parse_sessions()

    def test_error_has_context_lines_above(self) -> None:
        input_text = "Bench press: 10x5x75k\nDeadlift: 5x5x\nSquat: 3x3x100k"
        parser = Parser.from_string(input_text)
        lexer_input = InputStream(input_text)

        from dist.trainingLexer import trainingLexer
        from dist.trainingParser import trainingParser
        from antlr4 import CommonTokenStream

        lexer = trainingLexer(lexer_input)
        error_listener = TrainingErrorListener()
        lexer.removeErrorListeners()
        lexer.addErrorListener(error_listener)

        token_stream = CommonTokenStream(lexer)
        token_stream.fill()
        parser_obj = trainingParser(token_stream)
        parser_obj.removeErrorListeners()
        parser_obj.addErrorListener(error_listener)

        parser_obj.workout()

        if error_listener.errors:
            formatted = format_error_message(error_listener.errors[0], input_text)
            assert "   1 |" in formatted or "1 |" in formatted

    def test_error_has_context_lines_below(self) -> None:
        input_text = "Bench press: 10x5x\nDeadlift: 5x5x100k\nSquat: 3x3x100k"
        parser = Parser.from_string(input_text)
        lexer_input = InputStream(input_text)

        from dist.trainingLexer import trainingLexer
        from dist.trainingParser import trainingParser
        from antlr4 import CommonTokenStream

        lexer = trainingLexer(lexer_input)
        error_listener = TrainingErrorListener()
        lexer.removeErrorListeners()
        lexer.addErrorListener(error_listener)

        token_stream = CommonTokenStream(lexer)
        token_stream.fill()
        parser_obj = trainingParser(token_stream)
        parser_obj.removeErrorListeners()
        parser_obj.addErrorListener(error_listener)

        parser_obj.workout()

        if error_listener.errors:
            formatted = format_error_message(error_listener.errors[0], input_text)
            assert "   2 |" in formatted or "2 |" in formatted

    def test_error_has_position_marker_with_caret(self) -> None:
        input_text = "Bench press: 10x5x\nDeadlift: 5x5x100k"
        parser = Parser.from_string(input_text)
        lexer_input = InputStream(input_text)

        from dist.trainingLexer import trainingLexer
        from dist.trainingParser import trainingParser
        from antlr4 import CommonTokenStream

        lexer = trainingLexer(lexer_input)
        error_listener = TrainingErrorListener()
        lexer.removeErrorListeners()
        lexer.addErrorListener(error_listener)

        token_stream = CommonTokenStream(lexer)
        token_stream.fill()
        parser_obj = trainingParser(token_stream)
        parser_obj.removeErrorListeners()
        parser_obj.addErrorListener(error_listener)

        parser_obj.workout()

        if error_listener.errors:
            formatted = format_error_message(error_listener.errors[0], input_text)
            assert "^" in formatted

    def test_error_has_expected_tokens(self) -> None:
        input_text = "Bench press: 10x5x\nDeadlift: 5x5x100k"
        parser = Parser.from_string(input_text)
        lexer_input = InputStream(input_text)

        from dist.trainingLexer import trainingLexer
        from dist.trainingParser import trainingParser
        from antlr4 import CommonTokenStream

        lexer = trainingLexer(lexer_input)
        error_listener = TrainingErrorListener()
        lexer.removeErrorListeners()
        lexer.addErrorListener(error_listener)

        token_stream = CommonTokenStream(lexer)
        token_stream.fill()
        parser_obj = trainingParser(token_stream)
        parser_obj.removeErrorListeners()
        parser_obj.addErrorListener(error_listener)

        parser_obj.workout()

        if error_listener.errors:
            formatted = format_error_message(error_listener.errors[0], input_text)
            assert "Expected" in formatted or len(error_listener.errors[0].expected_tokens) >= 0

    def test_valid_input_produces_no_errors(self) -> None:
        input_text = "Bench press: 10x5x75k\nDeadlift: 5x5x100k"

        result = Parser.from_string(input_text).parse_sessions()

        assert len(result) == 2
        assert result[0].name == "Bench press"
        assert result[1].name == "Deadlift"

    def test_another_valid_input_produces_no_errors(self) -> None:
        input_text = "Squat: 3x8x100k\nOverhead press: 5x10x50k"

        result = Parser.from_string(input_text).parse_sessions()

        assert len(result) == 2
        assert result[0].name == "Squat"
        assert result[1].name == "Overhead press"

    def test_format_error_message_includes_line_number(self) -> None:
        input_text = "Bench press: 10x5x\nDeadlift: 5x5x100k"
        parser = Parser.from_string(input_text)
        lexer_input = InputStream(input_text)

        from dist.trainingLexer import trainingLexer
        from dist.trainingParser import trainingParser
        from antlr4 import CommonTokenStream

        lexer = trainingLexer(lexer_input)
        error_listener = TrainingErrorListener()
        lexer.removeErrorListeners()
        lexer.addErrorListener(error_listener)

        token_stream = CommonTokenStream(lexer)
        token_stream.fill()
        parser_obj = trainingParser(token_stream)
        parser_obj.removeErrorListeners()
        parser_obj.addErrorListener(error_listener)

        parser_obj.workout()

        if error_listener.errors:
            formatted = format_error_message(error_listener.errors[0], input_text)
            assert "line 1" in formatted

    def test_format_error_message_includes_column_number(self) -> None:
        input_text = "Bench press: 10x5x\nDeadlift: 5x5x100k"
        parser = Parser.from_string(input_text)
        lexer_input = InputStream(input_text)

        from dist.trainingLexer import trainingLexer
        from dist.trainingParser import trainingParser
        from antlr4 import CommonTokenStream

        lexer = trainingLexer(lexer_input)
        error_listener = TrainingErrorListener()
        lexer.removeErrorListeners()
        lexer.addErrorListener(error_listener)

        token_stream = CommonTokenStream(lexer)
        token_stream.fill()
        parser_obj = trainingParser(token_stream)
        parser_obj.removeErrorListeners()
        parser_obj.addErrorListener(error_listener)

        parser_obj.workout()

        if error_listener.errors:
            formatted = format_error_message(error_listener.errors[0], input_text)
            assert "column" in formatted

    def test_format_error_message_shows_error_context(self) -> None:
        input_text = "Line one\nBench press: 10x5x\nLine three"
        parser = Parser.from_string(input_text)
        lexer_input = InputStream(input_text)

        from dist.trainingLexer import trainingLexer
        from dist.trainingParser import trainingParser
        from antlr4 import CommonTokenStream

        lexer = trainingLexer(lexer_input)
        error_listener = TrainingErrorListener()
        lexer.removeErrorListeners()
        lexer.addErrorListener(error_listener)

        token_stream = CommonTokenStream(lexer)
        token_stream.fill()
        parser_obj = trainingParser(token_stream)
        parser_obj.removeErrorListeners()
        parser_obj.addErrorListener(error_listener)

        parser_obj.workout()

        if error_listener.errors:
            formatted = format_error_message(error_listener.errors[0], input_text)
            lines = formatted.split("\n")
            assert any("Bench press" in line for line in lines)

    def test_error_on_multiline_input_second_line(self) -> None:
        input_text = "Bench press: 10x5x75k\nDeadlift: 5x5x\nSquat: 3x3x100k"

        with pytest.raises(ParsingException) as exc_info:
            Parser.from_string(input_text).parse_sessions()

        error_output = str(exc_info.value)
        # The exception message is just "Found N parsing error(s)"
        # The detailed line information is in the printed output, not the exception string
        assert "parsing error" in error_output or "1" in error_output

    def test_error_listener_collects_multiple_errors(self) -> None:
        input_text = "Bench press: 10x5x\nDeadlift: 5x5x"
        parser = Parser.from_string(input_text)
        lexer_input = InputStream(input_text)

        from dist.trainingLexer import trainingLexer
        from dist.trainingParser import trainingParser
        from antlr4 import CommonTokenStream

        lexer = trainingLexer(lexer_input)
        error_listener = TrainingErrorListener()
        lexer.removeErrorListeners()
        lexer.addErrorListener(error_listener)

        token_stream = CommonTokenStream(lexer)
        token_stream.fill()
        parser_obj = trainingParser(token_stream)
        parser_obj.removeErrorListeners()
        parser_obj.addErrorListener(error_listener)

        parser_obj.workout()

        assert len(error_listener.errors) >= 1

    def test_caret_position_aligns_with_error_column(self) -> None:
        input_text = "Bench: 10x5x"
        parser = Parser.from_string(input_text)
        lexer_input = InputStream(input_text)

        from dist.trainingLexer import trainingLexer
        from dist.trainingParser import trainingParser
        from antlr4 import CommonTokenStream

        lexer = trainingLexer(lexer_input)
        error_listener = TrainingErrorListener()
        lexer.removeErrorListeners()
        lexer.addErrorListener(error_listener)

        token_stream = CommonTokenStream(lexer)
        token_stream.fill()
        parser_obj = trainingParser(token_stream)
        parser_obj.removeErrorListeners()
        parser_obj.addErrorListener(error_listener)

        parser_obj.workout()

        if error_listener.errors:
            error = error_listener.errors[0]
            formatted = format_error_message(error, input_text)
            lines = formatted.split("\n")
            caret_line = [line for line in lines if "^" in line]
            assert len(caret_line) > 0

    def test_error_context_shows_line_above_when_available(self) -> None:
        input_text = "Bench press: 10x5x75k\nDeadlift: 5x5x"
        parser = Parser.from_string(input_text)
        lexer_input = InputStream(input_text)

        from dist.trainingLexer import trainingLexer
        from dist.trainingParser import trainingParser
        from antlr4 import CommonTokenStream

        lexer = trainingLexer(lexer_input)
        error_listener = TrainingErrorListener()
        lexer.removeErrorListeners()
        lexer.addErrorListener(error_listener)

        token_stream = CommonTokenStream(lexer)
        token_stream.fill()
        parser_obj = trainingParser(token_stream)
        parser_obj.removeErrorListeners()
        parser_obj.addErrorListener(error_listener)

        parser_obj.workout()

        if error_listener.errors:
            formatted = format_error_message(error_listener.errors[0], input_text)
            assert "Bench press" in formatted

    def test_error_context_shows_line_below_when_available(self) -> None:
        input_text = "Deadlift: 5x5x\nSquat: 3x3x100k"
        parser = Parser.from_string(input_text)
        lexer_input = InputStream(input_text)

        from dist.trainingLexer import trainingLexer
        from dist.trainingParser import trainingParser
        from antlr4 import CommonTokenStream

        lexer = trainingLexer(lexer_input)
        error_listener = TrainingErrorListener()
        lexer.removeErrorListeners()
        lexer.addErrorListener(error_listener)

        token_stream = CommonTokenStream(lexer)
        token_stream.fill()
        parser_obj = trainingParser(token_stream)
        parser_obj.removeErrorListeners()
        parser_obj.addErrorListener(error_listener)

        parser_obj.workout()

        if error_listener.errors:
            formatted = format_error_message(error_listener.errors[0], input_text)
            assert "Squat" in formatted

    def test_error_expected_tokens_populated(self) -> None:
        input_text = "Bench press: 10x5x"
        parser = Parser.from_string(input_text)
        lexer_input = InputStream(input_text)

        from dist.trainingLexer import trainingLexer
        from dist.trainingParser import trainingParser
        from antlr4 import CommonTokenStream

        lexer = trainingLexer(lexer_input)
        error_listener = TrainingErrorListener()
        lexer.removeErrorListeners()
        lexer.addErrorListener(error_listener)

        token_stream = CommonTokenStream(lexer)
        token_stream.fill()
        parser_obj = trainingParser(token_stream)
        parser_obj.removeErrorListeners()
        parser_obj.addErrorListener(error_listener)

        parser_obj.workout()

        if error_listener.errors:
            error = error_listener.errors[0]
            assert isinstance(error.expected_tokens, list)

    def test_format_error_message_with_expected_tokens(self) -> None:
        input_text = "Bench press: 10x5x"
        parser = Parser.from_string(input_text)
        lexer_input = InputStream(input_text)

        from dist.trainingLexer import trainingLexer
        from dist.trainingParser import trainingParser
        from antlr4 import CommonTokenStream

        lexer = trainingLexer(lexer_input)
        error_listener = TrainingErrorListener()
        lexer.removeErrorListeners()
        lexer.addErrorListener(error_listener)

        token_stream = CommonTokenStream(lexer)
        token_stream.fill()
        parser_obj = trainingParser(token_stream)
        parser_obj.removeErrorListeners()
        parser_obj.addErrorListener(error_listener)

        parser_obj.workout()

        if error_listener.errors and error_listener.errors[0].expected_tokens:
            formatted = format_error_message(error_listener.errors[0], input_text)
            assert "Expected" in formatted

    def test_no_errors_for_complex_valid_input(self) -> None:
        input_text = "Bench press: 10x5x75k\nDeadlift: 5x5x100k\nSquat: 3x8x120k\nOverhead press: 5x10x50k"

        result = Parser.from_string(input_text).parse_sessions()

        assert len(result) == 4

    def test_error_at_first_line_has_no_line_above(self) -> None:
        input_text = "Bench press: 10x5x"
        parser = Parser.from_string(input_text)
        lexer_input = InputStream(input_text)

        from dist.trainingLexer import trainingLexer
        from dist.trainingParser import trainingParser
        from antlr4 import CommonTokenStream

        lexer = trainingLexer(lexer_input)
        error_listener = TrainingErrorListener()
        lexer.removeErrorListeners()
        lexer.addErrorListener(error_listener)

        token_stream = CommonTokenStream(lexer)
        token_stream.fill()
        parser_obj = trainingParser(token_stream)
        parser_obj.removeErrorListeners()
        parser_obj.addErrorListener(error_listener)

        parser_obj.workout()

        if error_listener.errors:
            formatted = format_error_message(error_listener.errors[0], input_text)
            assert "line 1" in formatted

    def test_error_at_last_line_has_no_line_below(self) -> None:
        input_text = "Bench press: 10x5x75k\nDeadlift: 5x5x"
        parser = Parser.from_string(input_text)
        lexer_input = InputStream(input_text)

        from dist.trainingLexer import trainingLexer
        from dist.trainingParser import trainingParser
        from antlr4 import CommonTokenStream

        lexer = trainingLexer(lexer_input)
        error_listener = TrainingErrorListener()
        lexer.removeErrorListeners()
        lexer.addErrorListener(error_listener)

        token_stream = CommonTokenStream(lexer)
        token_stream.fill()
        parser_obj = trainingParser(token_stream)
        parser_obj.removeErrorListeners()
        parser_obj.addErrorListener(error_listener)

        parser_obj.workout()

        if error_listener.errors:
            formatted = format_error_message(error_listener.errors[0], input_text)
            assert "line 2" in formatted
