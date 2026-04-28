---
id: TP-2
title: Dot notation grammar documentation
status: In Progress
assignee: []
created_date: '2026-04-27 12:53'
labels: []
dependencies:
  - PRD_DOT_NOTATION.md
---

## Overview

Complete documentation of dot notation formats for the training log parser. Dot notation provides a cleaner, more compact alternative to standard notation using periods (`.`) and forward slashes (`/`) as separators.

## Documentation

See **[PRD_DOT_NOTATION.md](../../PRD_DOT_NOTATION.md)** for complete product requirements.

## Dot Notation Formats

### 1. Whole Set Notation: `N.N.weight`

**Current Standard**: `1x10x23k`
**Dot Notation**: `1.10.23k`
**Meaning**: 1 set of 10 reps at 23kg

Replaces `x` separators with `.` for cleaner appearance.

**Examples:**
```
Bench press: 1.10.23      → 1 set of 10 reps at 23kg
Squat: 3.8.100k           → 3 sets of 8 reps at 100kg
Deadlift: 1.5.62.5k       → 1 set of 5 reps at 62.5kg
Overhead press: 5.6.40    → 5 sets of 6 reps at 40kg
```

**With RIR:**
```
Squat: 3.8.100k 2         → 3 sets, 8 reps, 100kg with 2 RIR
```

### 2. Range Notation: `N..weight/weight`

**Current Standard**: `10xx23,24`
**Dot Notation**: `10..23/24`
**Meaning**: 10 reps at 23kg, 10 reps at 24kg

Fixed reps with multiple weights separated by `/`.

**Examples:**
```
Squat: 10..23/24          → 10 reps at 23kg, 10 reps at 24kg
Bench: 8..60/70/80k       → 8 reps at 60kg, 70kg, and 80kg
Press: 5..40.5/42.5/45    → 5 reps at 40.5kg, 42.5kg, and 45kg
Deadlift: 3..100/110/120  → 3 reps at 100kg, 110kg, 120kg
```

### 3. Single Series: `N.weight`

**Pattern**: `<reps>.<weight>`
**Meaning**: Single set with specified reps at weight

**Examples:**
```
Pull-up: 10.20            → 10 reps at 20kg
Push-up: 15.0             → 15 reps bodyweight
Row: 8.50                 → 8 reps at 50kg
Dips: 12.0                → 12 reps bodyweight
```

## Key Advantages Over Standard Notation

| Aspect | Standard | Dot Notation |
|--------|----------|--------------|
| **Whole Set** | `1x10x23k` | `1.10.23k` |
| **Range** | `10xx23,24` | `10..23/24` |
| **Single** | `23` (implicit) | `10.23` (explicit) |
| **Clarity** | Symbols vary | Consistent separators |
| **Compactness** | Good | Better |

## Decimal Weight Support

Both notations support decimal weights naturally:

```
Standard:  1x5x62.5k
Dot:       1.5.62.5k

Standard:  5xx40.5,42.5,45
Dot:       5..40.5/42.5/45
```

## Edge Cases

```
# Zero weight (bodyweight exercises)
10..0/0                   → 10 reps bodyweight both sets

# Large numbers
1.100.200k                → 1 set of 100 reps at 200kg

# Single weight in range notation
10..50                    → 10 reps at 50kg (creates 1 set)
```

## Related Documents

- [PRD_DOT_NOTATION.md](../../PRD_DOT_NOTATION.md) - Complete product requirements
- [GRAMMAR_FORMATS.md](../../GRAMMAR_FORMATS.md) - Standard format documentation
- [SYNTAX.md](../../SYNTAX.md) - Detailed DSL syntax guide
- [GRAMMAR_DOCUMENTATION_INDEX.md](../../GRAMMAR_DOCUMENTATION_INDEX.md) - Documentation index

## Testing

Tests for dot notation are in:
- `parser/test_grammar_formats_e2e.py` - End-to-end format tests
- `parser/test_parser.py` - Parser unit tests

Run tests with:
```bash
make test-grammar-formats
```
