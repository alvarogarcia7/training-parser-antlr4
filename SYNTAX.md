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
- [Phase 2: iOS-Friendly Keyboard Syntax](#phase-2-ios-friendly-keyboard-syntax)
  - [Dot Separator](#dot-separator-)
  - [Double-Dot Separator](#double-dot-separator-)
  - [Slash-Delimited Weight Lists](#slash-delimited-weight-lists-)
  - [Comma as Decimal Separator](#comma-as-decimal-separator)
  - [RIR (Reps In Reserve) Dash Notation](#rir-reps-in-reserve-dash-notation)
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

## Phase 2: iOS-Friendly Keyboard Syntax

Phase 2 introduces alternative separators and notation that are keyboard-friendly on mobile devices, while maintaining full backwards compatibility with Phase 1 syntax.

### Dot Separator (`.`)

**Pattern**: `<sets>.<reps>.<weight>` (alternative to `<sets>x<reps>x<weight>`)

The dot (`.`) can be used as a separator equivalent to `x`. This is useful on iOS keyboards where entering 'x' requires extra taps.

**Examples**:
```
Squat: 5.5.100              ≡ 5x5x100
Bench press: 3.8.75k        ≡ 3x8x75k
Overhead press: 1.20.24     ≡ 1x20x24
```

**Use Cases**:
- Mobile device input where 'x' is inconvenient
- Keyboard layouts where 'x' requires shift or special key access
- Mixed notation with dots and x's in same session

### Double-Dot Separator (`..`)

**Pattern**: `<reps>..<weight>` (alternative to `<reps>xx<weight>`)

The double-dot (`..`) represents fixed reps with multiple weights.

**Examples**:
```
Squat: 1..24                ≡ 1xx24
Bench press: 15..40,50      ≡ 15xx40,50
Ms: 5..80,90,100           ≡ 5xx80,90,100
```

### Slash-Delimited Weight Lists (`/`)

**Pattern**: `<reps>..<weight>/<weight>/...` (alternative to `<reps>xx<weight>,<weight>,...`)

The slash (`/`) separates weights in a list, allowing comma to be used as a decimal separator.

**Examples**:
```
Squat: 20xx40/50/60         ≡ 20xx40,50,60
Deadlift: 1.20.24/27,5/28,1 ≡ 1x20x24,27.5,28.1
```

**Use Cases**:
- Locales where comma is the decimal separator
- Avoiding ambiguity between list commas and decimal commas
- Clear separation of weight values in progressive loading

### Comma as Decimal Separator

**Pattern**: `<weight>,<decimal>` (in slash-delimited contexts)

Within slash-delimited weight lists, comma (`,`) represents the decimal point.

**Examples**:
```
Ms: 20xx40/50,5/60,1        # 20 reps at 40kg, 50.5kg, 60.1kg
Ms: 62,5: 5x5               # 62.5kg weight with 5x5 reps
```

**Standalone Usage**:
```
Ms: 62,5                     # Single rep with 62.5kg weight
```

### RIR (Reps In Reserve) Dash Notation

**Pattern**: `<set>-<RIR>` (replaces Phase 1 space-based RIR)

RIR is now expressed with a dash (`-`) followed by an integer, indicating reps still available without failure. This replaces the Phase 1 space-integer format.

**Examples**:
```
Ms: 39-4                     # 39 reps with RIR 4
Ms: 15.18-3                  # 15 sets of 18 reps with RIR 3
Ms: 5.5.39-8                 # 5 sets of 5 reps at 39kg with RIR 8
Ms: 3x5x100k-2               # 3 sets of 5 reps at 100kg with RIR 2
Ms: 5xx80,90,100-3           # Fixed 5 reps with weights, RIR 3 for all
Ms: 5-2, 3-1                 # Multiple single reps, each with own RIR
```

**Applies To**:
- Single reps: `39-4`
- Group of reps: `15.18-3`
- Whole sets: `5.5.39-8`
- Fixed reps multi-weight: `5xx80,90,100-3`
- Slash-delimited weights: `1.20.24/27,5-3`

**Migration from Phase 1**:
- Phase 1: `Squat: 3x5x100k 2` → parsed as whole_set with RIR 2
- Phase 2: `Squat: 3x5x100k-2` → same meaning with dash notation
- Phase 1 space-RIR no longer supported; use dash notation instead

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

### Phase 2: iOS-Friendly Session (with dot separators)
```
Bench press: 3.8.75k
Squat: 5.5.100
Overhead press: 1.20.24
```

### Phase 2: With RIR Notation
```
Squat: 5.5.100-2            # 5 sets of 5 reps at 100kg, RIR 2
Bench press: 15.18-3         # 15 sets of 18 reps, RIR 3
Deadlift: 39-4               # 39 reps, RIR 4
Row: 3x5x80k-2, 3x3x85k-1   # Multiple sets with individual RIR values
```

### Phase 2: Slash-Delimited with Comma-Decimals
```
Squat: 20xx40/50/60          # 20 reps at 40kg, 50kg, 60kg
Deadlift: 1.20.24/27,5/28,1  # 1 set of 20 reps at 24kg, then 27.5kg, 28.1kg
Bench press: 5xx80,90,100-3  # Fixed 5 reps with weights, all RIR 3
```

## Grammar Rule Reference

The complete ANTLR4 grammar rules for set notation (Phase 2):

```antlr4
set_:
    INT rir_dash?                                           # single_rep_set_
    | weight ':'? set_?                                     # weight_
    | INT sep INT sep weight rir_dash?                      # whole_set_
    | INT double_sep weight_dot (COMMA weight_dot)* rir_dash? # fixed_reps_multiple_weight_v1
    | INT double_sep weight (SLASH weight)+ rir_dash?       # fixed_reps_multiple_weight_v2
    | set_ SLASH weight (SLASH weight)* rir_dash?           # whole_set_multi_weight_v2
    | INT sep INT rir_dash?                                 # group_of_rep_set
    | set_ ','? set_                                        # multiple_set_
    ;

sep        : 'x' | '.' ;
double_sep : 'xx' | '..' ;
rir_dash   : '-' INT ;

weight_dot : INT ('.' INT)? 'k'? ;
weight_com : INT (',' INT)? 'k'? ;
weight     : weight_com | weight_dot ;

exercise: exercise_name ':'? set_ NEWLINE* ;
exercise_name : 'Deadlift' | 'Squat' | 'Bench press' | 'Overhead press' | NAME ;

workout: exercise+ ;
```

### Rule Hierarchy

1. **`workout`**: Top-level rule, one or more exercises
2. **`exercise`**: Combines exercise name with set notation
3. **`exercise_name`**: Exercise identifier (predefined or custom keywords, or generic NAME)
4. **`set_`**: Recursive rule supporting all notation patterns (Phase 1 and Phase 2)
5. **`weight`**: Weight specification (integer or decimal, optional 'k')
6. **`rir_dash`**: RIR notation with dash separator (Phase 2)
7. **`sep`**: Single separator ('x' or '.')
8. **`double_sep`**: Double separator ('xx' or '..')

### Parsing Priority

The grammar rules are evaluated in the order they appear. When multiple patterns could match:

1. `single_rep_set_` - Bare integers with optional RIR
2. `weight_` - Weight with optional nested set
3. `whole_set_` - Three-component sets (N sep N sep weight)
4. `fixed_reps_multiple_weight_v1` - Fixed reps, v1 style (comma-separated)
5. `fixed_reps_multiple_weight_v2` - Fixed reps, v2 style (slash-separated)
6. `whole_set_multi_weight_v2` - Whole set with extra weights (slash-separated, Phase 2)
7. `group_of_rep_set` - Two-component sets (N sep N)
8. `multiple_set_` - Compound sets (comma-separated sets)

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
