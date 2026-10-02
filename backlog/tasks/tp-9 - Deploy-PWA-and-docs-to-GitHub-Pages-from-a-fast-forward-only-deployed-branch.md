---
id: TP-9
title: Deploy PWA and docs to GitHub Pages from a fast-forward-only deployed branch
status: To Do
assignee: []
created_date: '2026-10-02 07:49'
labels:
  - ci
  - pwa
  - feature
dependencies:
  - TP-8
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Deploy only when the maintainer fast-forwards the `deployed` branch to a commit already on main. Run the PWA tests only in that pipeline, and ship the PWA (site root) and the StrictDoc docs (/requirements/) together.

Current state: deploy-pwa.yml runs on every push to master touching the PWA paths and runs no tests; pwa-e2e-tests.yml runs on every PR with continue-on-error; publish-docs.yml publishes on every push to main; pwa-publish wipes gh-pages except requirements/ and its deploy does not download Pyodide, so the live site probably uses the CDN.

Decisions: branch name `deployed` (input, ff-only); output stays on gh-pages (whole-site replace, no keep_files); PWA at root, docs under /requirements/; no environment approval gate; no extra build record; a moving `live` tag marks the last good deploy; reference pattern is the peaceiris/actions-gh-pages step in alvarogarcia7/blog_source (but triggered by branch, not on every push, and with tests).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Workflow triggers only on push to the deployed branch; no path-filtered push, PR or dispatch triggers remain
- [ ] #2 Ruleset on deployed: block force pushes and deletion, restrict who can push
- [ ] #3 verify job fails unless the push is a fast-forward (github.event.forced false, before is an ancestor of sha) and sha is reachable from origin/main
- [ ] #4 Jobs build -> test -> deploy pass a single dist artifact: the tested files are the deployed files
- [ ] #5 Build produces the PWA at the site root and StrictDoc output under /requirements/, plus .nojekyll; deploy replaces the whole gh-pages site (no keep_files)
- [ ] #6 test job runs the e2e, no-network and offline tests from TP-8 with no continue-on-error; a failing test blocks deploy
- [ ] #7 build downloads Pyodide and compiles the grammar inside the job; nothing generated is committed to main
- [ ] #8 On success a live tag is moved to the deployed commit
- [ ] #9 pwa-e2e-tests.yml removed, publish-docs.yml no longer publishes, pwa-publish and docs-publish make targets replaced by a single site-build target; ci.yml still validates the docs on main
- [ ] #10 Dry run on a staging publish branch proves: ff push deploys, non-main commit fails verify, failing test skips deploy, docs and PWA both present
- [ ] #11 PWA_DEPLOYMENT.md and GITHUB_PAGES_SETUP.md updated, including the promote command: git push origin <sha>:deployed
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add make site-build (PWA root + docs) and make pwa-test-built.
2. Write deploy workflow: verify, build, test, deploy (peaceiris/actions-gh-pages@v4, GITHUB_TOKEN with contents: write), live tag step; shared concurrency group.
3. Remove the old workflows and publish targets.
4. Create the ruleset on deployed; document it.
5. Dry-run against a staging branch, then switch to gh-pages.
6. Update docs.
<!-- SECTION:PLAN:END -->
