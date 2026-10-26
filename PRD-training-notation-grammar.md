# PRD: Training Notation Grammar — Phase 2 (final)

**Repo:** `alvarogarcia7/training-parser-antlr4`
**Status:** All design questions resolved. Ready for implementation.
**Audience:** Claude (or any engineer) modifying `training.g4`.

---

## Document history

| Rev | Change |
|-----|--------|
| v1–v3 | Early drafts. Superseded. |
| v4  | Backwards-compatible design with open questions and alternatives. |
| v5  | **This revision.** Decisions locked. Breaking change from Phase 1 documented. |

---

## 1. Summary

Extend `training.g4` so that:

1. `.` is accepted as a single separator (equivalent to `x`).
2. `..` is accepted as a double separator (equivalent to `xx`).
3. `/` is accepted as a weight-list separator (equivalent to `,`).
4. `,` is accepted as a decimal point inside a weight, scoped to `/`-delimited contexts.
5. RIR is expressed as `-<INT>` and attaches to every leaf set shape (single rep, group of reps, whole set, fixed-reps multi-weight, v2 multi-weight whole set).

All v1 inputs continue to parse with the same tree shape. Phase 1's space-INT RIR is **replaced** by dash-INT (one-time breaking change; see §6).

## 2. Locked decisions

These were open questions in v4; the user resolved them:

| # | Question | Decision |
|---|----------|----------|
| Q1 | RIR spelling | **Dash-only** (`-N`). Phase 1's space-INT form is removed. |
| Q2 | RIR attachment scope | **Universal across all leaf set shapes.** Applies to single, group, whole, fixed-reps v1, fixed-reps v2, and whole-set multi-weight v2. Does not apply to `weight_` or `multiple_set_`. |
| Q3 | `.` in 2-component expressions (`80.5`) | **Prefer weight interpretation.** v1 preserved. |
| Q4 | Mixing `,` and `/` in one weight list | **Reject.** |
| Q5 | *(removed — was the empty "3." placeholder)* | — |
| Q6 | Standalone `62,5` as a weight | **Accept.** |
| Q7 | Locale signaling | **None.** Grammar is context-sensitive per expression. |
| Q8 | Mixed v1/v2 in one entry | **Allow.** |

## 3. Backwards compatibility

All v1 inputs parse with the same tree shape. Phase 1's space-INT RIR is **deliberately dropped** per Q1.

### 3.1 Inputs preserved (same tree as before)

```
Squat: 5x5x100                 # whole_set_
Deadlift: 1x5x140              # whole_set_
Bench press: 5xx80,90,100      # fixed_reps_multiple_weight_v1
Overhead press: 3x10           # group_of_rep_set
Squat: 80.5: 5x5               # weight_ with nested set
Squat: 80.5                    # weight_ standalone (NOT group_of_rep_set!)
Squat: 5xx40,5,50              # THREE weights: [40, 5, 50]
Bench-press: 5x5x100           # hyphen in name
Row en máquina: 15,8           # two single_rep_sets
Deadlift: 5                    # single_rep_set_
```

### 3.2 Inputs that parse differently than before

| Input | Phase 1 parse | v5 parse |
|-------|---------------|----------|
| `3x5x100k 2` | `whole_set_(3,5,100k, rir=2)` | `multiple_set_(whole_set_(3,5,100k), single_rep_set_(2))` |

This is the only regression. See §6 for migration guidance.

## 4. New syntax (Phase 2)

### 4.1 Dot and double-dot separators

`.` ≡ `x`; `..` ≡ `xx`. Examples:

```
Ms: 1.20.24                    ≡ 1x20x24
Ms: 1..24                      ≡ 1xx24
Ms: 5.5.39                     ≡ 5x5x39
```

### 4.2 Slash-delimited weight lists with comma-decimals

`/` is the v2 alternative to `,` as weight separator. Inside a `/`-delimited list, `,` is the decimal point. Examples:

```
Ms: 20xx40/50/60               ≡ 20xx40,50,60        (integer weights, different separator)
Ms: 1.20.24/27,5/28,1          ~ 1x20x24,27.5,28.1   (different tree shapes; same weights)
Ms: 62,5                       (standalone comma-decimal weight)
```

Mixing `,` and `/` in one list is a parse error: `20xx40,5/50` and `20xx40/5,50` both reject.

### 4.3 Dash RIR, universal

`-<INT>` attaches to any leaf set shape. Examples:

```
Ms: 39-4                       # single rep with RIR 4
Ms: 15.18-3                    # group of reps with RIR 3
Ms: 5.5.39-8                   # whole set with RIR 8
Ms: 3x5x100k-2                 # v1 whole set with v2 RIR
Ms: 5xx80,90,100-3             # fixed-reps multi-weight with RIR 3
Ms: 1.20.24/27,5/28,1-3        # v2 multi-weight whole set with RIR 3
Ms: 5-2, 3-1                   # two single reps, each with its own RIR
Ms: 5, 3-2                     # one single rep, then another with RIR; RIR attaches to the inner '3'
```

## 5. Proposed grammar (drop-in replacement for `training.g4`)

```antlr4
grammar training;

workout: exercise+;

EXERCISE_NAME: 'Deadlift' | 'Squat' | 'Bench press' | 'Overhead press' | NAME;
exercise_name : EXERCISE_NAME;

// NAME must start with a letter so that '-4' cannot be absorbed into a NAME token.
// Continuation characters still include '-' so that 'Bench-press' works.
NAME: [a-zA-Záéíóúñ] ALPHABET* (WS+ ALPHABET+)*;

// Two weight variants. weight_dot is v1-compatible (dot decimals).
// weight_com allows comma-decimals; used inside /-delimited contexts and for standalone
// comma-decimal weights (e.g. '62,5').
weight_dot : INT (DOT INT)? 'k'? ;
weight_com : INT (COMMA INT)? 'k'? ;
weight     : weight_dot | weight_com ;

INT: DIGIT+;

exercise: exercise_name ':'? set_ NEWLINE*;

sep        : X | DOT ;
double_sep : XX | DOTDOT ;
rir_dash   : DASH INT ;

set_:
  // --- Order matters. See §5.1 for the rationale. ---

  // 1. Single rep FIRST (with optional RIR). Preserves v1 behavior for bare INT
  //    (e.g. 'Deadlift: 5' → single_rep_set_, not weight_).
    INT rir_dash?                                           #single_rep_set_

  // 2. Weight SECOND (with optional nested set). Preserves v1 behavior for '80.5'
  //    (→ weight_, not group_of_rep_set). Bare comma-decimals ('62,5') also land here.
  | weight ':'? set_?                                       #weight_

  // 3. Whole set (3 components + optional RIR).
  | INT sep INT sep weight rir_dash?                        #whole_set_

  // 4. Fixed-reps multi-weight, v1 style (comma separator, dot decimals).
  | INT double_sep weight_dot (COMMA weight_dot)* rir_dash? #fixed_reps_multiple_weight_v1

  // 5. Fixed-reps multi-weight, v2 style (slash separator, either decimal).
  | INT double_sep weight (SLASH weight)+ rir_dash?         #fixed_reps_multiple_weight_v2

  // 6. Whole-set with extra weights, v2 style (new in Phase 2).
  //    'set_ SLASH weight ...' left-recurses into another set_.
  | set_ SLASH weight (SLASH weight)* rir_dash?             #whole_set_multi_weight_v2

  // 7. Group of reps (2 components + optional RIR).
  | INT sep INT rir_dash?                                   #group_of_rep_set

  // 8. Compound (multiple sets). Last, as a catch-all.
  | set_ ','? set_                                          #multiple_set_
  ;

// Lexer. Token ordering is load-bearing.
DOTDOT : '..' ;  // must precede DOT
DOT    : '.'  ;
XX     : 'xx' ;  // must precede X
X      : 'x'  ;
COMMA  : ','  ;
SLASH  : '/'  ;
DASH   : '-'  ;  // must precede NAME for '-4' to tokenize as DASH INT

fragment DIGIT: '0'..'9' ;

// ALPHABET unchanged from v1; '-' still allowed as a continuation char inside names.
// The letter-first constraint in NAME is what prevents '-' from being absorbed
// at the start of a new token.
ALPHABET: [a-zA-Z] | [áéíóúñ] | [-] ;

NEWLINE: '\r'? '\n' ;
WS:     [ \t]+ -> skip ;
```

### 5.1 Rule ordering rationale

The three-tier head of `set_` is the most delicate part of the grammar. Each placement is load-bearing:

1. **`single_rep_set_` first** — for inputs like `Deadlift: 5`. Without this placement, ANTLR's ALL(\*) would pick `weight_` (which also matches bare INT as a one-word weight), changing the parse tree shape from v1.

2. **`weight_` second, before `group_of_rep_set`** — for inputs like `Squat: 80.5`. Both `weight_(80.5)` and `group_of_rep_set(80, 5)` are valid parses of `80.5`; rule order picks the first, preserving v1.

3. **`group_of_rep_set` after `weight_` but after `whole_set_`** — `whole_set_` is more specific (3 components) so it matches first when applicable. `group_of_rep_set` only fires for 2-component expressions where `weight_` didn't consume the whole input.

Anything else in the ordering is driven by specificity (more specific → earlier).

### 5.2 Spot-check: every test input traced

| Input | Winning alt | Tree (sketch) |
|---|---|---|
| `5` | `single_rep_set_` | `single_rep_set_(5)` |
| `5-2` | `single_rep_set_` | `single_rep_set_(5, rir=2)` |
| `80.5` | `weight_` | `weight_(80.5)` |
| `80.5: 5x5` | `weight_` | `weight_(80.5, nested=group_of_rep_set(5,5))` |
| `80x5` | `group_of_rep_set` | `group_of_rep_set(80, 5)` |
| `15.18-3` | `group_of_rep_set` | `group_of_rep_set(15, 18, rir=3)` |
| `5x5x100` | `whole_set_` | `whole_set_(5, 5, 100)` |
| `5x5x100-2` | `whole_set_` | `whole_set_(5, 5, 100, rir=2)` |
| `5.5.39-8` | `whole_set_` | `whole_set_(5, 5, 39, rir=8)` |
| `1..24` | `whole_set_` | `whole_set_(1, 1, 24)` (with DOUBLE_SEP collapsing) — see §5.3 |
| `5xx80,90,100` | `fixed_reps_multiple_weight_v1` | `[80, 90, 100]` |
| `20xx40/50/60` | `fixed_reps_multiple_weight_v2` | `[40, 50, 60]` |
| `1.20.24/27,5/28,1` | `whole_set_multi_weight_v2` | inner=`whole_set_(1,20,24)`, extra=`[27.5, 28.1]` |
| `62,5` | `weight_` → `weight_com` | `weight_(62.5)` |
| `Bench-press: 5x5` | `group_of_rep_set` | name=`Bench-press`, set=`group_of_rep_set(5, 5)` |
| `5, 3-2` | `multiple_set_` | `multiple_set_(single_rep_set_(5), single_rep_set_(3, rir=2))` |
| `5-2, 3-1` | `multiple_set_` | `multiple_set_(single_rep_set_(5, rir=2), single_rep_set_(3, rir=1))` |
| `3x5x100 2` | `multiple_set_` | `multiple_set_(whole_set_(3,5,100), single_rep_set_(2))` — **breaking change from Phase 1** |

### 5.3 Note on `1..24`

`INT sep INT sep weight` means "INT followed by sep followed by INT followed by sep followed by weight." `1..24` lexes as `INT(1) DOTDOT INT(24)`. But `DOTDOT` is `double_sep`, not two `sep`s. So `1..24` actually parses via `fixed_reps_multiple_weight_v1` with `INT double_sep weight_dot`, giving `fixed_reps_multiple_weight_v1(1, [24])`.

Semantically: "1 rep at 24 kg, once." That matches v1's `1xx24` behavior. Good.

Inputs like `5..39` work the same way. If you want `1.1.24` (three components via sep), write it as `1.1.24`, not `1..24`.

## 6. Migration from Phase 1

One behavior change: **space-INT RIR is no longer recognized.**

```
Before (Phase 1):   3x5x100k 2     → whole_set_ with rir=2
After  (Phase 2):   3x5x100k 2     → TWO sets: whole_set_(3,5,100k) + single_rep_set_(2)
```

### 6.1 Automated rewrite

A one-off script can rewrite space-RIR to dash-RIR across any existing training logs:

```bash
# Matches 'NxNxW<space>N' at end-of-expression and rewrites to 'NxNxW-N'.
# Adjust '\s+' to taste; Phase 1 allowed any whitespace between weight and RIR.
sed -E 's/([0-9]+[xX][0-9]+[xX][0-9]+(\.[0-9]+)?k?)\s+([0-9]+)(\s*[,$\n])/\1-\3\4/g' \
    old-log.txt > new-log.txt
```

This only covers the `INT x INT x weight<space>rir` case that Phase 1 supported. No other shape had space-RIR.

### 6.2 Pre-flight check before merging Phase 2

Before the PR lands, grep the existing test corpus and sample files for Phase 1 space-RIR:

```bash
# Find any line that ends (or comma-ends) with a weight then space then small int
grep -E '[0-9]+[xX][0-9]+[xX][0-9]+(\.[0-9]+)?k?\s+[0-9]+(\s*[,$])' \
    tests/ data/ training-sample*.txt examples/
```

If this returns hits, decide per-case: rewrite them, or leave them and accept the semantic shift.

## 7. Test cases

### 7.1 Regression — must parse with identical tree shape

```
Squat: 5x5x100
Deadlift: 1x5x140
Bench press: 5xx80,90,100
Overhead press: 3x10
Squat: 80.5: 5x5
Squat: 80.5
Squat: 80.5k
Squat: 5xx40,5,50
Bench-press: 5x5x100
Row en máquina: 15,8
Deadlift: 5
```

### 7.2 Phase 1 migration — new parse, documented

```
Squat: 3x5x100k 2         # now parses as two sets; rewrite to 3x5x100k-2 for RIR
Squat: 3x5x100k-2         # Phase 2 equivalent of the above
```

### 7.3 Phase 2 positives

```
Ms: 1.20.24                 # dot separator
Ms: 1..24                   # double-dot, same as 1xx24
Ms: 5.5.39                  # dot, 3 components
Ms: 1.20.24/27,5/28,1       # whole set + slash multi-weights with comma-decimals
Ms: 20xx40/50/60            # slash-delimited integer weights
Ms: 62,5                    # bare comma-decimal weight
Ms: 39-4                    # single rep + RIR
Ms: 15.18-3                 # group + RIR
Ms: 5.5.39-8                # whole set + RIR
Ms: 5xx80,90,100-3          # fixed reps multi-weight + RIR
Ms: 1.20.24/27,5/28,1-3     # v2 multi-weight whole set + RIR
Ms: 5-2, 3-1                # two RIR-ed single reps
Ms: 5, 3-2                  # RIR attaches to inner '3', not compound
```

### 7.4 Must not parse

| Input | Reason |
|---|---|
| `Ms: 20xx40,5/50` | mixing `,` and `/` in one weight list |
| `Ms: 20xx40/5,50` | same |
| `Ms: /40/50` | list starts with separator |
| `Ms: 40//50` | empty slot in list |
| `Ms: 1..` | trailing separator |
| `Ms: 1-` | DASH not followed by INT |
| `Ms: -5` | DASH without preceding set |
| `-Ms: 5x5` | exercise name starts with `-` |

## 8. Acceptance criteria

- [ ] Grammar compiles under ANTLR4 with no warnings.
- [ ] §7.1 regression inputs parse with identical tree shapes (snapshot tests green against pre-Phase-2 output).
- [ ] §7.2 migration fixtures behave as documented; a CI warning is emitted if the old space-RIR pattern is detected.
- [ ] §7.3 Phase 2 positives all parse.
- [ ] §7.4 negatives all fail with line/col errors.
- [ ] `SYNTAX.md` and `GRAMMAR_FORMATS.md` updated and consistent with each other and with `training.g4`.
- [ ] README migration note added (short: "space-RIR → dash-RIR, sed recipe in §X").
- [ ] `training-sample.txt` extended with at least one line per Phase 2 shape.

## 9. Rollout

1. Branch: `feat/grammar-phase-2`.
2. Run §6.2 grep on the repo and any private training logs; list hits in the PR description.
3. Add §7 fixtures (regression must pass; Phase 2 positives and negatives must fail initially).
4. Modify `training.g4` per §5; regenerate parser.
5. Run suite. §7.1 must stay green (no tree shape drift); §7.3 must go green; §7.4 must report parse errors; §7.2 behaves per documentation.
6. Reconcile `SYNTAX.md` and `GRAMMAR_FORMATS.md`.
7. Open PR. Include:
   - Diff summary.
   - Before/after parse trees for §5.2 spot-checks.
   - Rewrite SQL/sed for Phase 1 users.

## 10. Risk register

| Risk | Likelihood | Mitigation |
|---|---|---|
| ANTLR's ALL(\*) picks unexpected alt due to subtle rule-ordering bug | Medium | §7.1 snapshot tests; §5.2 spot-check table; manual review of every alt. |
| `DASH` tokenization surprise in existing hyphenated names | Low | Letter-first NAME + longest-match on ALPHABET+ keeps `Bench-press` intact. `-4` tokenizes as DASH INT because NAME requires letter start. Covered by §7.1. |
| Left-recursion interaction: `multiple_set_` and `whole_set_multi_weight_v2` both left-recurse on `set_` | Medium | ANTLR4 supports direct left recursion; stress-test with inputs like `1.20.24,27.5/30-2`. |
| Existing Phase 1 users broken by space-RIR removal | Low-medium | §6 migration guidance; CI warning; pre-flight grep in rollout. |
| Greedy `rir_dash?` swallows the `-N` from the next expression | Low | `rir_dash` requires DASH followed immediately by INT; adjacent tokens with whitespace still split cleanly because `WS` is skipped uniformly. |
