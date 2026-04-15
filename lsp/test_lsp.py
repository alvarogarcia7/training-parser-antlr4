"""Tests for the LSP implementation."""

import pytest

from lsp.diagnostics import get_diagnostics
from lsp.completion import get_completions, get_exercise_completions, get_notation_completions
from lsp.hover import get_hover_info, get_notation_help
from lsp.formatting import format_document, format_line
from lsp.semantic_tokens import get_semantic_tokens, tokenize_line


class TestDiagnostics:
    """Test diagnostic functionality."""

    def test_valid_workout(self) -> None:
        """Test that valid workout has no diagnostics."""
        text = "Bench press: 3x8x75k\nSquat: 5x10x100k\n"
        diagnostics = get_diagnostics(text)
        assert len(diagnostics) == 0

    def test_syntax_error(self) -> None:
        """Test that syntax errors are detected."""
        text = "Bench press 75k 4, @#$\n"
        diagnostics = get_diagnostics(text)
        assert len(diagnostics) > 0

    def test_empty_document(self) -> None:
        """Test empty document has diagnostics (grammar requires at least one exercise)."""
        text = ""
        diagnostics = get_diagnostics(text)
        # Empty document is invalid according to grammar
        assert len(diagnostics) > 0


class TestCompletion:
    """Test completion functionality."""

    def test_exercise_completions(self) -> None:
        """Test exercise name completions."""
        completions = get_exercise_completions()
        assert len(completions) > 0
        labels = [c.label for c in completions]
        assert "Bench press" in labels
        assert "Squat" in labels
        assert "Deadlift" in labels

    def test_notation_completions(self) -> None:
        """Test notation pattern completions."""
        completions = get_notation_completions()
        assert len(completions) > 0
        labels = [c.label for c in completions]
        assert any("3x8x75k" in label for label in labels)
        assert any("xx" in label for label in labels)

    def test_context_aware_completion_start_of_line(self) -> None:
        """Test completions at start of line."""
        line = ""
        completions = get_completions(line, 0)
        assert len(completions) > 0
        # Should suggest exercises
        labels = [c.label for c in completions]
        assert "Bench press" in labels

    def test_context_aware_completion_after_colon(self) -> None:
        """Test completions after colon."""
        line = "Bench press: "
        completions = get_completions(line, len(line))
        # Should suggest notation patterns
        labels = [c.label for c in completions]
        assert any("3x8x75k" in label for label in labels)


class TestHover:
    """Test hover functionality."""

    def test_hover_on_whole_set_notation(self) -> None:
        """Test hover on whole set notation."""
        help_text = get_notation_help("3x8x75k")
        assert help_text is not None
        assert "Whole Set" in help_text
        assert "3 sets" in help_text
        assert "8 reps" in help_text

    def test_hover_on_group_notation(self) -> None:
        """Test hover on group notation."""
        help_text = get_notation_help("3x8")
        assert help_text is not None
        assert "Group of Reps" in help_text

    def test_hover_on_fixed_reps(self) -> None:
        """Test hover on fixed reps notation."""
        help_text = get_notation_help("8xx60k,70k,80k")
        assert help_text is not None
        assert "Fixed Reps" in help_text
        assert "3 sets" in help_text

    def test_hover_on_weight(self) -> None:
        """Test hover on weight."""
        help_text = get_notation_help("75k")
        assert help_text is not None
        assert "Weight" in help_text
        assert "75 kilograms" in help_text

    def test_hover_info_on_exercise(self) -> None:
        """Test hover info on complete exercise."""
        text = "Bench press: 3x8x75k\n"
        hover = get_hover_info(text, 0, 5)
        assert hover is not None
        assert hover.contents.value is not None


class TestFormatting:
    """Test formatting functionality."""

    def test_format_line_with_missing_space(self) -> None:
        """Test formatting line with missing space after colon."""
        line = "Bench press:3x8x75k"
        formatted = format_line(line)
        assert formatted == "Bench press: 3x8x75k"

    def test_format_line_already_formatted(self) -> None:
        """Test formatting already formatted line."""
        line = "Bench press: 3x8x75k"
        formatted = format_line(line)
        assert formatted == line

    def test_format_document(self) -> None:
        """Test document formatting."""
        text = "Bench press:3x8x75k\nSquat:5x10x100k"
        edits = format_document(text)
        assert len(edits) > 0

    def test_format_document_no_changes(self) -> None:
        """Test document that needs no formatting."""
        text = "Bench press: 3x8x75k\nSquat: 5x10x100k"
        edits = format_document(text)
        assert len(edits) == 0


class TestSemanticTokens:
    """Test semantic tokens functionality."""

    def test_tokenize_exercise_line(self) -> None:
        """Test tokenizing a complete exercise line."""
        line = "Bench press: 3x8x75k"
        tokens = tokenize_line(line, 0)
        assert len(tokens) > 0

    def test_semantic_tokens_full_document(self) -> None:
        """Test generating semantic tokens for full document."""
        text = "Bench press: 3x8x75k\nSquat: 5x10x100k\n"
        semantic_tokens = get_semantic_tokens(text)
        assert semantic_tokens is not None
        assert len(semantic_tokens.data) > 0
        # Data should be in groups of 5 (deltaLine, deltaStart, length, tokenType, modifiers)
        assert len(semantic_tokens.data) % 5 == 0

    def test_tokenize_empty_line(self) -> None:
        """Test tokenizing empty line."""
        line = ""
        tokens = tokenize_line(line, 0)
        assert len(tokens) == 0
