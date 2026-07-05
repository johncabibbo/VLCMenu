# VLC Menu

**Control VLC, tidy your media library, and reclaim disk space — all from the terminal.**

VLC Menu is a keyboard-driven, terminal front-end for [VLC](https://www.videolan.org/vlc/) on macOS. Define your folders once as **profiles** in a JSON config, then launch a curated playlist with a single keystroke and control everything — pause, skip, seek, shuffle, and file triage (delete / favorite / save) — without ever touching the mouse. An **Admin** toolset adds three library-maintenance features on top: **Organize Files**, **Delete Duplicates**, and **Optimize Media**.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Requirements](#requirements)
4. [Installation](#installation)
5. [Alias Setup — Run From Anywhere](#alias-setup--run-from-anywhere)
6. [Configuration](#configuration)
7. [Usage & Examples](#usage--examples)
8. [Troubleshooting](#troubleshooting)
9. [License / Copyright](#license--copyright)

---

## Overview

Instead of clicking through folders and dragging files into VLC, you describe your library as a set of **profiles** — each a named group of folders. Pick one and VLC Menu builds an XSPF playlist, opens it in VLC, and drops you into **Management Mode**, a single-key control surface running entirely in your terminal.

Over time it grew from a playlist launcher into a full **media-library workbench**. Press `[A]` at the main menu for the **Admin** section, which bundles three tools for keeping large video collections clean and lean.

---

## Features

### 📂 Organize Files
Sort a sprawling import folder into a clean category structure — without opening Finder.

- **Preview** every move before anything happens (dry-run first).
- **Organize** loose files into category subfolders based on your rules.
- **Fix Folders** repairs misnamed or misplaced category directories.
- **Validate** confirms every file landed where it belongs.
- **Short Clips** isolates throwaway / too-short videos for review.
- **Categories** manages the category list that drives sorting.
- **Folder-integrity warnings** flag *Unknown Folders* (on disk but not in your categories) and *Missing Profile Folders* (referenced by a profile but absent on disk) so broken references never go unnoticed.

### 🧹 Delete Duplicates
A two-phase duplicate finder that scans **every folder referenced by every profile**:

- **Phase 1 — Exact duplicates:** groups files by size, then confirms with an MD5 hash. Byte-for-byte matches, guaranteed.
- **Phase 2 — Similar filenames:** fuzzy-matches names (`difflib`, 75% threshold by default) to surface re-encodes and slightly-renamed copies a hash check misses.
- **Safe by default:** review each group and choose what to remove. "Deleted" files are **moved to `trash/`**, never hard-deleted — nothing is lost until *you* empty it.

### 🗜️ Optimize Media
Re-encode and compress an entire drive of video to recover storage, driven by per-volume profiles:

- Point a profile at a volume and batch-optimize everything under it.
- Per-profile **delete modes** (e.g. *delete-after-each*) control cleanup of originals as each file finishes.
- Arrow-key profile picker with a live folder summary, so you always know what you're about to process.

### ▶️ Core Playback
- **Profile-driven playlists** — build XSPF playlists from any combination of folders in one keystroke; hidden profiles are reachable by custom numeric ID.
- **Management Mode** — mouse-free control: `[Space]` pause, `[→/←]` next/prev, `[↑/↓]` seek ±15s, `[Tab]` shuffle, `[Shift+↑/↓]` volume.
- **In-place triage** — `[D]` Delete → `trash/`, `[F]` Fav → `fav/`, `[S]` Save → your configured `saved/`. VLC advances to the next track first, then the file is **moved** (not destroyed) and stripped from *all* playlists.
- **Reattach to a running VLC** — close the terminal but leave VLC playing? Relaunch and jump straight back into Management Mode.
- **Live-resizing UI** — headers and separators redraw on terminal resize (`SIGWINCH`); nothing wraps or breaks.

---

## Requirements

| Requirement | Notes |
|-------------|-------|
| **macOS** | Required — VLC is driven via AppleScript (`osascript`). Not supported on Windows. |
| **Python 3.10+** | Uses the standard library only (`subprocess`, `termios`, `hashlib`, `difflib`, `shutil`, …). |
| **VLC for Mac** | Installed at `/Applications/VLC.app`. Download from <https://www.videolan.org/vlc/>. |
| **CB9Lib** | UI, colors, config loading, and file utilities. **Bundled** in this release (`CB9Lib/` sits next to `vlcmenu.py`). |
| **A media volume** | An external drive or local folder containing your video files. |

> **Linux note:** the duplicate finder, organizer, and optimizer are pure Python and portable, but playback / Management Mode relies on macOS AppleScript, so full functionality requires macOS.

---

## Installation

1. **Get the files.** Clone the repository (or download and unzip the release):

   ```bash
   git clone <REPOSITORY_URL> VLCMenu
   cd VLCMenu
   ```

   The release ships everything it needs side-by-side:

   ```
   VLCMenu/
   ├── vlcmenu.py            # main script
   ├── vlcmenuConfig.json    # your profiles and paths
   ├── CB9Lib/               # bundled dependency (no separate install)
   ├── README.md
   ├── USER_MANUAL.md
   ├── QUICK_REFERENCE.md
   └── PROJECT_INFO.md
   ```

2. **Confirm Python 3.10+:**

   ```bash
   python3 --version
   ```

3. **Install VLC** (if not already present) at `/Applications/VLC.app`.

4. **Run it:**

   ```bash
   python3 vlcmenu.py
   ```

No `pip install` step is required — CB9Lib is bundled and everything else is standard library.

---

## Alias Setup — Run From Anywhere

So you can launch VLC Menu from any directory by typing `vlcmenu`.

### macOS / Linux (zsh or bash)

Add an alias to your shell startup file — `~/.zshrc` (default on modern macOS) or `~/.bashrc` / `~/.bash_profile`:

```bash
alias vlcmenu='python3 ~/path/to/VLCMenu/vlcmenu.py'
```

Reload your shell so the alias takes effect:

```bash
source ~/.zshrc      # or: source ~/.bashrc
```

Then, from anywhere:

```bash
vlcmenu
```

**Alternative — symlink onto your `PATH`:**

```bash
chmod +x ~/path/to/VLCMenu/vlcmenu.py
ln -s ~/path/to/VLCMenu/vlcmenu.py /usr/local/bin/vlcmenu
```

Now `vlcmenu` works in any new shell. Replace `~/path/to/VLCMenu/` with the real folder where you placed the release.

> **Windows:** VLC Menu depends on macOS AppleScript and is not supported natively on Windows. If you only need the Organize / Duplicate / Optimize tooling, run it under **WSL** or **Git Bash** with `python vlcmenu.py`; playback control will not function.

---

## Configuration

All behavior lives in **`vlcmenuConfig.json`** (following the `SCRIPTNAMEConfig.json` convention). Open it from the Profile menu with `[E]`, or edit it directly — then **restart the script** to apply changes.

### Structure

```json
{
  "_metadata": {
    "project": "VLCMenu",
    "version": "3.22",
    "lastUpdated": "2026-07-04",
    "description": "Profiles, paths, and settings for VLC Menu"
  },
  "paths": {
    "basePath":       "/Volumes/MyDrive/video",
    "playlistFolder": "/Volumes/MyDrive/video/playlist",
    "savedPath":      "/Volumes/MyDrive/video/saved",
    "vlcPath":        "/Applications/VLC.app/Contents/MacOS/VLC"
  },
  "managementMode": {
    "resizeTerminal": true,
    "terminalWidth":  800,
    "terminalHeight": 400,
    "moveWindow":     false
  },
  "profiles": [
    {
      "title": "Favs",
      "FOLDER_ROOT": "/Volumes/MyDrive/video/",
      "FOLDER_NAME_ARRAY": ["fav", "hot"],
      "PLAYLIST_NAME": "favs.xspf"
    }
  ]
}
```

### `paths`

| Key | Description |
|-----|-------------|
| `basePath` | Root media directory (`trash/`, `fav/` are created under it). |
| `playlistFolder` | Where generated `.xspf` playlists are written. |
| `savedPath` | Destination for the `[S]` Save action. |
| `vlcPath` | Full path to the VLC executable. |

### `managementMode`

| Key | Description | Default |
|-----|-------------|---------|
| `resizeTerminal` | Resize the terminal when entering Management Mode. | `true` |
| `terminalWidth` / `terminalHeight` | Target window size (px). | `800` / `400` |
| `moveWindow` | Reposition the window (`false` = resize only). | `false` |

### `profiles`

| Field | Required | Description |
|-------|----------|-------------|
| `title` | Yes | Name shown in the menu. |
| `FOLDER_ROOT` | Yes | Root path the folder names are relative to. |
| `FOLDER_NAME_ARRAY` | Yes | Subfolders to include in the playlist. |
| `PLAYLIST_NAME` | Yes | Output `.xspf` filename. |
| `id` | No | Custom numeric ID for direct selection (e.g. `1001`). |
| `hidden` | No | `true` hides it from the menu (still selectable by `id`). |

> **Never hard-code secrets** in the config. Paths only.

---

## Usage & Examples

Launch:

```bash
vlcmenu          # if you set up the alias
# or
python3 ~/path/to/VLCMenu/vlcmenu.py
```

### Flow

```
Launch
  │
  ├─ Is VLC already running? ── yes ─▶ [M] jump into Management Mode  (reattach)
  │
  ▼
Profile Menu ──[A] Admin──▶  Organize · Duplicates · Optimize · Validate · Categories
  │
  ├─ pick a profile ─▶ build XSPF playlist ─▶ open in VLC
  │
  ▼
Management Mode ─▶ pause · next/prev · seek · shuffle · delete/fav/save
```

### Profile menu keys

| Key | Action |
|-----|--------|
| `↑` / `↓` | Move selection (skips hidden profiles) |
| `Enter` | Load and play the highlighted profile |
| `1`–`99` + Enter | Select by position number or custom profile `id` |
| `A` + Enter | Open the **Admin** menu (Organize / Duplicates / Optimize) |
| `D` + Enter | Open the **Duplicate Finder** directly |
| `E` + Enter | Open `vlcmenuConfig.json` in your default editor |
| `Q` / `ESC` | Quit |

### Management Mode keys

| Key | Action |
|-----|--------|
| `Space` | Pause / play |
| `→` / `←` | Next / previous track |
| `↑` / `↓` | Seek +15s / −15s |
| `Shift + ↑ / ↓` | Volume up / down |
| `Tab` | Toggle shuffle |
| `D` / `F` / `S` | Delete → `trash/` · Fav → `fav/` · Save → `savedPath` (advances to next) |
| `O` | Reveal current file in Finder |
| `R` | Refresh display |
| `Q` / `ESC` | Quit |

> In Management Mode every key reacts instantly — no Enter needed.

### Worked example — build a "Favs" playlist

1. Add the `Favs` profile shown in [Configuration](#configuration) to `vlcmenuConfig.json` and save.
2. Run `vlcmenu`.
3. At the Profile menu, arrow to **Favs** and press `Enter`.
   - VLC Menu collects every video in `fav/` and `hot/`, writes `favs.xspf` to `playlistFolder`, and opens it in VLC.
4. You land in Management Mode:

   ```
   =====================================================================
    VLC Menu - Management Mode v3.22
   =====================================================================
   CURRENT: my_clip.mp4
       /Volumes/MyDrive/video/fav
   Length: 02:15 / 08:41 | Fullscreen: Off | Port: 8080
   ---------------------------------------------------------------------
   [R] Refresh  [D] Delete  [F] Fav  [S] Save  [Shift+L] Menu Toggle
   ```
5. Press `→` to skip, `F` to favorite, or `S` to move a keeper to your `saved/` folder.

### Worked example — clean up duplicates

1. From the Profile menu press `A` (Admin), then `D` (Duplicates) — or press `D` directly.
2. VLC Menu scans every folder used by every profile, then reports:
   - **Exact matches** (same size + MD5), and
   - **Similar names** (≥ 75% match).
3. For each group, review and pick which copies to move to `trash/`. Originals stay untouched until you empty `trash/`.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `Base path not accessible: /Volumes/...` | The drive isn't mounted. Mount it, or point `basePath` (and `basePath1/2/3`) at an available volume. VLC Menu falls back to the first accessible base path. |
| Nothing plays / VLC doesn't open | Confirm VLC is at `/Applications/VLC.app` and `paths.vlcPath` matches. Approve the Automation permission macOS prompts for on first run. |
| Keys don't respond in Management Mode | Make sure the terminal window (not VLC) has focus, and that you're in a real terminal (TTY). |
| `No module named CB9Lib` | Run `vlcmenu.py` from inside the release folder so the bundled `CB9Lib/` is on the path, or keep `CB9Lib/` next to the script. |
| Alias not found after adding it | Open a new terminal or `source` your shell rc file; confirm you edited the rc your shell actually loads (`~/.zshrc` on default macOS). |
| Playlist entries look stale after deleting files | Deletes strip the file from **all** `.xspf` files in `playlistFolder`; reload the profile to regenerate a fresh playlist. |

---

## License / Copyright

---
**Version:** 3.22
**Author:** Cloud Box 9 Inc.
**Maintainer / Owner:** Cloud Box 9 Inc.
**Last Updated:** Jul 5, 2026

Copyright © 2026 Cloud Box 9 Inc. All rights reserved.
