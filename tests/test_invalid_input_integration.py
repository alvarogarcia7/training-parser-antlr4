import pytest
from pathlib import Path

from parser.parser import Parser, ParsingException


class TestInvalidInputIntegration:
    """Integration tests using invalid input data files to verify error handling."""

    def test_invalid_input_missing_k_suffix(self) -> None:
        """Test that files with missing 'k' suffix are properly rejected."""
        input_path = Path(__file__).parent / "invalid_input_missing_k_suffix.txt"
        input_text = input_path.read_text()

        with pytest.raises(ParsingException):
            Parser.from_string(input_text).parse_sessions()

    def test_invalid_input_incomplete_lines(self) -> None:
        """Test that incomplete exercise lines are properly rejected."""
        input_path = Path(__file__).parent / "invalid_input_incomplete_lines.txt"
        input_text = input_path.read_text()

        with pytest.raises(ParsingException):
            Parser.from_string(input_text).parse_sessions()

    def test_invalid_input_syntax_errors(self) -> None:
        """Test that syntax errors with invalid characters are properly rejected."""
        input_path = Path(__file__).parent / "invalid_input_syntax_errors.txt"
        input_text = input_path.read_text()

        with pytest.raises(ParsingException):
            Parser.from_string(input_text).parse_sessions()

    def test_invalid_input_malformed_sets(self) -> None:
        """Test that malformed set notations are properly rejected."""
        input_path = Path(__file__).parent / "invalid_input_malformed_sets.txt"
        input_text = input_path.read_text()

        with pytest.raises(ParsingException):
            Parser.from_string(input_text).parse_sessions()

    def test_invalid_input_mixed_errors(self) -> None:
        """Test that files with mixed types of errors are properly rejected."""
        input_path = Path(__file__).parent / "invalid_input_mixed_errors.txt"
        input_text = input_path.read_text()

        with pytest.raises(ParsingException):
            Parser.from_string(input_text).parse_sessions()

    def test_invalid_input_empty_exercise(self) -> None:
        """Test that empty exercise definitions are properly rejected."""
        input_path = Path(__file__).parent / "invalid_input_empty_exercise.txt"
        input_text = input_path.read_text()

        with pytest.raises(ParsingException):
            Parser.from_string(input_text).parse_sessions()

    def test_invalid_input_no_exercise_name(self) -> None:
        """Test that exercises without names are properly rejected."""
        input_path = Path(__file__).parent / "invalid_input_no_exercise_name.txt"
        input_text = input_path.read_text()

        with pytest.raises(ParsingException):
            Parser.from_string(input_text).parse_sessions()

    def test_all_invalid_files_exist(self) -> None:
        """Verify that all expected invalid input files exist in tests directory."""
        expected_files = [
            "invalid_input_missing_k_suffix.txt",
            "invalid_input_incomplete_lines.txt",
            "invalid_input_syntax_errors.txt",
            "invalid_input_malformed_sets.txt",
            "invalid_input_mixed_errors.txt",
            "invalid_input_empty_exercise.txt",
            "invalid_input_no_exercise_name.txt",
        ]

        tests_dir = Path(__file__).parent
        for filename in expected_files:
            file_path = tests_dir / filename
            assert file_path.exists(), f"Expected test data file not found: {filename}"
            assert file_path.stat().st_size > 0, f"Test data file is empty: {filename}"
