# Grammar Format E2E Tests

This test file (`test_grammar_formats_e2e.py`) provides comprehensive end-to-end validation of all supported input formats in the training log grammar.

## Purpose

1. **Validation** - Ensure all grammar formats work correctly
2. **Documentation** - Serve as executable examples of each format
3. **Regression Prevention** - Catch breaking changes to the grammar
4. **Format Discovery** - Help users understand all available formats

## Organization

Tests are organized by format type:

### Exercise Names
- Predefined exercises (Deadlift, Squat, Bench press, Overhead press)
- Custom exercise names (simple, multi-word, accented, hyphenated)

### Weight Specifications
- Integer with/without 'k' suffix
- Decimal with/without 'k' suffix

### Set Notation Formats
- **Whole Set** (`NxNxweight`) - Complete set specification
- **Group of Reps** (`weight NxN`) - Weight-first notation
- **Fixed Reps Multiple Weights** (`Nxxweight,weight,...`) - Progressive loading
- **Single Rep** (`weight: N,N,N`) - Varying reps at same weight

### Combined Formats
- Mixing different notation styles in one exercise
- Complex multi-format combinations

### Edge Cases
- Bodyweight exercises (zero weight)
- High repetition counts
- Multiple sets
- Extra whitespace and newlines

## Running Tests

```bash
# Run all grammar format tests
make test-grammar-formats

# Or directly with pytest
pytest parser/test_grammar_formats_e2e.py -v

# Run specific test
pytest parser/test_grammar_formats_e2e.py::TestGrammarFormatsE2E::test_whole_set_basic -v

# Run with coverage
pytest parser/test_grammar_formats_e2e.py --cov=parser --cov-report=html
```

## Integration

These tests are automatically run as part of:
- `make test` - Full test suite
- `make test-grammar-formats` - Grammar format tests only
- Pre-commit hooks (if configured)

## Relationship to Documentation

Each test corresponds to examples in:
- `GRAMMAR_FORMATS.md` - Complete format guide with test references
- `SYNTAX.md` - Detailed syntax documentation with use cases

The test names are referenced in `GRAMMAR_FORMATS.md` to show which test validates each example.

## Adding New Tests

When adding new grammar features:

1. Add test case(s) to `test_grammar_formats_e2e.py`
2. Document the format in `GRAMMAR_FORMATS.md` with test reference
3. Update `SYNTAX.md` if needed with use case details
4. Run `make test-grammar-formats` to validate

## Test Structure

Each test follows this pattern:

```python
def test_format_description(self) -> None:
    """Docstring explaining what format is tested"""
    result = self.parse('Exercise: format')
    expected = [Exercise('Exercise', [self.serie(reps, weight)])]
    self.assertEqual(result, expected)
```

Helper methods:
- `self.serie(reps, weight, rir=None)` - Creates a Set_ object
- `self.parse(text)` - Parses text into Exercise list
