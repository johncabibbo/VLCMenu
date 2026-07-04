# VLC Menu — User Manual

**Version:** 2.90 | **Updated:** Mar 27, 2026

---

## Table of Contents

1. [Overview](#overview)
2. [Starting the Script](#starting-the-script)
3. [Menu 1 — VLC Status Check](#menu-1--vlc-status-check)
4. [Menu 2 — Profile Selection](#menu-2--profile-selection)
5. [Management Mode](#management-mode)
6. [Duplicate Finder](#duplicate-finder)
7. [File Operations](#file-operations)
8. [Configuration](#configuration)
9. [Profiles](#profiles)
10. [Terminal Resize Behavior](#terminal-resize-behavior)

---

## Overview

VLC Menu is a terminal-based VLC controller for macOS. It reads profiles from a JSON config file, builds XSPF playlists from folders of media files, loads them into VLC, and then provides a Management Mode for controlling playback without leaving the terminal.

---

## Starting the Script

```bash
cd ~/Documents/script/VLC
python3 vlcmenu.py
```

Or via alias if configured in your shell.

---

## Menu 1 — VLC Status Check

On launch, the script checks whether VLC is already running.

### VLC Is Not Running
The script skips directly to the Profile Selection menu.

### VLC Is Already Running
A prompt appears with the following options:

| Key | Action |
|-----|--------|
| `M` / Enter | Jump directly to Management Mode (default) |
| `S` | Stop the running VLC instance and go to Profile Selection |
| `C` | Leave VLC running and go to Profile Selection |
| `Q` / ESC | Quit the script |

> If VLC stops between the check and pressing `M`, the script detects this and removes the Management Mode option.

---

## Menu 2 — Profile Selection

Displays all visible profiles from `vlcmenuConfig.json`.

### Navigation

| Key | Action |
|-----|--------|
| `↑` / `↓` | Move selection up/down (skips hidden profiles) |
| `Enter` | Load and play the selected profile |
| `1`–`99` + Enter | Select by position number or custom profile ID |
| `E` + Enter | Open `vlcmenuConfig.json` in the default editor |
| `D` + Enter | Open Duplicate Finder |
| `Q` + Enter | Quit the script |
| `ESC` | Quit the script immediately |

### Profile Display
- The currently selected profile is marked with `▶`
- Hidden profiles (marked `"hidden": true` in config) are never displayed but can still be selected by their custom `id`

### Running a Profile
When a profile is selected:
1. Media files are collected from all folders in `FOLDER_NAME_ARRAY`
2. An XSPF playlist file is created in `paths.playlistFolder`
3. VLC opens (or reloads) the playlist
4. The terminal automatically resizes for Management Mode
5. Management Mode begins

---

## Management Mode

The main control interface while a file is playing. Displays the current filename and folder on screen and refreshes automatically.

### Menu Bar

```
[R] Refresh  [D] Delete  [F] Fav  [S] Save  [O] Open in Finder
[Space] Pause  [→] Next  [←] Prev  [↑] +15s  [↓] -15s  [Tab] Shuffle  [Q] Quit
```

### Controls

| Key | Action |
|-----|--------|
| `R` | Refresh display (re-reads current VLC state) |
| `D` | Delete current file — moves to `trash/`, advances to next track, removes from all XSPF playlists |
| `F` | Fav current file — moves to `fav/`, advances to next track, removes from all XSPF playlists |
| `S` | Save current file — moves to `saved/`, advances to next track, removes from all XSPF playlists |
| `O` | Reveal current file in Finder |
| `Space` | Toggle pause / play |
| `→` (right arrow) | Next track |
| `←` (left arrow) | Previous track |
| `↑` (up arrow) | Seek forward 15 seconds |
| `↓` (down arrow) | Seek back 15 seconds |
| `Tab` | Toggle shuffle mode |
| `Q` | Quit the script entirely |
| `ESC` | Quit the script entirely |

> All keys react instantly — no Enter required in Management Mode.

---

## Duplicate Finder

Accessed from the Profile Selection menu with `D`.

Scans all folders referenced by all profiles for duplicate files in two phases:

### Phase 1 — Exact Duplicates (MD5 Hash)
- Groups files by size first (quick pre-filter)
- Computes MD5 hash for each candidate group
- Files with matching hashes are exact duplicates

### Phase 2 — Similar Filenames (Fuzzy Match)
- Compares filenames using difflib sequence matching
- Default threshold: 75% similarity
- Useful for finding re-encoded or slightly renamed copies

### Duplicate Actions
For each duplicate group, you can:
- View all duplicates in the group
- Select files to delete (moved to `trash/`, not permanently removed)
- Skip the group

---

## File Operations

When a file is deleted, favorited, or saved in Management Mode:

1. VLC advances to the **next track** before the file is moved
2. The file is **moved** to the destination folder (not permanently deleted)
3. The file path is **removed from all `.xspf` playlist files** in `PLAYLIST_DIR`

### Destination Folders

| Action | Destination |
|--------|-------------|
| Delete (`D`) | `{basePath}/trash/` |
| Fav (`F`) | `{basePath}/fav/` |
| Save (`S`) | `paths.savedPath` (from config) |

All destination folders are created automatically if they do not exist.

---

## Configuration

Config file: `~/Documents/script/VLC/vlcmenuConfig.json`

Open for editing from the Profile menu with `E`, or directly in any text editor. **Restart the script after saving changes.**

### Structure

```json
{
  "_metadata": { ... },
  "paths": { ... },
  "managementMode": { ... },
  "profiles": [ ... ]
}
```

### `paths` Section

| Key | Description | Example |
|-----|-------------|---------|
| `basePath` | Root folder for all media | `/Volumes/MyDrive/video` |
| `playlistFolder` | Where `.xspf` playlists are saved | `/Volumes/MyDrive/video/playlist` |
| `savedPath` | Destination for [S] Save operation | `/Volumes/MyDrive/video/saved` |
| `vlcPath` | Full path to VLC executable | `/Applications/VLC.app/Contents/MacOS/VLC` |

### `managementMode` Section

| Key | Description | Default |
|-----|-------------|---------|
| `terminalWidth` | Terminal width (px) when entering Management Mode | `300` |
| `terminalHeight` | Terminal height (px) when entering Management Mode | `300` |
| `moveWindow` | Move the terminal window position | `false` |

> Set `moveWindow: false` to resize the terminal without changing its position.

---

## Profiles

Each profile in the `profiles` array defines a playlist to build from one or more folders.

### Profile Fields

| Field | Required | Description |
|-------|----------|-------------|
| `title` | Yes | Display name in the menu |
| `FOLDER_ROOT` | Yes | Root path that all folder names are relative to |
| `FOLDER_NAME_ARRAY` | Yes | Array of subfolder names to include |
| `PLAYLIST_NAME` | Yes | Filename for the generated `.xspf` playlist |
| `id` | No | Custom numeric ID for direct selection (e.g., `1001`) |
| `hidden` | No | `true` to hide from menu (still selectable by custom `id`) |

### Example Profile

```json
{
  "title": "Favs",
  "FOLDER_ROOT": "/Volumes/MyDrive/video/",
  "FOLDER_NAME_ARRAY": ["fav", "hot"],
  "PLAYLIST_NAME": "favs.xspf"
}
```

### Hidden Profile with Custom ID

```json
{
  "id": 1001,
  "title": "SpecialList",
  "FOLDER_ROOT": "/Volumes/SSD1/video/",
  "FOLDER_NAME_ARRAY": ["special"],
  "PLAYLIST_NAME": "special.xspf",
  "hidden": true
}
```

Type `1001` + Enter from the Profile menu to play this hidden profile.

### Profile Selection Logic

When a number is typed:
1. The script first checks if any profile has a matching custom `id`
2. If found, that profile is used (even if hidden)
3. If not found, the number is treated as a 1-based position in the visible list

---

## Terminal Resize Behavior

- The script listens for `SIGWINCH` (terminal resize signal)
- Separator lines (`---`, `===`) automatically adjust to the current terminal width
- The display redraws itself on the next input cycle after a resize

---

*Copyright © 2026 Cloud Box 9 Inc. All rights reserved.*
