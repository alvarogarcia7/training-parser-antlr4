# PWA Deployment Strategy

## Overview

The Progressive Web App (PWA) is deployed to GitHub Pages using a clean separation of concerns:
- **main/master branch**: Contains source code only (no build artifacts)
- **gh-pages branch**: Contains built PWA files, automatically generated from main
- **GitHub Actions**: Automates the build and deployment process

## Architecture

```
main branch (source code)
    ↓
GitHub Actions workflow (.github/workflows/deploy-pwa.yml)
    ↓
Build process (make pwa-publish)
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

### 2. Automatic Deployment
- Triggered on every push to main/master
- Selective triggering based on path changes:
  - `mobile-app/**` - PWA source code
  - `parser/**` - Parser modules
  - `src/**` - Data access and utilities
  - `data/**` - Data files
  - Workflow config files themselves
- Can be manually triggered via `workflow_dispatch`

### 3. Build Process
The deployment uses the `make pwa-publish` target which:

1. **pwa-build**: Packages PWA for deployment
   - Copies `mobile-app/*` to `dist/pwa/`
   - Copies `parser/`, `src/`, `dist/`, `data/` modules
   - Creates a complete, self-contained PWA bundle

2. **gh-pages branch management**:
   - Creates `gh-pages` branch if it doesn't exist
   - Uses git worktree to isolate gh-pages branch
   - Replaces all files with new PWA build
   - Commits and pushes to origin/gh-pages

## Local Testing

### Build PWA locally
```bash
make pwa-build
```
Output: `dist/pwa/` directory contains the complete PWA

### Serve PWA locally over HTTP
```bash
make pwa-serve-local
```
- Runs on `https://localhost:8444`
- Uses self-signed SSL certificates (required for service workers)
- Good for testing before deployment

### Serve PWA from dist/pwa directory
```bash
python3 -m http.server -d dist/pwa 8080
```
- Simple HTTP server on `http://localhost:8080`

## GitHub Pages Configuration

The repository should be configured with:
- **Pages source**: Deploy from branch
- **Branch**: `gh-pages`
- **Folder**: `/ (root)`

This is typically done in GitHub Settings → Pages → Build and deployment

## CI/CD Integration

The workflow includes proper permissions and environment setup:
- `contents: write` - Allows pushing to gh-pages branch
- `pages: write` - Required for GitHub Pages
- `id-token: write` - For OpenID Connect
- Automatic git configuration for commits

## Manual Deployment

If needed, you can manually deploy:
```bash
make pwa-publish
```

Note: This requires:
- Local development environment with uv
- Git credentials configured
- Write access to the repository

## Troubleshooting

### PWA not updated on GitHub Pages
1. Check GitHub Actions workflow run for errors
2. Verify gh-pages branch has latest build
3. Check GitHub Pages settings point to gh-pages branch
4. Clear browser cache (PWA caches aggressively)

### Build fails
1. Run `make pwa-build` locally to debug
2. Check that all source files exist:
   - `mobile-app/` directory
   - `parser/`, `src/`, `data/` modules
   - `dist/training{Lexer,Parser}.py` files
3. Verify ANTLR files are generated: `make build`

### Git worktree conflicts
If `make pwa-publish` fails with worktree errors:
```bash
git worktree list
git worktree remove /tmp/pwa-deploy
```

## Files Involved

- `.github/workflows/deploy-pwa.yml` - GitHub Actions workflow
- `makefiles/pwa.mk` - Build targets
- `mobile-app/` - PWA source code
- `dist/pwa/` - Built PWA (generated, not committed)

## Future Enhancements

- Add pre-deployment tests (PWA loading tests)
- Implement canary deployments to dev gh-pages branch first
- Add performance metrics tracking
- Implement rollback mechanism for failed deployments
- Consider CDN caching strategy for service workers
