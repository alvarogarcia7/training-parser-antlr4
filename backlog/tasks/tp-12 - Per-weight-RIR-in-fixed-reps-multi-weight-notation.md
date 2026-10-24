---
id: TP-12
title: Per-weight RIR in fixed-reps multi-weight notation
status: Done
assignee: []
created_date: '2026-10-24 09:00'
updated_date: '2026-10-24 09:00'
labels: []
dependencies: []
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
In fixed-reps multi-weight (v1, comma) notation, a bare-weight list must carry a
per-weight RIR and remain equivalent to the explicit reps.weight form. These two
lines must describe the same workout:

```
D: 10..50-4,65-4,65-4,65-3
D: 10..50-4,10.65-4,10.65-4,10.65-3
```

Both are 10 reps @ 50 kg then 10 reps @ 65 kg x3 = 10*(50+65*3) = 2450 kg, with
per-weight RIR 4, 4, 4, 3.

Previously the shorthand form lost the fixed rep count after the first weight:
`65-4` was read as "65 reps @ 0 kg", giving a volume of 500 kg.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 `10..50-4,65-4,65-4,65-3` and `10..50-4,10.65-4,10.65-4,10.65-3` produce identical sets
- [x] #2 Both total 2450 kg with per-weight RIR 4,4,4,3
- [x] #3 A lone trailing RIR still applies to every weight (`5xx80,90,100-3` -> all RIR 3)
- [x] #4 Dotted decimal weights still parse as weights (`8xx60.5` -> 8 reps @ 60.5 kg)
- [x] #5 The existing ANTLR grammar is extended (no new parser)
- [x] #6 Tests cover the equivalence and the regressions above
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
- `training.g4`: new `fixed_rep_weight : weight_dot rir_dash?` sub-rule; the v1
  fixed-reps alternative becomes `INT double_sep fixed_rep_weight (COMMA fixed_rep_weight)*`
  so the shared rep count from the `N..` prefix applies to every weight.
- `src/parser/parser.py` (`visitFixed_reps_multiple_weight_v1`): builds one
  series per weight with its own RIR. RIR resolution:
  - a lone trailing RIR is applied to all weights (preserves `5xx80,90,100-3`)
  - several explicit RIRs stay per-weight
  - a dotted element that restates the fixed rep count is a reps.weight
    restatement (`10..50,10.65` where 10==10 -> 10 reps @ 65); other dotted
    elements remain decimal weights (`8xx60.5` -> 8 reps @ 60.5 kg)
- Tests: `tests/test_fixed_reps_rir_equivalence.py`.
- Shipped in PR #23 (merged to master).
<!-- SECTION:NOTES:END -->
