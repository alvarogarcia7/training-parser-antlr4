"""Code actions provider for quick fixes and refactorings."""

from typing import List, Optional

from lsprotocol.types import (
    CodeAction,
    CodeActionKind,
    TextEdit,
    Range,
    Position,
    WorkspaceEdit,
    TextDocumentEdit,
    OptionalVersionedTextDocumentIdentifier,
)


def get_code_actions(
    uri: str, text: str, line: int, start_char: int, end_char: int
) -> List[CodeAction]:
    """Get code actions for the given range."""
    actions: List[CodeAction] = []
    lines = text.split("\n")

    if line >= len(lines):
        return actions

    current_line = lines[line]

    # Quick fix: Add missing colon after exercise name
    if ":" not in current_line and current_line.strip():
        # Check if line looks like it has an exercise name but missing notation
        parts = current_line.strip().split()
        if len(parts) >= 1 and not any(char in current_line for char in ["x", ","]):
            # Suggest adding a colon
            action = create_insert_colon_action(uri, line, current_line)
            if action:
                actions.append(action)

    # Quick fix: Format spacing around operators
    if ":" in current_line and ": " not in current_line:
        action = create_fix_colon_spacing_action(uri, line, current_line)
        if action:
            actions.append(action)

    # Refactor: Convert to whole set notation
    # e.g., "75k: 3x8" -> "3x8x75k"
    if ":" in current_line and "x" in current_line:
        parts = current_line.split(":", 1)
        if len(parts) == 2:
            weight_part = parts[0].strip()
            notation_part = parts[1].strip()

            # Check if weight_part looks like a weight and notation_part looks like NxN
            if weight_part and "k" in weight_part and "x" in notation_part:
                import re

                weight_match = re.search(r"([\d.]+k?)", weight_part)
                notation_match = re.match(r"(\d+x\d+)", notation_part)

                if weight_match and notation_match:
                    action = create_convert_to_whole_set_action(
                        uri, line, current_line, weight_match.group(1), notation_match.group(1)
                    )
                    if action:
                        actions.append(action)

    return actions


def create_insert_colon_action(uri: str, line: int, line_text: str) -> Optional[CodeAction]:
    """Create an action to insert a colon after the exercise name."""
    stripped = line_text.strip()
    if not stripped:
        return None

    # Find where to insert the colon (after the exercise name)
    # Assume everything on the line is the exercise name
    insert_pos = len(line_text.rstrip())

    edit = TextEdit(
        range=Range(
            start=Position(line=line, character=insert_pos),
            end=Position(line=line, character=insert_pos),
        ),
        new_text=": ",
    )

    workspace_edit = WorkspaceEdit(
        document_changes=[
            TextDocumentEdit(
                text_document=OptionalVersionedTextDocumentIdentifier(uri=uri, version=None),
                edits=[edit],
            )
        ]
    )

    return CodeAction(
        title="Add colon after exercise name",
        kind=CodeActionKind.QuickFix,
        edit=workspace_edit,
    )


def create_fix_colon_spacing_action(uri: str, line: int, line_text: str) -> Optional[CodeAction]:
    """Create an action to fix spacing around colons."""
    if ": " in line_text:
        return None  # Already properly formatted

    # Replace : with :
    new_text = line_text.replace(":", ": ", 1)

    edit = TextEdit(
        range=Range(
            start=Position(line=line, character=0),
            end=Position(line=line, character=len(line_text)),
        ),
        new_text=new_text,
    )

    workspace_edit = WorkspaceEdit(
        document_changes=[
            TextDocumentEdit(
                text_document=OptionalVersionedTextDocumentIdentifier(uri=uri, version=None),
                edits=[edit],
            )
        ]
    )

    return CodeAction(
        title="Fix colon spacing",
        kind=CodeActionKind.QuickFix,
        edit=workspace_edit,
    )


def create_convert_to_whole_set_action(
    uri: str, line: int, line_text: str, weight: str, notation: str
) -> Optional[CodeAction]:
    """Create an action to convert to whole set notation."""
    # Extract exercise name
    parts = line_text.split(":", 1)
    exercise_name = parts[0].strip()

    # Remove weight from exercise name if present
    import re

    exercise_name = re.sub(r"\s*[\d.]+k?\s*$", "", exercise_name)

    # Create new line with whole set notation
    new_text = f"{exercise_name}: {notation}x{weight}"

    edit = TextEdit(
        range=Range(
            start=Position(line=line, character=0),
            end=Position(line=line, character=len(line_text)),
        ),
        new_text=new_text,
    )

    workspace_edit = WorkspaceEdit(
        document_changes=[
            TextDocumentEdit(
                text_document=OptionalVersionedTextDocumentIdentifier(uri=uri, version=None),
                edits=[edit],
            )
        ]
    )

    return CodeAction(
        title=f"Convert to whole set notation ({notation}x{weight})",
        kind=CodeActionKind.RefactorRewrite,
        edit=workspace_edit,
    )
