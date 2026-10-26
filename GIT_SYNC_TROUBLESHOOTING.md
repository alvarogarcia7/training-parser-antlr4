# Git Sync Troubleshooting Guide

## "Sync failed: Could not find main" - Deep Dive

### What This Error Means

The PWA tried to push your workout to GitHub, but the remote repository is either:
1. **Empty** (no commits, no branches)
2. **Wrong URL** (points to non-existent repo)
3. **No `main` branch** (uses `master` instead)
4. **Wrong credentials** (authentication failed before branch check)

### Step-by-Step Diagnosis

#### Step 1: Verify Your Repository Exists

```bash
# In your terminal, try this:
git ls-remote https://github.com/USERNAME/training-workouts.git

# Should show something like:
# main  -> refs/heads/main
# If this fails: Repository doesn't exist or URL is wrong
```

**What to check:**
- ✅ Repository exists on GitHub
- ✅ URL is exactly right (copy from GitHub repo page)
- ✅ You have push access (not just read)

#### Step 2: Check if Repository Has Branches

```bash
# If repository exists but is empty, it has NO branches yet
# You'll see:
# (empty repository)

# This is the main cause of "Could not find main"
```

**What to do:**
- Add a README and commit it
- Or let PWA create the branch (latest version does this)

#### Step 3: Verify Your Credentials

```bash
# Test your GitHub token
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user

# Should show your user info
# If 403 Unauthorized: Token is wrong or expired
# If 404: Token doesn't have repo scope
```

**What to check:**
- ✅ Token has `repo` scope
- ✅ Token hasn't expired (3+ months)
- ✅ Token is copied correctly (no extra spaces)
- ✅ Username matches your GitHub username

### Solutions in Order

#### Solution 1: Create Repository With README (Easiest)

On GitHub:
```
1. Create new repository
2. ✅ Check "Initialize with README"
3. Create repo
4. Copy HTTPS URL
5. In PWA: Settings → Paste URL
6. Click Save
7. Try pushing again
```

**Expected result:** ✅ Push succeeds, file appears on GitHub

---

#### Solution 2: Initialize Existing Empty Repository

If you already created an empty repo:

**On your computer:**
```bash
# Clone it first
git clone https://github.com/USERNAME/training-workouts.git
cd training-workouts

# Create a file and push
echo "# Training Workouts" > README.md
git add README.md
git commit -m "Initial commit"
git push -u origin main

# Now the main branch exists!
```

**Then in PWA:**
1. Click Settings
2. Verify URL, username, token
3. Click Save
4. Try pushing again

**Expected result:** ✅ Push succeeds

---

#### Solution 3: Check Your GitHub Token

If other solutions don't work, your token might be invalid:

**Generate new token:**
1. GitHub → Settings → Developer Settings → Personal access tokens
2. Click "Tokens (classic)"
3. "Generate new token" → "Generate new token (classic)"
4. Settings:
   - Name: `training-parser`
   - Expiration: 90 days
   - Scope: ✅ `repo` (required!)
5. **Copy the token immediately**
6. In PWA Settings, paste the new token
7. Click Save
8. Try pushing again

**Expected result:** ✅ Push succeeds

---

#### Solution 4: Verify URL Format

The URL must be exact HTTPS URL from GitHub:

**✅ Correct:**
```
https://github.com/username/training-workouts.git
```

**❌ Wrong:**
```
git@github.com:username/training-workouts.git    # SSH format
https://github.com/username/training-workouts     # Missing .git
https://github.com/username/training-workouts/    # Trailing slash
```

**To get the right URL:**
1. Go to your repo on GitHub
2. Click **Code** (green button)
3. Select **HTTPS**
4. **Copy** the URL
5. Paste into PWA Settings
6. Try pushing again

**Expected result:** ✅ Push succeeds

---

#### Solution 5: Check if Repository is Actually Empty

Your PWA might have unsaved commits locally:

**Save a workout first:**
1. Enter workout text
2. Set date
3. Click **Parse**
4. Click **💾 Save**
5. Status: "Saved to local repo"
6. **Then** click **↑ Push**

**Why this matters:**
- Can't push an empty repo (no commits)
- Must have at least one saved workout
- Push sends your local commits to GitHub

**Expected result:** ✅ Push succeeds, file appears on GitHub

---

### Error Message Guide

| Error | Cause | Solution |
|-------|-------|----------|
| "Could not find main" | Repository empty or doesn't exist | Create repo with README, or push local commits |
| "Authentication failed" | Wrong token, username, or scope | Generate new token with `repo` scope |
| "Unauthorized (403)" | Token expired or insufficient scope | Check token permissions on GitHub |
| "Repository not found (404)" | Wrong URL or private repo you can't access | Verify URL, check you own the repo |
| "Nothing to pull" | Remote repository is empty | Push from this device first |
| "Could not find origin" | Remote URL not configured | Check Settings, verify URL format |

### Checklist for Success

Before pushing, verify:

- [ ] GitHub repo exists at the URL
- [ ] Repo has a README (or is initialized)
- [ ] URL is copied exactly: `https://github.com/USERNAME/repo.git`
- [ ] Username is your GitHub username
- [ ] Token was generated today or recently (not 6+ months ago)
- [ ] Token has `repo` scope
- [ ] You can access the repo on GitHub (not restricted)
- [ ] You have entered a workout in the PWA
- [ ] You clicked **💾 Save** (creates local commit)
- [ ] Status shows "Saved to local repo"

### Still Not Working?

#### Debug Steps

1. **Check browser console:**
   - Open PWA
   - Press **F12** (Developer Tools)
   - Go to **Console** tab
   - Try pushing
   - Look for error messages
   - Screenshot and share

2. **Test with command line:**
   ```bash
   # Can you clone the repo?
   git clone https://USERNAME:TOKEN@github.com/USERNAME/training-workouts.git test-clone

   # Can you push?
   cd test-clone
   echo "test" > test.txt
   git add test.txt
   git commit -m "test"
   git push

   # If these work, but PWA doesn't, it's a PWA issue
   # If these fail, it's a GitHub credentials issue
   ```

3. **Verify GitHub settings:**
   - Go to repo Settings
   - Check "Collaborators" (you should be listed)
   - Check branch protection rules (should allow direct push)
   - Check if repo is archived (can't push to archived repos)

4. **Try a test repo:**
   - Create a new test repository
   - Name it `test-sync`
   - Initialize with README
   - Configure PWA with new URL
   - Try pushing to test repo
   - If this works, main repo has an issue
   - If this fails, credentials are the problem

#### Get Help

If still stuck, provide:
1. Error message from status
2. Browser console errors (F12 → Console)
3. GitHub repo URL (without token!)
4. Results of: `git ls-remote https://github.com/USERNAME/repo.git`
5. Whether you can clone/push from your computer

### Root Causes

**Most Common:**
1. **Empty repository** (70%)
   - Fix: Add README and commit
2. **Token issues** (20%)
   - Fix: Generate new token with `repo` scope
3. **Wrong URL** (5%)
   - Fix: Copy exact URL from GitHub
4. **Authentication failure** (5%)
   - Fix: Verify credentials, check repo access

### Prevention

To avoid this in the future:

1. **Always create repo WITH README**
   - GitHub → New → ✅ "Initialize with README"

2. **Test before using**
   ```bash
   git ls-remote https://github.com/USERNAME/repo.git
   # Should show branches (main, master, etc)
   ```

3. **Keep token fresh**
   - Regenerate every 90 days
   - Never share it
   - Use separate tokens for different apps

4. **Save before push**
   - Enter workout
   - Click Parse
   - Click 💾 Save (crucial!)
   - Click ↑ Push

### Advanced: Repository Initialization

If you want to set up everything on your computer first:

```bash
# Create repo locally
mkdir training-workouts
cd training-workouts
git init

# Add initial files
echo "# Training Workouts" > README.md
git add README.md
git commit -m "Initial commit"

# Connect to GitHub (replace USERNAME and repo name)
git remote add origin https://github.com/USERNAME/training-workouts.git
git branch -M main
git push -u origin main

# Now repo is ready for PWA!
```

Then configure PWA with the repo URL, and you're all set.

### Video Alternative

If command line feels scary:
1. YouTube: "Create GitHub repository with README"
2. YouTube: "Generate GitHub personal access token"
3. Follow along
4. Use your token in PWA

### Questions?

- Is your repo on GitHub?
- Does it have a README file?
- Can you see it in your browser?
- Did you generate a token today?
- Did you copy the HTTPS URL?

If yes to all, PWA should work. If no to any, that's the issue to fix.
