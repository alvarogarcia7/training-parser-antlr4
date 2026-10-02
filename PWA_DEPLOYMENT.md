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
  - `src/parser/**` - Parser modules
  - `src/**` - Data access and utilities
  - `data/**` - Data files
  - Workflow config files themselves
- Can be manually triggered via `workflow_dispatch`

### 3. Build Process
The deployment uses the `make pwa-publish` target which:

1. **pwa-build**: Packages PWA for deployment
   - Copies `mobile-app/*` to `dist/pwa/`
   - Copies `src/` (including `src/parser/`), `dist/`, `data/` modules
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
   - `src/` (including `src/parser/`), `data/` modules
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

## Vendor Assets and Offline Support

The PWA includes vendor assets (such as Pyodide) for offline-first functionality:

### Vendor Assets Structure
- **vendor/**: Contains minified JavaScript files and runtime dependencies
- **Pyodide**: Python runtime for client-side parsing
  - Included in `mobile-app/pyodide/` (if available locally)
  - Automatically copied to `dist/pwa/vendor/` during build

### Managing Vendor Assets
- Update Pyodide: Download new version to `mobile-app/pyodide/` and run `make pwa-build`
- Track only source files: `mobile-app/pyodide/**` are NOT committed (see .gitignore)
- Built vendor files are in `dist/pwa/vendor/` (also not committed)

### Cache Strategy
- Service worker uses cache-first strategy for static assets
- Cache version is managed by `CACHE_VERSION` in `mobile-app/sw.js`
- Update `CACHE_VERSION` to invalidate all browser caches
- Example: `CACHE_VERSION = 'v1.0.0'` (change to `v1.0.1` to force refresh)

## Version.json and Cache Busting

### Purpose
The `version.json` file provides metadata for cache management:
- Helps browsers detect PWA updates
- Supports granular cache invalidation
- Enables offline-aware version checking

### Format
```json
{
  "version": "1.0.0",
  "pyodide_version": "0.24.0",
  "cache_version": "v1.0.0",
  "build_date": "2026-10-02",
  "assets": ["index.html", "sw.js", "vendor/app.js"]
}
```

### Cache Busting Strategy
1. **CACHE_VERSION**: Updated in `sw.js` for major version bumps
   - Forces all users to re-download static assets
   - Use when making breaking changes

2. **Build-specific caching**:
   - Each PWA build has a unique identifier
   - Served files include content hashes when available
   - Minimizes unnecessary re-downloads

3. **Service Worker updates**:
   - Check version.json periodically (if available)
   - Show "Update Available" notification to users
   - Allow users to refresh to latest version

## Testing Offline Functionality

### Local Testing with Playwright

#### Test offline parsing
```bash
make test-offline
```
This runs `e2e/offline.spec.js` which:
- Loads the app while online
- Takes the browser offline using Playwright's `setOffline()`
- Verifies parsing still works using cached Pyodide
- Reloads the page while offline (tests service worker cache)
- Restores network and verifies continued operation

#### Test with zero cross-origin requests
```bash
make test-no-network
```
This runs `e2e/no-network.spec.js` which:
- Intercepts all network requests using Playwright
- Blocks any cross-origin requests (simulating no external network)
- Verifies app loads and functions completely with self-origin only
- Ensures no CDN dependencies are hardcoded

#### Run all PWA tests
```bash
make test-pwa
```
This runs all tests:
1. `test-pwa-integrity`: Pytest checks for valid service worker, vendor assets
2. `test-offline`: Offline operation tests
3. `test-no-network`: No cross-origin network tests

### Testing Integrity with pytest

```bash
make test-pwa-integrity
```

Checks:
- Service worker has correct cache strategy
- HTML files have no unpkg/jsDelivr CDN references
- No external script sources in HTML
- Service worker CACHE_VERSION is defined
- PRECACHE_URLS match files in dist/pwa/
- Vendor JavaScript files are minified
- Service worker install/fetch handlers exist

### Manual Testing

#### Using built PWA
```bash
make pwa-build
python3 -m http.server -d dist/pwa 8080
```
Then open `http://localhost:8080/` and test offline using browser DevTools:
1. Open DevTools (F12)
2. Go to Network tab
3. Check "Offline" checkbox
4. Reload page
5. Try parsing a workout

#### Using local HTTPS server
```bash
make pwa-serve-local
```
Access at `https://localhost:8444/` with self-signed certificate

### Continuous Integration

GitHub Actions automatically runs:
- `make test-e2e` - All UI tests (including `ui.spec.js`)
- `make test-offline` - Offline tests (after PR merge)
- `make test-pwa-integrity` - Static analysis

## Future Enhancements

- Add performance metrics tracking for offline operations
- Implement selective sync for large datasets
- Add progressive image loading for offline mode
- Implement rollback mechanism for failed updates
- Consider differential caching by user tier/device
