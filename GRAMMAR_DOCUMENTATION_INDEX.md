# Grammar Documentation Index

Complete guide to the training log parser grammar, formats, and testing.

## Quick Start

**New to the parser?** Start here:
1. Read [QUICK_START_GRAMMAR.md](QUICK_START_GRAMMAR.md) for a 5-minute overview
2. Review [GRAMMAR_FORMATS.md](GRAMMAR_FORMATS.md) for complete format reference
3. Check [SYNTAX.md](SYNTAX.md) for detailed syntax and use cases
4. Run `make test-grammar-formats` to see all formats in action

## Documentation Files

### User Documentation

#### [QUICK_START_GRAMMAR.md](QUICK_START_GRAMMAR.md)
**5-minute quick start guide**
- Overview of main format types
- Simple examples
- Common patterns
- Key rules and tips

**Use this when:** You want a "quick introduction to get started"

#### [GRAMMAR_FORMATS.md](GRAMMAR_FORMATS.md)
**Complete format reference guide**
- Quick reference table of all formats
- Detailed explanation of each format type
- Examples with test references
- Complete workout session examples
- Running instructions

**Use this when:** You want to know "what formats are supported?"

#### [SYNTAX.md](SYNTAX.md)
**Detailed syntax documentation**
- In-depth explanation of each notation pattern
- Use cases for each format
- Best practices and tips
- Common mistakes to avoid
- Grammar rule reference

**Use this when:** You want to understand "how and when to use each format?"

### Developer Documentation

#### [parser/test_grammar_formats_e2e.py](parser/test_grammar_formats_e2e.py)
**Comprehensive E2E test suite**
- 70+ test cases covering all formats
- Organized by format type
- Executable examples of each format
- Edge case validation

**Use this when:** You want to see "working code examples" or "validate formats"

#### [parser/test_grammar_formats_e2e_README.md](parser/test_grammar_formats_e2e_README.md)
**Test suite documentation**
- Purpose and organization of E2E tests
- How to run tests
- How to add new tests
- Relationship to other documentation

**Use this when:** You want to understand or extend the test suite

#### [training.g4](training.g4)
**ANTLR4 grammar definition**
- Formal grammar specification
- Token and rule definitions
- Source of truth for parser behavior

**Use this when:** You want to see the "actual grammar rules"

## Format Categories

### Basic Formats
- [Exercise Names](GRAMMAR_FORMATS.md#exercise-names) - Predefined and custom names
- [Weight Specifications](GRAMMAR_FORMATS.md#weight-specifications) - Integer, decimal, with/without 'k'

### Set Notation Formats
- [Whole Set Notation](GRAMMAR_FORMATS.md#whole-set-notation-nxnxweight) - `NxNxweight` (e.g., `5x6x40k`)
- [Group of Reps Notation](GRAMMAR_FORMATS.md#group-of-reps-notation-weight-nxn) - `weight NxN` (e.g., `70k: 5x10`)
- [Fixed Reps Multiple Weights](GRAMMAR_FORMATS.md#fixed-reps-multiple-weights-nxxweightweight) - `Nxxweight,weight,...` (e.g., `15xx40k,50k`)
- [Single Rep Notation](GRAMMAR_FORMATS.md#single-rep-notation-weight-nnn) - `weight: N,N,N` (e.g., `60k: 20,15,8`)

### Advanced Features
- [Combining Formats](GRAMMAR_FORMATS.md#combining-formats) - Mix multiple notations in one exercise
- [RIR (Reps in Reserve)](GRAMMAR_FORMATS.md#whole-set-notation-nxnxweight) - Add RIR value to sets
- [Complete Examples](GRAMMAR_FORMATS.md#complete-examples) - Full workout sessions

## Testing

### Run Grammar Format Tests
```bash
# All grammar format tests
make test-grammar-formats

# Full test suite (includes grammar tests)
make test

# Specific test
pytest parser/test_grammar_formats_e2e.py::TestGrammarFormatsE2E::test_whole_set_basic -v
```

### Test Coverage
The E2E test suite covers:
- ✅ 4 predefined exercise names
- ✅ 4 custom exercise name types (simple, multi-word, accented, hyphenated)
- ✅ 4 weight specification formats
- ✅ 6+ whole set notation variations
- ✅ 4 group of reps notation variations
- ✅ 5 fixed reps multiple weights variations
- ✅ 5 single rep notation variations
- ✅ 10+ mixed format combinations
- ✅ 10+ edge cases and special scenarios
- ✅ Multiple complete workout examples

**Total: 70+ comprehensive test cases**

## Common Use Cases

### "I want to record a simple workout"
→ See [SYNTAX.md - Complete Examples](SYNTAX.md#complete-examples)

### "I want to track progressive overload"
→ See [GRAMMAR_FORMATS.md - Fixed Reps Multiple Weights](GRAMMAR_FORMATS.md#fixed-reps-multiple-weights-nxxweightweight)

### "I want to see all supported formats"
→ See [GRAMMAR_FORMATS.md - Quick Reference](GRAMMAR_FORMATS.md#quick-reference)

### "I want to understand when to use each format"
→ See [SYNTAX.md - Use Cases by Pattern](SYNTAX.md#tips-and-best-practices)

### "I want to validate my format works"
→ Run `make test-grammar-formats` or check [test_grammar_formats_e2e.py](parser/test_grammar_formats_e2e.py)

### "I want to add a new format to the grammar"
→ See [parser/test_grammar_formats_e2e_README.md - Adding New Tests](parser/test_grammar_formats_e2e_README.md#adding-new-tests)

## Integration with Build Pipeline

The grammar format tests are integrated into the build pipeline:

```makefile
make test
  ├── make typecheck          # Type checking
  ├── make compile-grammar    # Compile ANTLR grammar
  ├── make test-python        # All Python tests
  ├── make test-grammar-formats  # ← Grammar format E2E tests
  ├── make validate-datasets  # Dataset validation
  ├── make examples           # Run examples
  └── make test-lsp           # LSP tests
```

## Quick Format Examples

```
# Whole Set Notation
Overhead press: 5x6x40k

# Group of Reps Notation
Squat 70k: 5x10

# Fixed Reps Multiple Weights
Squat: 5xx60k,70k,80k,90k,100k

# Single Rep Notation
Deadlift 60k: 20,15,8,8

# Combined Formats
Bench press 10k: 4, 4x5, 1x1x60k

# Complete Workout
Bench press 75k: 4, 4x5
Squat 70k: 5x10
Overhead press: 5x5x40k
Deadlift 60k: 20,15,8,8
```

## Contributing

When adding new grammar features:

1. Update [training.g4](training.g4) with grammar rules
2. Add test cases to [test_grammar_formats_e2e.py](parser/test_grammar_formats_e2e.py)
3. Document in [GRAMMAR_FORMATS.md](GRAMMAR_FORMATS.md)
4. Add use cases to [SYNTAX.md](SYNTAX.md) if applicable
5. Run `make test` to validate all changes

## See Also

- [README.md](README.md) - Project overview and setup
- [AGENTS.md](AGENTS.md) - Development guide for AI agents
- [LSP_GUIDE.md](LSP_GUIDE.md) - Language Server Protocol features
