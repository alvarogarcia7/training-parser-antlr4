# Quick Start: Error Handling

This guide shows you how to use the new error handling feature in the training parser.

## Basic Usage

```python
from parser import Parser

# Parse input that may contain errors
input_text = """
Bench press 75k: 4, 4x5
Squat 70l: 5x10
Overhead press: 5x5x40k
"""

# Use the new parse() method
result = Parser.from_string(input_text).parse()

# Check results
print(f"Parsed {len(result.exercises)} exercises")
print(f"Found {len(result.errors)} errors")

# Display exercises
for exercise in result.exercises:
    print(f"  ✓ {exercise}")

# Display errors with line/column info
for error in result.errors:
    print(f"  ✗ {error}")
```

## Key Features

1. **Continue on Errors**: Parser doesn't stop at first error
2. **Line & Column Info**: Know exactly where each error occurred
3. **Partial Results**: Get all valid exercises even with errors
4. **Backward Compatible**: Old code using `parse_sessions()` still works

## ParseResult Object

```python
result = Parser.from_string(input_text).parse()

# Properties
result.exercises      # List of successfully parsed exercises
result.errors        # List of ParseError objects
result.has_errors    # True if any errors occurred
result.is_valid      # True if no errors (opposite of has_errors)

# Methods
result.get_error_summary()  # Returns formatted string of all errors
result.print_errors()       # Prints errors to stdout
```

## Error Information

Each `ParseError` contains:

```python
error.line              # Line number (1-indexed)
error.column            # Column position (0-indexed)
error.message           # Error description
error.offending_symbol  # The problematic token (if available)
str(error)             # Formatted error string
```

## Example Output

```
Input line 2:10 - mismatched input 'l' expecting {'k', ':', INT} (at 'l')
```

This tells you:
- **Line 2**: Error on the second line
- **Column 10**: Error at character position 10
- **Message**: What went wrong
- **Symbol**: The character 'l' that caused the issue

## See Also

- `ERROR_HANDLING.md` - Full documentation
- `examples/error_handling_example.py` - Comprehensive examples
- `parser/test_error_handling.py` - Test cases
