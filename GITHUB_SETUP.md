# GitHub Repository Setup for PWA Sync

## The "Could not find main" Error

**Error message:**
```
Sync failed: Could not find main.
Branch not found on remote. Create the repository with a README on GitHub first.
```

This happens when your GitHub repository doesn't have a `main` branch yet.

## Quick Fix

### Option 1: Create Repository Correctly (Recommended)

1. **Go to GitHub** → New Repository
2. **Name it**: `training-workouts` (or your choice)
3. **Important:** Check "Initialize this repository with a README"
4. Click **Create repository**

✅ This automatically creates the `main` branch.

### Option 2: Fix Existing Empty Repository

If you already created an empty repo, initialize it locally:

```bash
# Clone the empty repository
git clone https://github.com/USERNAME/training-workouts.git
cd training-workouts

# Create initial commit with README
echo "# Training Workouts" > README.md
git add README.md
git commit -m "Initial commit"
git push -u origin main
```

Then try syncing again in PWA.

### Option 3: Fallback to master Branch

If your repo uses `master` instead of `main`:

The PWA will automatically detect and use `master` if `main` doesn't exist.

**However**, GitHub's default is now `main`, so Option 1 is recommended.

## Step-by-Step Setup

### 1. Create GitHub Repository

```
GitHub → + → New repository
├─ Repository name: training-workouts
├─ ✓ Initialize with README
└─ Create repository
```

### 2. Get Your Credentials

**Repository URL:**
```
https://github.com/USERNAME/training-workouts.git
```

**Personal Access Token:**
1. GitHub → Settings → Developer Settings → Personal access tokens
2. Click "Tokens (classic)"
3. "Generate new token" → "Generate new token (classic)"
4. Give it:
   - Name: `Training Parser PWA`
   - Expiration: 90 days (or no expiration)
   - Scope: ✓ `repo` (full control)
5. Click "Generate token"
6. **Copy the token immediately** (won't show again!)

### 3. Configure PWA

In the Training Parser PWA:

1. Click **⚙️ Settings** (top right)
2. Fill in:
   - **Remote URL**: `https://github.com/USERNAME/training-workouts.git`
   - **Username**: `USERNAME` (your GitHub username)
   - **Token**: `ghp_xxxxxxxxxxxxx` (paste your token)
   - **Author**: Your name
3. Click **Save Settings**

### 4. Test Sync

1. **Enter a workout**:
   ```
   2025-09-25

   bench press: 4x75kg
   squat: 5x95kg
   ```

2. **Click Parse** → Should show exercises

3. **Click 💾 Save** → Status: "Saved to local repo (push to sync)"

4. **Click ↑ Push** → Status: "✓ Pushed to remote"

5. **Check GitHub** → File `2025-09-25.json` should appear in repo

✅ Success!

## Common Issues

### "Branch not found on remote"

**Cause:** Repository is empty (no initial commit).

**Fix:**
- Add README.md and push from computer (Option 2 above)
- Or recreate repository with README checkbox

### Push fails with "authentication failed"

**Cause:** Wrong username, token expired, or token doesn't have `repo` scope.

**Fix:**
1. Verify token has `repo` scope
2. Generate new token if expired (3+ months old)
3. Check username is exactly right
4. No spaces in token when pasting

### Pull says "Nothing to pull"

**Cause:** Repository is empty (no workouts pushed yet).

**Fix:**
- Push from this device first
- Or push from another device first, then pull

### Wrong branch (master vs main)

**Cause:** Repository uses `master` not `main`.

**Status:** PWA now auto-detects this ✓ (as of latest update)

**If still failing:**
- Rename branch on GitHub: Settings → Branches → Rename default branch to `main`
- Or update PWA settings to use correct repo

## Token Security

### ⚠️ Important
- **Don't share** your GitHub token
- **Keep it secret** like a password
- **Regenerate** if exposed
- **Expire tokens** after 90 days

### Token Scopes
- ✓ `repo` - Full control (needed for sync)
- ✓ `read:user` - Optional (read profile)
- ❌ Not needed: `delete_repo`, `admin`, `gist`

## Multiple Devices

### Device A (has workouts)
```
1. Configure PWA with repo URL, username, token
2. Enter and Parse workout
3. Click 💾 Save
4. Click ↑ Push
```

### Device B (wants workouts)
```
1. Same configuration as Device A
2. Click ↓ Pull
3. Workouts appear in History
4. Click to load any workout
```

## Backup Strategy

Your GitHub repository is a **complete backup**:
- ✅ All workouts saved
- ✅ Full history (git commits)
- ✅ Accessible from GitHub web interface
- ✅ Can download anytime

You can even:
- View on GitHub web
- Download as `.json` files
- Clone to computer
- Set up GitHub Pages for public display

## File Structure

After first push, your GitHub repo looks like:

```
training-workouts/
├── README.md
├── 2025-09-25.json    ← Your first workout
├── 2025-09-26.json    ← Your second workout
└── ...
```

Each `.json` file contains complete workout data.

## Advanced: Private vs Public

### Private Repository
- Default: Only you can see
- Secure: Your data isn't public
- Good for: Personal workouts
- (Recommended)

### Public Repository
- Anyone can view on GitHub
- Can set up GitHub Pages
- Good for: Sharing training programs
- Decide at repo creation

To change later:
- GitHub → Settings → Change repository visibility

## Troubleshooting Steps

1. **Verify repository exists** and has README
   ```
   Check: https://github.com/USERNAME/training-workouts
   Should see README.md file
   ```

2. **Test token with curl** (if you know terminal)
   ```bash
   curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user
   ```

3. **Check branch exists**
   ```
   GitHub → Code tab → Branch selector
   Should show "main" branch
   ```

4. **Test clone locally** (if you know git)
   ```bash
   git clone https://github.com/USERNAME/training-workouts.git
   # If this works, PWA should work too
   ```

5. **Check PWA settings** are saved
   - Click ⚙️
   - Verify all fields filled
   - Click Save again if not visible

## Getting Help

If still stuck:

1. **Verify repository is initialized:**
   - Go to GitHub repo page
   - Should see README.md file
   - Should see "main" branch in selector

2. **Check token scope:**
   - GitHub Settings → Developer Settings → Personal Tokens
   - Find your token → Click it
   - Verify `repo` scope is checked

3. **Check internet connection:**
   - Toggle ↓ Pull button
   - Check browser console (F12 → Console tab)
   - Look for network errors

4. **Try from fresh session:**
   - Clear browser cache
   - Close and reopen PWA
   - Try syncing again
