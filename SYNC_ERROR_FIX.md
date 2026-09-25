# Fix for "Sync failed: Could not find main" Error

## Summary

The PWA now has improved error handling and recovery for empty repositories. If you're still seeing this error, follow these steps.

## Quick Fix (2 minutes)

### On GitHub:
1. Go to your repo: `https://github.com/USERNAME/training-workouts`
2. If it says **"This repository is empty"** or shows no files:
   - Click **Add file** → **Create new file**
   - Name it: `README.md`
   - Type: `# Training Workouts`
   - Commit with: `Initial commit`
   - Push directly (default branch option)
3. Wait 5 seconds for page to refresh

### In PWA:
1. Go to **⚙️ Settings**
2. Verify:
   - **Remote URL**: `https://github.com/USERNAME/training-workouts.git`
   - **Username**: `USERNAME`
   - **Token**: Your GitHub token
3. Click **Save Settings**
4. Create a workout and try **↑ Push** again

✅ **Should work now!**

---

## What Changed

### Backend Improvements
- **Smarter branch detection**: PWA now tries multiple strategies
  - Use current branch if exists
  - Create branch if it doesn't exist (with `force: true`)
  - Fall back to `master` if `main` fails
- **Better error messages**:
  - Tells you to create repo with README
  - Distinguishes between auth errors and branch issues
  - Suggests specific fixes

### Code Changes
- `git-sync.js`: Enhanced push/pull with fallback logic
- `ui.js`: Improved error message display
- Documentation: Three detailed guides added

---

## Why This Happened

When you create an **empty GitHub repository** (without README):
- GitHub has no initial commit
- No branches exist (`main` or `master`)
- Git operations fail when trying to use non-existent branch
- PWA threw confusing error

## How to Avoid It

**Create GitHub repos with README:**
```
GitHub → New repository
├─ Repository name: training-workouts
├─ ✅ Initialize with README  ← IMPORTANT
└─ Create repository
```

This automatically:
- ✅ Creates `main` branch
- ✅ Adds README.md commit
- ✅ Makes repo ready for sync

## Documentation

Three guides are now available:

### 1. **GITHUB_SETUP.md** - Start Here
- Step-by-step GitHub repo setup
- How to generate GitHub token
- Configure PWA settings
- Test your first sync

### 2. **PWA_SYNC_GUIDE.md** - Detailed Reference
- Complete workflow explanation
- Saved file format documentation
- Multi-device sync strategy
- Advanced repository setup

### 3. **GIT_SYNC_TROUBLESHOOTING.md** - If You Get Stuck
- Deep dive into "Could not find main" error
- Step-by-step diagnosis
- Solutions in order of likelihood
- Debug commands to try
- Error message reference

### 4. **PWA_SYNC_QUICK_START.md** - Visual Quick Reference
- Button layouts and workflows
- Status message meanings
- Common actions table
- Multi-device sync example

## Testing It

### Test 1: New Repository (Recommended)
```bash
# Create fresh test repo on GitHub
# Name: test-training-sync
# ✅ Initialize with README
```

Then in PWA:
1. Settings → Enter test repo URL
2. Create workout
3. Parse
4. Save
5. Push
6. ✅ Should succeed

### Test 2: Verify File on GitHub
After push succeeds:
1. Go to: `https://github.com/USERNAME/test-training-sync`
2. Should see your workout file (e.g., `2025-09-25.json`)
3. Click it to view your saved data
4. ✅ Full JSON with exercises, sets, totals

## Common Issues After Fix

| Issue | Fix |
|-------|-----|
| Still says "Could not find main" | Repository is still empty. Add README on GitHub. |
| "Authentication failed" | Token wrong/expired. Generate new token on GitHub. |
| "Nothing to pull" | Repository is empty. Push from this device first. |
| File not appearing | Wait 10 seconds, refresh GitHub page. |
| Different device can't see workouts | Click ↓ Pull on other device after original Push. |

## If You Need More Help

1. **Read:** GIT_SYNC_TROUBLESHOOTING.md (detailed diagnosis)
2. **Check:** Your repository on GitHub
   - Does it have a README?
   - Does it have files?
   - Is it public/accessible?
3. **Test:** Manually clone to verify credentials:
   ```bash
   git clone https://USERNAME:TOKEN@github.com/USERNAME/repo.git
   ```
4. **Debug:** Open browser console (F12) and look for errors

## Files Modified

### Code Changes
- `mobile-app/src/git-sync.js` - Better branch detection and error handling
- `mobile-app/src/ui.js` - Improved error messages

### New Documentation
- `GITHUB_SETUP.md` - Complete GitHub setup guide
- `PWA_SYNC_GUIDE.md` - Detailed sync workflow
- `GIT_SYNC_TROUBLESHOOTING.md` - Deep troubleshooting guide
- `PWA_SYNC_QUICK_START.md` - Quick reference
- `SYNC_ERROR_FIX.md` - This file

## Success Indicators

✅ **Working correctly when:**
- Parse workout → ✓
- Click Save → Status: "Saved to local repo"
- Click Push → Status: "✓ Pushed to remote"
- File appears on GitHub
- On other device: Click Pull → Status: "✓ Pulled from remote"
- History shows your saved workouts

## Next Steps

1. **If error is gone**: Enjoy syncing! 🎉
2. **If error persists**: Read `GIT_SYNC_TROUBLESHOOTING.md`
3. **For details**: Read `GITHUB_SETUP.md` or `PWA_SYNC_GUIDE.md`
4. **For quick ref**: See `PWA_SYNC_QUICK_START.md`

---

**Latest Fix:** Branch detection now automatically handles empty repositories and falls back to `master` if `main` doesn't exist.

**Last Updated:** 2025-09-25

**Status:** ✅ Ready to sync
