---
id: TP-17
title: Parse statistics for sessions
status: Backlog
assignee: []
created_date: '2026-10-24 13:53'
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
