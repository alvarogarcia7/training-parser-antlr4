# Dot Notation Grammar Guide

This document describes the new dot-based notation formats added to the training log grammar.

## Overview

The grammar now supports two additional notation styles using dots (`.`) instead of `x`:
1. **Whole Set Dot Notation**: `N.N.weight` - Compact format for sets × reps × weight
2. **Range Notation**: `N..weight/weight/...` - Fixed reps with multiple weights using `/` separator

These notations complement the existing `x`-based formats and can be freely mixed with them.

## Whole Set Dot Notation

### Format
```
INT '.' INT '.' weight [rir]
```

### Components
- **First number**: Number of sets
- **Second number**: Repetitions per set
- **Third number**: Weight (supports decimals)
- **Optional k suffix**: Indicates kilograms (default if omitted)
- **Optional RIR**: Reps in Reserve after the weight

### Examples

#### Basic Usage
```
1.10.23       → 1 set of 10 reps at 23kg
1.10.23k      → 1 set of 10 reps at 23kg (explicit k)
3.8.100k      → 3 sets of 8 reps at 100kg
```

#### Decimal Weights
```
1.5.62.5k     → 1 set of 5 reps at 62.5kg
2.8.75.5      → 2 sets of 8 reps at 75.5kg
5.10.82.5k    → 5 sets of 10 reps at 82.5kg
```

#### With RIR (Reps in Reserve)
```
3.8.100k 2    → 3 sets of 8 reps at 100kg with 2 RIR
5.5.80k 1     → 5 sets of 5 reps at 80kg with 1 RIR
```

### Comparison with X Notation
| Dot Notation | X Notation | Result |
|--------------|------------|--------|
| `1.10.23k` | `1x10x23k` | 1 set of 10 reps at 23kg |
| `3.8.100k` | `3x8x100k` | 3 sets of 8 reps at 100kg |
| `5.5.60k` | `5x5x60k` | 5 sets of 5 reps at 60kg |

## Range Notation

### Format
```
INT '..' weight ('/' weight)*
```

### Components
- **First number**: Repetitions (fixed for all sets)
- **Weights**: One or more weights separated by `/`
- **Optional k suffix**: On each weight

### Examples

#### Basic Usage
```
10..23/24           → 10 reps at 23kg, 10 reps at 24kg
8..60/70/80         → 8 reps at 60kg, 70kg, and 80kg
5..100/110/120/130  → 5 reps at each weight (progressive overload)
```

#### Single Weight
```
10..50              → 10 reps at 50kg (equivalent to weight: reps format)
```

#### Decimal Weights
```
5..40.5/42.5/45     → 5 reps at 40.5kg, 42.5kg, and 45kg
8..60.5/70.5/80.5   → 8 reps at each decimal weight
```

#### With K Suffix
```
10..23k/24k         → 10 reps at 23kg and 24kg (explicit k)
8..60/70/80k        → 8 reps at 60kg, 70kg, and 80kg
```

### Comparison with XX Notation
| Range Notation | XX Notation | Result |
|----------------|-------------|--------|
| `10..23/24` | `10xx23,24` | 10 reps each at 23kg and 24kg |
| `8..60/70/80` | `8xx60,70,80` | 8 reps each at 60kg, 70kg, and 80kg |
| `5..100/110/120` | `5xx100,110,120` | 5 reps each at the three weights |

### Use Cases
- **Progressive overload**: `5..60/70/80/90/100k`
- **Warmup sets**: `5..100/110/120/130/140k`
- **Drop sets**: `8..80/60/40/20k` (decreasing weight)
- **Pyramid training**: `12..40/50/60 10..70 12..60/50/40`

## Mixing Notations

All notation styles can be freely combined in a single exercise:

### Examples

#### Dot + X Notation
```
Squat: 5xx60k,70k,80k 1.8.100k
→ Warmup with xx notation, top set with dot notation
```

#### Range + Whole Set
```
Bench: 3x8x75k 10..80/85/90
→ Main sets with x notation, backoff sets with range
```

#### All Notations Together
```
Squat: 60k: 10, 3.8.80k, 5xx100k,110k, 8..120/130
→ Warmup (weight: reps), main (dot), progressive (xx), top sets (range)
```

#### Multiple Dot Sequences
```
Bench press: 1.10.60k 1.8.70k 1.6.80k
→ Pyramid with single sets at different weights
```

#### Multiple Range Sequences
```
Squat: 10..60/70 8..80/90 5..100/110
→ Decreasing reps with increasing weights
```

## Complete Workout Examples

### Example 1: Powerlifting Session
```
Squat: 5..60/80/100/120k 3.5.140k 2
Bench press: 5..40/50/60/70k 3.5.80k 1
Deadlift: 5..100/120/140k 1.5.160k
```

### Example 2: Hypertrophy Session
```
Squat: 3.10.100k
Bench press: 3.8.75k
Row: 3.12.60k
Overhead press: 3.10.40k
```

### Example 3: Mixed Format Workout
```
Squat: 1.10.23 1.10.23.5 10..25/27.5/30
Bench: 60k: 12, 3.8.80k, 10..85/90
Deadlift: 5xx100/110/120 1.3.140k 2
```

## Decimal Weight Support

All notations support decimal weights for precise progression:

```
Bench press: 1.5.62.5k         (dot notation)
Squat: 5..60.5/62.5/65k        (range notation)
Deadlift: 3x5x82.5k            (x notation)
Press: 8xx40.5,42.5,45         (xx notation)
```

## Grammar Rules

### Weight Rule
```antlr4
weight: INT ('.' INT)? 'k'?
```
- Supports: `23`, `23k`, `23.5`, `23.5k`

### Set Rules (New Additions)
```antlr4
set_:
    ...
    | INT '.' INT '.' weight rir?          #whole_set_dots_
    | INT '..' weight ('/' weight)*        #range_reps_multiple_weight
    ;
```

## Parsing Precedence

When parsing ambiguous patterns:
1. `1.5.62.5k` → Parsed as `1 . 5 . 62.5k` (sets.reps.weight)
2. The grammar uses the longest match for multi-dot sequences
3. Double dots `..` are always treated as range operator

## Testing

Comprehensive tests are available in:
- `parser/test_parser.py` - Unit tests for both notations
- `parser/test_grammar_formats_e2e.py` - End-to-end integration tests

Run tests with:
```bash
make test
```

## Benefits

### Dot Notation Benefits
- More compact than `x` notation
- Clearer visual separation
- Familiar to users who prefer period separators
- Less typing for long workout logs

### Range Notation Benefits
- Natural progression syntax with `/`
- Clear indication of weight changes
- Compact for warmup/progression sequences
- Visually distinct from comma-separated formats

## Backward Compatibility

All existing formats remain fully supported:
- `NxNxweight` (whole set x notation)
- `Nxxweight,weight` (fixed reps xx notation)
- `weight: N,N,N` (single rep notation)
- `weight NxN` (group of reps notation)

Old workout logs continue to parse correctly without modification.
