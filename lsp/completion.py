"""Completion provider for the training language."""

from lsprotocol.types import (
    CompletionItem,
    CompletionItemKind,
    InsertTextFormat,
)


# Common exercise names
EXERCISE_NAMES = [
    "Bench press",
    "Squat",
    "Deadlift",
    "Overhead press",
    "Barbell row",
    "Pull-up",
    "Chin-up",
    "Dumbbell press",
    "Incline bench press",
    "Decline bench press",
    "Front squat",
    "Romanian deadlift",
    "Sumo deadlift",
    "Leg press",
    "Leg curl",
    "Leg extension",
    "Calf raise",
    "Lateral raise",
    "Face pull",
    "Bicep curl",
    "Tricep extension",
    "Cable fly",
    "Dumbbell fly",
    "Dips",
    "Lunges",
    "Bulgarian split squat",
    "Hip thrust",
    "Plank",
]


def get_exercise_completions() -> list[CompletionItem]:
    """Get completion items for exercise names."""
    return [
        CompletionItem(
            label=exercise,
            kind=CompletionItemKind.Class,
            detail="Exercise",
            insert_text=f"{exercise}: ",
            insert_text_format=InsertTextFormat.PlainText,
        )
        for exercise in EXERCISE_NAMES
    ]


def get_notation_completions() -> list[CompletionItem]:
    """Get completion items for set notation patterns."""
    return [
        CompletionItem(
            label="3x8x75k",
            kind=CompletionItemKind.Snippet,
            detail="Whole set notation: sets x reps x weight",
            documentation="Example: 3x8x75k = 3 sets of 8 reps at 75kg",
            insert_text="3x8x75k",
            insert_text_format=InsertTextFormat.PlainText,
        ),
        CompletionItem(
            label="75k: 3x8",
            kind=CompletionItemKind.Snippet,
            detail="Group of reps: weight: sets x reps",
            documentation="Example: 75k: 3x8 = 3 sets of 8 reps at 75kg",
            insert_text="75k: 3x8",
            insert_text_format=InsertTextFormat.PlainText,
        ),
        CompletionItem(
            label="75k: 8,7,6",
            kind=CompletionItemKind.Snippet,
            detail="Single rep notation: weight: rep, rep, rep...",
            documentation="Example: 75k: 8,7,6 = 3 sets with 8, 7, and 6 reps at 75kg",
            insert_text="75k: 8,7,6",
            insert_text_format=InsertTextFormat.PlainText,
        ),
        CompletionItem(
            label="8xx60k,70k,80k",
            kind=CompletionItemKind.Snippet,
            detail="Fixed reps with multiple weights",
            documentation="Example: 8xx60k,70k,80k = 8 reps at 60kg, 70kg, and 80kg",
            insert_text="8xx60k,70k,80k",
            insert_text_format=InsertTextFormat.PlainText,
        ),
    ]


def get_completions(line: str, character: int) -> list[CompletionItem]:
    """Get completion items based on the current context."""
    text_before_cursor = line[:character]

    # If line is empty or starts fresh, suggest exercises
    if not text_before_cursor.strip() or text_before_cursor.strip().endswith("\n"):
        return get_exercise_completions()

    # If we have a colon, suggest notation patterns
    if ":" in text_before_cursor:
        return get_notation_completions()

    # Check if we're typing an exercise name
    words = text_before_cursor.split()
    if words:
        last_word = words[-1].lower()
        # Filter exercises that start with the last word
        matching_exercises = [
            CompletionItem(
                label=exercise,
                kind=CompletionItemKind.Class,
                detail="Exercise",
                insert_text=f"{exercise}: ",
                insert_text_format=InsertTextFormat.PlainText,
            )
            for exercise in EXERCISE_NAMES
            if exercise.lower().startswith(last_word)
        ]
        if matching_exercises:
            return matching_exercises

    # Default: return both exercises and notations
    return get_exercise_completions() + get_notation_completions()
