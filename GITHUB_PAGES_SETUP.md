# GitHub Pages Deployment Setup

## Overview
The project now uses a controlled deployment workflow triggered by pushing to the `deployed` branch. Both the PWA and StrictDoc-generated requirements documentation are deployed together as a single unified site.

## Workflow Files

### 1. `.github/workflows/deploy.yml` (MAIN DEPLOYMENT)
**Purpose**: Builds PWA and documentation, runs tests, and deploys to GitHub Pages

**Triggers**:
- Push to `deployed` branch only
- Must be a fast-forward push
- Commit must be reachable from main branch

**Process**:
1. **verify job**: Validates deployment eligibility
   - Checks that push is not forced
   - Verifies it's a fast-forward
   - Confirms commit is from main branch

2. **build job**: Builds site
   - Builds PWA with `make pwa-build`
   - Builds docs with `make strictdoc-export`
   - Combines to `dist/site/` with `make site-build`
   - Uploads artifact for testing

3. **test job**: Tests built artifacts
   - Runs `npm run test:offline`
   - Runs `npm run test:no-network`
   - Runs `npm run test:e2e`
   - Fails deployment if tests don't pass

4. **deploy job**: Deploys to gh-pages
   - Uses peaceiris/actions-gh-pages action
   - Replaces entire gh-pages with new build
   - Creates/updates `live` tag

**Output**: Complete site deployed to gh-pages with PWA at root and docs at /requirements/

### 2. `.github/workflows/ci.yml` (VALIDATION ONLY)
**Purpose**: Validates code quality and requirements on every push to main/master

**Triggers**:
- Push to main/master/pipeline branches
- Pull requests to main/master

**Does NOT publish** - only validates:
- Type checking
- Unit tests
- Grammar compilation
- StrictDoc requirements validation

## GitHub Pages Configuration

### Required Setup

You need to enable GitHub Pages in the repository settings:

1. Go to **Repository Settings** → **Pages**
2. Set **Source** to: `Deploy from a branch`
3. Set **Branch** to: `gh-pages`
4. Click **Save**

The `gh-pages` branch will be created automatically when the first deployment workflow runs.

### Access the Deployed Site

Once enabled, the site will be available at:
```
https://<github-username>.github.io/<repository-name>/
```

For example (adjust for your actual repository):
```
https://alvarogarcia7.github.io/training-parser-antlr4/
```

- PWA is at the root: https://alvarogarcia7.github.io/training-parser-antlr4/
- Documentation is at: https://alvarogarcia7.github.io/training-parser-antlr4/requirements/

## Deployed Branch Protection

### Branch Ruleset Setup

Configure the `deployed` branch with protection rules via GitHub web UI:

1. Go to **Repository Settings** → **Rules** → **Rulesets**
2. Create new ruleset targeting `deployed` branch
3. Enable these restrictions:
   - **Block force pushes** - Ensures fast-forward only
   - **Block deletion** - Prevents accidental removal
   - **Require status checks to pass**:
     - verify
     - build
     - test
   - **Restrict who can push** (optional):
     - Maintainers/admins only

This ensures deployments can only come from reviewed, tested code on the main branch.

## Make Targets

The following make targets are used in the deployment:

- `make site-build` - Builds PWA and docs together (NEW)
- `make pwa-test-built` - Tests built PWA (NEW)
- `make pwa-build` - Builds PWA only
- `make strictdoc-validate` - Validates all .sdoc files (syntax, references, structure)
- `make strictdoc-export` - Exports requirements to HTML in `requirements/output/`
- `make strictdoc-server` - Local development server at http://localhost:5111
- `make pwa-publish` - Deprecated, use deployed branch workflow
- `make docs-publish` - Deprecated, use deployed branch workflow

## Workflow Permissions

The `deploy.yml` workflow requires these permissions (configured in the workflow file):
- `contents: write` - Allows pushing to gh-pages and creating/updating tags
- `pages: write` - Required for GitHub Pages deployment

These are already set in the workflow file and don't require manual configuration.

## How It Works

1. **Commit to main/master**:
   - Code is reviewed in pull request
   - CI workflow validates without publishing

2. **Promote commit to deployed**:
   - Maintainer runs: `git push origin <commit-sha>:deployed`
   - This triggers the deploy workflow

3. **Deploy workflow runs**:
   - verify job checks deployment eligibility
   - build job creates artifacts
   - test job runs full test suite
   - deploy job pushes to gh-pages if tests pass
   - live tag is updated to point to deployed commit

4. **Site is live**:
   - GitHub Pages immediately serves updated content
   - Both PWA and docs are synchronized

## Troubleshooting

### Deployment fails at verify stage
See PWA_DEPLOYMENT.md troubleshooting section for detailed guidance on:
- Force push detected
- Not a fast-forward push
- Commit not reachable from main

### Deployment fails at test stage
See PWA_DEPLOYMENT.md for how to:
- Run tests locally before deploying
- Fix failing tests
- Retry deployment

### Pages not updating after deployment
1. Confirm GitHub Pages is enabled in repository settings
2. Check that the branch is set to `gh-pages`
3. Verify deploy workflow actually completed successfully
4. Clear browser cache (PWA caches aggressively)
5. Check the `live` tag points to latest: `git ls-remote origin refs/tags/live`

### Local Testing
Test the build locally before deploying:
```bash
make site-build          # Build PWA + docs
make pwa-test-built      # Run all tests
# Open dist/site/index.html in browser
```

## Quick Reference

| Task | Command |
|------|---------|
| Deploy commit | `git push origin <sha>:deployed` |
| Check live tag | `git rev-list -n 1 live` |
| Test locally | `make pwa-test-built` |
| Build locally | `make site-build` |
| Rollback | `git push origin <old-sha>:deployed` |

## Files Changed by TP-9

- `.github/workflows/deploy.yml` - New main deployment workflow
- `.github/workflows/ci.yml` - Updated to validation-only (no publishing)
- `.github/workflows/pwa-e2e-tests.yml` - Deleted/disabled
- `.github/workflows/deploy-pwa.yml` - Deleted
- `.github/workflows/publish-docs.yml` - Deleted
- `makefiles/pwa.mk` - Added site-build and pwa-test-built targets
- `makefiles/strictdocs.mk` - Marked docs-publish as deprecated
- `PWA_DEPLOYMENT.md` - Updated with new workflow
- `GITHUB_PAGES_SETUP.md` - Updated with new workflow
