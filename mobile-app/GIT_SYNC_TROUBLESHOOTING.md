# Git Sync Troubleshooting Guide

This guide helps you solve common issues with git-sync in the Training Parser PWA.

## Quick Diagnostic Steps

1. Open browser DevTools (F12) and check Console for errors
2. Go to Settings → "Backend Info" to see active backend
3. Click "Test Connection" to validate current setup
4. Check your network connection
5. Verify token hasn't expired

## Error Messages and Solutions

### CORS Error

**Error Message:**  
```
CORS error: No 'Access-Control-Allow-Origin' header
Cross-Origin Request Blocked
```

**Causes:**
- Using git-protocol from a web context
- Self-hosted server without CORS configuration
- Network policy blocking request

**Solutions:**

1. **For GitHub repositories:** Use GitHub API backend instead
   ```
   Settings → Backend → Select "GitHub API"
   ```

2. **For git-protocol:** Set up cors-anywhere proxy
   ```bash
   npm run cors-proxy
   # Then in Settings:
   # Backend: git-protocol
   # CORS Proxy URL: http://localhost:8081
   ```

3. **For self-hosted servers:** Configure CORS headers
   ```
   Access-Control-Allow-Origin: *
   Access-Control-Allow-Methods: GET, POST, PUT
   Access-Control-Allow-Headers: Authorization, Content-Type
   ```

See [../docs/CORS_PROXY_SETUP.md](../docs/CORS_PROXY_SETUP.md) for detailed cors-anywhere setup.

---

### Authentication Failed

**Error Message:**  
```
401 Unauthorized
Authentication failed
Invalid credentials
```

**Causes:**
- Token is incorrect or expired
- Username doesn't match token
- Token permissions are insufficient

**GitHub API Specific:**

1. **Check token validity:**
   - Go to https://github.com/settings/tokens
   - Verify your token exists and hasn't expired
   - Click on token to see expiration date

2. **Check token permissions:**
   - Token needs at least `Contents: Read and write`
   - For private repos: `repo` full access needed
   - Click "Regenerate token" to refresh

3. **Verify username:**
   - Settings → Username should match GitHub username
   - Not your email address
   - Case sensitive

4. **Update token:**
   - Go to https://github.com/settings/tokens?type=beta
   - Generate new fine-grained token
   - Copy the new token (starts with `ghp_`)
   - Paste in Settings → Token field
   - Click "Test Connection"

**git-protocol Specific:**

1. **For GitHub repos:**
   - Username: your GitHub username
   - Token: fine-grained PAT (starts with `ghp_`)
   - Or: classic PAT (starts with `ghp_` or `ghp_`)

2. **For self-hosted:**
   - Username: git username for that server
   - Token/Password: credentials for that server
   - May need to use SSH keys instead

---

### Repository Not Found

**Error Message:**  
```
404 Not Found
Repository not found
https://github.com/user/repo.git not found
```

**Causes:**
- Repository URL is incorrect
- Repository doesn't exist
- Repository is private and token has no access
- Typo in username or repository name

**Solutions:**

1. **Verify repository exists:**
   - Go to https://github.com/username/repo
   - If 404, repository doesn't exist
   - Check spelling of username and repository

2. **Check repository access:**
   - Public repos: Should be accessible without token
   - Private repos: Need token with `repo` access
   - For GitHub API: Fine-grained token needs "Only select repositories" set to your repo

3. **Correct the URL:**
   ```
   ❌ https://github.com/user/repo      (missing .git)
   ❌ https://github.com/user-repo.git  (wrong format)
   ✓ https://github.com/username/repo.git
   ✓ https://github.com/username/repo
   ```

4. **For git-protocol:**
   ```
   ❌ http://github.com/user/repo       (should be git://)
   ❌ git://user/repo.git               (missing host)
   ✓ git://github.com/user/repo.git
   ✓ git://localhost:8888/test-repo.git
   ```

---

### Connection Refused

**Error Message:**  
```
Connection refused
ECONNREFUSED
Could not connect to localhost:8888
```

**Causes:**
- git server not running
- cors-anywhere proxy not running
- Wrong port number
- Firewall blocking connection

**Solutions:**

1. **Start git server (localhost):**
   ```bash
   npm run git-server
   # Or manually:
   git daemon --reuseaddr --base-path=/tmp --export-all --port=8888
   ```

2. **Start cors-anywhere (if using git-protocol):**
   ```bash
   npm run cors-proxy
   # Or manually:
   PORT=8081 node ./node_modules/cors-anywhere/server.js
   ```

3. **Check port in URL:**
   - Default git server: port 8888
   - Default cors-proxy: port 8081
   - If different, update Settings → CORS Proxy URL

4. **Check firewall:**
   ```bash
   # macOS
   sudo lsof -i :8888
   
   # Linux
   sudo netstat -tuln | grep 8888
   
   # Windows
   netstat -ano | findstr :8888
   ```

5. **Verify remote URL:**
   ```
   For localhost: git://localhost:8888/repo.git
   For remote: git://your-server.com/repo.git
   ```

---

### Unrelated Histories

**Error Message:**  
```
fatal: refusing to merge unrelated histories
Unrelated histories detected
```

**Causes:**
- Repository was initialized separately locally and remotely
- Pull into a repository that has no common history
- Switching backends

**Solutions:**

1. **Backup your local workouts first:**
   - Take screenshots or note workout details
   - These will be lost if you reset

2. **Option A: Reset repository:**
   - Settings → "Reset Repository"
   - Then pull from remote
   - Re-create local workouts if needed

3. **Option B: Force accept remote history:**
   - This will discard all local changes
   - Only do this if you want remote version

4. **Option C: Switch to different backend:**
   - Settings → Backend → Select different backend
   - Try pull with new backend

5. **Prevent in future:**
   - Always pull first before creating workouts
   - Keep local and remote in sync regularly

---

### Push Rejected

**Error Message:**  
```
rejected: master/main in use
Push rejected
Permission denied
```

**Causes:**
- No write permission to repository
- Trying to push to wrong branch (master vs main)
- Repository is bare and doesn't allow push to current branch
- Token permissions insufficient

**Solutions:**

1. **Check write permissions:**
   - For GitHub: Token needs `Contents: Read and write`
   - For self-hosted: User must have write access
   - Verify with repository owner

2. **Check default branch:**
   ```bash
   # For GitHub
   curl https://api.github.com/repos/user/repo | grep default_branch
   
   # Common defaults: main, master, develop
   ```

3. **Check token permissions (GitHub):**
   - https://github.com/settings/tokens
   - Click your token
   - Verify it has `Contents: Read and write`
   - Not just Read access

4. **For private repositories:**
   - Ensure token has full `repo` scope
   - For new fine-grained tokens: Set to "All repositories"
   - Or: Explicitly select your repository

---

### Pull Failed

**Error Message:**  
```
Pull failed
Could not fetch from remote
Bad request
```

**Causes:**
- Network connectivity issues
- Token expired
- Remote repository changed structure
- Git server is down

**Solutions:**

1. **Test network connectivity:**
   ```bash
   # Test if remote is reachable
   curl -I https://github.com/user/repo  # Should get 200
   ```

2. **Check token freshness:**
   - Go to https://github.com/settings/tokens
   - Verify token hasn't expired
   - If expired: Generate new token and update Settings

3. **Check remote repository:**
   - Visit repository on web
   - Verify it still exists
   - Check you still have access

4. **Clear local repository:**
   - Settings → "Clear Cache"
   - Try pull again

5. **Check git server status:**
   ```bash
   # If using local git server
   npm run git-server &
   ```

---

### Network Disconnection

**Error Message:**  
```
Network error
Fetch failed
Request timeout
Connection lost
```

**What happens:**
- Your local changes are **saved locally**
- Remote sync is **queued** for when online
- Other data remains intact

**Solutions:**

1. **No action needed immediately:**
   - Your workouts are safe locally
   - Keep the app open

2. **When back online:**
   - Click "Sync Now" or
   - Refresh the page (if you closed it)
   - Push will complete

3. **If closed the app:**
   - Reopen Training Parser
   - Go to Settings → "Sync Status"
   - Manual push will resume sync

4. **Check battery/data:**
   - Ensure device has power
   - Check mobile data is enabled
   - Switch networks (WiFi ↔ mobile)

5. **Check firewall:**
   - Corporate WiFi may block git:// ports
   - Try HTTPS or ask IT to allow port 8888/8081

---

## Backend-Specific Troubleshooting

### GitHub API Backend

**Best for:** GitHub.com repositories

**Specific Issues:**

1. **Rate limit exceeded:**
   ```
   API rate limit exceeded for user XXX
   ```
   - Solution: Wait 1 hour or get GitHub Pro
   - Use git-protocol backend as workaround

2. **Invalid scope:**
   ```
   Token scope insufficient
   ```
   - Go to https://github.com/settings/tokens
   - Regenerate token with `Contents: Read and write`
   - Update in Settings

3. **Repository deleted:**
   ```
   Repository not found (404)
   ```
   - Verify repository still exists on GitHub
   - Check spelling of username/repo
   - Ask repository owner for access

---

### git-protocol Backend

**Best for:** Self-hosted servers and local testing

**Specific Issues:**

1. **git daemon not running:**
   ```
   Connection refused on port 8888
   ```
   - Start: `npm run git-server`

2. **cors-anywhere not running:**
   ```
   CORS error: No Access-Control-Allow-Origin
   ```
   - Start: `npm run cors-proxy`
   - Verify in Settings: CORS Proxy URL = http://localhost:8081

3. **Repository not exported:**
   ```
   Fatal: Not a git repository
   ```
   - For git daemon: Repository must have `git-daemon-export-ok` file
   - Create with: `touch /path/to/repo/.git/git-daemon-export-ok`

4. **Permission denied (SSH):**
   ```
   Permission denied (publickey)
   ```
   - Switch to HTTPS URL format
   - Or: Configure SSH keys on git server

---

## Performance Issues

### Slow Sync

**Symptoms:**
- Push/pull taking >10 seconds
- App freezes during sync

**Solutions:**

1. **Check file size:**
   - Very large workout files slow sync
   - Split old workouts into smaller files

2. **Check network:**
   ```bash
   # Test bandwidth
   curl -I https://github.com
   
   # Should respond in <1 second
   ```

3. **Check repository size:**
   ```bash
   # For GitHub
   curl https://api.github.com/repos/user/repo | grep size
   ```

4. **Use git-protocol instead of GitHub API:**
   - GitHub API has more overhead
   - git-protocol is faster for small repos

5. **Clear local cache:**
   - Settings → "Clear Cache"
   - Rebuild from remote

---

### Memory Issues

**Symptoms:**
- App crashes during sync
- Browser tab unresponsive

**Solutions:**

1. **Close other tabs:**
   - Frees up memory for Training Parser

2. **Restart browser:**
   - Clears memory leaks

3. **Update browser:**
   - Ensure you have latest version

4. **Reduce workout file size:**
   - Limit exercises per session
   - Archive old workouts

---

## Data Recovery

### Lost Local Changes

**If you accidentally cleared cache:**

1. **Check browser history:**
   - Your files may still be in browser memory
   - Don't close tab if just happened

2. **Check recent backups:**
   - If synced to GitHub: Pull from main branch
   - Go to https://github.com/user/repo
   - Click "commits" to see history

3. **Manual recovery:**
   - Pull from remote
   - Create workouts again
   - Save and commit

---

### Lost Remote Changes

**If files disappeared from remote:**

1. **Check GitHub activity:**
   - https://github.com/user/repo/activity
   - Click on commits
   - See deleted files in commits

2. **Restore from backup:**
   - GitHub keeps commits for 90 days
   - Look for delete commit
   - Revert that commit

3. **Contact GitHub support:**
   - For deleted repositories
   - They may recover within 30 days

---

## Diagnosis Checklist

Before contacting support, verify:

- [ ] Network connection is active
- [ ] Browser tab has focus
- [ ] Repository URL is correct
- [ ] Token is valid and not expired
- [ ] Backend selection matches URL type
- [ ] No error in browser console (F12)
- [ ] Test Connection shows "OK"
- [ ] Try on different browser
- [ ] Try on different network (WiFi vs mobile)
- [ ] Clear browser cache and try again

## Getting More Information

### Enable Debug Mode

```javascript
// In browser console:
localStorage.setItem('debug', 'git-sync:*');
location.reload();

// Disable:
localStorage.removeItem('debug');
```

### Get Backend Info

```javascript
// In browser console:
getBackendInfo()

// Shows which backend is active
// Shows any recent errors
// Shows configuration (without token)
```

### Check Network Requests

1. Open DevTools (F12)
2. Go to Network tab
3. Perform sync operation
4. Check requests:
   - GitHub API: Should see https://api.github.com/repos/...
   - git-protocol: Should see git daemon connections

### Browser Console Errors

1. Open DevTools (F12)
2. Go to Console tab
3. Look for red error messages
4. Copy full error text
5. Search error message in this guide

---

## Still Having Issues?

### Check Related Docs

- [PWA_SYNC_GUIDE.md](./PWA_SYNC_GUIDE.md) - Full sync guide
- [../docs/CORS_PROXY_SETUP.md](../docs/CORS_PROXY_SETUP.md) - CORS setup
- [./src/git-sync-v2.js](./src/git-sync-v2.js) - Main module

### Debug Information to Collect

If contacting support, provide:

1. **Error message:** Exact text from error dialog
2. **Console logs:** From browser DevTools
3. **Settings:** Repository URL, backend type (not token)
4. **Browser:** Chrome/Firefox/Safari version
5. **OS:** Windows/macOS/Linux version
6. **Network:** Home WiFi / Mobile / Corporate
7. **Steps to reproduce:** How to trigger the issue

### Contact Support

- Check [../../README.md](../../README.md) for contact info
- Include debug information from above
- Include reproduction steps
- Attach console logs

---

## Common Workflows to Fix Issues

### Reset and Start Fresh

1. Go to Settings
2. Click "Clear All Settings"
3. Click "Clear Cache"
4. Close the app
5. Clear browser cache (Ctrl+Shift+Delete)
6. Reopen app
7. Set up again from scratch

### Switch Backends

1. Note your current settings
2. Go to Settings → Backend
3. Select different backend (GitHub API ↔ git-protocol)
4. Test Connection
5. If works: Try pull
6. If doesn't work: Switch back

### Disable CORS Proxy

1. Stop cors-anywhere: Ctrl+C
2. Wait 5 seconds
3. Update Settings → CORS Proxy URL: (empty)
4. Use GitHub API backend instead
5. Test Connection

### Force Git Server Restart

```bash
# Kill any existing processes
pkill -f "git daemon"
pkill -f "cors-anywhere"

# Wait a moment
sleep 2

# Start fresh
npm run git-server &
npm run cors-proxy &
```

---

## FAQ

**Q: Will I lose my data if I clear cache?**  
A: Local workouts are safe if synced to remote. Only clear cache if remote is up to date.

**Q: Can I use SSH keys instead of tokens?**  
A: Yes, for git-protocol backend on self-hosted servers. GitHub requires tokens or SSH configured globally.

**Q: What's the difference between Public and Private repositories?**  
A: Private repos need authentication. Public repos work without token (but slower).

**Q: How long are tokens valid?**  
A: GitHub tokens expire per your setting (default 90 days). Check at https://github.com/settings/tokens.

**Q: Can I use the same token on multiple devices?**  
A: Yes, but store securely. Never commit tokens to git.

**Q: What happens to my data if the remote repository is deleted?**  
A: Local copy remains. You can create new repository and push again.

**Q: Can I migrate from one repository to another?**  
A: Yes: Pull all from old repo → Create new remote → Push to new.

---

## Performance Benchmarks

Expected performance on typical network:

| Operation | GitHub API | git-protocol |
|-----------|-----------|--------------|
| Test Connection | ~500ms | ~100ms |
| List Workouts | ~200ms | ~50ms |
| Save 1 Workout | ~100ms | ~50ms |
| Push (1 file) | ~1s | ~500ms |
| Pull (1 file) | ~1s | ~500ms |
| Conflict Check | ~100ms | ~100ms |

If slower: Check network speed and repository size.

---

Last updated: 2024-10-02  
See [../../README.md](../../README.md) for version info
