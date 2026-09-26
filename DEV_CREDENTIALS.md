# Development Credentials Setup

This guide explains how to configure git credentials for PWA testing.

## Quick Start

1. **Copy the template**:
   ```bash
   cp .env.local.example .env.local
   ```

2. **Edit `.env.local`** with your credentials:
   ```
   GITHUB_URL=https://github.com/YOUR_USERNAME/YOUR_REPO.git
   GITHUB_USER=YOUR_USERNAME
   GITHUB_TOKEN=ghp_XXXXXXXXXXXXXXXXXXXX
   ```

3. **Start the development server**:
   ```bash
   make pwa-serve
   ```

4. **Open PWA**: http://localhost:8080

5. **Open Settings** → credentials are automatically pre-filled → **Test Connection**

Configuration is automatically loaded from `.env.local` by the development server.

## Available Configuration Variables

Add any of these to `.env.local`:

### GitHub
```
GITHUB_URL=https://github.com/YOUR_USERNAME/YOUR_REPO.git
GITHUB_USER=YOUR_USERNAME
GITHUB_TOKEN=ghp_XXXXXXXXXXXXXXXXXXXX
```

Get token: https://github.com/settings/tokens
- Scopes: `repo`, `read:user`

### GitLab
```
GITLAB_URL=https://gitlab.com/YOUR_USERNAME/YOUR_REPO.git
GITLAB_USER=YOUR_USERNAME
GITLAB_TOKEN=glpat_XXXXXXXXXXXXXXXXXXXX
```

Get token: https://gitlab.com/-/profile/personal_access_tokens
- Scopes: `api`, `read_repository`

### Private Git Server
```
PRIVATE_GIT_URL=https://your-git-domain.com/repo.git
PRIVATE_GIT_USER=your_username
PRIVATE_GIT_TOKEN=your_token_or_password
```

### Local Test Server
```
LOCAL_GIT_SERVER_URL=http://localhost:8888/test-repo.git
LOCAL_GIT_SERVER_USER=test
LOCAL_GIT_SERVER_TOKEN=test
```

## How It Works

### Setup Phase (One-time)
1. Developer copies `.env.local.example` to `.env.local`
2. Adds credentials to `.env.local`

### Runtime Phase
1. Developer runs `make pwa-serve` (development server)
2. Server reads `.env.local` and injects configuration into index.html
3. PWA automatically loads configuration on startup
4. Settings modal shows pre-filled credentials
5. Developer tests connection or proceeds with sync

### Storage
- Credentials stored in **localStorage** (browser)
- Persists across page reloads
- Single browser only (private)
- Can be cleared with `Config.clear()`
- Injected config cleared from memory after loading for security

## Developer Console Commands

Configuration is automatically loaded from `.env.local`. For manual adjustments in the browser console:

```javascript
// View current configuration
Config.export()

// Clear all stored configuration (to reset)
Config.clear()

// Set individual value manually (not recommended - use .env.local instead)
Config.set('git_url', 'https://github.com/user/repo.git')

// Get individual value
Config.get('git_url')

// Get all git settings as object
Config.getGitSettings()

// Reload page (after editing .env.local)
location.reload()
```

**Note:** Configuration is loaded by the development server from `.env.local` when you start `make pwa-serve`. Manual console entry is not needed in normal workflow.

## Security Considerations

### ✓ Safe
- Credentials loaded at startup from `.env.local` (server-side)
- `.env.local` is in .gitignore (never committed)
- Injected config cleared from window after loading
- Only affects single browser session
- Local development only

### ⚠️ Be Careful
- Browser developer tools expose localStorage
- Don't share browser screen/recording with credentials loaded
- Clear config when done: `Config.clear()`
- Use read-only tokens when possible (scope limits)
- `.env.local` contains secrets - keep it private

## Workflow Example

```bash
# 1. Copy template
cp .env.local.example .env.local

# 2. Create GitHub personal access token
# https://github.com/settings/tokens → Generate new token
# Scopes: repo, read:user

# 3. Edit .env.local with your credentials
GITHUB_URL=https://github.com/alvarogarcia7/training-data.git
GITHUB_USER=alvarogarcia7
GITHUB_TOKEN=ghp_YOUR_TOKEN_HERE

# 4. Start development server
make pwa-serve

# 5. Open http://localhost:8080
# 6. Open Settings modal → credentials already filled automatically
# 7. Click "Test Connection" → should succeed
# 8. Proceed with git sync
```

## Troubleshooting

### "Configuration not loading"
- Check that `.env.local` exists (not `.env.local.example`)
- Restart the development server: `make pwa-serve`
- Check browser console for logs: `[Config] Environment configuration loaded`

### Settings not pre-filling
- Verify `.env.local` has correct format: `KEY=VALUE`
- Check server logs for parsing errors
- Open Settings *after* page fully loads
- Try refresh: `location.reload()`

### "Failed to connect" after credentials load
- Verify token is valid: check git server access from terminal
- Check CORS proxy is running: `make pwa-cors-proxy`
- For GitHub: requires CORS proxy, can't use direct access from localhost

### Token exposed in git history
- `.env.local` is in .gitignore, won't be committed
- If accidentally committed: rotate the token immediately
- Tokens are masked in `Config.export()` output (first 10 chars only)

## Testing Different Scenarios

### Local Test Server (no auth)
Edit `.env.local`:
```
LOCAL_GIT_SERVER_URL=http://localhost:8888/test-repo.git
LOCAL_GIT_SERVER_USER=test
LOCAL_GIT_SERVER_TOKEN=test
```
Restart server, open PWA → credentials auto-filled.

### GitHub (public repo, needs auth for pushes)
```
GITHUB_URL=https://github.com/alvarogarcia7/training-data.git
GITHUB_USER=alvarogarcia7
GITHUB_TOKEN=ghp_YOUR_TOKEN
```
Restart server, open PWA → credentials auto-filled.

### GitLab (private repo)
```
GITLAB_URL=https://gitlab.com/your_username/your_repo.git
GITLAB_USER=your_username
GITLAB_TOKEN=glpat_YOUR_TOKEN
```
Restart server, open PWA → credentials auto-filled.

## How Configuration Loading Works

1. **Development Server** (`serve.py`):
   - Reads `.env.local` on each request for index.html
   - Parses KEY=VALUE pairs (skips comments and empty lines)
   - Maps environment variables to app keys:
     - `GITHUB_*` → `git_url`, `git_user`, `git_token`
     - `GITLAB_*` → same mapping
     - `LOCAL_GIT_SERVER_*` → same mapping
   - Injects configuration into `index.html` as JavaScript

2. **PWA Startup** (`ui.js` init):
   - Calls `autoLoadConfig()` on page load
   - Detects injected configuration
   - Loads values into `localStorage` via `Config` module
   - Clears injected config from memory for security

3. **Settings Modal** (`openSettings()`):
   - Reads from both saved settings (git-sync) and environment config
   - Pre-fills form fields with loaded credentials
   - Shows "Configuration loaded from environment" indicator

Benefits:
- ✅ No manual console commands needed
- ✅ Secure - server-side injection, cleared after loading
- ✅ Easy - edit `.env.local`, restart server, credentials auto-load
- ✅ Safe - won't be committed, cannot be executed by users
- ✅ User-proof - not dependent on user manually entering config
