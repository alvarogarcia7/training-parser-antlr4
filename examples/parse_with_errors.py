#!/usr/bin/env python3
"""
Utility script to parse a training file and display errors with context.
Usage: python examples/parse_with_errors.py <filename>
"""

import sys
from pathlib import Path
from parser import Parser, ParseError
from antlr4 import InputStream


def display_error_with_context(error: ParseError, lines: list[str]) -> None:
    """Display an error with surrounding context from the input."""
    print(f"\n{'=' * 60}")
    print(f"Error at Line {error.line}, Column {error.column}")
    print('=' * 60)

    # Show the problematic line with context
    if 0 < error.line <= len(lines):
        # Show previous line if available
        if error.line > 1:
            print(f"  {error.line - 1}: {lines[error.line - 2]}")

        # Show the error line with a pointer
        error_line = lines[error.line - 1]
        print(f"  {error.line}: {error_line}")

        # Add pointer to the error column
        pointer = ' ' * (len(str(error.line)) + 2 + error.column) + '^'
        print(pointer)

        # Show next line if available
        if error.line < len(lines):
            print(f"  {error.line + 1}: {lines[error.line]}")

    print(f"\nError: {error.message}")
    if error.offending_symbol:
        print(f"Offending symbol: '{error.offending_symbol}'")


def parse_file_with_error_report(filename: str) -> int:
    """Parse a file and display detailed error report."""

    # Read the file
    try:
        with open(filename, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        return 1
    except IOError as e:
        print(f"Error reading file: {e}")
        return 1

    lines = content.split('\n')

    # Parse the content
    parser = Parser(InputStream(content))
    result = parser.parse()

    # Display header
    print("=" * 60)
    print(f"Parsing: {filename}")
    print("=" * 60)
    print(f"Total lines: {len(lines)}")
    print(f"Parsed exercises: {len(result.exercises)}")
    print(f"Errors found: {len(result.errors)}")
    print("=" * 60)

    # Display successfully parsed exercises
    if result.exercises:
        print("\n✅ Successfully Parsed Exercises:")
        for i, exercise in enumerate(result.exercises, 1):
            print(f"  {i}. {exercise}")
    else:
        print("\n(No exercises were successfully parsed)")

    # Display errors with context
    if result.has_errors:
        print(f"\n❌ Errors Found ({len(result.errors)}):")
        for i, error in enumerate(result.errors, 1):
            print(f"\n[Error {i}/{len(result.errors)}]")
            display_error_with_context(error, lines)
    else:
        print("\n✅ No errors - all input parsed successfully!")

    return 0 if result.is_valid else 1


def main() -> int:
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python examples/parse_with_errors.py <filename>")
        print("\nExample:")
        print("  python examples/parse_with_errors.py training-sample.txt")
        print("  python examples/parse_with_errors.py examples/test_error_input.txt")
        return 1

    filename = sys.argv[1]
    return parse_file_with_error_report(filename)


if __name__ == "__main__":
    sys.exit(main())
