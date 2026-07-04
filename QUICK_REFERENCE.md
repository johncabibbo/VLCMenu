# VLC Menu — Quick Reference

**Version:** 2.90 | **Updated:** Mar 27, 2026

---

## Launch

```bash
cd ~/Documents/script/VLC && python3 vlcmenu.py
```

---

## Menu 1 — VLC Status Check *(only shown if VLC is running)*

| Key | Action |
|-----|--------|
| `M` / Enter | Go to Management Mode |
| `S` | Stop VLC, pick new playlist |
| `C` | Leave VLC running, pick new playlist |
| `Q` / ESC | Quit |

---

## Menu 2 — Profile Selection

| Key | Action |
|-----|--------|
| `↑` / `↓` | Navigate profiles |
| Enter | Play selected profile |
| `1`–`99` + Enter | Play by number or custom ID |
| `E` + Enter | Edit config file |
| `D` + Enter | Open Duplicate Finder |
| `Q` + Enter | Quit |
| ESC | Quit immediately |

---

## Management Mode *(all keys instant — no Enter)*

### Playback

| Key | Action |
|-----|--------|
| `Space` | Pause / Play |
| `→` | Next track |
| `←` | Previous track |
| `↑` | Seek forward 15 seconds |
| `↓` | Seek back 15 seconds |
| `Tab` | Toggle shuffle |

### File Operations

| Key | Action |
|-----|--------|
| `D` | Delete → move to `trash/`, next track |
| `F` | Fav → move to `fav/`, next track |
| `S` | Save → move to `savedPath`, next track |
| `O` | Reveal current file in Finder |

### Other

| Key | Action |
|-----|--------|
| `R` | Refresh display |
| `Q` / ESC | Quit script |

---

## Config File

`~/Documents/script/VLC/vlcmenuConfig.json`

```
paths.basePath          Root media folder
paths.playlistFolder    Where .xspf playlists are saved
paths.savedPath         Destination for [S] Save
paths.vlcPath           Path to VLC executable

managementMode.terminalWidth   Terminal width on entering Management Mode
managementMode.terminalHeight  Terminal height on entering Management Mode
managementMode.moveWindow      true = also reposition terminal window

profiles[].title              Display name
profiles[].FOLDER_ROOT        Root path for folders
profiles[].FOLDER_NAME_ARRAY  Subfolders to include
profiles[].PLAYLIST_NAME      Output .xspf filename
profiles[].id                 (optional) Custom selection number
profiles[].hidden             (optional) true = hide from menu
```

---

## File Operation Destinations

| Action | Folder |
|--------|--------|
| Delete (`D`) | `{basePath}/trash/` |
| Fav (`F`) | `{basePath}/fav/` |
| Save (`S`) | `paths.savedPath` |

All moves also remove the file from all `.xspf` playlist files.

---

*Copyright © 2026 Cloud Box 9 Inc. All rights reserved.*
