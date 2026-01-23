# Workout Training Log Syntax Guide

This document describes the Domain-Specific Language (DSL) for recording workout training sessions. The parser converts text-based workout entries into structured data.

## Table of Contents

- [Basic Structure](#basic-structure)
- [Exercise Names](#exercise-names)
- [Notation Patterns](#notation-patterns)
  - [Whole Set Notation](#whole-set-notation)
  - [Group of Reps Notation](#group-of-reps-notation)
  - [Fixed Reps with Multiple Weights](#fixed-reps-with-multiple-weights)
  - [Single Rep Notation](#single-rep-notation)
  - [Weight Prefix Notation](#weight-prefix-notation)
- [Weight Specification](#weight-specification)
- [Combining Patterns](#combining-patterns)
- [Complete Examples](#complete-examples)
- [Grammar Rule Reference](#grammar-rule-reference)

## Basic Structure

Each exercise entry follows this general format:

```
<exercise_name> [weight] [:] <set_notation> [<set_notation>...]
```

- **Exercise name**: Required, can include spaces and accents
- **Weight**: Optional, can be specified as prefix or within notation
- **Colon**: Optional separator between exercise and sets
- **Set notation**: One or more set specifications (see patterns below)
- **Newline**: Each exercise must end with a newline

## Exercise Names

Exercise names can be:
- Predefined exercises: `Deadlift`, `Squat`, `Bench press`, `Overhead press`
- Custom names: Any combination of letters (including accents like á, é, í, ó, ú, ñ), spaces, and hyphens

**Grammar Rule**: `exercise_name` → `EXERCISE_NAME`

**Examples**:
```
Bench press
Squat
Row en máquina
Cable-fly
```

## Notation Patterns

### Whole Set Notation

**Pattern**: `<sets>x<reps>x<weight>`

Specifies a complete set structure where all parameters are explicitly defined.

**Grammar Rule**: `set_` → `INT 'x' INT 'x' weight` (`whole_set_`)

**Use Cases**:
- Recording sets where all parameters are identical
- Most compact notation for consistent sets
- Ideal for compound lifts with same weight across sets

**Examples**:
```
Overhead press: 5x6x40k
  → 5 sets of 6 reps at 40kg

Bench press: 3x8x75k
  → 3 sets of 8 reps at 75kg

Squat: 1x1x100k
  → 1 set of 1 rep at 100kg
```

**Parsed Structure**:
```python
# 5x6x40k produces:
[
  {'repetitions': 6, 'weight': {'amount': 40.0, 'unit': 'kg'}},
  {'repetitions': 6, 'weight': {'amount': 40.0, 'unit': 'kg'}},
  {'repetitions': 6, 'weight': {'amount': 40.0, 'unit': 'kg'}},
  {'repetitions': 6, 'weight': {'amount': 40.0, 'unit': 'kg'}},
  {'repetitions': 6, 'weight': {'amount': 40.0, 'unit': 'kg'}}
]
```

### Group of Reps Notation

**Pattern**: `<weight> <sets>x<reps>`

Specifies weight first, then the number of sets and reps per set.

**Grammar Rule**: `set_` → `weight ':'? set_?` where nested `set_` → `INT 'x' INT` (`group_of_rep_set`)

**Use Cases**:
- When you want to specify weight separately from set/rep structure
- More readable when weight is a primary focus
- Useful for warmup sets or progressive overload tracking

**Examples**:
```
Squat 70k: 5x10
  → 5 sets of 10 reps at 70kg

Bench press 50k 3x8
  → 3 sets of 8 reps at 50kg (colon optional)

Deadlift 100k: 1x5
  → 1 set of 5 reps at 100kg
```

**Parsed Structure**:
```python
# 70k: 5x10 produces:
[
  {'repetitions': 10, 'weight': {'amount': 70.0, 'unit': 'kg'}},
  {'repetitions': 10, 'weight': {'amount': 70.0, 'unit': 'kg'}},
  {'repetitions': 10, 'weight': {'amount': 70.0, 'unit': 'kg'}},
  {'repetitions': 10, 'weight': {'amount': 70.0, 'unit': 'kg'}},
  {'repetitions': 10, 'weight': {'amount': 70.0, 'unit': 'kg'}}
]
```

### Fixed Reps with Multiple Weights

**Pattern**: `<reps>xx<weight>,<weight>[,<weight>...]`

Specifies a fixed number of reps with different weights across sets (note the double 'xx').

**Grammar Rule**: `set_` → `INT 'xx' weight (',' weight)*` (`fixed_reps_multiple_weight`)

**Use Cases**:
- Progressive loading: increasing weight while keeping reps constant
- Pyramid sets: varying weight across sets with same rep count
- Drop sets: decreasing weight with consistent reps
- Warmup progressions

**Examples**:
```
Squat: 15xx40k,50k
  → Set 1: 15 reps at 40kg
  → Set 2: 15 reps at 50kg

Bench press: 8xx60k,70k,80k
  → Set 1: 8 reps at 60kg
  → Set 2: 8 reps at 70kg
  → Set 3: 8 reps at 80kg

Deadlift: 5xx100,110,120,130
  → Set 1: 5 reps at 100kg
  → Set 2: 5 reps at 110kg
  → Set 3: 5 reps at 120kg
  → Set 4: 5 reps at 130kg
```

**Parsed Structure**:
```python
# 15xx40,50 produces:
[
  {'repetitions': 15, 'weight': {'amount': 40.0, 'unit': 'kg'}},
  {'repetitions': 15, 'weight': {'amount': 50.0, 'unit': 'kg'}}
]
```

### Single Rep Notation

**Pattern**: `<weight> [:]? <reps>[, <reps>...]`

Specifies a weight followed by individual rep counts for each set.

**Grammar Rule**: `set_` → `INT` (`single_rep_set_`) combined with `weight ':'? set_?`

**Use Cases**:
- Recording sets with varying reps at same weight
- AMRAP (As Many Reps As Possible) sets
- Tracking fatigue across sets
- Irregular set structures

**Examples**:
```
Deadlift 60k: 20, 15, 8, 8
  → Set 1: 20 reps at 60kg
  → Set 2: 15 reps at 60kg
  → Set 3: 8 reps at 60kg
  → Set 4: 8 reps at 60kg

Bench press 75k: 4, 4, 3, 2
  → 4 sets with descending reps at 75kg

Row en maquina 41k: 15, 8
  → Set 1: 15 reps at 41kg
  → Set 2: 8 reps at 41kg
```

**Parsed Structure**:
```python
# 60k: 20, 15, 8, 8 produces:
[
  {'repetitions': 20, 'weight': {'amount': 60.0, 'unit': 'kg'}},
  {'repetitions': 15, 'weight': {'amount': 60.0, 'unit': 'kg'}},
  {'repetitions': 8, 'weight': {'amount': 60.0, 'unit': 'kg'}},
  {'repetitions': 8, 'weight': {'amount': 60.0, 'unit': 'kg'}}
]
```

### Weight Prefix Notation

**Pattern**: `<weight> [:] <set_notation>`

Any set notation can be prefixed with a weight specification.

**Grammar Rule**: `set_` → `weight ':'? set_?` (`weight_`)

**Use Cases**:
- Consistent weight across varied set structures
- More flexible than whole set notation
- Can be combined with any other pattern

**Examples**:
```
Bench press 10k: 4, 4x5
  → Set 1: 4 reps at 10kg
  → Sets 2-6: 5 sets of 5 reps at 10kg

Squat 80k 3x5, 2x3
  → Sets 1-3: 3 sets of 5 reps at 80kg
  → Sets 4-5: 2 sets of 3 reps at 80kg
```

## Weight Specification

Weights can be specified in several formats:

**Grammar Rule**: `weight` → `INT ('.' INT)? 'k'?`

**Formats**:
- **Integer with 'k'**: `100k` (100 kilograms)
- **Integer without 'k'**: `100` (100 kilograms, 'k' is optional)
- **Decimal with 'k'**: `62.5k` (62.5 kilograms)
- **Decimal without 'k'**: `62.5` (62.5 kilograms)

**Note**: The unit is always interpreted as kilograms (kg). The 'k' suffix is optional but recommended for clarity.

**Examples**:
```
Bench press: 3x8x75k      # 75kg
Squat: 5x5x100            # 100kg
Deadlift: 1x1x62.5k       # 62.5kg
```

## Combining Patterns

Multiple set notations can be combined in a single exercise entry, separated by spaces or commas.

**Grammar Rule**: `set_` → `set_ ','? set_` (`multiple_set_`)

**Examples**:

### Mixing Whole Sets and Single Reps
```
Bench press 60k: 2,3, 1x1x60k 1x2x40k
  → Set 1: 2 reps at 60kg
  → Set 2: 3 reps at 60kg
  → Set 3: 1 rep at 60kg
  → Set 4: 2 reps at 40kg
```

### Mixing Fixed Reps and Group of Reps
```
Squat: 15xx40,50 1x1x10k
  → Set 1: 15 reps at 40kg
  → Set 2: 15 reps at 50kg
  → Set 3: 1 rep at 10kg
```

### Mixing Fixed Reps and Single Reps
```
Squat: 15xx40,50 60k: 12,11
  → Set 1: 15 reps at 40kg
  → Set 2: 15 reps at 50kg
  → Set 3: 12 reps at 60kg
  → Set 4: 11 reps at 60kg
```

### Multiple Whole Sets
```
Bench press 3x50x10k 3x15x10k 3x6x10k
  → Sets 1-3: 3 sets of 50 reps at 10kg
  → Sets 4-6: 3 sets of 15 reps at 10kg
  → Sets 7-9: 3 sets of 6 reps at 10kg
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

### Progressive Overload Session
```
Squat: 5xx60k,70k,80k,90k,100k
Bench press: 5xx40k,50k,60k,70k
Deadlift: 3xx100k,120k,140k
```

### Pyramid Training
```
Bench press: 12xx40k,50k,60k,70k 10xx80k 12xx70k,60k,50k,40k
```

### Mixed Format Session
```
Squat 60k: 10, 3x8x80k, 5xx100k,110k,120k
Bench press: 1x15x20k 5xx40k,50k,60k 3x5x70k
```

## Grammar Rule Reference

The complete ANTLR4 grammar rules for set notation:

```antlr4
set_:
    set_ ','? set_                          # multiple_set_
    | INT                                    # single_rep_set_
    | INT 'x' INT                           # group_of_rep_set
    | INT 'x' INT 'x' weight                # whole_set_
    | weight ':'? set_?                     # weight_
    | INT 'xx' weight (',' weight)*         # fixed_reps_multiple_weight
    ;

weight: INT ('.' INT)? 'k'? ;

exercise: exercise_name ':'? set_ NEWLINE* ;

workout: exercise+ ;
```

### Rule Hierarchy

1. **`workout`**: Top-level rule, one or more exercises
2. **`exercise`**: Combines exercise name with set notation
3. **`exercise_name`**: Exercise identifier (predefined or custom)
4. **`set_`**: Recursive rule supporting all notation patterns
5. **`weight`**: Weight specification (integer or decimal, optional 'k')

### Parsing Priority

The grammar rules are evaluated in the order they appear. When multiple patterns could match:

1. `multiple_set_` - Combines multiple set notations
2. `single_rep_set_` - Matches bare integers (rep counts)
3. `group_of_rep_set` - Matches `NxN` patterns
4. `whole_set_` - Matches `NxNxweight` patterns
5. `weight_` - Matches weight prefix with optional continuation
6. `fixed_reps_multiple_weight` - Matches `NxxW,W,...` patterns

This priority ensures that more specific patterns (like `whole_set_`) are matched before more general patterns (like `weight_`).

## Tips and Best Practices

### Consistency
- Choose one notation style per workout type for easier tracking
- Use whole set notation (`3x8x75k`) for consistent sets
- Use single rep notation (`75k: 8,7,6`) for AMRAP or fatigue tracking

### Readability
- Include the 'k' suffix for weights to improve clarity
- Use colons to separate exercise names from sets
- Add spaces between different set groups

### Use Cases by Pattern

| Pattern | Best For |
|---------|----------|
| Whole Set (`3x8x75k`) | Consistent sets, compound lifts, strength programs |
| Group of Reps (`75k: 3x8`) | Weight-focused tracking, bodybuilding |
| Fixed Reps Multiple Weights (`8xx60k,70k,80k`) | Progressive overload, pyramid sets, warmups |
| Single Rep (`75k: 8,7,6`) | AMRAP, cluster sets, fatigue tracking |
| Combined Patterns | Complex programs, periodization, mixed protocols |

### Common Mistakes to Avoid

❌ Missing newlines between exercises
```
Bench press: 3x8x75k Squat: 5x5x100k  # Wrong
```

✅ Each exercise on its own line
```
Bench press: 3x8x75k
Squat: 5x5x100k
```

❌ Single 'x' with multiple weights (use 'xx')
```
Squat: 5x40k,50k,60k  # Wrong: will not parse correctly
```

✅ Double 'xx' for fixed reps with multiple weights
```
Squat: 5xx40k,50k,60k
```

❌ Mixing units (parser assumes all weights are in kg)
```
Bench press: 3x8x165lbs  # Wrong: parser doesn't support lbs
```

✅ Convert to kilograms
```
Bench press: 3x8x75k  # 165lbs ≈ 75kg
```
