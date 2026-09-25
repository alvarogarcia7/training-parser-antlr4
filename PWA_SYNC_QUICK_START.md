# PWA Save & Sync - Quick Start

## Button Layout

```
┌─────────────────────────────────────────────┐
│  Header: ⚙️ Settings         Status: Ready  │
├─────────────────────────────────────────────┤
│                                             │
│  [Parse]  [⬇ Download JSON]                │
│  [💾 Save] [↓ Pull] [↑ Push] [↗ Share]     │
│                                             │
│  Workout History Section (shows saved      │
│  workouts - click to load)                  │
└─────────────────────────────────────────────┘
```

## Typical Workflow

### First Time Setup

```
1. Click ⚙️ Settings
   ├─ Enter Remote URL: https://github.com/you/training.git
   ├─ Enter Username: your-github-username
   ├─ Enter Token: ghp_xxxxxxxxxxxxx
   └─ Click "Save Settings"
```

### Save and Sync Workout

```
2. Enter date and workout text
   └─ Example: "2025-09-25\nbench press: 4x75kg"

3. Click Parse
   └─ Validates and generates JSON

4. Click 💾 Save
   └─ Saves BOTH text and JSON to local git
   └─ Status: "Saved to local repo (push to sync)"

5. Click ↑ Push
   └─ Uploads to GitHub/remote repository
   └─ Status: "✓ Pushed to remote"

6. (Optional) Click ↓ Pull
   └─ Syncs workouts from other devices
   └─ Updates history section
```

## File Saved to Remote

When you click **💾 Save**, this is created:

**File**: `2025-09-25.json`

**Contents**:
```json
{
  "date": "2025-09-25",
  "original_text": "bench press: 4x75kg",
  "generated_json": {
    "payload": { ... }
  },
  "timestamp": "2025-09-25T14:30:45Z"
}
```

✅ Original text preserved
✅ Full JSON with exercises
✅ Timestamp for tracking

## Common Actions

### Load Past Workout

```
1. Check "Workout History" section (below results)
2. Click any date (e.g., "2025-09-25")
3. Original text is restored
4. Results are recalculated
```

### Sync Across Devices

```
Device A:
  1. Click 💾 Save
  2. Click ↑ Push

Device B:
  1. Click ↓ Pull
  2. Check "Workout History"
  3. Click workout to load
```

### Export Workout

```
After parsing:
- [⬇ Download JSON] - Downloads JSON file
- [📋 Copy] - Copies TSV to clipboard
- [↗ Share] - Shares via link
```

## Status Messages

| Message | Meaning | Action |
|---------|---------|--------|
| "Saved to local repo (push to sync)" | Saved locally | Click ↑ Push when ready |
| "✓ Pushed to remote" | Synced to GitHub | Done! Other devices can pull |
| "✓ Pulled from remote" | Downloaded updates | Check history for new workouts |
| "Git not configured" | Settings incomplete | Click ⚙️ to configure |
| "Offline" | No internet | Can still save locally |
| "Back online — syncing..." | Reconnected | Auto-syncing |

## What Gets Saved

### 💾 Save Button Saves:
- ✅ Original workout text (exactly as you typed)
- ✅ Date
- ✅ Complete parsed JSON with:
  - All exercises
  - All sets with reps and weights
  - Volume calculations
  - Total statistics
- ✅ Timestamp when saved

### What Gets Synced:
- ✅ All saved workouts in `YYYY-MM-DD.json` format
- ✅ Git commit history (who saved, when)
- ❌ Browser local storage (not synced)
- ❌ Settings (keep separately on each device)

## No Remote? No Problem

Even without configuring a remote:
- ✅ Click 💾 Save to save locally
- ✅ Click to load from history
- ✅ Download JSON for export
- ❌ Can't sync to other devices

## Tips

### Best Practice
```
After each workout:
1. Parse
2. Review results
3. Click 💾 Save
4. (When online) Click ↑ Push
```

### Multi-Device
```
Before working on new device:
1. Click ⚙️ configure remote
2. Click ↓ Pull (get all past workouts)
3. Start typing new workout
```

### Backup
```
GitHub = automatic backup
Local history = 30-50MB storage
Annual backup = Click [⬇ Download JSON] for each
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Buttons not showing | Click ⚙️ to configure remote URL, username, token |
| Push fails | Check internet, verify GitHub token is valid |
| Can't find workout | Click ↓ Pull first to sync from remote |
| Local storage full | Download JSON backups and clear history |
| Lost data | Stored on GitHub! Click ↓ Pull to recover |

## Next Steps

- Read **PWA_SYNC_GUIDE.md** for detailed documentation
- Check GitHub repository for all saved workouts
- Set up on multiple devices and start syncing!
