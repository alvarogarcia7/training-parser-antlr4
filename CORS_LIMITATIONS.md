# CORS Limitations & Solutions for Private Git Servers

## The Problem

When you see this error:
```
Access to fetch at 'https://your-gitlab-domain/...' has been blocked by CORS policy:
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

**This is the browser protecting you.** The browser's Same-Origin Policy (SOP) prevents JavaScript from making requests to different origins unless the server explicitly allows it via CORS headers.

## Why This Happens

| Scenario | Works? | Reason |
|----------|--------|--------|
| PWA at `example.com` → GitHub `github.com` | ❌ | GitHub doesn't send CORS headers for git operations |
| PWA at `gitlab.example.com` → GitHub | ❌ | Different origins |
| PWA at `gitlab.example.com` → Same `gitlab.example.com` | ✅ | **Same origin - no CORS needed** |

## Solutions

### Solution 1: Deploy PWA on Same Domain (BEST) ✅

**Deploy the PWA on your GitLab domain:**

```bash
# Deploy to: https://gitlab.crypto.tii.ae/pwa/
# Git server: https://gitlab.crypto.tii.ae/agb-project-incubator/training-parser-data.git
# Result: Same origin = no CORS issues
```

**Advantages:**
- ✅ No CORS issues
- ✅ No proxy needed
- ✅ Fastest connections
- ✅ Secure (same domain)
- ✅ No external dependencies

**Setup:**
1. Build PWA: `make pwa-publish`
2. Serve from GitLab domain (requires GitLab server configuration)

---

### Solution 2: Use Local CORS Proxy (Development)

**For local development, run a CORS proxy:**

```bash
# Install CORS proxy
npm install -g cors-anywhere

# Start proxy on port 8081
cors-anywhere

# Then modify git-sync.js to use local proxy:
corsProxy: 'http://localhost:8081'
```

**Advantages:**
- ✅ Works for development
- ✅ Easy to set up
- ✅ No external dependencies
- ✅ Full control

**Disadvantages:**
- ❌ Only for local development
- ❌ Can't be used in production (runs on localhost)

---

### Solution 3: Configure Server CORS Headers

**Configure your GitLab to send CORS headers:**

In GitLab nginx config:
```nginx
add_header Access-Control-Allow-Origin *;
add_header Access-Control-Allow-Methods "GET, POST, OPTIONS, PUT, DELETE";
add_header Access-Control-Allow-Headers "Content-Type, Authorization";
```

**Advantages:**
- ✅ Works from any domain
- ✅ Secure (can restrict origins)
- ✅ No proxy needed

**Disadvantages:**
- ❌ Requires server configuration
- ❌ Exposes git endpoint to CORS

---

### Solution 4: Use Public CORS Proxy (With Caveats)

**The `cors.isomorphic-git.org` proxy should work, but:**

```
Issues:
- Returns 502 Bad Gateway for some private servers
- May not be accessible to GitLab on private networks
- May have rate limits
- Adds network latency
```

This is why the public CORS proxy is failing - it can't reach your private GitLab instance.

---

## Current Status

**Your Setup:**
```
PWA: http://localhost:8080 (development)
GitLab: https://gitlab.crypto.tii.ae (private server)
Connection: ❌ CORS blocked (different origins)
Public CORS proxy: ❌ 502 Bad Gateway
```

## Recommended Fix

**For development:**
1. Use local CORS proxy
2. Update `git-sync.js` to use `http://localhost:8081`
3. Test locally

**For production:**
1. Deploy PWA on same GitLab domain
2. OR configure GitLab CORS headers
3. Then no proxy needed

---

## Error Messages Guide

| Error | Cause | Solution |
|-------|-------|----------|
| "CORS blocked" | Server doesn't send CORS headers | Deploy on same domain |
| "502 Bad Gateway" | CORS proxy can't reach server | Use local proxy or same domain |
| "Failed to fetch" | Network unreachable | Check if server accessible |
| "Unauthorized (401)" | Got past CORS, auth failed | Check credentials |

---

## Testing CORS

**Check if server sends CORS headers:**
```bash
curl -i -H "Origin: http://localhost:8080" \
  https://gitlab.crypto.tii.ae/agb-project-incubator/training-parser-data.git/info/refs?service=git-upload-pack

# Look for:
# Access-Control-Allow-Origin: *
# OR
# Access-Control-Allow-Origin: http://localhost:8080
```

If these headers are missing, the server doesn't support CORS.

---

## Implementation Options

### Option A: Local CORS Proxy (Testing)

Fastest way to test:

```bash
# Terminal 1: Start CORS proxy
npm install -g cors-anywhere
cors-anywhere

# Terminal 2: Edit git-sync.js
# Change: corsProxy: 'https://cors.isomorphic-git.org'
# To: corsProxy: 'http://localhost:8081'

# Terminal 3: Run PWA and test
make pwa-serve
```

### Option B: Configure GitLab (Production)

For permanent solution, configure GitLab CORS in its nginx:

```nginx
# /etc/gitlab/gitlab.rb or nginx config
location ~ ^/path/to/repo\.git/ {
    if ($request_method = 'OPTIONS') {
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
        add_header Access-Control-Allow-Headers "Content-Type, Authorization";
        add_header Access-Control-Max-Age 86400;
        return 204;
    }
    add_header Access-Control-Allow-Origin *;
    # ... rest of config
}
```

### Option C: Deploy PWA on GitLab Domain (Best)

```bash
# Build PWA
make pwa-publish

# Copy dist to GitLab server
scp -r dist/* user@gitlab.crypto.tii.ae:/var/www/html/pwa/

# Access at: https://gitlab.crypto.tii.ae/pwa/
# Now: Same origin, no CORS needed!
```

---

## Why isomorphic-git.org Proxy Failed

The public CORS proxy (`cors.isomorphic-git.org`) returned 502 because:

1. **Network isolation:** Your GitLab is on a private network
2. **Firewall rules:** The proxy server can't reach your domain
3. **Proxy limitations:** Designed for public servers, not private instances

This is not a bug - it's a design choice for security.

---

## Summary

| Method | Dev | Prod | Complexity | Security |
|--------|-----|------|------------|----------|
| Local CORS Proxy | ✅ | ❌ | Low | Medium |
| GitLab CORS headers | ⚠️ | ✅ | Medium | Medium |
| Same domain | ✅ | ✅ | Medium | High |

**Recommended:** Deploy PWA on same domain as GitLab for best UX and security.
