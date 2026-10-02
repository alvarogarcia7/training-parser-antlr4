---
id: TP-8
title: 'PWA: fully local, offline-first, low-data assets'
status: Done
assignee: []
created_date: '2026-10-02 07:49'
labels:
  - pwa
  - feature
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Make the mobile PWA (mobile-app/) run entirely from files served by its own origin, and cache them aggressively because mobile data is expensive.

Findings in the current code:
- pyodide-worker.js silently falls back to the jsDelivr CDN when a local path fails (and ./pyodide/pyodide.js resolves to mobile-app/src/pyodide/, which does not exist), so tests pass even when local loading is broken.
- index.html loads isomorphic-git and lightning-fs from unpkg; the CSP allows both CDNs.
- sw.js is network-first for every app file, so each online launch re-requests ~70 files. It precaches CDN URLs, not the local Pyodide files; PYTHON_SOURCES use ../src paths that probably resolve outside the site root once built; APP_SHELL omits src/config.js.
- The ~60 antlr4 file names are duplicated in sw.js and pyodide-worker.js, and production paths come from sed rewrites in makefiles/pwa.mk.

Decisions: vendor assets at build time (not committed); bundle Python as a rarely-changing vendor archive plus app.zip loaded with pyodide.unpackArchive(); sw.js becomes cache-first; a tiny version.json is fetched on launch.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 No runtime request leaves the app origin (enforced by an e2e test that aborts all cross-origin requests)
- [x] #2 Pyodide, isomorphic-git and lightning-fs are vendored at build time from npm/download scripts and are not committed
- [x] #3 CDN fallback removed from pyodide-worker.js and index.html; a missing local asset shows a clear error; CSP no longer allows CDN origins
- [x] #4 Python code is shipped as a vendor archive (antlr4 runtime + libs) and app.zip (src, generated parser, synonyms, schema) loaded via pyodide.unpackArchive(); PYTHON_FILES lists and sed path rewrites are removed
- [x] #5 sw.js is cache-first for hashed/versioned assets; Pyodide has its own cache keyed by Pyodide version; old caches are deleted on activate
- [x] #6 Launch fetches only a tiny version.json; when it changes, only entries not already cached are downloaded; update is applied via an update-available prompt, not skipWaiting mid-session
- [x] #7 sw.js ignores /requirements/ (docs share the site root) and navigator.storage.persist() is requested
- [x] #8 Offline e2e passes (load once, setOffline, reload, parse works) against the built dist/pwa served by a plain static server
- [x] #9 pytest check: no https:// hosts in index.html/sw.js/worker and every precache entry exists in the build output
- [x] #10 PWA_DEPLOYMENT.md and local-testing docs updated
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Build step: vendor JS libs + Pyodide into build output; generate hashed names and a precache manifest + version.json.
2. Build vendor archive and app.zip; replace PYTHON_FILES and the sed rewrites; worker loads archives via unpackArchive.
3. Remove CDN fallback; fix worker paths; update index.html and CSP.
4. Rewrite sw.js: cache-first, per-version Pyodide cache, version.json check, update prompt, scope exclusions.
5. Add no-network and offline Playwright tests and the static pytest guard; make them run against dist/pwa.
6. Update docs.
<!-- SECTION:PLAN:END -->
