---
id: TP-10
title: 'Git sync reliability: GitHub API backend and shallow git-protocol backend'
status: To Do
assignee: []
created_date: '2026-10-02 07:50'
labels:
  - pwa
  - sync
  - feature
dependencies:
  - TP-9
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Fix the PWA git sync. The git smart-HTTP endpoints of github.com send no CORS headers (probe: GET 200 without Access-Control-Allow-Origin, OPTIONS 405), so a PWA on github.io cannot reach them without a proxy; the REST API does support CORS. Decision: two backends behind one interface; no hosted proxy.

Likely root causes in mobile-app/src/git-sync.js (verify with tests before fixing):
1. The local repo never clones the remote: git.init plus an empty Initial commit has no shared history, so pull fails (unrelated histories) and push is rejected.
2. Force-push fallbacks (and main/master swapping) can overwrite remote data.
3. verifyPushSuccess indexes the listServerRefs array as an object, so a successful push likely reports failure.
4. detectRemoteDefaultBranch reads HEAD.target, only populated with symrefs: true.
5. With the public proxy the PAT is embedded in the URL and persisted in .git/config in IndexedDB.
6. Errors are classified by message substrings; isomorphic-git errors carry a .code.
7. One file per date means same-day edits on two devices conflict.
8. No single-writer lock between tabs; online event pushes unconditionally; ~half the file is debug logging.
9. tests/git-integration.spec.js tests src/git-lib.js (a separate copy), and the CI git server is started with timeout 5, so browser sync is effectively untested.

Also correct backlog/decisions/decision-2 which claims GitHub Pages -> GitHub works with no CORS issue.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A sync interface (pull, push, list, load) with two backends; backend chosen by settings, defaulting to the GitHub API on non-localhost and git-protocol on localhost
- [ ] #2 GitHub REST backend (contents API) works from the github.io origin with a fine-grained PAT scoped to one repo; no proxy
- [ ] #3 Git-protocol backend: shallow single-branch clone (depth 1), fetch or clone before the first commit, fast-forward pull, push with no force, symrefs-based default branch, typed error codes, token sent only via Authorization (never in the URL or .git/config)
- [ ] #4 Local development uses the existing cors-anywhere (PORT=8081 node ./node_modules/cors-anywhere/server.js), documented and wrapped in a make target
- [ ] #5 Workout files get unique names (date plus short id) so merges do not conflict; existing YYYY-MM-DD.json files still load
- [ ] #6 navigator.locks guards writes; reconnect sync is queued and idempotent; logging goes through one leveled logger
- [ ] #7 Node tests exercise the same module the browser uses against a bare-repo test server for: empty remote, main, master, diverged history, rejected push, bad token, offline
- [ ] #8 e2e with a test git server that stays up for the whole run: push from page A, pull on page B, assert contents; e2e test 4 no longer accepts a failed push
- [ ] #9 decision-2 and the sync guides (PWA_SYNC_GUIDE, GIT_SYNC_TROUBLESHOOTING) corrected
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Reproduce the suspected bugs with failing tests (verify, symrefs, unrelated histories).
2. Extract the sync interface; move the shared logic to an ESM module used by both Node tests and the browser.
3. Implement the git-protocol backend fixes.
4. Implement the GitHub REST backend.
5. Settings UI: backend selection and token guidance.
6. Tests, make targets, docs.
<!-- SECTION:PLAN:END -->
