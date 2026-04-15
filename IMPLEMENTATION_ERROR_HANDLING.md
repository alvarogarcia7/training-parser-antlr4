# Error Handling Implementation Summary

## Overview

Implemented comprehensive error handling for the training parser that:
- **Captures syntax errors** with line and column information
- **Continues parsing** after encountering errors
- **Returns partial results** with both successfully parsed exercises and error details
- **Maintains backward compatibility** with existing code

## Files Modified

### 1. `parser/model.py`
**Added:**
- `ParseError` class: Stores error information (line, column, message, offending symbol)
- `ParseResult` class: Contains both exercises and errors from parsing
  - Properties: `has_errors`, `is_valid`
  - Methods: `get_error_summary()`, `print_errors()`

### 2. `parser/parser.py`
**Added:**
- `TrainingErrorListener` class: Custom ANTLR error listener that captures syntax errors
- `Parser.parse()` method: New method that returns `ParseResult` with error handling

**Modified:**
- `Formatter` class: Added try-except blocks to all visitor methods to gracefully handle errors
  - `visitExercise()`: Catches errors during exercise processing
  - `visitExercise_name()`: Handles missing/invalid exercise names
  - `visitWeight()`: Handles invalid weight values
  - `visitWhole_set_()`: Handles malformed set definitions
  - `visitGroup_of_rep_set()`: Handles malformed group sets
  - `visitSingle_rep_set_()`: Handles malformed single sets
  - `visitFixed_reps_multiple_weight()`: Handles malformed fixed rep sets
  - `visitErrorNode()`: No longer raises exceptions
- `Parser.parse_sessions()`: Now uses `parse()` internally, raises ValueError on errors for backward compatibility

### 3. `parser/__init__.py`
**Added exports:**
- `ParseError`
- `ParseResult`
- `TrainingErrorListener`

### 4. `main.py`
**Updated:**
- Changed to use new `parse()` method
- Added error display functionality
- Now shows both exercises and errors

## Files Created

### Documentation
1. **`ERROR_HANDLING.md`** - Comprehensive error handling documentation
   - Feature overview
   - API documentation
   - Usage examples
   - Implementation details

2. **`QUICK_START_ERROR_HANDLING.md`** - Quick reference guide
   - Basic usage examples
   - Key features summary
   - Common patterns

### Examples
3. **`examples/error_handling_example.py`** - Comprehensive examples
   - Example with errors
   - Example with valid input
   - Using error summary methods
   - Backward compatibility demonstration
   - Detailed error information display

4. **`examples/parse_with_errors.py`** - CLI utility
   - Parse files and display errors with context
   - Shows error location in source
   - Useful for debugging training files

5. **`examples/test_error_input.txt`** - Sample file with intentional errors
   - Used for testing error handling

### Tests
6. **`parser/test_error_handling.py`** - Comprehensive test suite
   - Tests valid input produces no errors
   - Tests invalid input captures errors
   - Tests partial parsing of mixed valid/invalid input
   - Tests error contains line/column information
   - Tests error string representation
   - Tests ParseResult methods
   - Tests multiple error capture
   - Tests backward compatibility
   - Tests parsing continues after errors
   - Tests line number accuracy

## Key Features

### 1. Error Information
Each `ParseError` contains:
```python
error.line              # Line number (1-indexed)
error.column            # Column position (0-indexed)
error.message           # Descriptive error message
error.offending_symbol  # The token that caused the error
```

### 2. Partial Parsing
The parser continues after errors, extracting all valid exercises:
```python
Input: 3 lines (1 invalid)
Result: 2 exercises parsed + 1 error captured
```

### 3. Backward Compatibility
Existing code using `parse_sessions()` continues to work:
```python
# Old code - still works
exercises = Parser.from_string(text).parse_sessions()  # Raises on error

# New code - better error handling
result = Parser.from_string(text).parse()  # Never raises
if result.has_errors:
    for error in result.errors:
        print(error)
```

### 4. Error Recovery
The Formatter visitor uses try-except blocks to:
- Skip malformed exercises
- Continue to next valid exercise
- Preserve all successfully parsed data
- Avoid cascading failures

### 5. Flexible Error Reporting
Multiple ways to access error information:
```python
result = parser.parse()

# Check if valid
if result.is_valid:
    process(result.exercises)

# Get error summary
print(result.get_error_summary())

# Print errors
result.print_errors()

# Access individual errors
for error in result.errors:
    print(f"Line {error.line}: {error.message}")
```

## Usage Patterns

### Pattern 1: Parse and Check
```python
result = Parser.from_string(input_text).parse()
if result.is_valid:
    process_exercises(result.exercises)
else:
    log_errors(result.errors)
```

### Pattern 2: Parse with Reporting
```python
result = Parser.from_string(input_text).parse()
for exercise in result.exercises:
    save(exercise)
if result.has_errors:
    notify_user(result.get_error_summary())
```

### Pattern 3: File Parsing
```python
with open('training.txt') as f:
    result = Parser(InputStream(f.read())).parse()

print(f"Parsed {len(result.exercises)} exercises")
print(f"Errors: {len(result.errors)}")
```

## Testing

Run the test suite:
```bash
python -m pytest parser/test_error_handling.py -v
```

Run the example:
```bash
python examples/error_handling_example.py
```

Parse a file with error reporting:
```bash
python examples/parse_with_errors.py training-sample.txt
```

## Error Message Format

Errors are displayed in a clear, actionable format:
```
Line 2:10 - mismatched input 'l' expecting {'k', ':', INT} (at 'l')
```

Breaking down the format:
- `Line 2` - Which line has the error
- `:10` - Character position in that line
- `mismatched input 'l'` - What was found
- `expecting {'k', ':', INT}` - What was expected
- `(at 'l')` - The offending symbol

## Benefits

1. **Better User Experience**: Users see exactly where errors occur
2. **Partial Success**: Don't lose all work due to one typo
3. **Debugging**: Line/column info makes fixing errors easy
4. **Robustness**: Parser doesn't crash on unexpected input
5. **Flexibility**: Choose how to handle errors (ignore, log, fix)
6. **Compatibility**: Existing code continues to work

## Technical Details

### Error Listener Integration
```python
# Custom error listener captures all syntax errors
error_listener = TrainingErrorListener()
lexer.addErrorListener(error_listener)
parser.addErrorListener(error_listener)

# Errors are collected during parsing
tree = parser.workout()

# Errors available after parsing
for error in error_listener.errors:
    process_error(error)
```

### Visitor Error Handling
```python
def visitExercise(self, ctx):
    try:
        super().visitExercise(ctx)
        exercise = self.builder.addSeriesIfComplete()
        if exercise is not None:
            self.result.append(exercise)
    except Exception:
        # Skip this exercise, continue with next
        pass
```

### Error Recovery Strategy
1. **Lexer/Parser Level**: ANTLR captures syntax errors via error listener
2. **Visitor Level**: Try-except blocks catch runtime errors
3. **Builder Level**: Validation happens during construction
4. **Result Level**: Both successes and failures are returned

## Future Enhancements

Potential improvements:
- Add warning level (non-fatal issues)
- Include suggestions for common mistakes
- Add error recovery hints
- Support custom error handlers
- Add error filtering/grouping
