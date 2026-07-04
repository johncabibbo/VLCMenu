# VLC Menu

**Version:** 2.90
**Last Updated:** Mar 27, 2026
**Maintainer:** Cloud Box 9 Inc.

---

## Overview

VLC Menu is a JSON-driven terminal application for Mac that lets you quickly launch curated VLC playlists from named profiles, then control playback from the command line without touching the mouse.

## Quick Start

```bash
cd ~/Documents/script/VLC
python3 vlcmenu.py
```

## Requirements

- macOS (AppleScript required)
- Python 3.10+
- VLC installed at `/Applications/VLC.app`
- CB9Lib (`~/Documents/script/CB9Lib`)
- External drive/volume mounted with media files

## Files

| File | Description |
|------|-------------|
| `vlcmenu.py` | Main script |
| `vlcmenuConfig.json` | Profiles, paths, and settings |

## Workflow

```
Launch → VLC Running Check → Profile Menu → Load Playlist → Management Mode
```

1. **VLC Check** — If VLC is already running, jump straight to Management Mode or stop it and pick a new playlist.
2. **Profile Menu** — Arrow keys or number to pick a playlist profile.
3. **Playlist Loads** — VLC opens (or reloads) with media files from the selected folders.
4. **Management Mode** — Control playback, delete/fav/save files, seek forward/back, shuffle.

## Key References

- Full usage: `USER_MANUAL.md`
- Keyboard shortcuts: `QUICK_REFERENCE.md`
- Version history: `CHANGE_LOG.md`
- Technical details: `PROJECT_INFO.md`
- Config format: See `USER_MANUAL.md` → Configuration

---
*Copyright © 2026 Cloud Box 9 Inc. All rights reserved.*
