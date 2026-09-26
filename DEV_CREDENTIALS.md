# Development Credentials Setup

This guide explains how to configure git credentials for PWA testing.

## Quick Start

1. **Edit `.env.local`** with your credentials:
   ```
   GITHUB_URL=https://github.com/YOUR_USERNAME/YOUR_REPO.git
   GITHUB_USER=YOUR_USERNAME
   GITHUB_TOKEN=ghp_XXXXXXXXXXXXXXXXXXXX
   ```

2. **Open PWA**: http://localhost:8080

3. **In browser console**, load the credentials:
   ```javascript
   Config.loadEnvDefaults({
     git_url: 'https://github.com/YOUR_USERNAME/YOUR_REPO.git',
     git_user: 'YOUR_USERNAME',
     git_token: 'YOUR_TOKEN'
   })
   ```

4. **Open Settings** → credentials will be pre-filled → **Test Connection**

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
1. Developer adds credentials to `.env.local`
2. PWA loads, but doesn't have access to .env file (browser security)

### Runtime Phase
1. Developer opens browser console
2. Calls `Config.loadEnvDefaults({...})` with credentials from .env.local
3. Credentials stored in browser localStorage
4. Settings modal shows pre-filled fields
5. Developer tests connection or proceeds with sync

### Storage
- Credentials stored in **localStorage** (browser)
- Persists across page reloads
- Single browser only (private)
- Can be cleared with `Config.clear()`

## Developer Console Commands

```javascript
// Load environment defaults
Config.loadEnvDefaults({
  git_url: 'https://github.com/user/repo.git',
  git_user: 'username',
  git_token: 'token'
})

// View current configuration
Config.export()

// Clear all stored configuration
Config.clear()

// Set individual values
Config.set('git_url', 'https://github.com/user/repo.git')

// Get individual value
Config.get('git_url')

// Get all git settings as object
Config.getGitSettings()
```

## Security Considerations

### ✓ Safe
- Credentials stored in browser localStorage (not sent to server)
- .env.local is in .gitignore (never committed)
- Only affects single browser session

### ⚠️ Be Careful
- Browser developer tools expose localStorage
- Don't share browser screen/recording with credentials loaded
- Clear config when done: `Config.clear()`
- Use read-only tokens when possible (scope limits)

## Workflow Example

```bash
# 1. Create GitHub personal access token
# https://github.com/settings/tokens → Generate new token
# Scopes: repo, read:user
# Copy token to clipboard

# 2. Edit .env.local
echo "GITHUB_TOKEN=ghp_YOUR_TOKEN_HERE" >> .env.local

# 3. Start all services
make setup-local-git-server
make pwa-cors-proxy &
make pwa-serve

# 4. In browser console (developer tools F12)
Config.loadEnvDefaults({
  git_url: 'https://github.com/alvarogarcia7/training-data.git',
  git_user: 'alvarogarcia7',
  git_token: 'ghp_YOUR_TOKEN_HERE'
})

# 5. Open Settings modal → credentials pre-filled
# 6. Click "Test Connection"
# 7. Proceed with git sync
```

## Troubleshooting

### "Config is not defined"
- Make sure you're in the browser console (F12)
- Config is exposed via `window.Config` in mobile-app/src/config.js
- Try: `window.Config.export()`

### Settings not pre-filling
- Check that config values were loaded: `Config.export()`
- Make sure you opened Settings *after* loading config
- Clear and reload: `Config.clear()` then refresh page

### "Failed to connect" after loading config
- Verify token is valid: check git server access from terminal
- Check CORS proxy is running: `make pwa-cors-proxy`
- For GitHub: requires CORS proxy, can't use direct access from localhost

### Token exposed in git history
- .env.local is in .gitignore, won't be committed
- If accidentally committed: rotate the token immediately
- Tokens are masked in Config.export() output

## Testing Different Scenarios

### Local Test Server (no auth)
```javascript
Config.loadEnvDefaults({
  git_url: 'http://localhost:8888/test-repo.git',
  git_user: 'test',
  git_token: 'test'
})
```

### GitHub (public repo, needs auth for pushes)
```javascript
Config.loadEnvDefaults({
  git_url: 'https://github.com/alvarogarcia7/training-data.git',
  git_user: 'alvarogarcia7',
  git_token: 'ghp_YOUR_TOKEN'
})
```

### GitLab (private repo)
```javascript
Config.loadEnvDefaults({
  git_url: 'https://gitlab.com/your_username/your_repo.git',
  git_user: 'your_username',
  git_token: 'glpat_YOUR_TOKEN'
})
```
