# Error Handling in Training Parser

The training parser now supports robust error handling that allows parsing to continue even when encountering incorrect input. Errors are captured with line and column information, and the parser returns both successfully parsed exercises and error details.

## Features

- **Partial Parsing**: The parser continues processing after encountering errors, extracting all valid exercises
- **Detailed Error Information**: Each error includes:
  - Line number where the error occurred
  - Column (character position) where the error occurred
  - Error message describing what went wrong
  - The offending symbol/text (if available)
- **Backward Compatible**: Existing code using `parse_sessions()` continues to work as before

## Usage

### New API: `parse()` method

The new `parse()` method returns a `ParseResult` object containing both exercises and errors:

```python
from parser import Parser

# Parse input with potential errors
parser = Parser.from_string("""
Bench press 75k: 4, 4x5
Squat 70l: 5x10
Overhead press: 5x5x40k
""")

result = parser.parse()

# Access parsed exercises
for exercise in result.exercises:
    print(exercise)

# Check for errors
if result.has_errors:
    print(f"\nFound {len(result.errors)} error(s):")
    for error in result.errors:
        print(f"  {error}")
else:
    print("✓ All input parsed successfully")
```

### ParseResult Class

The `ParseResult` class provides:

**Properties:**
- `exercises`: List of successfully parsed `Exercise` objects
- `errors`: List of `ParseError` objects
- `has_errors`: Boolean indicating if any errors occurred
- `is_valid`: Boolean indicating if parsing was completely successful (no errors)

**Methods:**
- `get_error_summary()`: Returns a formatted string with all errors
- `print_errors()`: Prints all errors to stdout

### ParseError Class

Each `ParseError` contains:
- `line`: Line number (1-indexed)
- `column`: Column number (0-indexed)
- `message`: Description of the error
- `offending_symbol`: The token that caused the error (if available)

### Legacy API: `parse_sessions()` method

For backward compatibility, the original `parse_sessions()` method still works:

```python
from parser import Parser

# This will raise ValueError if there are any errors
try:
    exercises = Parser.from_string(input_text).parse_sessions()
except ValueError as e:
    print(f"Parsing error: {e}")
```

## Examples

### Example 1: Valid Input

```python
from parser import Parser

input_text = """
Bench press 75k: 4, 4x5
Squat 70k: 5x10
"""

result = Parser.from_string(input_text).parse()

print(f"Parsed {len(result.exercises)} exercises")
print(f"Errors: {len(result.errors)}")
# Output:
# Parsed 2 exercises
# Errors: 0
```

### Example 2: Input with Errors

```python
from parser import Parser

# Input with an invalid character 'l' instead of 'k'
input_text = """
Bench press 75k: 4, 4x5
Squat 70l: 5x10
Overhead press: 5x5x40k
"""

result = Parser.from_string(input_text).parse()

print(f"Parsed {len(result.exercises)} exercises")
print(f"Errors: {len(result.errors)}")

# Display errors with line and column information
for error in result.errors:
    print(f"  Line {error.line}:{error.column} - {error.message}")

# Output:
# Parsed 2 exercises (Bench press and Overhead press)
# Errors: 1
#   Line 2:10 - mismatched input 'l' expecting {'k', ':', INT}
```

### Example 3: Using Error Summary

```python
from parser import Parser

input_text = """
Bench press 75k: 4, 4x5
Invalid syntax here @#$
Squat 70k: 5x10
"""

result = Parser.from_string(input_text).parse()

# Print formatted error summary
result.print_errors()

# Or get as string
summary = result.get_error_summary()
print(summary)
```

### Example 4: File Parsing with Error Handling

```python
from parser import Parser
from antlr4 import InputStream

def parse_file(file_path: str):
    with open(file_path, 'r') as f:
        content = f.read()

    parser = Parser(InputStream(content))
    result = parser.parse()

    print(f"✓ Successfully parsed {len(result.exercises)} exercises")

    if result.has_errors:
        print(f"\n⚠ Found {len(result.errors)} errors:")
        for i, error in enumerate(result.errors, 1):
            print(f"  {i}. {error}")

    return result

# Usage
result = parse_file('training-log.txt')
```

## Running the Examples

A complete example is provided in `examples/error_handling_example.py`:

```bash
python examples/error_handling_example.py
```

This will demonstrate:
1. Parsing input with intentional errors
2. Displaying line/column information for each error
3. Showing successfully parsed exercises
4. Parsing completely valid input

## Implementation Details

### Error Listener

The parser uses a custom `TrainingErrorListener` that captures all syntax errors reported by ANTLR:

```python
from parser import TrainingErrorListener

error_listener = TrainingErrorListener()
# Attach to lexer and parser
lexer.addErrorListener(error_listener)
parser.addErrorListener(error_listener)

# After parsing
for error in error_listener.errors:
    print(error)
```

### Error Recovery

The parser automatically attempts to recover from errors and continue parsing:

1. **Syntax Errors**: Captured by the error listener with line/column information
2. **Invalid Tokens**: Skipped, parsing continues with next valid token
3. **Malformed Exercises**: Skipped, other exercises are still parsed
4. **Visitor Errors**: Caught and handled gracefully, allowing parsing to continue

### What Gets Parsed

When errors occur:
- **Valid exercises** before the error are parsed successfully
- **Valid exercises** after the error are parsed successfully
- **Invalid/malformed exercises** are skipped
- All errors are collected and reported with their locations

## Error Messages

Common error messages you might see:

- `mismatched input 'X' expecting Y` - Wrong character/token at position
- `extraneous input 'X' expecting Y` - Extra unexpected character
- `missing X at Y` - Required token is missing
- `no viable alternative at input` - Parser cannot determine how to proceed

All messages include the exact line and column where the problem occurred.
