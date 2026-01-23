from dataclasses import dataclass
from typing import Any, Optional

from antlr4 import Recognizer
from antlr4.error.ErrorListener import ErrorListener


@dataclass
class SyntaxError:
    line: int
    column: int
    offending_symbol: Any
    message: str
    expected_tokens: list[str]


class TrainingErrorListener(ErrorListener):
    def __init__(self) -> None:
        super().__init__()
        self.errors: list[SyntaxError] = []

    def syntaxError(
        self,
        recognizer: Recognizer,
        offending_symbol: Any,
        line: int,
        column: int,
        msg: str,
        e: Any,
    ) -> None:
        expected_tokens = self._get_expected_tokens(recognizer, e)
        error = SyntaxError(
            line=line,
            column=column,
            offending_symbol=offending_symbol,
            message=msg,
            expected_tokens=expected_tokens,
        )
        self.errors.append(error)

    def _get_expected_tokens(self, recognizer: Recognizer, exception: Any) -> list[str]:
        expected: list[str] = []
        if exception is None or not hasattr(exception, "getExpectedTokens"):
            return expected

        expected_token_set = exception.getExpectedTokens()
        for token_type in expected_token_set:
            token_name = self._get_token_name(recognizer, token_type)
            if token_name:
                expected.append(token_name)

        return expected

    def _get_token_name(self, recognizer: Recognizer, token_type: int) -> Optional[str]:
        if token_type < 0:
            return None

        if token_type < len(recognizer.literalNames):
            literal_name = recognizer.literalNames[token_type]
            if literal_name is not None and isinstance(literal_name, str):
                cleaned: str = literal_name.strip("'\"")
                return cleaned

        if token_type < len(recognizer.symbolicNames):
            symbolic_name = recognizer.symbolicNames[token_type]
            if symbolic_name is not None and isinstance(symbolic_name, str):
                return str(symbolic_name)

        return None


def format_error_message(error: SyntaxError, input_text: str) -> str:
    lines = input_text.split("\n")
    error_line_idx = error.line - 1

    context_lines: list[str] = []

    if error_line_idx > 0:
        context_lines.append(f"{error.line - 1:4d} | {lines[error_line_idx - 1]}")

    if error_line_idx < len(lines):
        context_lines.append(f"{error.line:4d} | {lines[error_line_idx]}")

    marker = " " * (7 + error.column) + "^"
    context_lines.append(marker)

    if error_line_idx + 1 < len(lines):
        context_lines.append(f"{error.line + 1:4d} | {lines[error_line_idx + 1]}")

    context = "\n".join(context_lines)

    expected_str = ""
    if error.expected_tokens:
        expected_str = f"\nExpected one of: {', '.join(error.expected_tokens)}"

    return f"""Syntax error at line {error.line}, column {error.column}:
{context}

Error: {error.message}{expected_str}"""
