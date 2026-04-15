"""Hover provider for the training language."""

import re
from typing import Optional

from antlr4 import InputStream
from lsprotocol.types import Hover, MarkupContent, MarkupKind

from parser import Parser, Exercise


def format_exercise_info(exercise: Exercise) -> str:
    """Format exercise information for hover display."""
    lines = [f"**{exercise.name}**\n"]

    if not exercise.sets_:
        lines.append("No sets recorded")
        return "\n".join(lines)

    # Show set information
    lines.append(f"**Sets:** {len(exercise.sets_)}")

    # Show total volume
    total_volume = exercise.total_volume()
    lines.append(f"**Total Volume:** {total_volume:.1f} kg")

    # Show individual sets (limit to first 10)
    lines.append("\n**Set Breakdown:**")
    for i, set_ in enumerate(exercise.sets_[:10], 1):
        rir_info = f" (RIR: {set_.rir})" if set_.rir is not None else ""
        lines.append(
            f"- Set {i}: {set_.repetitions} reps @ {set_.weight.amount}{set_.weight.unit}{rir_info}"
        )

    if len(exercise.sets_) > 10:
        lines.append(f"... and {len(exercise.sets_) - 10} more sets")

    return "\n".join(lines)


def get_notation_help(text: str) -> Optional[str]:
    """Get help text for specific notation patterns."""
    text = text.strip()

    # Whole set notation: 3x8x75k
    if re.match(r"^\d+x\d+x[\d.]+k?$", text):
        parts = text.replace("k", "").split("x")
        sets, reps, weight = parts[0], parts[1], parts[2]
        return (
            f"**Whole Set Notation**\n\n"
            f"`{text}` = {sets} sets of {reps} reps at {weight}kg\n\n"
            f"This is the most compact notation for recording consistent sets."
        )

    # Group of reps: 3x8
    if re.match(r"^\d+x\d+$", text):
        parts = text.split("x")
        sets, reps = parts[0], parts[1]
        return (
            f"**Group of Reps Notation**\n\n"
            f"`{text}` = {sets} sets of {reps} reps\n\n"
            f"Combine with a weight prefix like: `75k: {text}`"
        )

    # Fixed reps multiple weights: 8xx60k,70k,80k
    if "xx" in text and "," in text:
        match = re.match(r"^(\d+)xx([\d.,k]+)$", text)
        if match:
            reps = match.group(1)
            weights = match.group(2)
            weight_count = weights.count(",") + 1
            return (
                f"**Fixed Reps with Multiple Weights**\n\n"
                f"`{text}` = {weight_count} sets of {reps} reps with progressive weights\n\n"
                f"Each weight represents one set with the same rep count."
            )

    # Weight specification
    if re.match(r"^[\d.]+k?$", text):
        weight = text.replace("k", "")
        return (
            f"**Weight Specification**\n\n"
            f"`{text}` = {weight} kilograms\n\n"
            f"Can be used as a prefix for set notation."
        )

    return None


def get_hover_info(text: str, line: int, character: int) -> Optional[Hover]:
    """Get hover information for the position in the document."""
    lines = text.split("\n")

    if line >= len(lines):
        return None

    current_line = lines[line]

    # Try to parse the entire line as an exercise
    try:
        input_stream = InputStream(current_line + "\n")
        parser = Parser(input_stream)
        exercises = parser.parse_sessions()

        if exercises:
            exercise = exercises[0]
            content = MarkupContent(
                kind=MarkupKind.Markdown, value=format_exercise_info(exercise)
            )
            return Hover(contents=content)
    except Exception:
        pass

    # If full parse fails, try to identify specific notation patterns
    # Extract word/pattern at cursor position
    if character < len(current_line):
        # Find token boundaries around cursor
        start = character
        end = character

        # Expand left to start of token
        while start > 0 and current_line[start - 1] not in " \t\n:,":
            start -= 1

        # Expand right to end of token
        while end < len(current_line) and current_line[end] not in " \t\n:,":
            end += 1

        token = current_line[start:end].strip()

        if token:
            help_text = get_notation_help(token)
            if help_text:
                content = MarkupContent(kind=MarkupKind.Markdown, value=help_text)
                return Hover(contents=content)

    # Provide general help
    general_help = (
        "**Training Language Syntax**\n\n"
        "Format: `Exercise name: set_notation`\n\n"
        "**Notation Patterns:**\n"
        "- `3x8x75k` - Whole set: 3 sets of 8 reps at 75kg\n"
        "- `75k: 3x8` - Weight prefix with group of reps\n"
        "- `75k: 8,7,6` - Single reps with varying counts\n"
        "- `8xx60k,70k,80k` - Fixed reps with multiple weights\n\n"
        "Hover over specific patterns for detailed help."
    )

    content = MarkupContent(kind=MarkupKind.Markdown, value=general_help)
    return Hover(contents=content)
