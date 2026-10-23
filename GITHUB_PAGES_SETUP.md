# GitHub Pages Deployment Setup

## Overview
This project is configured to automatically publish StrictDoc-generated requirements documentation to GitHub Pages on every push to the main/master branch.

## Workflow Files

### 1. `.github/workflows/publish-docs.yml` (NEW)
**Purpose**: Builds and publishes documentation to GitHub Pages

**Triggers**:
- Push to `master` or `main` branch
- Manual workflow dispatch via GitHub UI

**Process**:
1. Check out repository
2. Set up Python 3.14
3. Install dependencies with uv
4. Export StrictDoc to HTML (`make strictdoc-export`)
5. Upload artifact to GitHub Pages
6. Deploy using `actions/deploy-pages@v4`

**Output**: `requirements/output/` directory deployed to GitHub Pages

### 2. `.github/workflows/ci.yml` (UPDATED)
**New Step**: Validates StrictDoc requirements before running tests

Added step `Validate StrictDoc requirements` that runs `make strictdoc-validate` to ensure all `.sdoc` files are syntactically correct and references are valid.

## GitHub Pages Configuration

### Required Setup

You need to enable GitHub Pages in the repository settings:

1. Go to **Repository Settings** → **Pages**
2. Set **Source** to: `Deploy from a branch`
3. Set **Branch** to: `gh-pages`
4. Click **Save**

The `gh-pages` branch will be created automatically when the workflow first runs.

### Access the Published Docs

Once enabled, documentation will be available at:
```
https://<github-username>.github.io/<repository-name>/requirements/
```

For example (adjust for your actual repository):
```
https://alvarogarcia7.github.io/training-parser-antlr4/requirements/
```

## Make Targets

The following make targets are used in the deployment:

- `make strictdoc-validate` - Validates all .sdoc files (syntax, references, structure)
- `make strictdoc-export` - Exports requirements to HTML in `requirements/output/`
- `make strictdoc-server` - Local development server at http://localhost:5111

## Workflow Permissions

The `publish-docs.yml` workflow requires these permissions (configured in the workflow file):
- `contents: read` - Read repository contents
- `pages: write` - Write to GitHub Pages
- `id-token: write` - OIDC token for GitHub Pages deployment

These are already set in the workflow file and don't require manual configuration.

## How It Works

1. **On Push to Main/Master**:
   - Workflow automatically triggers
   - CI workflow validates requirements syntax
   - publish-docs workflow builds and deploys

2. **Manual Trigger**:
   - Go to **Actions** → **Publish Documentation to GitHub Pages**
   - Click **Run workflow** to rebuild docs

3. **Automatic Deployment**:
   - Generated HTML is deployed to the `gh-pages` branch
   - Accessible immediately via GitHub Pages URL

## Troubleshooting

### Workflow fails with "Page build failure"
- Check the GitHub Pages deployment tab in Actions
- Ensure `requirements/output/` directory is generated correctly
- Verify StrictDoc validation passes in CI

### Pages not updating
- Confirm GitHub Pages is enabled in repository settings
- Check that the branch is set to `gh-pages`
- Wait a few minutes after push, GitHub Pages rebuild takes time

### Local Testing
Test the export locally before pushing:
```bash
make strictdoc-validate  # Ensure requirements are valid
make strictdoc-export    # Generate HTML
# Open requirements/output/index.html in browser
```

## Reference

Implementation based on pattern from:
https://github.com/nmfta-repo/vcr-experiment/blob/main/.github/workflows/publish.yml
