# PWA Git Sync and Save Guide

## Overview

The PWA includes built-in git synchronization allowing you to:
1. **Save** workouts locally with both original text and generated JSON
2. **Push** (Sync) saved workouts to a remote repository
3. **Pull** latest workouts from remote repository
4. View and load past workouts from local history

## Setup

### Enable Git Sync

1. Click the **⚙️ Settings** button (top right)
2. Configure:
   - **Remote URL**: Your git repository URL (e.g., `https://github.com/username/training-workouts.git`)
   - **Username**: Your GitHub username (or git username)
   - **Token**: GitHub personal access token (with `repo` scope)
   - **Author Name**: Name for git commits (default: "Training Parser")

3. Click **Save Settings**

The Save, Pull, and Push buttons will appear once configured.

## Workflow

### 1. Enter and Parse Workout

```
Input date and workout text → Click Parse
```

Example:
```
2025-09-25

bench press: 4x75, 5x75
squat: 5x5x95, 3x8x85
```

### 2. Save to Local Repository

**Click 💾 Save** to:
- Save original workout text (as entered)
- Generate and save JSON envelope with:
  - Set-centric JSON payload
  - Exercise data
  - Totals and statistics
  - Timestamp
- Create a local git commit
- File named: `YYYY-MM-DD.json`

Status: "Saved to local repo (push to sync)"

### 3. Push to Remote Repository

**Click ↑ Push** to:
- Upload local commits to remote git repository
- Sync across devices
- Create backup in the cloud

Status: "✓ Pushed to remote"

### 4. Pull from Remote Repository

**Click ↓ Pull** to:
- Download latest commits from remote
- Get workouts saved on other devices
- Merge changes

Status: "✓ Pulled from remote"

## Saved File Format

When you click **Save**, a JSON file is created containing:

```json
{
  "date": "2025-09-25",
  "original_text": "bench press: 4x75, 5x75\nsquat: 5x5x95, 3x8x85",
  "generated_json": {
    "payload": {
      "type": "workout",
      "date": "2025-09-25",
      "workout_id": "unique-id",
      "exercises": [
        {
          "name": "bench press",
          "sets": [
            { "repetitions": 4, "weight": { "amount": 75, "unit": "kg" } },
            { "repetitions": 5, "weight": { "amount": 75, "unit": "kg" } }
          ]
        }
      ],
      "totals": { ... }
    }
  },
  "timestamp": "2025-09-25T14:30:45.123Z"
}
```

### Key Sections

- **original_text**: Exact workout text as you entered it
- **generated_json**: Full parsed data with statistics
  - `exercises`: Array of exercise objects
  - `sets`: Individual sets with reps and weight
  - `totals`: Total volume, exercise count, etc.

## History

The **Workout History** section (below results) shows:
- All saved workouts in reverse chronological order
- Click any entry to load it
- Shows date as filename (e.g., "2025-09-25")

When loaded, the:
- Original workout text is restored
- Results are re-calculated from JSON
- You can re-export or edit and re-save

## Offline Usage

### Save Without Remote

You can click **Save** even without configuring a remote. Workouts save to local storage, but won't sync to other devices or the cloud.

### Auto-Sync When Online

If configured for remote sync:
- Clicking **Save** creates a local commit (offline-safe)
- When you return online, click **Push** to upload
- Status updates to show sync state

## Advanced: Repository Setup

### GitHub Example

1. Create a repository: `training-workouts`
2. Initialize with empty README
3. Get HTTPS URL: `https://github.com/username/training-workouts.git`
4. Create personal access token:
   - Settings → Developer Settings → Personal Access Tokens
   - Scope: `repo` (full control of private repositories)
5. Use in PWA settings:
   - **Remote URL**: `https://github.com/username/training-workouts.git`
   - **Username**: `username`
   - **Token**: `ghp_xxxxxxxxxxxxx`

### Self-Hosted Git

Works with any git HTTP backend:
```
Remote URL: https://git.example.com/training.git
Username: your-git-user
Token: your-access-token
```

## Troubleshooting

### "Git not configured" Message

- Click ⚙️ Settings
- Verify Remote URL is set
- Click Save Settings
- Buttons should appear

### Push/Pull Fails

**Common issues:**
- Token expired or incorrect
- Wrong repository URL
- No internet connection
- Repository not initialized

**Fix:**
1. Verify credentials in Settings
2. Test with simple SSH command: `git ls-remote <url>`
3. Check repository on GitHub has branch `main`

### Can't Find Saved Workout

1. Click **Pull** to sync from remote first
2. Check **Workout History** section
3. Verify date in workout input

### Sync Conflicts

If working from multiple devices:
- **Recommended**: Each device saves to different dates/sessions
- **Or**: Pull before making changes to sync latest
- isomorphic-git handles merge automatically

## Tips

### Backup Strategy

1. Save regularly (after each workout)
2. Push to remote when online
3. Workouts preserved on GitHub even if local storage cleared

### Batch Operations

- Save multiple workouts, then Push once
- Or Pull multiple times to sync entire history

### Export Options

- **⬇ Download JSON**: Get current parsed result as JSON file
- **↗ Share**: Share results via URL (if available)
- **📋 Copy**: Copy TSV to clipboard for spreadsheet

### Multi-Device Sync

1. Device A: Save workouts, click Push
2. Device B: Click Pull to get them
3. Continue working on either device, keep pushing/pulling

## File Storage

Workouts stored in:
- **Browser**: IndexedDB via LightningFS
- **Remote**: Git repository on GitHub/self-hosted
- **Local files**: Use ⬇ Download to export

Files persist until:
- Browser storage is cleared
- 30-50MB quota exceeded (depending on browser)
- Explicitly deleted
