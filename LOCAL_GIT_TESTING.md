# Local Git Server Testing Guide

For development and testing of PWA git sync without depending on GitHub or GitLab, use these local servers.

## Quick Start

**Terminal 1: Start Git HTTP Server**
```bash
cd /tmp/git-server
node git-http-server.js
# ✅ Git HTTP Server running on http://localhost:8888
```

**Terminal 2: Start CORS Proxy**
```bash
node /tmp/cors-proxy.js
# ✅ CORS Proxy listening on http://localhost:8081
```

**Terminal 3: Start PWA**
```bash
cd training-parser-antlr4
make pwa-serve
# 🚀 PWA on http://localhost:8080
```

## How It Works

```
PWA (localhost:8080)
  ↓ (HTTP request with CORS headers)
CORS Proxy (localhost:8081)
  ↓ (forwards request without CORS restrictions)
Git Server (localhost:8888)
  ↓ (returns git data with CORS headers)
CORS Proxy
  ↓ (adds Access-Control-Allow-Origin: *)
PWA
```

## Testing

1. Open PWA in browser: **http://localhost:8080**
2. Click **⚙ Settings**
3. Click **Test Connection**
4. Should see: ✅ Connected! Found 1 branch(es): main (via proxy)

### What's Happening

- PWA detects localhost environment
- Automatically uses local test repo: `http://localhost:8888/test-repo.git`
- Credentials: `username=test, token=test`
- CORS proxy forwards the request
- Git server returns branch info with CORS headers

## Repository Details

**Location:** `/tmp/git-server/test-repo.git`
**Branch:** `main`
**Content:** Initial README.md

### Adding More Commits

```bash
cd /tmp/git-server
mkdir temp-clone && cd temp-clone
git clone ../test-repo.git .
echo "New workout data" >> data.txt
git config user.email "test@local"
git config user.name "Test User"
git add .
git commit -m "Add test data"
git push
cd /tmp/git-server && rm -rf temp-clone
```

## Troubleshooting

### "Connection refused" on port 8888
- Git server not running
- Run: `node /tmp/git-server/git-http-server.js`

### "Failed to fetch" via proxy
- Proxy not running
- Run: `node /tmp/cors-proxy.js`

### "No remote URL configured"
- localStorage doesn't have settings
- Manually set URL in Settings modal: `http://localhost:8888/test-repo.git`
- Or on localhost, test should auto-populate

### Git operations failing
- Check all three servers are running
- Verify no port conflicts (8080, 8081, 8888)
- Check browser console for detailed errors

## Next Steps

Once local testing works:

1. **Test with GitHub:**
   - Set remote URL: `https://github.com/you/repo.git`
   - Set GitHub username and PAT token
   - Test should connect to GitHub through public CORS proxy

2. **Deploy to GitHub Pages:**
   - Build: `make pwa-publish`
   - Push to gh-pages branch
   - PWA at: `https://username.github.io/training-parser`
   - Set repo URL in settings to your GitHub repo
   - Should work without CORS proxy (same-origin)

3. **Deploy to Private GitLab:**
   - Build: `make pwa-publish`
   - Deploy to GitLab server on same domain
   - PWA at: `https://gitlab.example.com/pwa`
   - Git server: `https://gitlab.example.com/repo.git`
   - No CORS proxy needed (same-origin)

## Architecture

```
┌─────────────────────────────────────┐
│   Frontend: isomorphic-git          │
│   (runs in browser, no CORS access) │
└─────────────────────────────────────┘
           ↓ (CORS blocked)
┌─────────────────────────────────────┐
│   CORS Proxy (cors-proxy.js)        │
│   Forwards requests without CORS    │
└─────────────────────────────────────┘
           ↓ (HTTP, no CORS needed)
┌─────────────────────────────────────┐
│   Git Server (git-http-server.js)   │
│   Serves git data via HTTP          │
└─────────────────────────────────────┘
```

For production, replace the CORS proxy with:
- Same-origin deployment (PWA + Git on same domain)
- GitHub Pages (works directly, isomorphic-git special handling)
- Public CORS proxy (cors.isomorphic-git.org) for cross-origin
