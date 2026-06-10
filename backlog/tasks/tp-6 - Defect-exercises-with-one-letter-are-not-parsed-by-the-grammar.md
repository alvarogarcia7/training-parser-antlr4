---
id: TP-6
title: 'Defect: exercises with one letter are not parsed by the grammar'
status: Done
assignee: []
created_date: '2026-06-10 13:49'
labels: []
dependencies: []
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
```
a: 1.10.20
```

is not parsed, while

```
ab: 1.10.20
```

is correctly parsed.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create new tests for names
<!-- AC:END -->
