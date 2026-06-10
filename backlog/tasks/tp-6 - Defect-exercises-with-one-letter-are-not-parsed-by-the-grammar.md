---
id: TP-6
title: 'Defect: exercises with one letter are not parsed by the grammar'
status: Done
assignee: []
created_date: '2026-06-10 13:49'
updated_date: '2026-06-10 13:56'
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

Part of LLR-PARSER-2 (MID: 4b85b056a2f84c8fa5d0484ba4d70ddc)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create new tests for names
<!-- AC:END -->
