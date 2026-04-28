# Product Requirements Document: RIR (Reps In Reserve) Support

## Overview
This document defines RIR (Reps In Reserve) support across both traditional 'x' notation and iOS-friendly dot notation for the training parser.

## Motivation
RIR notation allows users to track effort level in workouts by specifying how many reps could have been performed but weren't. This is useful for tracking proximity to failure and managing fatigue. Supporting RIR across both x and dot notations ensures consistency and gives users choice in their preferred syntax.

## Requirements

### RIR Definition
RIR (Reps In Reserve) is specified using dash notation: `-N` where N is the number of reps left in reserve.

**Example**: `5.5.100-2` = 5 sets of 5 reps at 100kg with 2 reps left in reserve

## Supported Formats

### 1. Single Rep with RIR
**X Notation**: `INT-N`
- Pattern: `20-3`
- Meaning: 20 reps with 3 reps in reserve

**Dot Notation**: `INT-N` (same)
- Pattern: `20-3`
- Meaning: 20 reps with 3 reps in reserve

### 2. Group of Reps with RIR
**X Notation**: `NxM-RIR`
- Pattern: `3x10-2`
- Meaning: 3 sets of 10 reps with 2 reps in reserve (per set)

**Dot Notation**: `N.M-RIR`
- Pattern: `3.10-2`
- Meaning: 3 sets of 10 reps with 2 reps in reserve (per set)

### 3. Whole Set with RIR
**X Notation**: `NxMxweight-RIR`
- Pattern: `3x5x100k-2`
- Meaning: 3 sets of 5 reps at 100kg with 2 reps in reserve (per set)

**Dot Notation**: `N.M.weight-RIR`
- Pattern: `3.5.100k-2`
- Meaning: 3 sets of 5 reps at 100kg with 2 reps in reserve (per set)

### 4. Fixed Reps Multi-Weight with RIR
**X Notation**: `NxxW1,W2,...-RIR`
- Pattern: `5xx80,90,100-3`
- Meaning: 5 reps at 80kg, 5 reps at 90kg, 5 reps at 100kg, each with 3 reps in reserve

**Dot Notation**: `N..W1/W2/...-RIR` (Point 2 range notation)
- Pattern: `5..80/90/100-3`
- Meaning: 5 reps at 80kg, 5 reps at 90kg, 5 reps at 100kg, each with 3 reps in reserve

### 5. Point 4: Single Series N.weight with RIR
**Dot Notation Only**: `N.weightk-RIR`
- Pattern: `5.100k-2`
- Meaning: 5 reps at 100kg with 2 reps in reserve

## Grammar Implementation

All RIR patterns use the `rir_dash` rule:
```antlr4
rir_dash : DASH INT ;
```

This rule is optional (`rir_dash?`) in all set_ alternatives that support RIR:
- `single_rep_set_`: `INT rir_dash?`
- `single_rep_with_weight_k`: `INT DOT INT K_UNIT rir_dash?`
- `group_of_rep_set`: `INT sep INT rir_dash?`
- `whole_set_`: `INT sep INT sep weight rir_dash?`
- `fixed_reps_multiple_weight_v1`: `INT double_sep weight_dot (COMMA weight_dot)* rir_dash?`
- `fixed_reps_multiple_weight_v2`: `INT double_sep weight (SLASH weight)+ rir_dash?`
- `whole_set_multi_weight_v2`: `set_ SLASH weight (SLASH weight)* rir_dash?`

## Test Coverage

### RIR Support Matrix

| Format | X Notation | Dot Notation | Example | Status |
|--------|-----------|-------------|---------|--------|
| Single Rep | `20-3` | `20-3` | 20 reps, RIR 3 | ✅ Passing |
| Group of Reps | `3x10-2` | `3.10-2` | 3 sets of 10, RIR 2 | ✅ Passing |
| Whole Set | `3x5x100k-2` | `3.5.100k-2` | 3x5@100kg, RIR 2 | ✅ Passing |
| Fixed Reps Multi | `5xx80,90-3` | `5..80/90-3` | 5@80kg, 5@90kg, RIR 3 | ✅ Passing |
| N.weight (Point 4) | N/A | `5.100k-2` | 5 reps@100kg, RIR 2 | ✅ Passing |

### Test Count
- Phase 2 RIR tests: 8
- Point 4 RIR tests: 2
- RIR verification tests (x vs dot): 7
- **Total RIR tests: 17** ✅ All passing

## Backward Compatibility

RIR notation is **fully backward compatible**:
- All existing workouts without RIR continue to parse identically
- RIR is entirely optional (`rir_dash?` in grammar)
- No changes to existing format parsing
- Users can incrementally add RIR notation to workouts

## Implementation Notes

### Parser Visitor
The `rir_dash` extraction pattern is consistent across all visitor methods:

```python
rir: int | None = None
rir_ctx = ctx.rir_dash()
if rir_ctx is not None:
    rir = int(rir_ctx.getText()[1:])  # Remove leading '-'
```

### Series Builder
All `add_*` methods in `series_builder.py` accept optional `rir` parameter:
- `add_series(reps, weight, rir=None)`
- `add_single_rep_set(reps, rir=None)`
- `add_group_of_reps(series, reps, rir=None)`
- `add_whole_set(series, reps, weight, rir=None)`

### Model Validation
The `Set_` dataclass validates RIR:
```python
if rir is not None and rir < 0:
    raise ValueError(f"RIR must be non-negative, got {rir}")
```

## Examples

### Workout Log Example
```
Squat: 3.5.100k-2, 2.5.100k-3, 1.5.100k-5
Bench: 3x5x80k-1 5x3x60k-4
Deadlift: 1x5x140k-1
```

Parsed as:
- Squat: 3 sets @100kg RIR2, 2 sets @100kg RIR3, 1 set @100kg RIR5
- Bench: 3 sets @80kg RIR1, 5 sets @60kg RIR4
- Deadlift: 1 set @140kg RIR1

## Future Enhancements

Potential future improvements:
1. **Variable RIR per set**: Track different RIR values for each set in compound patterns
2. **Decimal RIR**: Support for fractional RIR (e.g., -2.5)
3. **Visual formatting**: Enhanced display of RIR in reports (e.g., "5@100kg (-2)" for clarity)

## Limitations

None currently identified. RIR is fully supported across both x and dot notation modes.

## Success Criteria
✅ RIR dash notation `-N` works in all set_ alternatives that support RIR
✅ Both x notation (NxM-RIR) and dot notation (N.M-RIR) produce identical results
✅ Point 4 N.weight format (N.weightk-RIR) fully supports RIR
✅ All 282 tests passing, including comprehensive RIR verification tests
✅ Backward compatibility maintained for workouts without RIR
