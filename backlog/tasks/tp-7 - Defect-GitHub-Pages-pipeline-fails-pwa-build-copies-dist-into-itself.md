---
id: TP-7
title: 'Defect: GitHub Pages pipeline fails — pwa-build copies dist into itself'
status: Done
assignee: []
created_date: '2026-09-29 00:00'
updated_date: '2026-09-29 00:00'
labels: [defect, ci]
dependencies: []
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The `deploy-pwa` GitHub Actions workflow fails at the `pwa-build` step:

```
cp: cannot copy a directory, 'dist', into itself, 'dist/pwa/dist'
make: *** [makefiles/pwa.mk:11: pwa-build] Error 1
```

Root cause: `makefiles/pwa.mk` line 11 ran `cp -r dist dist/pwa/`, but `dist/pwa/` is a subdirectory of `dist/`, creating a circular copy.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 `make pwa-build` completes without error
- [x] #2 dist contents (excluding pwa subdir) are copied into `dist/pwa/dist/`
- [x] #3 GitHub Pages pipeline passes
<!-- AC:END -->
