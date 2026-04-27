# Product Requirements Document: Dot Notation for Training Log Grammar

## Overview
This PRD defines new notation formats for the training log parser to support more compact and intuitive syntax using dots (`.`) instead of `x` for certain patterns.

## Motivation
The current grammar uses `x` as a separator in patterns like `5x6x40k` (5 sets of 6 reps at 40kg) and `15xx40,50` (15 reps at multiple weights). The dot notation provides:
- More compact syntax for certain use cases
- Clearer visual separation between components
- Familiarity for users who prefer period-based separators

## Requirements

### 1. Whole Set Notation with Dots: `N.N.weight`
**Current Format**: `1x10x23k` (1 set of 10 reps at 23kg)
**New Format**: `1.10.23` or `1.10.23k` (1 set of 10 reps at 23kg)

**Specifications**:
- Pattern: `INT '.' INT '.' weight`
- First number = number of sets
- Second number = number of repetitions per set
- Third number = weight (supports both integer and decimal)
- The `k` suffix is optional (defaults to kilograms)
- Must support decimal weights (e.g., `1.10.23.5k` for 23.5kg)

**Examples**:
```
Bench press: 1.10.23      → 1 set of 10 reps at 23kg
Squat: 3.8.100k           → 3 sets of 8 reps at 100kg
Deadlift: 1.5.62.5k       → 1 set of 5 reps at 62.5kg
```

### 2. Range Notation with Fixed Reps: `N..weight1/weight2`
**Current Format**: `10xx23,24` (10 reps each at 23kg and 24kg)
**New Format**: `10..23/24` (10 reps each at 23kg and 24kg)

**Specifications**:
- Pattern: `INT '..' weight ('/' weight)*`
- First number = repetitions (fixed for all sets)
- Weights separated by `/` instead of `,`
- Each weight represents one set at the specified weight
- Must support decimal weights
- The `k` suffix is optional on each weight

**Examples**:
```
Squat: 10..23/24          → 10 reps at 23kg, 10 reps at 24kg
Bench: 8..60/70/80k       → 8 reps at 60kg, 70kg, and 80kg
Press: 5..40.5/42.5/45    → 5 reps at 40.5kg, 42.5kg, and 45kg
```

### 3. Decimal Weight Support (Already Supported - Requirement Clarification)
**Requirement**: Continue to support decimal weights in all notations

**Specifications**:
- Pattern for weight: `INT ('.' INT)? 'k'?`
- Examples of valid weights: `23`, `23k`, `23.5`, `23.5k`, `62.5`, `100.25k`

## Grammar Changes Required

### Current Grammar (Relevant Sections)
```antlr4
weight: INT ('.' INT)? 'k'? ;
set_:
    set_ ','? set_ #multiple_set_
    | INT #single_rep_set_
    | INT 'x' INT #group_of_rep_set
    | INT 'x' INT 'x' weight rir? #whole_set_
    | weight ':'? set_? #weight_
    | INT 'xx' weight (',' weight)* #fixed_reps_multiple_weight
    ;
```

### Proposed Grammar Changes
```antlr4
weight: INT ('.' INT)? 'k'? ;
set_:
    set_ ','? set_ #multiple_set_
    | INT #single_rep_set_
    | INT 'x' INT #group_of_rep_set
    | INT 'x' INT 'x' weight rir? #whole_set_
    | INT '.' INT '.' weight rir? #whole_set_dots_
    | weight ':'? set_? #weight_
    | INT 'xx' weight (',' weight)* #fixed_reps_multiple_weight
    | INT '..' weight ('/' weight)* #range_reps_multiple_weight
    ;
```

**Key Additions**:
1. `INT '.' INT '.' weight rir?` → `#whole_set_dots_` - Whole set with dot notation
2. `INT '..' weight ('/' weight)*` → `#range_reps_multiple_weight` - Range notation with slash-separated weights

## Implementation Requirements

### Parser Changes (`parser/parser.py`)
1. Add `visitWhole_set_dots_` method to handle `N.N.weight` pattern
   - Extract: number_of_sets, number_of_reps, weight
   - Support optional RIR (Reps in Reserve)
   - Call `builder.add_whole_set(...)` similar to `visitWhole_set_`

2. Add `visitRange_reps_multiple_weight` method to handle `N..weight/weight` pattern
   - Extract: repetitions and list of weights
   - Call `builder.add_fixed_reps_multiple_weights(...)` similar to `visitFixed_reps_multiple_weight`

### SeriesBuilder Changes (`parser/series_builder.py`)
- **No changes required** - Existing methods `add_whole_set()` and `add_fixed_reps_multiple_weights()` can be reused

### Test Requirements
Add comprehensive tests to `parser/test_parser.py` and `parser/test_grammar_formats_e2e.py`:

1. **Whole Set Dot Notation Tests**:
   - Basic: `1.10.23` → 1 set of 10 reps at 23kg
   - With k suffix: `1.10.23k` → 1 set of 10 reps at 23kg
   - Multiple sets: `3.8.100k` → 3 sets of 8 reps at 100kg
   - Decimal weight: `1.5.62.5k` → 1 set of 5 reps at 62.5kg
   - With RIR: `3.8.100k 2` → 3 sets of 8 reps at 100kg with 2 RIR

2. **Range Notation Tests**:
   - Basic: `10..23/24` → 10 reps at 23kg, 10 reps at 24kg
   - Three weights: `8..60/70/80` → 8 reps each at 60kg, 70kg, 80kg
   - With k suffix: `10..23k/24k` → 10 reps each at 23kg and 24kg
   - Decimal weights: `5..40.5/42.5/45` → 5 reps each at 40.5kg, 42.5kg, 45kg

3. **Mixed Format Tests**:
   - Combine dot notation with existing formats
   - Combine range notation with existing formats
   - Test both new notations together

4. **Edge Cases**:
   - Single weight in range notation: `10..50` (valid, creates 1 set)
   - Zero weight: `10..0/0` (bodyweight progression)
   - Large numbers: `1.100.200k` (endurance with heavy weight)

## Backward Compatibility
- All existing formats (`NxNxweight`, `Nxxweight,weight`) remain supported
- No breaking changes to existing grammar
- Users can mix old and new notations in the same workout log

## Success Criteria
1. Grammar compiles successfully with ANTLR4
2. All new notation formats parse correctly
3. All existing tests continue to pass
4. New tests provide comprehensive coverage of new formats
5. Decimal weights work in all contexts
6. Documentation updated to reflect new formats

## Out of Scope
- Changing existing notation syntax
- Adding other separator characters beyond `.` and `/`
- Supporting ranges with notation other than `/` (e.g., `-` for ranges like `10..23-30`)

## Example Usage

### Complete Workout with New Notation
```
Squat: 1.10.23 1.10.23.5 1.8.25k
Bench press: 10..60/70/80k
Deadlift: 3.5.100k 2
Overhead press: 5..40.5/42.5/45
```

### Mixed with Existing Notation
```
Squat: 5xx60k,70k,80k 1.8.100k
Bench press: 3x8x75k 10..80/85/90
```

## Notes
- The dot in `N.N.weight` could conflict with decimal notation (e.g., `1.10.23.5` for weight 23.5kg), but context makes it unambiguous: the pattern requires exactly 3 components before any decimal in the weight
- Grammar precedence should ensure `1.5.62.5k` is parsed as `1 . 5 . 62.5k` not `1.5 . 62.5k`
- The range notation `..` is distinct from single `.` to avoid ambiguity
