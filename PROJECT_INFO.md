# VLC Menu — Project Info

**Version:** 2.90 | **Updated:** Mar 27, 2026

---

## Project Details

| Field | Value |
|-------|-------|
| Script | `vlcmenu.py` |
| Language | Python 3.12 |
| Platform | macOS (AppleScript required) |
| Location | `~/Documents/script/VLC/` |
| Config | `vlcmenuConfig.json` |
| Library | CB9Lib |
| Maintainer | Cloud Box 9 Inc. |

---

## Dependencies

| Dependency | Purpose |
|------------|---------|
| Python 3.10+ | Runtime (`/opt/homebrew/opt/python@3.12/libexec/bin/python3`) |
| VLC for Mac | Media playback (`/Applications/VLC.app`) |
| CB9Lib | UI, colors, config loading, file utilities |
| `osascript` | VLC control via AppleScript |
| Standard library: `subprocess`, `termios`, `tty`, `signal`, `hashlib`, `difflib`, `shutil` | Input, process control, file hashing |

---

## Architecture

```
vlcmenu.py
├── Startup
│   ├── load_paths_config()       — reads vlcmenuConfig.json, sets globals
│   └── check_vlc_and_prompt()   — Menu 1: VLC running?
│
├── interactive_menu()            — Menu 2: Profile Selection
│   ├── display_profiles()        — renders menu with ▶ indicator
│   ├── get_key() / collect_input() — hybrid instant/buffered input
│   ├── run_profile()             — builds XSPF, opens VLC
│   └── duplicate_finder_menu()  — Phase 1 (hash) + Phase 2 (fuzzy)
│
└── management_mode()             — Playback control loop
    ├── display_current_file()   — AppleScript: get VLC current item
    ├── vlc_pause/next/previous/seek/shuffle()  — AppleScript commands
    ├── delete_current_file()    — move to trash/, remove from playlists
    ├── move_to_fav()            — move to fav/, remove from playlists
    ├── move_to_saved()          — move to savedPath/, remove from playlists
    └── remove_from_playlist()  — strips path from all .xspf files
```

---

## Key Functions

| Function | Description |
|----------|-------------|
| `load_paths_config()` | Reads `vlcmenuConfig.json`, populates all global path variables |
| `check_vlc_and_prompt()` | Detects running VLC; returns `'continue'`, `'management'`, or `'exit'` |
| `interactive_menu(config)` | Main profile selection loop with arrow-key navigation |
| `run_profile(profile)` | Collects media files, creates XSPF playlist, opens VLC |
| `create_xspf_playlist(files, path)` | Writes an XSPF 1.0 playlist file |
| `management_mode()` | Playback control loop; all commands dispatched here |
| `display_current_file()` | Uses AppleScript to read VLC's current item name and path |
| `get_vlc_current_file()` | Returns dict with `status`, `path`, `filename` from VLC |
| `vlc_next_track()` | AppleScript: `tell application "VLC" to next` |
| `vlc_previous_track()` | AppleScript: `tell application "VLC" to previous` |
| `vlc_pause()` | AppleScript: `tell application "VLC" to play` (toggles) |
| `vlc_seek(seconds)` | AppleScript: `set current time to (current time + N)` |
| `vlc_shuffle()` | System Events: clicks Playback → Shuffle menu item |
| `open_in_finder(path)` | `open -R path` to reveal file in Finder |
| `delete_current_file(path)` | Moves file to `trash/` folder |
| `move_to_fav(path)` | Moves file to `fav/` folder |
| `move_to_saved(path)` | Moves file to `savedPath` folder |
| `remove_from_playlist(path)` | Removes file entry from all `.xspf` files in `PLAYLIST_DIR` |
| `get_key()` | Raw single-keypress using `termios`/`tty`; handles arrow escape sequences |
| `collect_input(first_char)` | Buffered input for multi-character strings (waits for Enter) |
| `get_menu_input(prompt)` | Hybrid: ESC/arrows instant, all others buffered |
| `find_duplicates_by_hash(files)` | Groups by size then MD5 hash |
| `find_similar_filenames(files, threshold)` | `difflib` ratio ≥ 0.75 |
| `resize_terminal_for_management()` | AppleScript/System Events: resize Terminal window |
| `resize_vlc_fullheight()` | Resize VLC window to full screen height |
| `check_resize()` | Checks `SIGWINCH` flag; used to redraw on terminal resize |
| `find_profile_by_id(profiles, id)` | Match profile by custom `id` field |
| `get_next_visible_index(profiles, idx, dir)` | Arrow navigation skipping hidden profiles |

---

## Global Variables (set from config at startup)

| Variable | Config Key | Description |
|----------|------------|-------------|
| `VLC_PATH` | `paths.vlcPath` | Path to VLC executable |
| `BASE_PATH` | `paths.basePath` | Root media directory |
| `PLAYLIST_DIR` | `paths.playlistFolder` | Where `.xspf` files are written |
| `TRASH_PATH` | derived | `{BASE_PATH}/trash/` |
| `FAV_PATH` | derived | `{BASE_PATH}/fav/` |
| `SAVED_PATH` | `paths.savedPath` | Save destination |
| `MGMT_TERMINAL_WIDTH` | `managementMode.terminalWidth` | Terminal width for Management Mode |
| `MGMT_TERMINAL_HEIGHT` | `managementMode.terminalHeight` | Terminal height for Management Mode |
| `MGMT_MOVE_WINDOW` | `managementMode.moveWindow` | Reposition window on resize |

---

## Input Handling

The script uses a hybrid input model:

| Input Type | Method | Keys |
|------------|--------|------|
| Instant (no Enter) | `get_key()` via raw `termios` | ESC, arrow keys, Enter |
| Buffered (waits for Enter) | `collect_input()` | Letters, numbers, all others |

This allows single-digit profiles to be selected without pressing Enter in some contexts, while still supporting multi-digit profile numbers (e.g., `12`, `1001`).

---

## Playlist Format

Playlists are written in **XSPF 1.0** format. Each playlist is named per profile (`PLAYLIST_NAME`) and saved to `paths.playlistFolder`.

Files starting with `.` (dotfiles) are excluded from playlists.

When a file is moved (Delete/Fav/Save), its `<track>` entry is removed from **all** `.xspf` files in `PLAYLIST_DIR`, not just the currently active playlist.

---

## AppleScript Commands Used

| Purpose | AppleScript |
|---------|-------------|
| Next track | `tell application "VLC" to next` |
| Previous track | `tell application "VLC" to previous` |
| Pause/Play | `tell application "VLC" to play` |
| Seek | `tell application "VLC" to set current time to (current time + N)` |
| Get current file path | `tell application "VLC" to get path of current item` |
| Get current file name | `tell application "VLC" to get name of current item` |
| Shuffle | System Events click on `Playback > Shuffle` menu item |
| Open in Finder | `open -R <path>` (shell command) |
| Resize Terminal | System Events scripting for Terminal.app |

---

*Copyright © 2026 Cloud Box 9 Inc. All rights reserved.*
