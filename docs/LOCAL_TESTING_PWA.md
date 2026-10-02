# Testing PWA Offline Functionality Locally

This guide covers how to test the Progressive Web App (PWA) offline-first capabilities on your local development machine.

## Quick Start

### 1. Build the PWA
```bash
make pwa-build
```

This creates `dist/pwa/` with all necessary files for offline operation.

### 2. Serve and Test
```bash
make test-offline
```

This starts a local server and runs offline tests with Playwright.

## Testing Offline Locally

### Using HTTP Server

The simplest way to test offline is with Python's built-in HTTP server:

```bash
make pwa-build
python3 -m http.server -d dist/pwa 8080
```

Then open `http://localhost:8080/` in your browser.

### Testing Offline Mode

#### Using Browser DevTools

1. Open the PWA at `http://localhost:8080/`
2. Wait for the page to fully load (status shows "ready")
3. Open Developer Tools (F12 or Ctrl+Shift+I)
4. Go to the **Network** tab
5. Check the **Offline** checkbox
6. Refresh the page (F5)

Expected behavior:
- Page loads from service worker cache
- Pyodide (Python runtime) loads from cache
- Parsing still works offline
- No network errors in console

#### Using Playwright Tests

Run comprehensive offline tests:

```bash
make test-offline
```

This tests:
- Loading app online, then going offline
- Offline parsing with Pyodide
- Page reload while offline
- No cross-origin requests during operation
- Recovery when coming back online

### Verify No Network Requests

Test that the app makes no external network calls:

```bash
make test-no-network
```

This:
- Intercepts all network requests
- Blocks any cross-origin requests
- Verifies app works without external dependencies
- Validates all resources are self-hosted

## Updating Vendor Assets

### Downloading Pyodide

To update Pyodide (Python runtime):

```bash
make download-pyodide
```

This downloads the latest Pyodide distribution to `mobile-app/pyodide/`.

### Rebuilding with Vendor Assets

After updating vendor files, rebuild the PWA:

```bash
make pwa-build-offline
```

This:
1. Downloads latest Pyodide
2. Builds PWA with vendor assets
3. Creates complete offline bundle in `dist/pwa/`

### Committing Changes

Only commit source files, NOT vendor outputs:

```bash
# DO NOT commit these:
# dist/pwa/           (generated)
# mobile-app/vendor/  (built from source)
# vendor/vendor-*.tar.gz (binary archives)

# DO commit these:
# mobile-app/sw.js    (service worker)
# mobile-app/index.html
# mobile-app/src/     (PWA JavaScript)
```

The `.gitignore` already excludes vendor artifacts.

## Service Worker Cache Strategy

### How It Works

The service worker uses a **cache-first** strategy:

1. **On install**: Precache all static assets listed in `PRECACHE_URLS`
2. **On fetch**: Return from cache if available; fall back to network
3. **On activate**: Clear old cache versions

### Cache Invalidation

When you need users to get new versions:

1. Update `CACHE_VERSION` in `mobile-app/sw.js`:
   ```javascript
   const CACHE_VERSION = 'v1.0.1';  // Changed from v1.0.0
   ```

2. Rebuild and deploy:
   ```bash
   make pwa-build
   make pwa-publish
   ```

3. Next time users visit, the old cache is cleared and new version is loaded

### Checking Cache in DevTools

1. Open DevTools (F12)
2. Go to **Application** tab
3. Expand **Cache Storage**
4. Look for cache named with current `CACHE_VERSION`
5. Inspect cached resources

## Running Full PWA Test Suite

### All PWA Tests
```bash
make test-pwa
```

Runs three test suites in order:
1. **PWA Integrity** - Static checks of config and assets
2. **Offline Tests** - Offline operation verification
3. **No-Network Tests** - Zero cross-origin validation

### Individual Test Suites

#### Integrity Tests (Python/pytest)
```bash
make test-pwa-integrity
```

Validates:
- Service worker configuration
- No unpkg/jsDelivr CDN references
- Vendor JavaScript files exist and are minified
- All PRECACHE_URLS are accessible
- HTML manifest configuration

#### Offline Tests (Playwright)
```bash
make test-offline
```

Validates:
- App loads online
- Parsing works offline
- Page reload works offline
- No cross-origin requests during offline operation

#### No-Network Tests (Playwright)
```bash
make test-no-network
```

Validates:
- Zero external network requests
- All resources from self-origin
- Parsing works with request blocking

## Debugging Offline Issues

### Service Worker Not Installing

Check browser console for errors:
- DevTools → Console tab
- Look for "ServiceWorker" errors
- Check that `sw.js` is accessible at root

### Pyodide Not Loading

The Python runtime takes 10-20 seconds on first load. Wait for status to show "ready".

If it times out:
1. Check browser console for errors
2. Verify `mobile-app/pyodide/` exists or is downloaded
3. Check network tab for blocked requests
4. Try clearing cache: DevTools → Application → Clear Site Data

### Cache Not Updating

After changing `CACHE_VERSION`:
1. Clear site data: DevTools → Application → Clear Site Data
2. Refresh the page
3. Service worker should install new cache

### Cross-Origin Requests

If tests fail with cross-origin errors:
1. Check what resource is being requested (DevTools → Network tab)
2. Verify it's not hardcoded in source files
3. Search codebase: `grep -r "https://" --include="*.js" --include="*.html"`
4. Move resource to `dist/pwa/vendor/` or inline it

## Testing Checklist

Use this checklist when testing offline functionality:

- [ ] App loads at `http://localhost:8080/`
- [ ] Status indicator shows "ready"
- [ ] Can parse valid workout data online
- [ ] Can go offline using DevTools
- [ ] Can reload page while offline
- [ ] Can parse workout data while offline
- [ ] No console errors while offline
- [ ] Can come back online
- [ ] Can parse again after coming online
- [ ] DevTools Network tab shows no external requests
- [ ] Service worker shows in Application → Service Workers
- [ ] Cache Storage contains current version cache
- [ ] `make test-offline` passes
- [ ] `make test-no-network` passes
- [ ] `make test-pwa-integrity` passes

## Performance Tips

### First Load Optimization
- Pyodide is large (~50MB compressed). First load takes time.
- Consider showing loading animation during initial setup
- Results are cached, so subsequent loads are instant

### Reducing Bundle Size
- Check `dist/pwa/` size: `du -sh dist/pwa/`
- Minify JavaScript files
- Consider splitting vendor files
- Use gzip compression in service worker

### Testing with Slow Network
Use DevTools Network tab throttling:
1. DevTools → Network tab
2. Change throttle from "No throttling" to "Slow 3G"
3. Test behavior on slow connections

## Continuous Integration

GitHub Actions automatically tests offline functionality on every push to `master`:
- Runs `make test-e2e` for UI tests
- Runs `make test-offline` for offline tests
- Runs `make test-pwa-integrity` for static checks

Check workflow logs: `.github/workflows/`

## See Also

- [PWA_DEPLOYMENT.md](../PWA_DEPLOYMENT.md) - Deployment strategy
- [makefiles/pwa.mk](../makefiles/pwa.mk) - Build and test targets
- [mobile-app/sw.js](../mobile-app/sw.js) - Service worker configuration
- [e2e/offline.spec.js](../e2e/offline.spec.js) - Offline tests
- [e2e/no-network.spec.js](../e2e/no-network.spec.js) - Network blocking tests
- [tests/pwa-checklist.py](../tests/pwa-checklist.py) - Integrity checks
