"""Example usage of the LSP components programmatically."""

from lsp.diagnostics import get_diagnostics
from lsp.completion import get_completions
from lsp.hover import get_hover_info
from lsp.formatting import format_document
from lsp.semantic_tokens import get_semantic_tokens


def example_diagnostics() -> None:
    """Example: Getting diagnostics for a workout log."""
    print("=== DIAGNOSTICS EXAMPLE ===\n")

    # Valid workout
    valid_text = "Bench press: 3x8x75k\nSquat: 5x10x100k\n"
    diagnostics = get_diagnostics(valid_text)
    print(f"Valid workout - Diagnostics: {len(diagnostics)}")

    # Invalid workout
    invalid_text = "Bench press 75k 4, @#$\n"
    diagnostics = get_diagnostics(invalid_text)
    print(f"Invalid workout - Diagnostics: {len(diagnostics)}")
    for diag in diagnostics:
        print(f"  - Line {diag.range.start.line}: {diag.message}")


def example_completions() -> None:
    """Example: Getting completions."""
    print("\n=== COMPLETIONS EXAMPLE ===\n")

    # Completions at start of line
    line = ""
    completions = get_completions(line, 0)
    print(f"Start of line - {len(completions)} completions")
    print(f"  First 5: {[c.label for c in completions[:5]]}")

    # Completions after colon
    line = "Bench press: "
    completions = get_completions(line, len(line))
    print(f"\nAfter colon - {len(completions)} completions")
    print(f"  First 3: {[c.label for c in completions[:3]]}")


def example_hover() -> None:
    """Example: Getting hover information."""
    print("\n=== HOVER EXAMPLE ===\n")

    text = "Bench press: 3x8x75k\n"
    hover = get_hover_info(text, 0, 5)  # Hover on "Bench press"

    if hover and hover.contents:
        print("Hover info for 'Bench press: 3x8x75k':")
        # Get the markdown value
        if hasattr(hover.contents, 'value'):
            content = hover.contents.value
            # Show first 200 chars
            print(f"  {content[:200]}...")


def example_formatting() -> None:
    """Example: Formatting a document."""
    print("\n=== FORMATTING EXAMPLE ===\n")

    # Unformatted text
    text = "Bench press:3x8x75k\nSquat:5x10x100k"
    print(f"Before formatting:\n{text}\n")

    # Get formatting edits
    edits = format_document(text)
    print(f"Number of edits: {len(edits)}")

    # Apply edits (simplified - just show what would be applied)
    if edits:
        for edit in edits:
            print(f"  Edit at line {edit.range.start.line}: '{edit.new_text}'")


def example_semantic_tokens() -> None:
    """Example: Getting semantic tokens."""
    print("\n=== SEMANTIC TOKENS EXAMPLE ===\n")

    text = "Bench press: 3x8x75k\n"
    tokens = get_semantic_tokens(text)

    print(f"Text: {text.strip()}")
    print(f"Semantic tokens data length: {len(tokens.data)}")
    print(f"Number of tokens: {len(tokens.data) // 5}")  # Each token is 5 integers
    print(f"First 10 values: {tokens.data[:10]}")


def main() -> None:
    """Run all examples."""
    print("Training Language Server - Example Usage\n")
    print("=" * 50)

    example_diagnostics()
    example_completions()
    example_hover()
    example_formatting()
    example_semantic_tokens()

    print("\n" + "=" * 50)
    print("\nFor interactive usage, integrate with an LSP-compatible editor.")
    print("See LSP_GUIDE.md for setup instructions.")


if __name__ == "__main__":
    main()
