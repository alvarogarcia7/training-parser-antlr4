---
id: TP-17
title: Parse statistics for sessions
status: Backlog
assignee: []
created_date: '2026-10-24 13:53'
updated_date: '2026-10-25 08:42'
labels: []
dependencies: []
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Parse statistics from within the file:

```
# stats: (apple watch) 500 total kcal, 402 active kcal, 50 min, 111 average bpm, 71-162 range bpm
# stats: (polar) 355 kcal, 50 min, 108-140 bpm, 54% from fat
```

1. Allow multiple statistics for a single training session
2. Each statistic can have a specific format. In this example, apple watch and polar.
3. Polar: zm means zone minutes, 108-140 specifies average and max beats per minute
4. Apple watch: 71-162 means average 71 and max 162
5. BPM should have an absolute max of 220 bpm.
4. Allow incomplete data in each statistic, to parse as much as possible from the human-typed input.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The statistics must be parsed from the original file (used from src.bulk_export.run) and included into the database output, both for set-centric and bench-centric.
- [ ] #2 In bin/parse_bulk.sh, show how many files have detected statistics, which not, which ones have been successfully parsed statistics, which not.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Parse as much information as possible from these examples:

```
# Stats: 43 min, 37 zone min, 120-153 bpm, 382 kcal

# stats: (apple watch) 416 total kcal, 308 active kcal, 55 min, 95 average bpm, 66-145 range bpm
# stats: (polar rosa) 56 min, 98-138 bpm, cardio load 24, 310 kcal, 60% fat
# stats: (apple watch) 353 total kcal, 265 active kcal, 45 min, 101 average bpm, 75-134 range bpm
# stats: (polar rosa) 45 min, 96-125 bpm, cardio load 17, 228 kcal, 64% fat

# Stats: 66 min, 66 zone min, 122-146 bpm, 607 kcal
# Stats: 81m, 68 min zone, 120-164 bpm, 716 kcal
# Stats 35 min, 58 zone min, 138-164 bpm, 421 kcal

# Stats: 75 min, 60 zone minutes, 118-155 bpm, 617 kcal

# Stats: 32 min actividad, 104-153 bpm, 60 carga basal, tiempo: 1h 50m, 714 kcal, 56% actividad

# Stats: 59m, 22 zm, 104-146 bpm, 360kcal
# Stats: 96m, 66zm, 116-163bpm, 813 kcal
# Stats: 33m, 21 zm, 116-144 bpm, 254 kcal

#Stats: 35 min, 28 zm, 121-154 bpm, 318 kcal
# Stats: 74m, 88zm, 126-161 bpm, 746 bpm
# Stats: 40m, 34zm, 114-139 bpm, 350 bpm

# Stats: 44 zone minutes
# Stats: 61 zone minutes

# Stats up to here: 44 min, 10 zone min, 100-130 bpm, 212 kcal

# Stats: 51 min, 32 zone minutes, 114-142 bpm, 391 kcal

# Stats: 22:49 de la noche. Pocas ganas. apenas 10 minutos porque hace mucho calor

# Stats: 117m, 124 zone minutes, 124-162 bpm, 1105 kcal
```
<!-- SECTION:NOTES:END -->
