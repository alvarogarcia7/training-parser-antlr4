"""Diagnostics provider for the training language."""

from typing import Any

from antlr4 import InputStream, CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener
from lsprotocol.types import Diagnostic, DiagnosticSeverity, Position, Range

from dist.trainingLexer import trainingLexer
from dist.trainingParser import trainingParser


class DiagnosticErrorListener(ErrorListener):  # type: ignore
    """Custom error listener for collecting syntax errors as LSP diagnostics."""

    def __init__(self) -> None:
        super().__init__()
        self.diagnostics: list[Diagnostic] = []

    def syntaxError(
        self,
        recognizer: Any,
        offendingSymbol: Any,
        line: int,
        column: int,
        msg: str,
        e: Any,
    ) -> None:
        """Capture syntax errors and convert them to LSP diagnostics."""
        # ANTLR uses 1-based line numbers, LSP uses 0-based
        start_line = line - 1
        start_char = column

        # Try to determine end position from offending symbol
        end_line = start_line
        end_char = start_char + 1

        if offendingSymbol is not None:
            text = str(offendingSymbol.text)
            if text:
                end_char = start_char + len(text)

        diagnostic = Diagnostic(
            range=Range(
                start=Position(line=start_line, character=start_char),
                end=Position(line=end_line, character=end_char),
            ),
            severity=DiagnosticSeverity.Error,
            source="training-lsp",
            message=msg,
        )
        self.diagnostics.append(diagnostic)


def get_diagnostics(text: str) -> list[Diagnostic]:
    """Parse the text and return any syntax errors as diagnostics."""
    input_stream = InputStream(text)
    lexer = trainingLexer(input_stream)
    token_stream = CommonTokenStream(lexer)

    # Remove default error listeners and add our custom one
    error_listener = DiagnosticErrorListener()
    lexer.removeErrorListeners()
    lexer.addErrorListener(error_listener)

    parser = trainingParser(token_stream)
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener)

    # Parse the workout
    try:
        parser.workout()
    except Exception as e:
        # If parsing fails catastrophically, add a general diagnostic
        diagnostic = Diagnostic(
            range=Range(
                start=Position(line=0, character=0),
                end=Position(line=0, character=1),
            ),
            severity=DiagnosticSeverity.Error,
            source="training-lsp",
            message=f"Parsing error: {str(e)}",
        )
        error_listener.diagnostics.append(diagnostic)

    return error_listener.diagnostics
