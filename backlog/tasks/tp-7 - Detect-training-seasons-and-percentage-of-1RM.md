---
id: TP-7
title: Detect training seasons and percentage of 1RM
status: Done
assignee: []
created_date: '2026-09-29 10:40'
updated_date: '2026-09-29 12:30'
labels: []
dependencies: []
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Python tool to detect training "seasons". A configuration file establishes the
minimum time without a training session; after that break has passed, the next
session starts a new season.

In each season, compute the percentage of 1RM for each exercise, using the
Brzycki formula (`1RM = weight * 36 / (37 - reps)`) to estimate the 1RM.
Example: with a 1RM of 100 kg, training with 50 kg is 50% 1RM.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Minimum break without training is configured in data/config/seasons.yaml
- [x] #2 A break of at least that many days starts a new season
- [x] #3 Per season, each exercise gets a Brzycki 1RM estimate
- [x] #4 Per season, each set is reported as a percentage of the season 1RM
- [x] #5 Unit tests cover season splitting, 1RM and %1RM
- [x] #6 Input is a directory with one or more set-centric JSON files
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
- `src/seasons.py`: season detection and per-season intensity
- `src/one_rep_max.py`: Brzycki 1RM and %1RM
- `bin/detect_seasons.py`: CLI (text/JSON output), `make seasons DIR=...`
- Input: directory searched recursively for `*.json`; each file is one
  set-centric workout (enveloped or bare) or an array of them. Other
  formats (e.g. bench-centric) are rejected with an error.
- `data/config/seasons.yaml`: `min_break_days`, `min_sessions`, `max_reps_for_1rm`
- Brzycki overestimates at high reps, so only sets with at most
  `max_reps_for_1rm` reps drive the estimate (fallback: sets up to 36 reps).
- Tests: `tests/test_seasons.py` (`make test-seasons`)
<!-- SECTION:NOTES:END -->
