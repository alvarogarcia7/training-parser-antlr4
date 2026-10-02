# CORS Proxy Setup Guide

This guide explains when and how to set up `cors-anywhere` for the Training Parser PWA.

## What is CORS?

CORS (Cross-Origin Resource Sharing) is a browser security feature that prevents web pages from making requests to different domains without explicit permission.

### The Problem

When using `git-protocol` backend from the PWA (running on `https://github.io`), the browser blocks requests to:
- `git://localhost:8888/` (localhost)
- `git://your-server.com/` (different domain)

This is a security feature, but it prevents git-protocol from working.

### The Solution

`cors-anywhere` is a proxy that:
1. Accepts your request from the PWA
2. Forwards it to the git server
3. Adds CORS headers to the response
4. Returns the response to your browser

Now the browser sees same-origin request and allows it.

## When Do You Need It?

### You NEED cors-anywhere if:

- [ ] Using git-protocol backend
- [ ] Git server is on localhost (for testing)
- [ ] Git server is on different domain
- [ ] Server doesn't have CORS headers configured

### You DON'T need cors-anywhere if:

- [ ] Using GitHub API backend (recommended for GitHub.com)
- [ ] Git server has CORS headers configured
- [ ] Using SSH with key authentication
- [ ] Server is same domain as PWA

## Setup Instructions

### Option 1: Using npm script (Recommended)

#### Prerequisites

- Node.js 14+ installed
- npm 6+
- Internet connection

#### Steps

1. **Install dependency:**
   ```bash
   cd /home/appuser/repos/training-parser-antlr4
   npm install cors-anywhere
   ```

2. **Start cors-anywhere:**
   ```bash
   npm run cors-proxy
   ```

   Or manually:
   ```bash
   PORT=8081 node ./node_modules/cors-anywhere/server.js
   ```

3. **Verify it's running:**
   - You should see: `CORS-anywhere listening on port 8081`
   - Test with: `curl http://localhost:8081/http://example.com`

4. **Configure in PWA Settings:**
   - Open Training Parser
   - Go to Settings
   - Set:
     - Backend: `git-protocol`
     - CORS Proxy URL: `http://localhost:8081`
     - Remote URL: `git://localhost:8888/test-repo.git`
   - Click "Test Connection"

#### Stopping cors-anywhere

```bash
# Press Ctrl+C in the terminal where it's running
# Or kill the process:
pkill -f cors-anywhere
```

### Option 2: Manual Installation

```bash
# Install globally
npm install -g cors-anywhere

# Start with custom port
cors-anywhere -p 8081

# Or with environment variable
PORT=8081 cors-anywhere
```

### Option 3: Docker

```bash
# Run in Docker
docker run -p 8081:8081 \
  chuckleplant/cors-anywhere:latest

# Then configure in PWA:
# CORS Proxy URL: http://localhost:8081
```

### Option 4: Development Server

If using webpack or similar dev server:

```javascript
// webpack.config.js
module.exports = {
  devServer: {
    proxy: {
      '/cors-proxy': {
        target: 'http://localhost:8081',
        pathRewrite: { '^/cors-proxy': '' },
        changeOrigin: true
      }
    }
  }
};
```

## Configuration

### Default Configuration

```
Port: 8081
Host: 0.0.0.0 (listen on all interfaces)
Timeout: 120 seconds
Max Requests: 10 per 10 minutes (default rate limit)
```

### Environment Variables

```bash
# Custom port
PORT=9000 node ./node_modules/cors-anywhere/server.js

# Custom host
HOST=127.0.0.1 PORT=8081 node ./node_modules/cors-anywhere/server.js

# Set ALLOWED_ORIGINS (comma-separated)
ALLOWED_ORIGINS=localhost,127.0.0.1 PORT=8081 \
  node ./node_modules/cors-anywhere/server.js
```

### Rate Limiting

By default, cors-anywhere limits requests:
- 10 requests per 10 minutes from same IP
- Rate limit headers in response

To increase limit:

```bash
# Modify locally:
# Edit node_modules/cors-anywhere/server.js
# Find: keyGenerator and adjust limits
```

## Testing cors-anywhere

### Test 1: Basic Connectivity

```bash
# Check if cors-anywhere is running
curl -I http://localhost:8081

# Should return: 404 (expected for proxy root)
# Not: Connection refused
```

### Test 2: Proxy a Request

```bash
# Proxy a request to example.com
curl http://localhost:8081/http://example.com

# Should return: HTML from example.com with CORS headers
```

### Test 3: Git Server

```bash
# If git server is running on localhost:8888
# This won't work from curl, but shows concept
curl http://localhost:8081/git://localhost:8888/test-repo.git

# In browser console, this would work (no CORS error)
```

## Integration with Training Parser

### In Settings UI

1. Open Training Parser PWA
2. Click Settings (gear icon)
3. Configure:
   ```
   Backend: git-protocol
   CORS Proxy URL: http://localhost:8081
   Remote URL: git://localhost:8888/test-repo.git
   ```
4. Click "Test Connection"

### Programmatic Configuration

```javascript
// In mobile-app/src/git-sync-v2.js
const settings = {
  remoteUrl: 'git://localhost:8888/test-repo.git',
  corsProxyUrl: 'http://localhost:8081',
  backend: 'git-protocol'
};

saveSettings(settings);
```

### Auto-detection

The system can auto-detect CORS issues:

```javascript
// Automatically try cors-proxy if git-protocol fails
// Backend fallback chain:
// 1. Direct git-protocol
// 2. git-protocol via cors-proxy
// 3. GitHub API (if GitHub URL)
```

## Troubleshooting

### cors-anywhere won't start

**Error: `Address already in use`**
```bash
# Port 8081 is in use, find the process:
lsof -i :8081

# Kill it:
kill -9 <PID>

# Or use different port:
PORT=8082 node ./node_modules/cors-anywhere/server.js
```

**Error: `command not found: cors-anywhere`**
```bash
# Install it:
npm install cors-anywhere

# Or use npx:
PORT=8081 npx cors-anywhere
```

### Still getting CORS errors

1. **Verify cors-anywhere is running:**
   ```bash
   curl -I http://localhost:8081
   # Should get 404, not Connection refused
   ```

2. **Check CORS Proxy URL in settings:**
   - Should be: `http://localhost:8081` (not https://)
   - No trailing slash

3. **Check Remote URL format:**
   - Should be: `git://localhost:8888/test-repo.git`
   - Not: `http://` or `https://`

4. **Check git server is running:**
   ```bash
   npm run git-server
   # Should show: git daemon started on port 8888
   ```

5. **Try different port:**
   ```bash
   PORT=9000 node ./node_modules/cors-anywhere/server.js
   # Then update Settings: CORS Proxy URL = http://localhost:9000
   ```

### git-protocol still slow

- cors-anywhere adds ~100-200ms overhead
- Consider using GitHub API for github.com repos
- Or self-host cors-anywhere on your server

## Make Targets

### Add to Makefile

The project Makefile should include:

```makefile
cors-proxy:
	PORT=8081 node ./node_modules/cors-anywhere/server.js
.PHONY: cors-proxy

git-server:
	git daemon --reuseaddr --base-path=/tmp --export-all --port=8888 --verbose
.PHONY: git-server

# Start both for local testing
dev-sync-local: git-server cors-proxy
.PHONY: dev-sync-local
```

Usage:
```bash
# Start both in background
npm run git-server &
npm run cors-proxy &

# Or in Makefile:
make cors-proxy &
make git-server &
```

## Security Considerations

### What cors-anywhere Does NOT Do

⚠ cors-anywhere is **not** for:
- Masking CORS for external APIs
- Bypassing API authentication requirements
- Hiding requests from network monitoring
- Production use without security review

### What cors-anywhere DOES Do

✓ cors-anywhere is for:
- Local development and testing
- Proxying your own servers
- Adding CORS headers to responses
- Same-origin policy workarounds

### Security Best Practices

1. **Only run locally:**
   - cors-anywhere on port 8081 is for development
   - Don't expose to internet without auth

2. **Restrict origins:**
   - Set ALLOWED_ORIGINS to whitelist domains
   - Default allows all (safe for localhost)

3. **Use HTTPS in production:**
   - PWA should be over HTTPS
   - All proxied URLs should be HTTPS

4. **Monitor requests:**
   - cors-anywhere logs all requests
   - Check console output regularly

5. **Limit rate:**
   - Default rate limit: 10 req/10min
   - Adjust based on your needs

## Alternatives to cors-anywhere

### If You Want More Control

1. **Self-hosted CORS proxy:**
   - Build custom proxy in Node.js
   - Add authentication
   - Control rate limits

2. **Configure server CORS:**
   - Add CORS headers to git server
   - Requires server admin access
   - More secure

3. **Use GitHub API:**
   - Recommended for GitHub.com repos
   - No CORS proxy needed
   - Better performance

4. **SSH with git:**
   - SSH keys instead of tokens
   - No CORS issues
   - Requires SSH setup

## Performance Tuning

### Expected Latency

- Direct git-protocol: ~50-100ms
- Via cors-anywhere: ~150-250ms
- GitHub API: ~500-1000ms

### Optimization Tips

1. **Keep proxy local:**
   - Running on same machine = fastest
   - ~150ms over localhost

2. **Use HTTP not HTTPS:**
   - HTTP faster for localhost
   - cors-anywhere: `http://localhost:8081`

3. **Reduce request size:**
   - Smaller workout files sync faster
   - Large repos slow down

4. **Use git-protocol not GitHub API:**
   - For local testing
   - Direct protocol faster than REST API

## Monitoring

### Log Output

```
[timestamp] CORS-anywhere listening on port 8081
[timestamp] Request: GET http://example.com/
[timestamp] Response: 200 OK
```

### Check Status

```bash
# Is it running?
ps aux | grep cors-anywhere

# What port?
lsof -i :8081

# Recent requests?
tail -f cors-anywhere.log
```

## Cleanup

### Stop Services

```bash
# Stop cors-anywhere
pkill -f cors-anywhere

# Stop git server
pkill -f "git daemon"

# Kill all node processes (careful!)
pkill -f node
```

### Remove Installation

```bash
# Remove cors-anywhere
npm uninstall cors-anywhere

# Or clean everything
npm clean-install
```

## Next Steps

1. **Verify setup:**
   - `npm run cors-proxy` in one terminal
   - `npm run git-server` in another terminal
   - Open PWA and test connection

2. **Run tests:**
   ```bash
   npm run test:git
   npm run test:e2e
   ```

3. **Check logs:**
   - Open browser DevTools (F12)
   - Go to Console tab
   - Run sync operation
   - Look for errors

4. **Read guides:**
   - [PWA_SYNC_GUIDE.md](../mobile-app/PWA_SYNC_GUIDE.md)
   - [GIT_SYNC_TROUBLESHOOTING.md](../mobile-app/GIT_SYNC_TROUBLESHOOTING.md)

## FAQ

**Q: Is cors-anywhere safe?**  
A: Safe for local development. Don't expose to internet without security measures.

**Q: Do I need cors-anywhere for GitHub?**  
A: No, use GitHub API backend instead. No CORS issues.

**Q: Can cors-anywhere cache requests?**  
A: No, it's a simple proxy. Add caching in front if needed.

**Q: What if cors-anywhere crashes?**  
A: Restart it. No data loss. Local workouts are safe.

**Q: Can I run multiple instances?**  
A: Yes, use different ports (8081, 8082, etc).

**Q: Does it work with HTTPS?**  
A: Yes, specify `https://` in CORS Proxy URL and remote URL.

## Resources

- [cors-anywhere GitHub](https://github.com/Rob--W/cors-anywhere)
- [CORS Explained](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [git-daemon documentation](https://git-scm.com/docs/git-daemon)
- [Training Parser README](../README.md)

## See Also

- [PWA_SYNC_GUIDE.md](../mobile-app/PWA_SYNC_GUIDE.md) - Sync setup guide
- [GIT_SYNC_TROUBLESHOOTING.md](../mobile-app/GIT_SYNC_TROUBLESHOOTING.md) - Troubleshooting
- [Makefile](../Makefile) - Make targets

---

Last updated: 2024-10-02
