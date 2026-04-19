# Complete Grammar Format Guide

This document provides a comprehensive reference of all supported input formats for the training log parser. Each format is documented with examples and corresponding test cases that validate the functionality.

**All examples in this guide are backed by automated tests** in `parser/test_grammar_formats_e2e.py`.

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Exercise Names](#exercise-names)
3. [Weight Specifications](#weight-specifications)
4. [Set Notation Formats](#set-notation-formats)
   - [Whole Set Notation](#whole-set-notation-nxnxweight)
   - [Group of Reps Notation](#group-of-reps-notation-weight-nxn)
   - [Fixed Reps Multiple Weights](#fixed-reps-multiple-weights-nxxweightweight)
   - [Single Rep Notation](#single-rep-notation-weight-nnn)
5. [Combining Formats](#combining-formats)
6. [Complete Examples](#complete-examples)
7. [Running Tests](#running-tests)

## Quick Reference

| Format | Syntax | Example | Use Case |
|--------|--------|---------|----------|
| **Whole Set** | `NxNxweight` | `5x6x40k` | 5 sets of 6 reps at 40kg |
| **Group of Reps** | `weight NxN` | `70k: 5x10` | 5 sets of 10 reps at 70kg |
| **Fixed Reps Multiple Weights** | `Nxxweight,weight,...` | `15xx40k,50k` | 15 reps at 40kg, then 15 reps at 50kg |
| **Single Rep** | `weight: N,N,N` | `60k: 20,15,8` | Different reps at same weight |
| **With RIR** | `NxNxweight RIR` | `3x5x100k 2` | With 2 Reps In Reserve |

## Exercise Names

### Predefined Exercises

The following exercise names are predefined in the grammar:
- `Deadlift`
- `Squat`
- `Bench press`
- `Overhead press`

**Test Examples:**
```python
# test_predefined_exercise_deadlift
'Deadlift 100k: 5'

# test_predefined_exercise_squat
'Squat 100k: 5'

# test_predefined_exercise_bench_press
'Bench press 75k: 8'

# test_predefined_exercise_overhead_press
'Overhead press 40k: 6'
```

### Custom Exercise Names

You can use any custom exercise name containing:
- Letters (a-z, A-Z)
- Accented characters (á, é, í, ó, ú, ñ)
- Spaces
- Hyphens (-)

**Test Examples:**
```python
# test_custom_exercise_simple_name
'Bench 60k: 10'

# test_custom_exercise_multi_word_name
'Row en maquina 41k: 15'

# test_custom_exercise_with_accents
'Row en máquina 41k: 1'

# test_custom_exercise_with_hyphen
'Cable-fly 20k: 12'
```

## Weight Specifications

Weights can be specified in four formats:

| Format | Example | Notes |
|--------|---------|-------|
| Integer with 'k' | `100k` | Recommended for clarity |
| Integer without 'k' | `100` | 'k' is optional |
| Decimal with 'k' | `62.5k` | For fractional weights |
| Decimal without 'k' | `62.5` | 'k' is optional |

**All weights are interpreted as kilograms (kg).**

**Test Examples:**
```python
# test_weight_integer_with_k
'Squat 100k: 5'

# test_weight_integer_without_k
'Squat 100: 5'

# test_weight_decimal_with_k
'Bench press 62.5k: 5'

# test_weight_decimal_without_k
'Bench press 62.5: 5'
```

## Set Notation Formats

### Whole Set Notation (NxNxweight)

**Format:** `<sets>x<reps>x<weight>`

Complete set specification where all parameters are defined in one expression.

**Use Cases:**
- Consistent sets across a compound lift
- Most compact notation
- Strength training programs

**Syntax:**
- `N` = number of sets (integer)
- `N` = number of reps (integer)
- `weight` = weight specification

**Optional:** RIR (Reps In Reserve) can be appended as a space-separated integer

**Test Examples:**
```python
# test_whole_set_basic
'Overhead press: 5x6x40k'
# Result: 5 sets of 6 reps at 40kg

# test_whole_set_single_set
'Deadlift: 1x1x100k'
# Result: 1 set of 1 rep at 100kg

# test_whole_set_multiple_sets
'Bench press: 3x8x75k'
# Result: 3 sets of 8 reps at 75kg

# test_whole_set_decimal_weight
'Squat: 3x5x82.5k'
# Result: 3 sets of 5 reps at 82.5kg

# test_whole_set_without_k_suffix
'Squat: 3x5x100'
# Result: 3 sets of 5 reps at 100kg

# test_whole_set_with_rir
'Squat: 3x5x100k 2'
# Result: 3 sets of 5 reps at 100kg with 2 RIR
```

### Group of Reps Notation (weight NxN)

**Format:** `<weight> [:]? <sets>x<reps>`

Weight specified first, followed by set and rep structure.

**Use Cases:**
- Weight-focused tracking
- Bodybuilding programs
- When weight is the primary variable

**Syntax:**
- `weight` = weight specification
- `:` = optional separator
- `N` = number of sets (integer)
- `N` = number of reps (integer)

**Test Examples:**
```python
# test_group_of_reps_with_colon
'Squat 70k: 5x10'
# Result: 5 sets of 10 reps at 70kg

# test_group_of_reps_without_colon
'Squat 70k 5x10'
# Result: 5 sets of 10 reps at 70kg

# test_group_of_reps_single_set
'Deadlift 100k: 1x5'
# Result: 1 set of 5 reps at 100kg

# test_group_of_reps_decimal_weight
'Bench press 67.5k: 3x8'
# Result: 3 sets of 8 reps at 67.5kg
```

### Fixed Reps Multiple Weights (Nxxweight,weight,...)

**Format:** `<reps>xx<weight>,<weight>[,<weight>...]`

Fixed reps across multiple sets with different weights. **Note the double 'xx'.**

**Use Cases:**
- Progressive overload (increasing weight)
- Pyramid sets (weight progression)
- Drop sets (decreasing weight)
- Warmup progressions

**Syntax:**
- `N` = number of reps (integer) - same for all sets
- `xx` = double 'x' separator (distinguishes from group notation)
- `weight,weight,...` = comma-separated weight values

**Test Examples:**
```python
# test_fixed_reps_two_weights
'Squat: 15xx40k,50k'
# Result: 15 reps at 40kg, 15 reps at 50kg

# test_fixed_reps_three_weights
'Bench press: 8xx60k,70k,80k'
# Result: 8 reps at each of 60kg, 70kg, 80kg

# test_fixed_reps_four_weights
'Deadlift: 5xx100,110,120,130'
# Result: 5 reps at each weight

# test_fixed_reps_decimal_weights
'Squat: 8xx60.5,70.5,80.5'
# Result: 8 reps at each weight

# test_fixed_reps_progressive_overload
'Squat: 5xx60k,70k,80k,90k,100k'
# Result: Progressive loading with 5 reps per set
```

### Single Rep Notation (weight: N,N,N)

**Format:** `<weight> [:]? <rep>,<rep>[,<rep>...]`

Weight specified once, followed by varying rep counts for each set.

**Use Cases:**
- AMRAP (As Many Reps As Possible) sets
- Tracking fatigue across sets
- Descending rep schemes
- Irregular set structures

**Syntax:**
- `weight` = weight specification
- `:` = optional separator
- `N,N,...` = comma-separated rep counts

**Test Examples:**
```python
# test_single_rep_with_colon
'Deadlift 60k: 20, 15, 8, 8'
# Result: 4 sets with varying reps at 60kg

# test_single_rep_without_spaces
'Deadlift 60k: 20,15,8,8'
# Result: Same, without spaces

# test_single_rep_descending_reps
'Bench press 75k: 4, 4, 3, 2'
# Result: Descending reps showing fatigue

# test_single_rep_two_sets
'Row en maquina 41k: 15, 8'
# Result: 2 sets with different reps

# test_single_rep_single_set
'Deadlift 100k: 5'
# Result: Single set of 5 reps
```

## Combining Formats

Multiple set notations can be combined in a single exercise entry. They are separated by spaces or commas.

### Mixing Single and Group Notation

**Test Examples:**
```python
# test_mixed_single_and_group_with_colon
'Bench press 10k: 4, 4x5'
# Result: 1 set of 4 reps, then 4 sets of 5 reps

# test_mixed_single_and_group_without_colon
'Bench press 10k 4, 4x5'
# Result: Same without colon
```

### Mixing Whole Set Notations

**Test Examples:**
```python
# test_mixed_whole_sets
'Bench press 1x1x60k 1x2x40k'
# Result: 1 rep at 60kg, then 2 reps at 40kg

# test_mixed_three_whole_sets
'Bench press 3x50x10k 3x15x10k 3x6x10k'
# Result: Drop set pattern with varying reps
```

### Mixing Whole Set and Single Rep

**Test Examples:**
```python
# test_mixed_whole_set_and_single_rep
'Bench press 3x50x10k 60: 12,11'
# Result: 3 sets of 50 reps at 10kg, then 12 and 11 reps at 60kg

# test_mixed_whole_set_and_single_rep_with_k
'Bench press 3x50x10k 60k: 12,11'
# Result: Same with 'k' suffix
```

### Mixing Single Then Whole Sets

**Test Examples:**
```python
# test_mixed_single_then_whole_sets
'Bench 60k: 2,3, 1x1x60k 1x2x40k'
# Result: 2 reps, 3 reps, 1 rep, 2 reps at various weights
```

### Mixing Fixed Reps and Other Formats

**Test Examples:**
```python
# test_mixed_fixed_reps_and_whole_set
'Squat: 15xx40,50 1x1x10k'
# Result: 15 reps at 40kg, 15 at 50kg, 1 at 10kg

# test_mixed_fixed_reps_and_single_rep
'Squat: 15xx40,50 60k: 12,11'
# Result: Progressive weights then additional sets
```

### Complex Mixed Formats

**Test Examples:**
```python
# test_complex_mixed_format
'Squat 60k: 10, 3x8x80k, 5xx100k,110k,120k'
# Result: Complex combination of all formats
```

## Complete Examples

### Simple Workout Session

```
Bench press 75k: 4, 4x5
Squat 70k: 5x10
Overhead press: 5x5x40k
Deadlift 60k: 20, 15,8,8
Row en maquina 41k: 15, 8
```

**Test:** `test_multiple_exercises_complex`

### Progressive Overload Session

```
Squat: 5xx60k,70k,80k,90k,100k
Bench press: 5xx40k,50k,60k,70k
Deadlift: 3xx100k,120k,140k
```

**Test:** `test_multiple_exercises_progressive_overload`

### Pyramid Training

```
Bench press: 12xx40k,50k,60k,70k 10xx80k 12xx70k,60k,50k,40k
```

**Test:** `test_pyramid_training_session`

### Drop Set Pattern

```
Bench press: 8xx80k,60k,40k,20k
```

**Test:** `test_drop_set_pattern`

## Special Cases

### Bodyweight Exercises (Zero Weight)

```python
# test_weight_zero_integer
'Push-up 0k: 20'

# test_weight_zero_decimal
'Pull-up 0.0k: 10'
```

### High Repetition Endurance Training

```python
# test_triple_digit_reps
'Squat 20k: 100'
```

### Many Sets

```python
# test_many_sets_whole_notation
'Bench press: 10x5x60k'
```

### Extra Newlines

```python
# test_exercise_with_extra_newlines
'Squat 100k: 5\n\n\n'

# test_multiple_exercises_with_blank_lines
'Bench press 75k: 8\n\nSquat 100k: 5\n'
```

## Running Tests

All format examples are validated by end-to-end tests in `parser/test_grammar_formats_e2e.py`.

### Run All E2E Format Tests

```bash
# Run just the grammar format tests
pytest parser/test_grammar_formats_e2e.py -v

# Run with detailed output
pytest parser/test_grammar_formats_e2e.py -v -s

# Run a specific test
pytest parser/test_grammar_formats_e2e.py::TestGrammarFormatsE2E::test_whole_set_basic -v
```

### Run All Tests (Including E2E)

```bash
# Run complete test suite
make test

# Run just Python tests (includes E2E)
make test-python
```

## Grammar Rules Reference

The complete ANTLR4 grammar rules:

```antlr4
grammar training;

workout: exercise+;

EXERCISE_NAME: 'Deadlift' | 'Squat' | 'Bench press'| 'Overhead press' | NAME;
exercise_name : EXERCISE_NAME;
NAME: ALPHABET+ (WS+ ALPHABET+)*;

weight: INT ('.' INT)? 'k'? ;
INT: DIGIT+;
exercise: exercise_name ':'? set_ NEWLINE*;

set_:
    set_ ','? set_                          #multiple_set_
    | INT                                    #single_rep_set_
    | INT 'x' INT                           #group_of_rep_set
    | INT 'x' INT 'x' weight rir?           #whole_set_
    | weight ':'? set_?                     #weight_
    | INT 'xx' weight (',' weight)*         #fixed_reps_multiple_weight
    ;

rir: INT;

fragment DIGIT: '0'..'9' ;

ALPHABET: [a-zA-Z] | [áéíóúñ] | [-] ;
NEWLINE:'\r'? '\n' ;
WS:   [ \t]+ -> skip;
```

## See Also

- [SYNTAX.md](SYNTAX.md) - Detailed syntax documentation with use cases
- [parser/test_grammar_formats_e2e.py](parser/test_grammar_formats_e2e.py) - Complete test suite
- [parser/test_parser.py](parser/test_parser.py) - Additional parser tests
- [training.g4](training.g4) - ANTLR4 grammar definition
