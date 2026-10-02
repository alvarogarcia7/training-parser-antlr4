# PWA Git Sync Guide

This guide explains how to use git-sync in the Training Parser PWA to synchronize workout data across devices and tabs.

## Overview

The Training Parser uses a **dual-backend git-sync system** that allows synchronization with both GitHub and custom git servers. The system automatically selects the best backend for your repository:

- **GitHub API** for github.com repositories (primary, recommended for GitHub)
- **git-protocol** for self-hosted or other git servers

## Backend Selection

### GitHub API Backend

**Best for:** GitHub.com repositories with fine-grained personal access tokens

**Requirements:**
- GitHub account
- Fine-grained Personal Access Token (recommended over classic tokens)
- HTTPS connection (no special setup needed)

**Advantages:**
- No CORS issues (GitHub API handles them)
- More reliable for GitHub repositories
- Better rate limiting and error messages
- Works on any network

**How to use:**
1. Generate a fine-grained PAT at https://github.com/settings/tokens?type=beta
2. Select "Only select repositories"
3. Grant `Contents: Read and write` permission
4. Copy the token and paste in Settings
5. Enter your repository URL: `https://github.com/username/repo.git`

### git-protocol Backend

**Best for:** Self-hosted git servers or GitHub over git protocol

**Requirements:**
- Repository accessible via `git://` or `https://` URL
- For localhost testing: cors-anywhere proxy (port 8081)
- For remote self-hosted: CORS headers configured or proxy setup

**Advantages:**
- Works with any git server
- Lighter weight than GitHub API
- Good for local/offline-first workflows
- Native git protocol support

**How to use:**

1. **For localhost/local testing:**
   - Start cors-anywhere proxy: `npm run cors-proxy`
   - Use URL format: `git://localhost:8888/repo.git`

2. **For self-hosted git:**
   - Repository must be accessible via CORS or through cors-anywhere
   - URL format: `git://your-server.com/repo.git`

3. **For GitHub via git-protocol:**
   - Use: `git://github.com/username/repo.git`
   - May require cors-anywhere proxy depending on network

## Backend Auto-Selection

The system automatically chooses backends based on your repository URL:

```
https://github.com/user/repo.git  → GitHub API (primary) + git-protocol (fallback)
git://github.com/user/repo.git     → git-protocol (primary)
git://your-server.com/repo.git     → git-protocol (primary)
https://your-server.com/repo.git   → git-protocol (primary)
```

### Manual Backend Override

You can manually select a backend in Settings:

- **Auto** (default) - Let system choose based on URL
- **GitHub API** - Force GitHub API backend
- **git-protocol** - Force git-protocol backend

## Configuration

### Settings UI

Open Settings in the PWA to configure:

1. **Remote URL** - Repository URL (https://... or git://...)
2. **Backend** - GitHub API / git-protocol / Auto
3. **Username** - Your GitHub username (GitHub API only)
4. **Token** - Personal access token or git credentials
5. **CORS Proxy** - URL of cors-anywhere instance (if needed)
6. **Author Name** - Name for commits

### Settings Storage

- Settings are stored in **localStorage** under key `git_settings`
- **Tokens are NEVER persisted** to IndexedDB or localStorage
- Tokens are kept in memory only during the session
- Clear settings: Open Settings and click "Clear All"

## Token Management

### GitHub API Token

Generate at: https://github.com/settings/tokens?type=beta

**Recommended Settings:**
- Token type: Fine-grained personal access token
- Repository access: Only select repositories
- Permissions:
  - `Contents: Read and write`
  - `Metadata: Read-only`
- Expiration: 90 days (rotate regularly)

**Token Format:**
- Starts with `ghp_` (fine-grained)
- Example: `ghp_1234567890abcdefghijklmnopqrstuv`

### git-protocol Authentication

- For GitHub: Use your GitHub username and personal access token
- For self-hosted: Use git-over-http credentials or SSH keys

**Important:** Tokens are **NEVER logged** or exposed in:
- Console output
- Error messages
- LocalStorage/IndexedDB
- Debug tools

Tokens are kept in **memory only** and cleared when you:
- Close the browser tab
- Clear settings
- Sign out

## Synchronization Workflows

### Single Device, Multiple Tabs

1. Open Training Parser in two browser tabs
2. Both tabs show the same data (via localStorage sync)
3. Create/modify workout in Tab 1
4. Tab 2 automatically reflects changes
5. Push from Tab 1 syncs to remote
6. Pull in Tab 2 gets latest remote changes

### Multiple Devices

1. Device A: Create workout → Push to remote
2. Device B: Pull from remote → See same workout
3. Device A: Modify workout → Push
4. Device B: Pull → See updated workout

### Offline Scenario

1. Go offline
2. Create/modify workouts (stored locally)
3. Come back online
4. Push syncs to remote
5. Other devices pull to see changes

## Testing Backends

### Test GitHub API

```bash
# With a real GitHub repository
# 1. Create a test repository on GitHub
# 2. Generate a fine-grained PAT
# 3. Open Settings, configure:
#    - URL: https://github.com/yourname/test-repo.git
#    - Username: your-github-username
#    - Token: ghp_...
# 4. Click "Test Connection"
```

### Test git-protocol (localhost)

```bash
# Start local git server
npm run git-server

# In another terminal, start cors-anywhere
npm run cors-proxy

# Open Settings and configure:
# - URL: git://localhost:8888/test-repo.git
# - Backend: auto (or select git-protocol)
# - Click "Test Connection"
```

## Error Handling

### Common Issues

**"CORS error"**
- Solution 1: Use GitHub API backend for GitHub repositories
- Solution 2: Start cors-anywhere proxy and configure in settings
- Solution 3: For self-hosted, configure CORS headers on server

**"Authentication failed"**
- Check token is correct
- For GitHub: Token must have at least `Contents: Read and write`
- For git-protocol: Check username and token match repository credentials
- Regenerate token if expired

**"Repository not found"**
- Verify repository URL is correct
- Check repository is public (or token has access)
- For self-hosted: Verify git server is running

**"Connection refused"**
- For localhost: Start `npm run git-server`
- For localhost with git-protocol: Start `npm run cors-proxy`
- For remote: Check network connectivity

**"Unrelated histories"**
- This happens when pulling into a fresh repository
- Backup your local workouts first
- Use Settings → "Reset repository"
- Then pull again

### See Also

- [GIT_SYNC_TROUBLESHOOTING.md](./GIT_SYNC_TROUBLESHOOTING.md) - Detailed troubleshooting
- [CORS_PROXY_SETUP.md](../docs/CORS_PROXY_SETUP.md) - cors-anywhere setup guide

## API Reference

### Core Functions

All functions are in `mobile-app/src/git-sync-v2.js`:

```javascript
// Initialize git system
await initGit()

// Test connection to remote
const result = await testConnection()
// Returns: { ok: true|false, message: string }

// Push local changes
const result = await push()
// Returns: { ok: true|false, message?: string }

// Pull remote changes
const result = await pull()
// Returns: { ok: true|false, message?: string }

// Save workout locally
const filename = await saveWorkout(dateStr, content)

// Load workout locally
const content = await loadWorkout(filename)

// List workouts
const files = await listWorkouts()

// Get backend info
const info = getBackendInfo()
```

### Settings API

```javascript
// Load settings
const settings = loadSettings()

// Save settings
saveSettings({
  remoteUrl: 'https://...',
  username: 'username',
  token: 'token...',
  author: 'Name',
  backend: 'auto'
})
```

## Performance

- **Initial sync:** ~1-2 seconds (depending on repository size)
- **Incremental sync:** ~500ms (single file)
- **Conflict resolution:** ~100ms (detection)
- **Token validation:** ~100ms (API test)

## Browser Compatibility

- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support (iOS 12+)
- Internet Explorer: Not supported

## Security

### What's Secure

✓ Tokens never persisted to disk  
✓ Tokens cleared on session end  
✓ GitHub API uses Basic Auth over HTTPS  
✓ All operations use HTTPS when available  
✓ git-protocol can use SSH keys  

### What to Know

⚠ Tokens are in browser memory (accessible to malicious scripts)  
⚠ LocalStorage is not encrypted  
⚠ CORS proxy runs on your machine (can see traffic)  
⚠ Clear browser cache to remove old settings  

### Best Practices

1. Use fine-grained tokens (not classic PATs)
2. Rotate tokens every 90 days
3. Review repository access regularly
4. Use HTTPS for all URLs
5. Close browser tab when done (clears tokens)
6. Never commit tokens to git

## Advanced Configuration

### CORS Proxy for git-protocol

If using git-protocol from a web context:

```javascript
// In settings
{
  backend: 'git-protocol',
  corsProxyUrl: 'http://localhost:8081'
}
```

See [CORS_PROXY_SETUP.md](../docs/CORS_PROXY_SETUP.md) for setup instructions.

### Custom Author Name

Commits will be attributed to this name:

```javascript
// In settings
{
  author: 'Your Name'
}
```

### Fallback Backends

The system automatically falls back if primary backend fails:

```
GitHub API fails → Try git-protocol
git-protocol fails → Report error
```

You can see which backend is active in Settings → "Backend Info".

## Frequently Asked Questions

**Q: Can I use the same repository on multiple devices?**  
A: Yes! Each device syncs independently. Create workflow where Device A pushes, then Device B pulls.

**Q: Can two devices edit the same file simultaneously?**  
A: No, conflict detection will alert you. Resolve by choosing one version and re-syncing.

**Q: What happens if I lose internet while editing?**  
A: Your edits are saved locally. When you come back online, push to sync.

**Q: How do I switch backends?**  
A: Open Settings and change the "Backend" dropdown. System will re-test connection.

**Q: Can I use both GitHub API and git-protocol for the same repo?**  
A: Yes! For GitHub repos, GitHub API is primary with git-protocol fallback.

**Q: Is my data private?**  
A: Only if your repository is private and you keep your token secure.

**Q: What if I forget my token?**  
A: Regenerate it at https://github.com/settings/tokens and update in Settings.

## Support

For issues:
1. Check [GIT_SYNC_TROUBLESHOOTING.md](./GIT_SYNC_TROUBLESHOOTING.md)
2. Review [CORS_PROXY_SETUP.md](../docs/CORS_PROXY_SETUP.md) if using git-protocol
3. Check browser console for error messages
4. Verify settings in Settings → "Backend Info"

## See Also

- [GIT_SYNC_TROUBLESHOOTING.md](./GIT_SYNC_TROUBLESHOOTING.md) - Detailed troubleshooting guide
- [docs/CORS_PROXY_SETUP.md](../docs/CORS_PROXY_SETUP.md) - CORS proxy setup
- [mobile-app/src/git-sync-v2.js](./src/git-sync-v2.js) - Main module
- [mobile-app/src/git-sync-factory.js](./src/git-sync-factory.js) - Backend selection logic
