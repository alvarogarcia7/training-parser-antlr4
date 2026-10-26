---
id: TP-13
title: Sets are not shared between exercises (continuous set numbering)
status: Done
assignee: []
created_date: '2026-10-24 10:00'
updated_date: '2026-10-24 10:00'
labels: []
dependencies: []
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Unless specified, sets are not shared between exercises. Set numbers run
continuously across the whole workout, so each exercise owns a distinct
contiguous range:

```
Smith Machine Squat -> series 1, 2, 3
Squat               -> series 4, 5, 6
```

Previously set-centric serialization restarted numbering at 1 for every
exercise, which made different exercises appear to share the same series.
Reusing the same set numbers across exercises is reserved for superseries (no
rest between exercises) and must be specified explicitly, rather than falling
out of per-exercise numbering that happens to restart at 1.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Set numbers are continuous across exercises within one workout
- [x] #2 "Smith Machine Squat" gets 1,2,3 and "Squat" gets 4,5,6
- [x] #3 Set numbers are globally unique within a workout
- [x] #4 A single exercise still starts at 1
- [x] #5 Tests cover the example and global uniqueness
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
- `src/parser/serializer.py` (`serialize_to_set_centric`): a single running
  set-number counter across all exercises instead of `enumerate(..., start=1)`
  per exercise.
- Existing serializer tests updated from per-exercise reset to continuous
  numbering.
- Tests: `tests/test_continuous_set_numbering.py` (incl. the Smith Machine
  Squat / Squat example).
- Shipped in PR #24 (merged to master).
<!-- SECTION:NOTES:END -->
