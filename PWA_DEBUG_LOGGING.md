# PWA Debug Logging Guide

## How to Access Logs

The PWA now includes detailed logging to help diagnose sync issues.

### Step 1: Open Developer Tools

**Windows/Linux:**
- Click in the PWA window
- Press **F12**

**Mac:**
- Click in the PWA window
- Press **Cmd + Option + I**

**Or manually:**
- Right-click in the app
- Select **Inspect** or **Inspect Element**

### Step 2: Go to Console Tab

In Developer Tools:
1. Click the **Console** tab (usually on the right or bottom panel)
2. You should see a prompt like `> ` at the bottom

### Step 3: Trigger the Action

In the PWA:
1. Create a workout and Parse it
2. Click **💾 Save** or **↑ Push** or **↓ Pull**

### Step 4: Read the Logs

Look in the console for log messages starting with:
- `[git-sync]` - git operations
- `[ui]` - user interface actions

Scroll up in the console to see all messages from the operation.

## Understanding the Logs

### Log Format

```
[component:function] Message details
```

Example:
```
[git-sync:push] Starting push operation
[git-sync:push] Remote URL: https://***@github.com/user/repo.git
[git-sync:push] Username: user
[git-sync:push] Adding remote origin
[git-sync:push] Remote added successfully
[git-sync:push] Current branch detected: main
[git-sync:push] Attempting push to branch: main
[git-sync:push] First attempt: push as-is
[git-sync:push] Auth requested for user: user
[git-sync:push] Push successful on first attempt
```

### Log Levels

- **Info** `[component]` - Normal operation, no error
- **Warning** `⚠️` - Something unexpected but operation continues
- **Error** `❌` - Operation failed
- **Log** - Standard output (appears as plain text)

### Common Log Sequences

#### Successful Save
```
[ui:saveWorkout] Save button clicked
[ui:saveWorkout] Date: 2025-09-25 Exercises: 3
[ui:saveWorkout] Calling serialize worker
[ui:saveWorkout] Initializing git
[git-sync:init] Initializing git
[git-sync:init] Creating LightningFS instance
[git-sync:init] Directory already exists
[git-sync:init] Repository already exists
[git-sync:init] Git initialization complete
[ui:saveWorkout] Saving workout to git
[git-sync] Writing file: /workout-data/2025-09-25.json
[git-sync] File written successfully
[git-sync] Adding to git: 2025-09-25.json
[git-sync] Committing...
[git-sync] Commit successful
[ui:saveWorkout] Save successful
```

#### Successful Push
```
[ui:syncNow] Push button clicked
[ui:syncNow] Starting push to remote
[git-sync:push] Starting push operation
[git-sync:push] Remote URL: https://***@github.com/***/***.git
[git-sync:push] Adding remote origin
[git-sync:push] Remote added successfully
[git-sync:push] Current branch detected: main
[git-sync:push] Attempting push to branch: main
[git-sync:push] First attempt: push as-is
[git-sync:push] Auth requested for user: username
[git-sync:push] Push successful on first attempt
[ui:syncNow] Push successful
```

#### Push Fails - Empty Repository
```
[git-sync:push] Attempting push to branch: main
[git-sync:push] First attempt: push as-is
[git-sync:push] Auth requested for user: username
[git-sync:push] First push attempt failed: Could not find ref refs/heads/main
[git-sync:push] Branch not found, attempting with force: true
[git-sync:push] Force push failed: Could not find ref refs/heads/main
[git-sync:push] Attempting fallback to master branch
[git-sync:push] All push attempts failed. Master error: Could not find ref refs/heads/master
[git-sync:push] Diagnosis: Repository not initialized or empty
```

#### Push Fails - Authentication Error
```
[git-sync:push] Remote added successfully
[git-sync:push] Adding remote origin
[git-sync:push] First attempt: push as-is
[git-sync:push] Auth requested for user: username
[git-sync:push] First push attempt failed: 403 Unauthorized
[git-sync:push] Diagnosis: Authentication error
```

## Troubleshooting with Logs

### "Could not find main"
Look for:
```
[git-sync:push] Could not find ref refs/heads/main
[git-sync:push] Could not find ref refs/heads/master
[git-sync:push] Diagnosis: Repository not initialized or empty
```

**Fix:** Repository is empty. Create it on GitHub with a README.

### Authentication Failed
Look for:
```
[git-sync:push] 403 Unauthorized
[git-sync:push] Unauthorized (403)
[git-sync:push] Diagnosis: Authentication error
```

**Fix:** Check GitHub token and username. Generate new token if expired.

### CORS Error
Look for:
```
[git-sync:push] CORS error
[git-sync:push] Diagnosis: CORS error
```

**Fix:** Try on different network or WiFi. Contact repo administrator.

### Network Issues
Look for:
```
[git-sync:push] fetch failed: Network error
[git-sync:push] Connection refused
```

**Fix:** Check internet connection. Verify GitHub is accessible.

## Saving Logs for Support

### Copy Logs
1. Select all console text: **Ctrl+A** (Windows) or **Cmd+A** (Mac)
2. Copy: **Ctrl+C** or **Cmd+C**
3. Paste into email or issue

### Export Logs
1. Right-click in console
2. Select **Save as...** (if available)
3. Save as `.txt` file

### Screenshot
1. Press **Print Screen** or **Cmd+Shift+3**
2. Crop the console area
3. Share the image

## Common Diagnosis Patterns

| Pattern | Meaning | Action |
|---------|---------|--------|
| `Could not find ref refs/heads/main` | No main branch on remote | Add README to GitHub repo |
| `Could not find ref refs/heads/master` | No master branch on remote | Push from computer first |
| `403 Unauthorized` | Authentication failed | Regenerate GitHub token |
| `no matching push spec` | Repository doesn't exist | Verify repo URL |
| `CORS error` | Cross-origin request blocked | Try different network |
| `Directory already exists` | Repo already initialized | Normal, can ignore |
| `Repository already exists` | Git already set up | Normal, can ignore |
| `Pull successful` / `Push successful` | Operation succeeded | Check GitHub or history |

## Advanced: Filtering Logs

### Only Git Sync
Type in console:
```javascript
console.log('Showing only git-sync logs');
```

Or paste filters into console to only see specific logs:
```javascript
// Clear and show only push attempts
console.clear();
// Then trigger push button
```

### Find Errors Only
Use browser search (Ctrl+F or Cmd+F) in console for:
- "Error"
- "failed"
- "Unauthorized"
- "Could not find"

## Sharing Logs for Help

When asking for help, include:

1. **Full console log** from the action that failed
2. **What you were trying to do** (Save/Push/Pull)
3. **Your repository URL** (without token!)
4. **Your GitHub username**
5. **Error message** shown in PWA status

Example:
```
Trying to push, getting: "Sync failed: Could not find main"

Console shows:
[git-sync:push] Could not find ref refs/heads/main
[git-sync:push] Could not find ref refs/heads/master
[git-sync:push] Diagnosis: Repository not initialized or empty

Repository: https://github.com/username/training-workouts
Username: username
```

## Privacy Note

The logs do NOT include:
- ❌ Your GitHub token
- ❌ Your password
- ❌ File contents (only filenames)

The logs mask sensitive info:
```
Remote URL: https://***@github.com/user/repo.git  # Token hidden
```

Safe to share logs publicly!

## Frequently Asked Diagnostic Questions

**Q: How do I know if push is working?**
A: Look for `[git-sync:push] Push successful` in console

**Q: What does "Auth requested" mean?**
A: PWA is sending your GitHub token. Normal and expected.

**Q: Can I see my file contents in logs?**
A: No, logs only show filenames like `2025-09-25.json`, not contents

**Q: Are logs saved if I close the app?**
A: No, they're cleared when browser closes. Copy them first if needed.

**Q: What's the difference between INFO and ERROR logs?**
A: INFO = normal operation, ERROR = something failed. Look for ERROR if having issues.

**Q: Can logs help fix "Could not find main"?**
A: Yes! If logs show this error, repo is empty. Fix: Add README to GitHub.

## For Developers

To add more logging:
1. Find the function in `git-sync.js` or `ui.js`
2. Add: `console.log('[component:function] message')`
3. Use descriptive messages
4. Follow the naming pattern

Example:
```javascript
console.log('[git-sync:push] Attempting fallback to master');
```
