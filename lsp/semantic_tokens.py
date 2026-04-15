"""Semantic tokens provider for syntax highlighting."""

import re
from typing import List

from lsprotocol.types import (
    SemanticTokens,
    SemanticTokensLegend,
    SemanticTokenTypes,
)


# Define token types we'll use
TOKEN_TYPES = [
    SemanticTokenTypes.Class,  # Exercise names
    SemanticTokenTypes.Number,  # Numbers (sets, reps, weights)
    SemanticTokenTypes.Operator,  # Operators (x, xx, :)
    SemanticTokenTypes.Keyword,  # Weight units (k)
    SemanticTokenTypes.Comment,  # Comments if we add them later
]

TOKEN_TYPE_MAP = {
    "exercise": 0,
    "number": 1,
    "operator": 2,
    "unit": 3,
    "comment": 4,
}


def get_semantic_tokens_legend() -> SemanticTokensLegend:
    """Get the legend describing semantic token types."""
    return SemanticTokensLegend(
        token_types=TOKEN_TYPES,
        token_modifiers=[],
    )


class Token:
    """Represents a semantic token."""

    def __init__(self, line: int, start_char: int, length: int, token_type: int):
        self.line = line
        self.start_char = start_char
        self.length = length
        self.token_type = token_type


def tokenize_line(line: str, line_num: int) -> List[Token]:
    """Tokenize a single line and return semantic tokens."""
    tokens: List[Token] = []

    # Check if line contains an exercise (has a colon or ends with notation)
    colon_pos = line.find(":")

    if colon_pos > 0:
        # Everything before colon is exercise name
        exercise_name = line[:colon_pos].strip()
        if exercise_name:
            # Find start position of exercise name (skip leading whitespace)
            start = len(line) - len(line.lstrip())
            tokens.append(
                Token(
                    line=line_num,
                    start_char=start,
                    length=len(exercise_name),
                    token_type=TOKEN_TYPE_MAP["exercise"],
                )
            )

        # Tokenize the notation part after colon
        notation_part = line[colon_pos + 1 :]
        tokens.extend(tokenize_notation(notation_part, line_num, colon_pos + 1))

        # Add the colon as an operator
        tokens.append(
            Token(
                line=line_num,
                start_char=colon_pos,
                length=1,
                token_type=TOKEN_TYPE_MAP["operator"],
            )
        )
    else:
        # Try to identify exercise name at the start
        match = re.match(r"^(\s*)([a-zA-Z][\w\s\-áéíóúñ]*)", line)
        if match:
            leading_space = match.group(1)
            exercise_name = match.group(2).strip()
            if exercise_name:
                start = len(leading_space)
                tokens.append(
                    Token(
                        line=line_num,
                        start_char=start,
                        length=len(exercise_name),
                        token_type=TOKEN_TYPE_MAP["exercise"],
                    )
                )

                # Tokenize the rest as notation
                rest = line[start + len(exercise_name) :]
                tokens.extend(tokenize_notation(rest, line_num, start + len(exercise_name)))

    return tokens


def tokenize_notation(text: str, line_num: int, offset: int) -> List[Token]:
    """Tokenize set notation patterns."""
    tokens: List[Token] = []

    # Pattern for numbers (including decimals)
    for match in re.finditer(r"\d+\.?\d*", text):
        tokens.append(
            Token(
                line=line_num,
                start_char=offset + match.start(),
                length=len(match.group()),
                token_type=TOKEN_TYPE_MAP["number"],
            )
        )

    # Pattern for operators (x, xx, :)
    for match in re.finditer(r"xx|x|:", text):
        tokens.append(
            Token(
                line=line_num,
                start_char=offset + match.start(),
                length=len(match.group()),
                token_type=TOKEN_TYPE_MAP["operator"],
            )
        )

    # Pattern for weight unit 'k'
    for match in re.finditer(r"k(?=\s|,|$|\))", text):
        tokens.append(
            Token(
                line=line_num,
                start_char=offset + match.start(),
                length=1,
                token_type=TOKEN_TYPE_MAP["unit"],
            )
        )

    return tokens


def get_semantic_tokens(text: str) -> SemanticTokens:
    """Generate semantic tokens for the entire document."""
    all_tokens: List[Token] = []

    lines = text.split("\n")
    for line_num, line in enumerate(lines):
        tokens = tokenize_line(line, line_num)
        all_tokens.extend(tokens)

    # Sort tokens by position
    all_tokens.sort(key=lambda t: (t.line, t.start_char))

    # Convert to LSP semantic token format (delta-encoded)
    data: List[int] = []
    prev_line = 0
    prev_start = 0

    for token in all_tokens:
        # Calculate deltas
        delta_line = token.line - prev_line
        delta_start = token.start_char - (prev_start if delta_line == 0 else 0)

        # Append: deltaLine, deltaStart, length, tokenType, tokenModifiers
        data.extend(
            [
                delta_line,
                delta_start,
                token.length,
                token.token_type,
                0,  # No modifiers
            ]
        )

        prev_line = token.line
        prev_start = token.start_char

    return SemanticTokens(data=data)
