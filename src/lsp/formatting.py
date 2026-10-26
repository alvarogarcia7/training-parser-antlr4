"""Document formatting provider for the training language."""

from typing import Optional

from lsprotocol.types import TextEdit, Range, Position


def format_document(text: str) -> list[TextEdit]:
    """Format the entire document according to training language conventions."""
    lines = text.split("\n")
    formatted_lines = []

    for line in lines:
        formatted_line = format_line(line)
        formatted_lines.append(formatted_line)

    # Join lines and create a single edit replacing the entire document
    formatted_text = "\n".join(formatted_lines)

    if formatted_text == text:
        return []  # No changes needed

    # Calculate the range for the entire document
    end_line = len(lines) - 1
    end_char = len(lines[-1]) if lines else 0

    return [
        TextEdit(
            range=Range(
                start=Position(line=0, character=0),
                end=Position(line=end_line, character=end_char),
            ),
            new_text=formatted_text,
        )
    ]


def format_line(line: str) -> str:
    """Format a single line of training language code."""
    stripped = line.strip()

    if not stripped:
        return ""

    # Basic formatting rules:
    # 1. Ensure space after colon if present
    if ":" in stripped and ": " not in stripped:
        stripped = stripped.replace(":", ": ", 1)

    # 2. Ensure space after commas in set notation
    parts = stripped.split(":")
    if len(parts) == 2:
        exercise_part = parts[0]
        sets_part = parts[1]

        # Format commas in sets part
        formatted_sets = format_sets_notation(sets_part)
        stripped = f"{exercise_part}: {formatted_sets}"

    return stripped


def format_sets_notation(sets: str) -> str:
    """Format the sets notation part of an exercise line."""
    # Ensure space after commas
    formatted = sets.replace(",", ", ")

    # Remove multiple spaces
    while "  " in formatted:
        formatted = formatted.replace("  ", " ")

    return formatted.strip()


def format_range(text: str, start_line: int, end_line: int) -> list[TextEdit]:
    """Format a specific range of lines in the document."""
    lines = text.split("\n")
    edits = []

    for line_num in range(start_line, min(end_line + 1, len(lines))):
        original_line = lines[line_num]
        formatted_line = format_line(original_line)

        if formatted_line != original_line:
            edits.append(
                TextEdit(
                    range=Range(
                        start=Position(line=line_num, character=0),
                        end=Position(line=line_num, character=len(original_line)),
                    ),
                    new_text=formatted_line,
                )
            )

    return edits
