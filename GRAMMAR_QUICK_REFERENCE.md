# Grammar Quick Reference

Quick reference for all supported training log notation formats.

## Basic Format

```
Exercise name: sets
```

## Weight Specification

| Format | Example | Meaning |
|--------|---------|---------|
| Integer with k | `100k` | 100 kilograms |
| Integer without k | `100` | 100 kilograms (default) |
| Decimal with k | `62.5k` | 62.5 kilograms |
| Decimal without k | `62.5` | 62.5 kilograms |

## Set Notations

### 1. Whole Set Notation (X Format)
**Format**: `NxNxweight [rir]`

| Example | Meaning |
|---------|---------|
| `5x6x40k` | 5 sets of 6 reps at 40kg |
| `3x8x75k` | 3 sets of 8 reps at 75kg |
| `1x10x100k` | 1 set of 10 reps at 100kg |
| `3x5x100k 2` | 3 sets of 5 reps at 100kg with 2 RIR |

### 2. Whole Set Notation (Dot Format) ⭐ NEW
**Format**: `N.N.weight [rir]`

| Example | Meaning |
|---------|---------|
| `1.10.23` | 1 set of 10 reps at 23kg |
| `1.10.23k` | 1 set of 10 reps at 23kg |
| `3.8.100k` | 3 sets of 8 reps at 100kg |
| `1.5.62.5k` | 1 set of 5 reps at 62.5kg |
| `3.8.100k 2` | 3 sets of 8 reps at 100kg with 2 RIR |

### 3. Group of Reps Notation
**Format**: `weight [:]NxN`

| Example | Meaning |
|---------|---------|
| `70k: 5x10` | 5 sets of 10 reps at 70kg |
| `70k 5x10` | 5 sets of 10 reps at 70kg (no colon) |
| `100k: 1x5` | 1 set of 5 reps at 100kg |

### 4. Single Rep Notation
**Format**: `weight [:] N,N,N,...`

| Example | Meaning |
|---------|---------|
| `60k: 20,15,8,8` | 4 sets at 60kg with varying reps |
| `75k: 4,4,3,2` | Descending reps (fatigue) |
| `100k: 5` | Single set of 5 reps at 100kg |

### 5. Fixed Reps Multiple Weights (XX Format)
**Format**: `Nxxweight,weight,...`

| Example | Meaning |
|---------|---------|
| `15xx40k,50k` | 15 reps at 40kg, then 15 reps at 50kg |
| `8xx60,70,80` | 8 reps each at 60kg, 70kg, and 80kg |
| `5xx60k,70k,80k,90k` | Progressive overload: 5 reps at each weight |

### 6. Range Notation (Slash Format) ⭐ NEW
**Format**: `N..weight/weight/...`

| Example | Meaning |
|---------|---------|
| `10..23/24` | 10 reps at 23kg, then 10 reps at 24kg |
| `8..60/70/80` | 8 reps each at 60kg, 70kg, and 80kg |
| `5..40.5/42.5/45` | 5 reps each at 40.5kg, 42.5kg, and 45kg |
| `5..100/110/120/130` | Progressive overload with range notation |

## Mixed Formats

You can combine any formats in a single exercise:

```
Squat: 5xx60k,70k,80k 1.8.100k
Bench: 3x8x75k 10..80/85/90
Squat: 60k: 10, 3.8.80k, 5xx100k,110k, 8..120/130
```

## Complete Examples

### Example 1: Simple Workout
```
Squat: 3.8.100k
Bench press: 3.8.75k
Deadlift: 1.5.140k
```

### Example 2: Progressive Overload
```
Squat: 5..60/70/80/90/100k
Bench press: 5..40/50/60/70k
Deadlift: 5..100/120/140k
```

### Example 3: Mixed Format
```
Squat: 1.10.23 1.10.23.5 10..25/27.5/30
Bench: 60k: 12, 3.8.80k, 10..85/90
Deadlift: 5xx100/110/120 1.3.140k 2
```

### Example 4: Real Training Session
```
Bench press: 10k: 4, 4x5
Squat 70k: 5x10
Overhead press: 5x6x40k
Deadlift 60k: 20, 15, 8, 8
Row en maquina 41k: 15, 8
```

## RIR (Reps in Reserve)

Add RIR as a number after the weight in whole set notations:

```
3x5x100k 2          → 3 sets of 5 reps at 100kg with 2 RIR
3.8.100k 2          → 3 sets of 8 reps at 100kg with 2 RIR
1.5.140k 1          → 1 set of 5 reps at 140kg with 1 RIR
```

## Exercise Names

### Predefined Exercises
- `Deadlift`
- `Squat`
- `Bench press`
- `Overhead press`

### Custom Exercises
- Any combination of letters, spaces, hyphens
- Supports accented characters: `Row en máquina`
- Multi-word names: `Cable-fly`, `Leg press`

## Special Characters

| Character | Usage |
|-----------|-------|
| `x` | Separates sets and reps in NxNxweight |
| `xx` | Fixed reps with multiple weights |
| `.` | Decimal point in weights OR separator in N.N.weight |
| `..` | Range operator for N..weight/weight |
| `/` | Weight separator in range notation |
| `,` | Rep separator OR weight separator (xx notation) |
| `:` | Optional separator between weight and reps |
| `k` | Optional kilogram suffix |
| Space | Separates set specifications |

## Notes

1. **Decimal weights** work in all formats: `62.5k`, `75.5`, etc.
2. **K suffix optional**: Both `100k` and `100` mean 100kg
3. **Colon optional**: `70k: 5x10` same as `70k 5x10`
4. **Multiple formats**: Mix and match in same exercise
5. **Whitespace flexible**: Spaces around operators are optional

## Format Comparison

| Result | X Format | Dot Format | XX Format | Range Format |
|--------|----------|------------|-----------|--------------|
| 3 sets × 8 reps × 100kg | `3x8x100k` | `3.8.100k` | N/A | N/A |
| 10 reps each at 23kg, 24kg | N/A | N/A | `10xx23,24` | `10..23/24` |
| 5 reps each at 3 weights | N/A | N/A | `5xx60,70,80` | `5..60/70/80` |
