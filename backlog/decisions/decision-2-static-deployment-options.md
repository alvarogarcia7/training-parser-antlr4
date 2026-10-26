# Decision 2: Static Deployment Options for PWA Git Sync

**Date:** 2026-09-25
**Status:** DECIDED
**Context:** Deploying a PWA with git sync to GitHub Pages and private git servers

## The Question

Can we deploy the training parser PWA to GitHub Pages and sync workouts with a private GitLab instance using only static/frontend code?

**Answer: No, not completely. But there are practical solutions.**

---

## The Reality

### The Constraint: CORS is Enforced by the Browser

CORS (Cross-Origin Resource Sharing) is a browser security feature that **cannot be bypassed with frontend code alone**.

```
Origin A (GitHub Pages): https://username.github.io
Origin B (Private GitLab): https://gitlab.instance

Browser blocks requests from A → B without:
1. Server (B) sending CORS headers, OR
2. A being on the same domain as B, OR
3. Using a CORS proxy
```

**This is by design.** Frontend code cannot bypass CORS—it's literally a security feature to prevent JavaScript from bypassing it.

### What Doesn't Work

| Approach                       | Result        | Why                               |
|--------------------------------|---------------|-----------------------------------|
| Direct fetch to private server | ❌ CORS blocks | No CORS headers from server       |
| `fetch` with special headers   | ❌ CORS blocks | Preflight fails                   |
| Service Worker intercept       | ❌ CORS blocks | Browser enforces CORS before SW   |
| `mode: 'no-cors'`              | ❌ Fails       | Can't read headers needed for git |
| Encode in URL                  | ❌ CORS blocks | Still different origin            |

### Why Public CORS Proxy Fails

The public CORS proxy (`cors.isomorphic-git.org`) returned **502 Bad Gateway** because:
- Your private GitLab is unreachable from the public internet
- The proxy runs on a different network
- **This is not a bug**—it's the proxy working as designed

---

## Solutions That Actually Work

### ✅ Solution 1: Use GitHub as Git Server (BEST)

**For GitHub Pages → GitHub repo: Works perfectly, no CORS issues.**

```
PWA: https://username.github.io/training-parser
Git Server: https://github.com/username/training-workouts
Result: isomorphic-git has special handling for github.com
```

**Why it works:**
- GitHub handles CORS correctly
- isomorphic-git has built-in support
- No proxy needed
- No backend needed
- All static code

**Implementation:**
```javascript
// In PWA settings:
Remote URL: https://github.com/username/training-workouts.git
Username: github_username
Token: github_pat_token
// Just works ✅
```

**Advantages:**
- ✅ No CORS issues
- ✅ No backend needed
- ✅ No proxy needed
- ✅ All static/frontend code
- ✅ Free GitHub Pages hosting
- ✅ Simple configuration

---

### ✅ Solution 2: Deploy on Same Domain (SECOND BEST)

**For production: Deploy PWA on the same domain as your git server.**

```
PWA: https://gitlab.instance/pwa/
Git Server: https://gitlab.instance/project/repo.git
Result: Same origin = no CORS needed
```

**Why it works:**
- Same origin = browser doesn't enforce CORS
- No proxy needed
- No backend needed

**Implementation:**
```bash
# Build PWA
make pwa-publish

# Deploy to your GitLab server
scp -r dist/* user@gitlab.instance:/var/www/pwa/

# Access at: https://gitlab.instance/pwa/
```

**Advantages:**
- ✅ No CORS issues
- ✅ No proxy needed
- ✅ No backend needed
- ✅ Works with private servers
- ✅ All static code

---

### ⚠️ Solution 3: Local CORS Proxy (Development Only)

**For development/testing: Run cors-anywhere locally.**

```bash
# Terminal 1
npm install -g cors-anywhere
cors-anywhere  # Starts on localhost:8081

# Terminal 2
make pwa-serve  # PWA on localhost:8080

# PWA automatically uses local proxy
```

**Why it works:**
- Local proxy can reach any server
- PWA auto-detects localhost and uses proxy
- No code changes needed

**Advantages:**
- ✅ Works for testing private servers
- ✅ No server-side CORS configuration needed
- ✅ Quick setup

**Disadvantages:**
- ❌ Only for development
- ❌ Doesn't work on GitHub Pages
- ❌ Requires running proxy

---

### ❌ Solution 4: GitHub Pages + Private Server (NOT POSSIBLE)

**Cannot be done with only static/frontend code.**

```
PWA: https://username.github.io (GitHub Pages)
Git Server: https://gitlab.instance (private)
CORS: Browser blocks cross-origin requests
Solution: Would require backend proxy
```

**To make this work, you would need a backend:**
```javascript
// Backend endpoint
GET /api/proxy?url=<github-pages-origin>&target=<gitlab-url>

// Returns with proper CORS headers
Access-Control-Allow-Origin: https://username.github.io
```

But that's a backend solution, not static code.

---

## Decision Matrix

| Solution               | GitHub Pages | Private Server | Static Only | Setup Time |   Recommended    |
|------------------------|:------------:|:--------------:|:-----------:|:----------:|:----------------:|
| Use GitHub repo        |      ✅       |       ❌        |      ✅      |   5 min    |     **BEST**     |
| Deploy on same domain  |      ⚠️      |       ✅        |      ✅      |   15 min   |     **GOOD**     |
| Local CORS proxy       |      ⚠️      |       ✅        |      ✅      |   2 min    |   **Dev only**   |
| Private GitLab + Pages |      ❌       |       ❌        |      ❌      | Impossible | **Not possible** |

---

## Recommendation

### For GitHub Pages Users

**Use GitHub as your git server:**

1. Create GitHub repository: `https://github.com/you/training-workouts`
2. Deploy PWA to GitHub Pages
3. Configure PWA to use GitHub repo
4. **It just works.** No CORS issues, no proxy, no backend.

### For Private Git Servers

**Deploy PWA on the same domain:**

1. Build PWA: `make pwa-publish`
2. Deploy to: `https://your-gitlab-domain/pwa/`
3. Configure PWA to use your GitLab repo
4. **It just works.** Same origin, no CORS.

### For Development Testing

**Use local cors-anywhere:**

1. `npm install -g cors-anywhere && cors-anywhere`
2. Run PWA locally: `make pwa-serve`
3. PWA auto-detects and uses local proxy
4. Test against any server (GitHub, GitLab, private instances)

---

## What We Implemented

✅ **Automatic localhost proxy detection**
- PWA detects if running on localhost
- Uses local proxy if available
- Falls back to public proxy in production
- No code changes needed

✅ **CSP allows localhost development**
- Added `http://localhost:*` to CSP
- Developers can use local cors-anywhere
- Production CSP remains strict (https only)

✅ **Comprehensive documentation**
- CORS_LIMITATIONS.md explains the constraints
- Clear solutions for each scenario
- Implementation guides for each option

---

## Conclusion

**Frontend-only static code cannot bypass CORS.** This is not a limitation of our implementation—it's a fundamental browser security constraint.

**The practical solutions are:**
1. **Use GitHub** (recommended for GitHub Pages)
2. **Deploy on same domain** (recommended for private servers)
3. **Use local proxy** (for development/testing)

All three options work with **fully static code** deployed to GitHub Pages or any hosting. Pick based on your git server.

---

## Related Documentation

- `CORS_LIMITATIONS.md` - Detailed CORS explanation and all solutions
- `git-sync.js` - getCorsProxy() function for automatic detection
- `index.html` - CSP policy allowing localhost for development
