# PWA Deployment Strategy

## Overview

The Progressive Web App (PWA) and documentation are deployed to GitHub Pages using a controlled deployment model:
- **main/master branch**: Contains source code only (no build artifacts)
- **deployed branch**: Fast-forward-only branch used to trigger deployments
- **gh-pages branch**: Contains built site (PWA + docs), automatically generated from deployed branch
- **GitHub Actions**: Automates build, test, and deployment process with verification checks

## Architecture

```
main branch (source code)
    ↓
Maintainer pushes to deployed branch (fast-forward only)
    ↓
GitHub Actions workflow (.github/workflows/deploy.yml)
    ↓
verify job (checks fast-forward, validates commit origin)
    ↓
build job (builds PWA + docs)
    ↓
test job (runs offline, no-network, e2e tests)
    ↓
deploy job (pushes to gh-pages with peaceiris action)
    ↓
live tag (marks successful deployment)
    ↓
gh-pages branch (built artifacts)
    ↓
GitHub Pages server
    ↓
https://owner.github.io/repo-name/
```

## Key Features

### 1. Clean Repository
- Main branch contains only source code
- Build artifacts are NEVER committed to main branch
- All derived files are generated on-demand during deployment
- Deployments are explicitly promoted via the `deployed` branch

### 2. Controlled Deployment
- Triggered only by pushing to the `deployed` branch
- Push must be a fast-forward (no force-push)
- Commit must be reachable from main branch
- Ensures deployments only come from reviewed, merged code
- Fails fast if conditions are not met (no partial deployments)

### 3. Build and Test Process
The deployment pipeline includes:

1. **verify job**: Validates deployment eligibility
   - Ensures push is fast-forward (not forced)
   - Verifies commit is ancestor of current SHA
   - Confirms commit is reachable from origin/main
   - Fails if any check doesn't pass

2. **build job**: Builds PWA and documentation
   - Runs `make site-build` to package PWA at root and docs at /requirements/
   - Downloads Pyodide for offline support
   - Creates .nojekyll file for proper GitHub Pages handling
   - Uploads artifact for testing and deployment

3. **test job**: Tests built artifacts
   - Downloads built artifacts
   - Runs `npm run test:offline` - tests offline functionality
   - Runs `npm run test:no-network` - tests without network
   - Runs `npm run test:e2e` - end-to-end browser tests
   - **Fails deployment if tests don't pass** (no continue-on-error)
   - Uses exact same files that will be deployed

4. **deploy job**: Deploys tested artifacts
   - Uses peaceiris/actions-gh-pages action
   - Deploys to gh-pages branch with `force_orphan: true`
   - Replaces entire gh-pages content (clean slate)
   - Creates/updates `live` tag pointing to deployed commit

## Deploying via the deployed Branch

### Step-by-step deployment process

1. **Test your changes locally** (on main/master branch)
   ```bash
   make site-build
   make pwa-test-built  # Runs offline, no-network, and e2e tests
   ```

2. **Find the commit SHA to deploy**
   ```bash
   git log --oneline -5
   # Pick a commit SHA that passed local tests
   ```

3. **Push the commit to deployed branch**
   ```bash
   git push origin <commit-sha>:deployed
   ```
   This creates or updates the `deployed` branch to point at your commit.

4. **Watch the workflow**
   - Go to GitHub Actions tab
   - Find the "Deploy from deployed branch" workflow run
   - Watch verify → build → test → deploy jobs execute in order
   - If any job fails, the deployment stops

5. **Check the live tag**
   After successful deployment:
   ```bash
   git tag -l live
   git rev-list -n 1 live
   ```
   The `live` tag should point to your deployed commit.

### The live tag

- Points to the last successful deployment
- Updated automatically after each successful deploy
- Force-updated (moved), not recreated
- Useful for quick rollback: `git push origin <previous-sha>:deployed`

### Rollback

If deployment has issues:
1. Find the previous good commit SHA
2. Push it to deployed: `git push origin <previous-sha>:deployed`
3. New workflow will run, test, and deploy the previous version

## Local Testing

### Build PWA + docs locally
```bash
make site-build
```
Output: `dist/site/` directory contains complete site (PWA at root, docs at /requirements/)

### Test built artifacts
```bash
make pwa-test-built
```
This runs the same tests that the deployment pipeline runs.

### Serve site locally
```bash
python3 -m http.server -d dist/site 8080
```
Open http://localhost:8080/ to browse the site.

## GitHub Pages Configuration

The repository should be configured with:
- **Pages source**: Deploy from branch
- **Branch**: `gh-pages`
- **Folder**: `/ (root)`

This is typically done in GitHub Settings → Pages → Build and deployment

## Branch Protection Rules

The `deployed` branch should have these protections configured via GitHub web UI:
- Block force pushes (ensures fast-forward only)
- Block deletion
- Require status checks to pass: verify, build, test
- Optionally: restrict push access to admins/maintainers only

## Troubleshooting

### Deployment fails at verify stage
- **Force push detected**: Don't use `git push --force` to deployed branch
- **Not a fast-forward**: Deployed branch is ahead of current commit; push a newer commit instead
- **Not reachable from main**: Commit is not on main branch; merge to main first, then push to deployed

### Deployment fails at test stage
1. Pull latest code to main/master
2. Run tests locally: `make pwa-test-built`
3. Fix any failing tests
4. Push commit to main/master
5. After merge confirmed, retry deployment: `git push origin <sha>:deployed`

### Build fails
1. Run locally: `make site-build`
2. Check that all source files exist:
   - `mobile-app/` directory
   - `src/` (including `src/parser/`), `data/` modules
   - `requirements/` directory with .sdoc files
   - `dist/training{Lexer,Parser}.py` files (run `make compile-grammar` if missing)
3. Check Pyodide: `ls -la mobile-app/pyodide/` (if offline mode expected)

### Website doesn't reflect latest deployment
1. Check `live` tag points to latest commit: `git rev-list -n 1 live`
2. Check GitHub Pages settings point to `gh-pages` branch
3. Clear browser cache (PWA caches aggressively)
4. Check gh-pages branch history: `git log --oneline gh-pages -5`

### Rollback to previous version
1. Find previous good commit: `git log --oneline <sha> -n 10`
2. Deploy it: `git push origin <previous-sha>:deployed`
3. Verify deployment succeeds and site reverts

## Files Involved

- `.github/workflows/deploy.yml` - Main deployment workflow
- `.github/workflows/ci.yml` - Validation only (no publishing)
- `makefiles/pwa.mk` - PWA build targets
- `makefiles/strictdocs.mk` - Documentation targets
- `mobile-app/` - PWA source code
- `requirements/` - Requirements documentation (StrictDoc)
- `dist/site/` - Built site (generated, not committed)

### Deprecated files
- `.github/workflows/pwa-e2e-tests.yml` - Replaced by deploy.yml
- `.github/workflows/deploy-pwa.yml` - Replaced by deploy.yml
- `.github/workflows/publish-docs.yml` - Replaced by deploy.yml
- `make pwa-publish` - Replaced by deploy workflow
- `make docs-publish` - Replaced by deploy workflow
