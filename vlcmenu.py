#!/opt/homebrew/opt/python@3.12/libexec/bin/python3
#
# =============================================================================
# Filename: vlcmenu.py
# Project: VLC
# Version: 3.22
# Last Modified Date: 2026-06-03
# Maintainer: Cloud Box 9 Inc.
# -----------------------------------------------------------------------------
# Description:
#   JSON-driven VLC profile selector for Mac/Linux environments.
#   Each profile defines folder root, folder array, and playlist name.
#   Profiles load media files from specified folders into VLC.
#   Playlists are saved to configurable base path (prompted on first run).
#   Designed for deployment in ~/Documents/script/VLC.
#   Integrated with CB9Lib for enhanced UI, colors, and utilities.
#
# -----------------------------------------------------------------------------
# Revision History:
# -----------------------------------------------------------------------------
# v3.22 (2026-06-03)
#   • Fixed: every playlist failed with "Base path not accessible:
#     /Volumes/BPA2tbP1/industryVideo". The config defines only basePath1/2/3
#     (no unsuffixed "basePath"), so BASE_PATH fell back to a dead hardcoded
#     default and failed check_base_path_accessible() for all profiles.
#   • load_paths_config(): basePath default is now "" and, when basePath is
#     unset or its drive is not mounted, BASE_PATH resolves to the first
#     accessible entry in BASE_PATH_LIST (basePath1/2/3). Self-heals on remount.
#   • Config: added explicit "basePath": "/Volumes/BPA2tb-A1/industryVideo"
#     so trash/fav/saved share the same drive as playlistFolder/savedPath.
#   • Removed ALL hardcoded path literals from the script — every path now
#     comes from vlcmenuConfig.json:
#       - no-config else branch no longer invents BASE_PATH/VLC_PATH (empty;
#         lets check_base_path_accessible() report the real problem)
#       - vlcPath fallback no longer hardcodes /Applications/VLC.app
#       - shortenPath() uses the live home dir, not a literal ~
#       - validation + short-clips reports write to organizeMedia.reportFolder
#         (new config key, default ~/Desktop) instead of a hardcoded ~/Desktop
#       - MO_LOG_FILE reads mediaOptimize.logFile (new config key)
# v3.21 (2026-05-29)
#   • Added [A] Admin menu to the main menu. Admin = a self-contained port of
#     organizeMedia.py (Preview/Organize/Duplicates/Rescan/Fix/Validate/Short
#     Clips/Categories/Clear Cache) rebranded to the VLC Menu header.
#   • Added [M] Media Optimize inside Admin: a self-contained port of
#     mediaOptimize.py (profile select → file select → ffmpeg convert → summary).
#   • New config sections in vlcmenuConfig.json: "organizeMedia" and
#     "mediaOptimize". Source scripts organizeMedia.py / mediaOptimize.py are
#     neither modified nor imported.
# v3.21 (2026-05-18)
#   • folderShortList resolution: each name searched in basePath → basePath1/2/3 →
#     folderRoot pairs in order; first match wins, no duplicates across drives
# v3.20 (2026-05-18)
#   • Config: added folderRoot1/2 + folderNameArray1/2 to paths section
#   • FOLDER_ROOT_PAIRS global holds (root, name_array) pairs loaded from config
#   • show_move_folder_menu(): also includes named subfolders from folderRoot1/2;
#     basePath1/2/3 scan all subfolders, folderRoot1/2 include only named subfolders
# v3.19 (2026-05-18)
#   • Config: added basePath1, basePath2, basePath3 to paths section
#   • BASE_PATH_LIST global aggregates basePath + basePath1/2/3 (any that are non-empty)
#   • show_move_folder_menu(): scans all active base paths; multi-path mode shows
#     a [label] suffix (last segment of the base path) next to each folder in magenta
# v3.18 (2026-05-08)
#   • Move folder menu: explicit case-insensitive alphabetical sort on both
#     short list and all-folders views
# v3.17 (2026-05-08)
#   • [I] Move folder menu: opens in Short List mode (folderShortList config key);
#     press [A] to toggle to all folders and back; FOLDER_SHORT_LIST global loaded
#     in load_paths_config()
# v3.16 (2026-05-08)
#   • [I] Move folder menu: rescan BASE_PATH on every redraw so newly created
#     folders appear immediately without reopening the menu
# v3.15 (2026-05-06)
#   • Fix freeze in Move folder picker: guard collect_input() — skip any escape-sequence
#     or non-printable key so a partial CSI sequence can't corrupt terminal state
#   • Fixed VERSION constant (was left at v3.12 in prior commits)
# v3.14 (2026-05-06)
#   • Move folder picker: 2-column layout, folder names truncated to 20 chars with ellipsis
# v3.13 (2026-05-06)
#   • [I] Move: presents alphabetical subfolder picker from BASE_PATH
#   • User picks folder with ↑/↓ or number; file is moved and VLC advances to next track
#   • Added move_to_subfolder() and show_move_folder_menu() helpers
# v3.12 (2026-05-04)
#   • Shift+↑ / Shift+↓ adjusts VLC volume in management mode
#   • get_key() extended to read full multi-char CSI escape sequences (e.g. \x1b[1;2A)
#   • Added vlc_volume_adjust(delta) helper; VOLUME_STEP = 25 (~10% per keypress)
# v3.11 (2026-05-04)
#   • Management mode: compact status block (CURRENT: label, folder indented, Length|Fullscreen|Port on one line)
#   • Management mode: collapsible bottom menu — compact by default, [Shift+M] toggles to full view
#   • Management mode: menu bar pinned to the bottom of the terminal window via ANSI cursor positioning
#   • [Shift+M] (uppercase L) = menu toggle; [L] (lowercase) = Later
# v3.10 (2026-05-04)
#   • Added [C] Clean Up option to main menu
#   • Counts files and total size in the Trash subfolder, confirms before deleting
#   • Permanently removes all files (and empty subdirs) in TRASH_PATH
# v3.9 (2026-04-12)
#   • run_profile() now shuffles the collected media_files list with random.shuffle()
#     before creating the XSPF playlist, so each playlist load starts in a new random order.
#   • Added `import random` to standard imports.
# v3.8 (2026-04-10)
#   • Added EXTRA_PATHS optional field to profiles: list of absolute folder paths
#     to include in a playlist in addition to FOLDER_ROOT + FOLDER_NAME_ARRAY.
#     Works in run_profile(), show_profile_info(), and duplicate_finder_menu().
# v3.7 (2026-04-02)
#   • Added [E] Exit All: stops VLC and exits the script
#   • Added [H] Help: displays full key binding reference screen
#   • Added [L] Later: moves current file to savedForLater folder and advances to next video
#   • SAVED_FOR_LATER_PATH global added; configurable via savedForLaterPath in vlcmenuConfig.json
# v3.6 (2026-04-02)
#   • Shuffle is automatically enabled when a playlist is loaded and VLC starts
# v3.5 (2026-03-30)
#   • display_current_file() now shows current position and total length (e.g. 12:34 / 1:45:00)
# v3.4 (2026-03-30)
#   • display_current_file() now shows HTTP port when a video is playing
#   • On start (profile load), no longer resizes or moves terminal or VLC windows
#     — removed resize_vlc_fullheight() and resize_terminal_for_management() from all
#       profile-launch call sites (arrow select, numeric select, and direct management entry)
# v3.3 (2026-03-30)
#   • Added resizeTerminal option to managementMode config section.
#   • When resizeTerminal is false, resize_terminal_for_management() is skipped entirely.
#   • MGMT_RESIZE_TERMINAL global added; loaded from config with default true.
# v3.2 (2026-03-28)
#   • Management mode: added [W] to toggle VLC fullscreen mode.
#   • Added vlc_fullscreen() and vlc_get_fullscreen_state() functions.
#   • display_current_file() now shows Fullscreen: On/Off status.
# v3.1 (2026-03-28)
#   • Playlist menu: removed separator dashes between items; now shows a single
#     dash line before the first playlist and after the last.
# v3.0 (2026-03-27)
#   • Replaced all AppleScript media control with VLC HTTP interface
#   • Each VLC instance gets its own HTTP port — multi-instance support
#   • VLC launched directly via binary with --extraintf http --http-port PORT
#   • Added _vlc_http_get(), _vlc_http_command(), wait_for_vlc_http() helpers
#   • Added --port CLI arg: run second vlcmenu with --port 8081 to control second VLC
#   • stop_vlc() now terminates the specific launched process instead of pkill all
#   • vlc_shuffle() uses pl_random HTTP command instead of System Events menu click
#   • get_vlc_current_file() derives file path from playlist.json current item
# -----------------------------------------------------------------------------
# v2.91 (2026-03-27)
#   • After ↑/↓ seek, display current position and title in the terminal
#   • Added vlc_get_playback_info() — fetches time, duration, and title in one AppleScript call
# -----------------------------------------------------------------------------
# v2.90 (2026-03-27)
#   • Management Mode: ↑ seeks forward 15 seconds, ↓ seeks back 15 seconds
#   • Added vlc_seek(seconds) using AppleScript current time offset
#
# v2.89 (2026-03-10)
#   • Added custom "id" property for profiles (e.g., "id": 1001)
#   • Profiles can be selected by custom ID or by menu position
#   • Custom IDs take precedence over positional numbers
#   • Useful for hidden profiles with memorable shortcut numbers
#
# v2.88 (2026-03-10)
#   • Added "hidden" property for profiles in config file
#   • Hidden profiles don't display in menu but can still be played by number
#   • Example: "hidden": true in a profile object hides it from menu
#
# v2.87 (2026-02-22)
#   • Added [O] Open in Finder option to Management Mode menu
#   • Reveals currently playing file in Finder
#
# v2.86 (2026-02-21)
#   • Added [Tab] Shuffle option to Management Mode menu
#   • Updated CURRENT VLC STATUS to show filename on first line, folder on second line
#   • Added vlc_shuffle() function to toggle playlist shuffle via System Events
#
# v2.85 (2026-02-13)
#   • Removed post-playlist menu - now goes directly to Management Mode after playlist loads
#   • Streamlined workflow: Menu 1 (VLC running?) → Menu 2 (Playlist) → Management Mode
#
# v2.84 (2026-02-12)
#   • Added moveWindow config option to managementMode section
#   • When moveWindow is true (default), terminal is moved and resized as before
#   • When moveWindow is false, terminal is only resized without moving position
#
# v2.83 (2026-02-07)
#   • Menu 1: Added option to go directly to Management Mode if VLC is running
#   • Menu 1: Management Mode hidden if VLC stops, S becomes default
#   • VLC window resizes to full screen height when starting a playlist
#   • Terminal window resizes to 60% width x 300px height when entering Management Mode
#   • Terminal focus is kept/restored when starting VLC
#   • Updated post-playlist menu format: [M] Management Mode - Default, [Q/Esc] Exit
#   • ESC key now instantly quits from any menu (no Enter required)
#   • Terminal resize dimensions now configurable in vlcmenuConfig.json (managementMode section)
#
# v2.82 (2026-02-05)
#   • Files moved via Delete/Fav/Save are now removed from XSPF playlist files
#   • Added remove_from_playlist() function to update all playlist files
#
# v2.81 (2026-02-05)
#   • Moved VLC_PATH to config file (paths.vlcPath)
#   • Added [S] Save option to move video to saved folder and advance
#   • Added savedPath to config file for Save destination
#   • Fixed shorten_path() to dynamically detect user's home folder
#
# v2.80 (2026-01-31)
#   • Added automatic redraw on terminal resize (SIGWINCH handler)
#   • Separator lines now adjust to new terminal width without wrapping
#
# v2.79 (2026-01-31)
#   • Merged vlcmenuPaths.json into vlcmenuConfig.json
#   • Added playlistFolder setting to config
#   • Changed quit key from B to Q in post-playlist options
#   • ESC now exits script from anywhere
#   • Hybrid input: ESC and arrows react instantly, all other keys wait for Enter
#   • Multi-digit profile selection supported (1-99+)
# -----------------------------------------------------------------------------
# v2.78 (2026-01-25)
#   • Restored arrow key navigation (↑/↓) in main menu
#   • Main menu now uses get_key() for instant keypress detection
#   • ESC key exits from main menu
#   • Single-digit profile selection (1-9) still works instantly
# -----------------------------------------------------------------------------
# v2.77 (2026-01-21)
#   • Changed main menu input from get_key() to input() for buffered input
#   • Profile selection now requires Enter key (supports multi-digit: 1-99+)
#   • Removed arrow key navigation from main menu (kept in Management Mode)
#   • Removed Shift+1-9 profile info shortcut
#   • Post-playlist options now use input() instead of get_key()
# -----------------------------------------------------------------------------
# v2.76 (2026-01-17)
#   • Added Duplicate Finder feature [D] key from main menu
#   • Phase 1: Finds exact duplicates by file hash (MD5)
#   • Phase 2: Finds similar filenames using fuzzy matching (75% threshold)
#   • Groups files by size first for efficient hash comparison
#   • Allows selective deletion with files moved to trash folder
#   • Scans all folders from all profiles for comprehensive coverage
# -----------------------------------------------------------------------------
# v2.75 (2026-01-17)
#   • Added ESC key to gracefully exit from post-playlist options menu
#   • Changed input method to get_key() for instant keypress detection
#   • No longer requires Enter key after pressing A, B, or ESC
# -----------------------------------------------------------------------------
# v2.74 (2026-01-17)
#   • Changed default option after playlist loads from Exit to Management Mode
#   • Pressing Enter now enters Management Mode instead of exiting
#   • Option A is now Management Mode (default), Option B is Exit
# -----------------------------------------------------------------------------
# v2.73 (2026-01-12)
#   • Added "F- Fav" option to Management Mode menu
#   • F key moves current file to fav folder and advances to next track
#   • Created move_to_fav() function similar to delete_current_file()
#   • Added FAV_PATH global variable for fav folder location
#   • Fav folder created automatically at {BASE_PATH}/fav
# -----------------------------------------------------------------------------
# v2.72 (2026-01-10)
#   • Added arrow key navigation to Management Mode menu
#   • Up/Down arrows select options with visual indicator (▶)
#   • Enter key executes selected option
#   • ESC exits Management Mode
#   • All hotkeys (R, D, Q, Space, arrows) still work as shortcuts
# -----------------------------------------------------------------------------
# v2.71 (2026-01-10)
#   • Added keyboard controls to Management Mode
#   • Space bar: Pause/Play toggle
#   • Right arrow: Next track
#   • Left arrow: Previous track
#   • Added vlc_previous_track() and vlc_pause() functions
#   • Changed input handling in management_mode() to use get_key() for arrow key support
# -----------------------------------------------------------------------------
# v2.7 (2026-01-10)
#   • Added volume mount check before folder operations
#   • Added check_base_path_accessible() function to verify volume is mounted
#   • run_profile() now checks if base path is accessible before creating folders
#   • Management mode delete operation checks volume accessibility before moving files
#   • Provides helpful error messages when volume is not mounted
# -----------------------------------------------------------------------------
# v2.6 (2026-01-08)
#   • Q in Management Mode now exits the entire script
#   • Delete (D) no longer asks for confirmation
#   • Delete advances VLC to next track before moving file to trash
#   • Base path (/Volumes/BPA2tbP1/industryVideo/) now configurable
#   • Script asks for base path on first run and saves to vlcmenu_paths.json
#   • All hardcoded paths replaced with configurable base path
# -----------------------------------------------------------------------------
# v2.5 (2026-01-08)
#   • Changed all user input prompts to require Enter key
#   • Exit/Management mode choice now requires Enter
#   • Management mode menu options require Enter
#   • Delete confirmation requires Enter
# -----------------------------------------------------------------------------
# v2.4 (2026-01-08)
#   • Added Management Mode after profile completion
#   • Management Mode options: R (Refresh current file), D (Delete current file to trash)
#   • After profile runs, user can choose A (Exit - default) or B (Management Mode)
#   • Delete moves current playing file to /Volumes/BPA2tbP1/industryVideo/trash
# -----------------------------------------------------------------------------
# v2.3 (2026-01-08)
#   • Added VLC process detection on startup
#   • User prompted if VLC is already running: Stop/Continue/Exit options
#   • Can terminate existing VLC process before launching new playlist
# -----------------------------------------------------------------------------
# v2.2 (2026-01-06)
#   • Changed playlist save location to base video folder
#   • Added filtering to ignore hidden files and files starting with .
#   • Updated file collection to exclude dotfiles from playlists
# -----------------------------------------------------------------------------
# v2.1 (2026-01-02)
#   • Added arrow key navigation (↑/↓) like showAliases
#   • Renamed config.json to vlcmenuconfig.json
#   • Q or ESC now exits gracefully
#   • Enter runs the selected profile
#   • Visual indicator (▶) shows selected profile
#   • Selection wraps around (top/bottom)
#   • Numeric keys (1-9) still supported for quick selection
#   • Fixed VLC integration for macOS using 'open -a VLC' command
#   • Creates proper XSPF playlist files instead of command-line args
#   • Removed unsupported --one-instance and --playlist-enqueue options
#   • Script exits after running profile (no return to menu)
# -----------------------------------------------------------------------------
# v2.0 (2026-01-02)
#   • Complete refactor with CB9Lib integration
#   • Enhanced UI with header(), colors, and single-keypress input
#   • Added proper file header with Project, Version, Description
#   • Styled opening, menu, and exit to match backup/backupMySQL scripts
#   • Playlists now saved to ./playlist subfolder
#   • Clear existing VLC playlist before adding new items
#   • Added [E] Edit config.json option
#   • Added [Shift+Number] Profile info display
#   • Professional Cloud Box 9 branding and exit sequence
# -----------------------------------------------------------------------------
# v1.0 (Prior)
#   • Initial basic implementation
#   • Simple menu with text-based selection
# -----------------------------------------------------------------------------
# Copyright © 2026 Cloud Box 9 Inc. All rights reserved.
# =============================================================================

import json
import random
import subprocess
import os
import sys
import termios
import tty
import shutil
import hashlib
import difflib
import signal
import time
import re
import select
import threading
from datetime import datetime
from collections import defaultdict
import urllib.request
import urllib.parse
import base64
import json as _json

# Global flag for terminal resize
_resize_flag = False

def _handle_resize(signum, frame):
    """Signal handler for terminal resize."""
    global _resize_flag
    _resize_flag = True

# Register the resize handler
signal.signal(signal.SIGWINCH, _handle_resize)

# CB9Lib imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # bundled CB9Lib (self-contained)
from CB9Lib import (
    clear_screen, header, footerMenu, exit_screen, get_width,
    color_text, RED, GREEN, YELLOW, CYAN, MAGENTA, WHITE, BOLD, BRIGHT_YELLOW,
    DIM, RESET,
    load_json_config, save_json_config,
    ensure_folder, folder_exists, file_exists,
    get_project_sound, play_sound
)

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

VERSION = "v3.21"

# HTTP interface globals (set from config or --port arg)
HTTP_PORT     = 8080
HTTP_PASSWORD = "vlc"
HTTP_HOST     = "localhost"
_vlc_process  = None   # Track the launched VLC process for stop_vlc()
VOLUME_STEP   = 25     # Volume units per Shift+↑/↓ keypress (256 = 100%)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "vlcmenuConfig.json")

# -----------------------------------------------------------------------------
# Global Variables (set at runtime from config)
# -----------------------------------------------------------------------------

VLC_PATH = None  # Will be set from config
BASE_PATH = None  # Will be set from config
BASE_PATH_LIST = []  # All configured base paths (basePath + basePath1/2/3)
FOLDER_ROOT_PAIRS = []  # list of (root, name_array) from folderRoot1/2 + folderNameArray1/2
PLAYLIST_DIR = None  # Will be set from config
TRASH_PATH = None  # Will be set from config
FAV_PATH = None  # Will be set from config
SAVED_PATH = None  # Will be set from config
SAVED_FOR_LATER_PATH = None  # Will be set from config
MGMT_TERMINAL_WIDTH = 300  # Will be set from config
MGMT_TERMINAL_HEIGHT = 300  # Will be set from config
MGMT_MOVE_WINDOW = True  # Will be set from config
MGMT_RESIZE_TERMINAL = True  # Will be set from config
FOLDER_SHORT_LIST = []  # Will be set from config

# -----------------------------------------------------------------------------
# Utility Functions
# -----------------------------------------------------------------------------

def load_paths_config() -> dict:
    """Load paths configuration from vlcmenuConfig.json."""
    global BASE_PATH, BASE_PATH_LIST, FOLDER_ROOT_PAIRS, PLAYLIST_DIR, TRASH_PATH, FAV_PATH, SAVED_PATH, SAVED_FOR_LATER_PATH, VLC_PATH
    global MGMT_TERMINAL_WIDTH, MGMT_TERMINAL_HEIGHT, MGMT_MOVE_WINDOW, MGMT_RESIZE_TERMINAL
    global FOLDER_SHORT_LIST

    config = load_json_config(CONFIG_PATH)
    if config and 'paths' in config:
        paths = config['paths']
        BASE_PATH = paths.get("basePath", "").strip()
        # Build list of all active base paths (basePath + basePath1/2/3)
        BASE_PATH_LIST = [BASE_PATH] if BASE_PATH else []
        for key in ('basePath1', 'basePath2', 'basePath3'):
            p = paths.get(key, '').strip()
            if p:
                BASE_PATH_LIST.append(p)
        # If basePath is unset (or its drive is not mounted), fall back to the
        # first configured base path that is actually accessible. Prevents the
        # whole menu from failing when only basePath1/2/3 are defined.
        if not BASE_PATH or not os.path.isdir(BASE_PATH):
            BASE_PATH = next((bp for bp in BASE_PATH_LIST if bp and os.path.isdir(bp)),
                             BASE_PATH or (BASE_PATH_LIST[0] if BASE_PATH_LIST else ""))
        # Build folderRoot pairs (folderRoot1/2 + matching folderNameArray1/2)
        FOLDER_ROOT_PAIRS = []
        for n in ('1', '2'):
            root  = paths.get(f'folderRoot{n}', '').strip()
            names = paths.get(f'folderNameArray{n}', [])
            if root and names:
                FOLDER_ROOT_PAIRS.append((root, names))
        PLAYLIST_DIR = paths.get("playlistFolder", BASE_PATH)
        TRASH_PATH = os.path.join(BASE_PATH, "trash")
        FAV_PATH = os.path.join(BASE_PATH, "fav")
        SAVED_PATH = paths.get("savedPath", os.path.join(BASE_PATH, "saved"))
        SAVED_FOR_LATER_PATH = paths.get("savedForLaterPath", os.path.join(BASE_PATH, "savedForLater"))
        VLC_PATH = paths.get("vlcPath", "").strip()

        # Load management mode settings
        if 'managementMode' in config:
            mgmt = config['managementMode']
            MGMT_TERMINAL_WIDTH = mgmt.get("terminalWidth", 300)
            MGMT_TERMINAL_HEIGHT = mgmt.get("terminalHeight", 300)
            MGMT_MOVE_WINDOW = mgmt.get("moveWindow", True)
            MGMT_RESIZE_TERMINAL = mgmt.get("resizeTerminal", True)

        # Load folder short list
        FOLDER_SHORT_LIST = config.get('folderShortList', [])

        # Load HTTP interface settings
        global HTTP_PORT, HTTP_PASSWORD, HTTP_HOST
        if 'httpInterface' in config:
            http = config['httpInterface']
            HTTP_PORT     = http.get('port',     8080)
            HTTP_PASSWORD = http.get('password', 'vlc')
            HTTP_HOST     = http.get('host',     'localhost')

        return paths
    else:
        # No config file / no "paths" section: invent nothing. All paths come
        # from vlcmenuConfig.json. Leave paths empty so check_base_path_accessible()
        # reports "Base path not configured" instead of falling back to a stale
        # hardcoded volume that may no longer exist.
        BASE_PATH = ""
        BASE_PATH_LIST = []
        FOLDER_ROOT_PAIRS = []
        PLAYLIST_DIR = ""
        TRASH_PATH = ""
        FAV_PATH = ""
        SAVED_PATH = ""
        SAVED_FOR_LATER_PATH = ""
        VLC_PATH = ""
        MGMT_TERMINAL_WIDTH = 300
        MGMT_TERMINAL_HEIGHT = 300
        MGMT_MOVE_WINDOW = True
        MGMT_RESIZE_TERMINAL = True
        return {}

def check_resize() -> bool:
    """Check if terminal was resized and clear the flag."""
    global _resize_flag
    if _resize_flag:
        _resize_flag = False
        return True
    return False


def get_key():
    """Capture single keypress; handle arrow-key escape sequences gracefully."""
    import fcntl
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        try:
            ch = sys.stdin.read(1)
        except IOError:
            # Interrupted by signal (e.g., resize)
            return None
        if ch == "\x1b":
            # Set non-blocking mode to check if more data is available
            old_flags = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, old_flags | os.O_NONBLOCK)
            try:
                next1 = sys.stdin.read(1)
                if next1 == "[":
                    # Read until the sequence terminator (letter or ~)
                    seq = ""
                    while True:
                        try:
                            c = sys.stdin.read(1)
                            if c:
                                seq += c
                                if c.isalpha() or c == "~":
                                    break
                            else:
                                break
                        except IOError:
                            break
                    ch = f"\x1b[{seq}"
                else:
                    ch += next1
            except IOError:
                # No more data available - ESC was pressed alone
                pass
            finally:
                # Restore blocking mode
                fcntl.fcntl(fd, fcntl.F_SETFL, old_flags)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def shorten_path(path: str) -> str:
    """Replace user's home folder with ~ for cleaner display."""
    home_dir = os.path.expanduser("~")
    return path.replace(home_dir, "~")

# -----------------------------------------------------------------------------
# VLC HTTP Interface Helpers
# -----------------------------------------------------------------------------

def _vlc_http_get(endpoint: str, params: dict = None):
    """Make a GET request to the VLC HTTP interface. Returns parsed JSON dict or None."""
    url = f"http://{HTTP_HOST}:{HTTP_PORT}{endpoint}"
    if params:
        url += '?' + urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(url)
        credentials = base64.b64encode(f":{HTTP_PASSWORD}".encode()).decode()
        req.add_header('Authorization', f"Basic {credentials}")
        with urllib.request.urlopen(req, timeout=3) as resp:
            return _json.loads(resp.read().decode())
    except Exception:
        return None


def _vlc_http_command(command: str, val: str = None) -> bool:
    """Send a playback command to VLC. Returns True on success."""
    params = {'command': command}
    if val is not None:
        params['val'] = val
    return _vlc_http_get('/requests/status.json', params) is not None


def wait_for_vlc_http(timeout: float = 10.0) -> bool:
    """Wait up to `timeout` seconds for VLC HTTP interface to respond."""
    import time
    deadline = time.time() + timeout
    while time.time() < deadline:
        if _vlc_http_get('/requests/status.json') is not None:
            return True
        time.sleep(0.3)
    return False


def is_vlc_running() -> bool:
    """Check if VLC HTTP interface is responding on the configured port."""
    return _vlc_http_get('/requests/status.json') is not None

def stop_vlc():
    """Stop the VLC process launched by this session."""
    global _vlc_process
    try:
        if _vlc_process and _vlc_process.poll() is None:
            _vlc_process.terminate()
            _vlc_process = None
        else:
            # Fallback: kill any VLC on our port via HTTP quit command
            _vlc_http_command('quit')
        print(color_text("\nVLC process stopped.", fg=GREEN))
    except Exception as e:
        print(color_text(f"\nError stopping VLC: {e}", fg=RED))

def check_vlc_and_prompt():
    """
    Menu 1: Check if VLC is running and prompt user for action.
    Returns 'continue' to show playlist menu, 'management' to go directly to management mode, 'exit' to exit.
    If VLC is running: show M (Management Mode) as default.
    If VLC is not running: hide M option and make S the default.
    """
    vlc_running = is_vlc_running()

    if not vlc_running:
        return 'continue'  # VLC not running, continue normally to playlist menu

    clear_screen()
    header("VLC Menu", VERSION)

    print(color_text("\nVLC is already running.", fg=YELLOW, style=BOLD))
    print("\nWhat would you like to do?")
    print(f"  {color_text('M', fg=BRIGHT_YELLOW, style=BOLD)}. Management Mode (default)")
    print(f"  {color_text('S', fg=BRIGHT_YELLOW, style=BOLD)}. Stop VLC and choose a new playlist")
    print(f"  {color_text('C', fg=BRIGHT_YELLOW, style=BOLD)}. Continue to playlist menu (leave VLC running)")
    print(f"  {color_text('Q', fg=BRIGHT_YELLOW, style=BOLD)}. Quit")
    print("\nPress Enter for Management Mode, ESC to quit")

    while True:
        choice = get_menu_input("\nOption: ")

        # Re-check if VLC is still running before allowing Management Mode
        if choice == "" or choice == "M":
            if is_vlc_running():
                return 'management'
            else:
                print(color_text("VLC is no longer running. Please choose another option.", fg=RED))
                import time
                time.sleep(1.5)
                # Redraw menu without M option
                clear_screen()
                header("VLC Menu", VERSION)
                print(color_text("\nVLC is not running.", fg=YELLOW, style=BOLD))
                print("\nWhat would you like to do?")
                print(f"  {color_text('S', fg=BRIGHT_YELLOW, style=BOLD)}. Choose a playlist (default)")
                print(f"  {color_text('Q/ESC', fg=BRIGHT_YELLOW, style=BOLD)}. Quit")
                print("\nPress Enter to choose a playlist, ESC to quit")
                continue
        elif choice == "S":
            stop_vlc()
            # Give VLC time to fully terminate
            import time
            time.sleep(0.5)
            return 'continue'
        elif choice == "C":
            return 'continue'
        elif choice == "Q":
            show_exit_screen()
        else:
            print(color_text("Invalid option. Please choose M, S, C, Q, or press Enter/ESC.", fg=RED))
            import time
            time.sleep(1.5)

def vlc_next_track():
    """Advance VLC to the next track in the playlist."""
    return _vlc_http_command('pl_next')

def vlc_previous_track():
    """Go back to the previous track in the playlist."""
    return _vlc_http_command('pl_previous')

def vlc_seek(seconds):
    """Seek VLC forward (positive) or backward (negative) by the given number of seconds."""
    val = f"+{seconds}s" if seconds >= 0 else f"{seconds}s"
    return _vlc_http_command('seek', val)

def vlc_get_playback_info() -> dict:
    """
    Fetch current playback time, duration, and title from VLC via HTTP.
    Returns dict with keys: current_time (int), duration (int), title (str).
    Returns None if VLC is not responding.
    """
    status = _vlc_http_get('/requests/status.json')
    if not status:
        return None
    meta  = status.get('information', {}).get('category', {}).get('meta', {})
    title = meta.get('filename', '') or meta.get('title', '')
    return {
        'current_time': int(status.get('time',   0)),
        'duration':     int(status.get('length', 0)),
        'title':        title
    }


def _format_seconds(secs: int) -> str:
    """Format an integer number of seconds as m:ss or h:mm:ss."""
    secs = max(0, secs)
    h, rem = divmod(secs, 3600)
    m, s   = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def vlc_pause():
    """Toggle pause/play in VLC."""
    return _vlc_http_command('pl_pause')

def vlc_shuffle():
    """Toggle random/shuffle mode in VLC."""
    return _vlc_http_command('pl_random')

def vlc_volume_adjust(delta: int) -> int:
    """Adjust volume by delta units (256 = 100%). Returns new level, or -1 on error."""
    status = _vlc_http_get('/requests/status.json')
    if not status:
        return -1
    current = int(status.get('volume', 256))
    new_vol = max(0, min(512, current + delta))
    _vlc_http_command('volume', str(new_vol))
    return new_vol

def vlc_fullscreen():
    """Toggle fullscreen mode in VLC."""
    return _vlc_http_command('fullscreen')

def vlc_get_fullscreen_state() -> bool:
    """Return True if VLC is currently in fullscreen, False otherwise."""
    status = _vlc_http_get('/requests/status.json')
    if not status:
        return False
    return bool(status.get('fullscreen', False))

def open_in_finder(filepath: str):
    """Open Finder and reveal the specified file."""
    try:
        subprocess.run(
            ['open', '-R', filepath],
            capture_output=True,
            text=True,
            timeout=5
        )
        return True
    except Exception as e:
        print(color_text(f"Error opening Finder: {e}", fg=RED))
        return False

def resize_vlc_fullheight():
    """Resize VLC window to full screen height when starting playlist."""
    try:
        # AppleScript to resize VLC to full height
        script = '''
        tell application "Finder"
            set screenBounds to bounds of window of desktop
            set screenHeight to item 4 of screenBounds
        end tell
        tell application "VLC"
            set bounds of window 1 to {0, 0, 800, screenHeight}
        end tell
        '''
        subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            timeout=5
        )
        return True
    except Exception as e:
        return False

def resize_terminal_for_management():
    """Resize Terminal window for management mode using config settings."""
    if not MGMT_RESIZE_TERMINAL:
        return True
    try:
        if MGMT_MOVE_WINDOW:
            # Move and resize
            script = f'''
            tell application "Terminal"
                set bounds of front window to {{0, 0, {MGMT_TERMINAL_WIDTH}, {MGMT_TERMINAL_HEIGHT}}}
            end tell
            '''
        else:
            # Resize only, keep current position
            script = f'''
            tell application "Terminal"
                set currentBounds to bounds of front window
                set x1 to item 1 of currentBounds
                set y1 to item 2 of currentBounds
                set bounds of front window to {{x1, y1, x1 + {MGMT_TERMINAL_WIDTH}, y1 + {MGMT_TERMINAL_HEIGHT}}}
            end tell
            '''
        subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            timeout=5
        )
        return True
    except Exception as e:
        return False

def focus_terminal():
    """Return focus to Terminal app."""
    try:
        subprocess.run(
            ['osascript', '-e', 'tell application "Terminal" to activate'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return True
    except Exception as e:
        return False

def get_vlc_current_file() -> dict:
    """Get the current playing file path and name from VLC via HTTP."""
    status = _vlc_http_get('/requests/status.json')
    if status is None:
        return {"status": "not_running", "path": None, "filename": None}

    meta     = status.get('information', {}).get('category', {}).get('meta', {})
    filename = meta.get('filename', '') or meta.get('title', '')

    # Get URI from playlist to derive the file path
    playlist = _vlc_http_get('/requests/playlist.json')
    filepath = None
    if playlist:
        def _find_current(node):
            if isinstance(node, dict):
                if node.get('current') == 'current':
                    uri = node.get('uri', '')
                    if uri.startswith('file://'):
                        return urllib.parse.unquote(uri[7:])
                for v in node.values():
                    result = _find_current(v)
                    if result:
                        return result
            elif isinstance(node, list):
                for item in node:
                    result = _find_current(item)
                    if result:
                        return result
            return None
        filepath = _find_current(playlist)

    if filepath:
        return {
            "status": "playing",
            "path":   filepath,
            "filename": filename or os.path.basename(filepath)
        }
    elif filename:
        return {"status": "playing", "path": None, "filename": filename}
    else:
        return {"status": "no_file", "path": None, "filename": None}

def delete_current_file(filePath: str) -> bool:
    """Move current file to trash folder."""
    try:
        # Ensure trash folder exists
        ensure_folder(TRASH_PATH)

        # Get just the filename
        filename = os.path.basename(filePath)
        destPath = os.path.join(TRASH_PATH, filename)

        # Handle duplicate filenames
        counter = 1
        while os.path.exists(destPath):
            name, ext = os.path.splitext(filename)
            destPath = os.path.join(TRASH_PATH, f"{name}_{counter}{ext}")
            counter += 1

        # Move the file
        shutil.move(filePath, destPath)
        return True

    except Exception as e:
        print(color_text(f"Error moving file: {e}", fg=RED))
        return False

def move_to_fav(filePath: str) -> bool:
    """Move current file to fav folder."""
    try:
        # Ensure fav folder exists
        ensure_folder(FAV_PATH)

        # Get just the filename
        filename = os.path.basename(filePath)
        destPath = os.path.join(FAV_PATH, filename)

        # Handle duplicate filenames
        counter = 1
        while os.path.exists(destPath):
            name, ext = os.path.splitext(filename)
            destPath = os.path.join(FAV_PATH, f"{name}_{counter}{ext}")
            counter += 1

        # Move the file
        shutil.move(filePath, destPath)
        return True

    except Exception as e:
        print(color_text(f"Error moving file: {e}", fg=RED))
        return False

def move_to_saved(filePath: str) -> bool:
    """Move current file to saved folder."""
    try:
        # Ensure saved folder exists
        ensure_folder(SAVED_PATH)

        # Get just the filename
        filename = os.path.basename(filePath)
        destPath = os.path.join(SAVED_PATH, filename)

        # Handle duplicate filenames
        counter = 1
        while os.path.exists(destPath):
            name, ext = os.path.splitext(filename)
            destPath = os.path.join(SAVED_PATH, f"{name}_{counter}{ext}")
            counter += 1

        # Move the file
        shutil.move(filePath, destPath)
        return True

    except Exception as e:
        print(color_text(f"Error moving file: {e}", fg=RED))
        return False

def move_to_saved_for_later(filePath: str) -> bool:
    """Move current file to savedForLater folder."""
    try:
        ensure_folder(SAVED_FOR_LATER_PATH)
        filename = os.path.basename(filePath)
        destPath = os.path.join(SAVED_FOR_LATER_PATH, filename)
        counter = 1
        while os.path.exists(destPath):
            name, ext = os.path.splitext(filename)
            destPath = os.path.join(SAVED_FOR_LATER_PATH, f"{name}_{counter}{ext}")
            counter += 1
        shutil.move(filePath, destPath)
        return True
    except Exception as e:
        print(color_text(f"Error moving file: {e}", fg=RED))
        return False

def move_to_subfolder(filePath: str, destFolder: str) -> bool:
    """Move a file to the specified destination folder."""
    try:
        ensure_folder(destFolder)
        filename = os.path.basename(filePath)
        destPath = os.path.join(destFolder, filename)
        counter = 1
        while os.path.exists(destPath):
            name, ext = os.path.splitext(filename)
            destPath = os.path.join(destFolder, f"{name}_{counter}{ext}")
            counter += 1
        shutil.move(filePath, destPath)
        return True
    except Exception as e:
        print(color_text(f"Error moving file: {e}", fg=RED))
        return False

def show_move_folder_menu() -> str | None:
    """Display a numbered list of subfolders from all configured base paths; return chosen path or None.

    Starts in short-list mode (folderShortList from config). Press [A] to toggle
    to the full folder list and back. Sources:
    - basePath / basePath1/2/3 — all subfolders scanned
    - folderRoot1/2 + folderNameArray1/2 — only named subfolders included
    """
    active_paths = [bp for bp in BASE_PATH_LIST if bp and os.path.isdir(bp)]
    active_pairs = [(r, n) for r, n in FOLDER_ROOT_PAIRS if r and n and os.path.isdir(r)]

    if not active_paths and not active_pairs:
        return None

    multi_base = (len(active_paths) + len(active_pairs)) > 1
    selected   = 0
    show_all   = False  # Start in short-list mode

    while True:
        # Rescan all sources on every redraw; list of (name, full_path, bp_label)
        all_folders = []
        # basePath / basePath1/2/3 — all subfolders
        for bp in active_paths:
            bp_label = os.path.basename(bp.rstrip('/'))
            try:
                for e in os.scandir(bp):
                    if e.is_dir():
                        all_folders.append((e.name, os.path.join(bp, e.name), bp_label))
            except Exception:
                continue
        # folderRoot1/2 — only named subfolders
        for root, names in active_pairs:
            root_label = os.path.basename(root.rstrip('/'))
            for name in names:
                full = os.path.join(root, name)
                if os.path.isdir(full):
                    all_folders.append((name, full, root_label))
        all_folders.sort(key=lambda x: x[0].lower())

        if not all_folders:
            return None

        # Apply short list filter — resolve each name in priority order:
        # basePath → basePath1 → basePath2 → basePath3 → folderRoot pairs.
        # Each name appears at most once (no duplicates across drives).
        if not show_all and FOLDER_SHORT_LIST:
            resolved = []
            seen = set()
            for name in FOLDER_SHORT_LIST:
                name_lower = name.lower()
                if name_lower in seen:
                    continue
                # Search base paths in order
                for bp in active_paths:
                    full = os.path.join(bp, name)
                    if os.path.isdir(full):
                        bp_label = os.path.basename(bp.rstrip('/'))
                        resolved.append((name, full, bp_label))
                        seen.add(name_lower)
                        break
                else:
                    # Fall through to folderRoot pairs
                    for root, names in active_pairs:
                        if any(n.lower() == name_lower for n in names):
                            full = os.path.join(root, name)
                            if os.path.isdir(full):
                                root_label = os.path.basename(root.rstrip('/'))
                                resolved.append((name, full, root_label))
                                seen.add(name_lower)
                                break
            resolved.sort(key=lambda x: x[0].lower())
            subfolders = resolved if resolved else all_folders
        else:
            subfolders = all_folders

        # Keep selection in bounds after a rescan or mode switch
        if selected >= len(subfolders):
            selected = len(subfolders) - 1

        check_resize()
        width = shutil.get_terminal_size().columns
        clear_screen()
        header("VLC Menu - Move to Folder", VERSION)
        print(color_text(f"  Mode: {'All Folders' if show_all else 'Short List'}", fg=CYAN))
        print()

        col_count = 2
        rows = (len(subfolders) + col_count - 1) // col_count
        for row in range(rows):
            line = ""
            for col in range(col_count):
                idx = row + col * rows
                if idx >= len(subfolders):
                    break
                name, full_path, bp_label = subfolders[idx]

                arrow = color_text("▶", fg=BRIGHT_YELLOW, style=BOLD) if idx == selected else " "
                num   = color_text(f"{idx + 1:2}.", fg=CYAN)

                if multi_base:
                    display = (name[:15] + "…") if len(name) > 16 else name
                    display = f"{display:<16}"
                    short_lbl = (bp_label[:9] + "…") if len(bp_label) > 10 else bp_label
                    lbl_str = color_text(f"[{short_lbl:<9}]", fg=MAGENTA)
                    if idx == selected:
                        item = color_text(display, fg=BRIGHT_YELLOW, style=BOLD)
                    else:
                        item = color_text(display, fg=WHITE)
                    line += f"  {arrow} {num} {item}{lbl_str}  "
                else:
                    display = (name[:19] + "…") if len(name) > 20 else name
                    display = f"{display:<20}"
                    if idx == selected:
                        item = color_text(display, fg=BRIGHT_YELLOW, style=BOLD)
                    else:
                        item = color_text(display, fg=WHITE)
                    line += f"  {arrow} {num} {item}   "
            print(line)

        print()
        print("-" * width)
        all_key_label = color_text("[A]", fg=BRIGHT_YELLOW, style=BOLD)
        all_key_text  = " Short List  " if show_all else " All Folders  "
        legend = (
            color_text("[↑/↓]", fg=BRIGHT_YELLOW, style=BOLD) + " Navigate  " +
            color_text("[Enter]", fg=BRIGHT_YELLOW, style=BOLD) + " Select  " +
            color_text("[#]", fg=BRIGHT_YELLOW, style=BOLD) + " Jump to #  " +
            all_key_label + all_key_text +
            color_text("[ESC/Q]", fg=BRIGHT_YELLOW, style=BOLD) + " Cancel"
        )
        print(legend)
        print("-" * width)
        print("Option: ", end='', flush=True)

        k = get_key()

        if k is None or check_resize():
            continue

        if k == "\x1b":
            return None

        if k == "\x1b[A":   # Up arrow
            selected = (selected - 1) % len(subfolders)
            continue

        if k == "\x1b[B":   # Down arrow
            selected = (selected + 1) % len(subfolders)
            continue

        if k in ("\r", "\n"):
            return subfolders[selected][1]  # full_path

        # Ignore any escape sequence that didn't match the arrow checks above.
        # Passing a partial CSI sequence (e.g. "\x1b[") to collect_input() sends
        # broken bytes to the terminal and causes it to freeze waiting for Enter.
        if not k or k.startswith("\x1b") or not k.isprintable():
            continue

        # Buffered numeric / q / a input
        raw = collect_input(k).strip().lower()
        if not raw:
            continue
        if raw == "q":
            return None
        if raw == "a":
            show_all = not show_all
            selected = 0
            continue
        if raw.isdigit():
            n = int(raw)
            if 1 <= n <= len(subfolders):
                return subfolders[n - 1][1]  # full_path
        # Any other input — ignore and redraw

def show_help():
    """Display the full key binding reference screen and wait for any key."""
    width = shutil.get_terminal_size().columns
    clear_screen()
    header("VLC Menu - Help", VERSION)
    print()
    print(color_text("  File Actions", fg=BRIGHT_YELLOW, style=BOLD))
    print(f"  {color_text('[R]', fg=BRIGHT_YELLOW, style=BOLD)}  Refresh        Redraw the management mode screen")
    print(f"  {color_text('[D]', fg=BRIGHT_YELLOW, style=BOLD)}  Delete         Move current file to trash and advance to next")
    print(f"  {color_text('[F]', fg=BRIGHT_YELLOW, style=BOLD)}  Fav            Move current file to fav folder and advance to next")
    print(f"  {color_text('[S]', fg=BRIGHT_YELLOW, style=BOLD)}  Save           Move current file to saved folder and advance to next")
    print(f"  {color_text('[L]', fg=BRIGHT_YELLOW, style=BOLD)}  Later          Move current file to savedForLater and advance to next (lowercase l)")
    print(f"  {color_text('[I]', fg=BRIGHT_YELLOW, style=BOLD)}  Move           Move current file to a chosen subfolder and advance to next")
    print(f"  {color_text('[O]', fg=BRIGHT_YELLOW, style=BOLD)}  Open Finder    Reveal currently playing file in Finder")
    print()
    print(color_text("  Playback Controls", fg=BRIGHT_YELLOW, style=BOLD))
    print(f"  {color_text('[Space]', fg=BRIGHT_YELLOW, style=BOLD)}  Pause/Resume   Toggle pause and play")
    print(f"  {color_text('[→]', fg=BRIGHT_YELLOW, style=BOLD)}  Next           Skip to next track")
    print(f"  {color_text('[←]', fg=BRIGHT_YELLOW, style=BOLD)}  Previous       Go to previous track")
    print(f"  {color_text('[↑]', fg=BRIGHT_YELLOW, style=BOLD)}  +15s           Seek forward 15 seconds")
    print(f"  {color_text('[↓]', fg=BRIGHT_YELLOW, style=BOLD)}  -15s           Seek back 15 seconds")
    print(f"  {color_text('[Shift+↑]', fg=BRIGHT_YELLOW, style=BOLD)}  Vol+       Increase volume (~10%)")
    print(f"  {color_text('[Shift+↓]', fg=BRIGHT_YELLOW, style=BOLD)}  Vol-       Decrease volume (~10%)")
    print(f"  {color_text('[W]', fg=BRIGHT_YELLOW, style=BOLD)}  Fullscreen     Toggle VLC fullscreen")
    print(f"  {color_text('[Tab]', fg=BRIGHT_YELLOW, style=BOLD)}  Shuffle       Toggle shuffle mode")
    print()
    print(color_text("  Application", fg=BRIGHT_YELLOW, style=BOLD))
    print(f"  {color_text('[Shift+M]', fg=BRIGHT_YELLOW, style=BOLD)}  Menu Toggle  Show/Hide Full Menu")
    print(f"  {color_text('[H]', fg=BRIGHT_YELLOW, style=BOLD)}  Help           Show this help screen")
    print(f"  {color_text('[E]', fg=BRIGHT_YELLOW, style=BOLD)}  Exit All       Stop VLC and exit the script")
    print(f"  {color_text('[Q]', fg=BRIGHT_YELLOW, style=BOLD)}  Quit           Exit the script (VLC keeps running)")
    print(f"  {color_text('[ESC]', fg=BRIGHT_YELLOW, style=BOLD)}  Exit All      Same as [E]")
    print()
    print("-" * width)
    print(color_text("  Press any key to return...", fg=CYAN))
    print("-" * width)
    get_key()

def remove_from_playlist(filePath: str) -> bool:
    """Remove a file from all XSPF playlist files in the playlist directory."""
    import xml.etree.ElementTree as ET
    from urllib.parse import quote, unquote

    if not PLAYLIST_DIR or not os.path.exists(PLAYLIST_DIR):
        return False

    # Create the file URI to match in playlist
    file_uri = f"file://{quote(filePath)}"
    removed_count = 0

    try:
        for filename in os.listdir(PLAYLIST_DIR):
            if not filename.endswith('.xspf'):
                continue

            playlist_path = os.path.join(PLAYLIST_DIR, filename)
            try:
                # Parse the XSPF file
                tree = ET.parse(playlist_path)
                root = tree.getroot()

                # XSPF namespace
                ns = {'xspf': 'http://xspf.org/ns/0/'}

                # Find trackList
                trackList = root.find('xspf:trackList', ns)
                if trackList is None:
                    # Try without namespace
                    trackList = root.find('trackList')
                    if trackList is None:
                        continue

                # Find and remove matching tracks
                tracks_to_remove = []
                for track in trackList:
                    location = track.find('xspf:location', ns)
                    if location is None:
                        location = track.find('location')
                    if location is not None and location.text:
                        # Compare URIs (handle encoding differences)
                        track_path = unquote(location.text.replace('file://', ''))
                        if track_path == filePath or location.text == file_uri:
                            tracks_to_remove.append(track)

                # Remove the tracks
                for track in tracks_to_remove:
                    trackList.remove(track)
                    removed_count += 1

                # Save if we removed anything
                if tracks_to_remove:
                    ET.indent(tree, space="  ")
                    tree.write(playlist_path, encoding='utf-8', xml_declaration=True)

            except ET.ParseError:
                continue
            except Exception:
                continue

        return removed_count > 0

    except Exception as e:
        print(color_text(f"Error updating playlist: {e}", fg=RED))
        return False

# -----------------------------------------------------------------------------
# Duplicate Finder Functions
# -----------------------------------------------------------------------------

def get_file_hash(filepath: str, block_size: int = 65536) -> str:
    """Calculate MD5 hash of a file."""
    hasher = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            for block in iter(lambda: f.read(block_size), b''):
                hasher.update(block)
        return hasher.hexdigest()
    except Exception:
        return None

def scan_media_files(folders: list, root: str) -> list:
    """Scan folders for media files and return list of file info dicts."""
    media_extensions = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg'}
    files = []

    for folder in folders:
        folder_path = os.path.join(root, folder)
        if not os.path.exists(folder_path):
            continue

        for filename in os.listdir(folder_path):
            if filename.startswith('.'):
                continue
            filepath = os.path.join(folder_path, filename)
            if os.path.isfile(filepath):
                ext = os.path.splitext(filename)[1].lower()
                if ext in media_extensions:
                    try:
                        size = os.path.getsize(filepath)
                        files.append({
                            'filename': filename,
                            'filepath': filepath,
                            'folder': folder,
                            'size': size,
                            'hash': None  # Computed lazily
                        })
                    except OSError:
                        continue
    return files

def find_duplicates_by_hash(files: list) -> list:
    """Find duplicate files by size and hash. Returns list of duplicate groups."""
    # Group files by size first (quick filter)
    size_groups = defaultdict(list)
    for f in files:
        size_groups[f['size']].append(f)

    # Only check hashes for files with same size
    duplicates = []
    total_to_hash = sum(len(group) for group in size_groups.values() if len(group) > 1)
    hashed_count = 0

    for size, group in size_groups.items():
        if len(group) < 2:
            continue

        # Compute hashes for this group
        hash_groups = defaultdict(list)
        for f in group:
            hashed_count += 1
            print(f"\r  Hashing file {hashed_count}/{total_to_hash}...", end='', flush=True)
            file_hash = get_file_hash(f['filepath'])
            if file_hash:
                f['hash'] = file_hash
                hash_groups[file_hash].append(f)

        # Add groups with duplicates
        for file_hash, hash_group in hash_groups.items():
            if len(hash_group) > 1:
                duplicates.append(hash_group)

    print()  # New line after progress
    return duplicates

def find_similar_filenames(files: list, threshold: float = 0.75) -> list:
    """Find files with similar names using fuzzy matching."""
    similar_groups = []
    processed = set()

    # Normalize filename for comparison (remove extension, numbers, special chars)
    def normalize(name):
        base = os.path.splitext(name)[0].lower()
        # Remove common suffixes like _1, -copy, (1), etc.
        import re
        base = re.sub(r'[-_\s]*(copy|\d+|\(\d+\))[-_\s]*$', '', base, flags=re.IGNORECASE)
        return base

    total = len(files)
    for i, f1 in enumerate(files):
        if f1['filepath'] in processed:
            continue

        print(f"\r  Comparing file {i+1}/{total}...", end='', flush=True)
        group = [f1]
        norm1 = normalize(f1['filename'])

        for f2 in files[i+1:]:
            if f2['filepath'] in processed:
                continue

            norm2 = normalize(f2['filename'])

            # Check similarity ratio
            ratio = difflib.SequenceMatcher(None, norm1, norm2).ratio()
            if ratio >= threshold:
                group.append(f2)
                processed.add(f2['filepath'])

        if len(group) > 1:
            similar_groups.append(group)
            processed.add(f1['filepath'])

    print()  # New line after progress
    return similar_groups

def format_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"

def display_and_delete_duplicates(duplicate_groups: list, title: str) -> int:
    """Display duplicate groups and allow user to delete. Returns count of deleted files."""
    if not duplicate_groups:
        print(color_text("\nNo duplicates found.", fg=GREEN))
        return 0

    total_deleted = 0
    width = shutil.get_terminal_size().columns

    for group_idx, group in enumerate(duplicate_groups):
        clear_screen()
        header("VLC Menu - Duplicate Finder", VERSION)

        print(color_text(f"\n{title}", fg=CYAN, style=BOLD))
        print(f"Group {group_idx + 1} of {len(duplicate_groups)}")
        print("-" * width)

        # Display files in this group
        print(color_text("\nFiles in this group:", fg=YELLOW))
        for idx, f in enumerate(group):
            size_str = format_size(f['size'])
            print(f"\n  {color_text(str(idx + 1), fg=BRIGHT_YELLOW, style=BOLD)}. {f['filename']}")
            print(f"     Folder: {f['folder']}")
            print(f"     Size: {size_str}")
            if f.get('hash'):
                print(f"     Hash: {f['hash'][:16]}...")

        print("\n" + "-" * width)
        print(color_text("\nOptions:", fg=CYAN))
        print(f"  Enter file number(s) to {color_text('DELETE', fg=RED)} (comma-separated, e.g., 2,3)")
        print(f"  {color_text('K', fg=BRIGHT_YELLOW)} = Keep all (skip this group)")
        print(f"  {color_text('Q/ESC', fg=BRIGHT_YELLOW)} = Quit duplicate finder")
        print(f"\n  {color_text('Tip:', fg=CYAN)} Keep file #1 (original), delete others")

        choice = get_menu_input("\nOption: ")

        if choice == 'Q':
            print(color_text("\nExiting duplicate finder...", fg=YELLOW))
            break
        elif choice == 'K' or choice == '':
            print(color_text("Keeping all files in this group.", fg=GREEN))
            continue
        else:
            # Parse file numbers to delete
            try:
                nums = [int(x.strip()) for x in choice.split(',')]
                files_to_delete = []
                for num in nums:
                    if 1 <= num <= len(group):
                        files_to_delete.append(group[num - 1])
                    else:
                        print(color_text(f"Invalid number: {num}", fg=RED))

                if files_to_delete:
                    print(color_text(f"\nDeleting {len(files_to_delete)} file(s)...", fg=YELLOW))
                    for f in files_to_delete:
                        if delete_current_file(f['filepath']):
                            print(color_text(f"  Moved to trash: {f['filename']}", fg=GREEN))
                            total_deleted += 1
                        else:
                            print(color_text(f"  Failed to delete: {f['filename']}", fg=RED))

                    import time
                    time.sleep(1)
            except ValueError:
                print(color_text("Invalid input. Skipping this group.", fg=RED))
                import time
                time.sleep(1)

    return total_deleted

def clean_up_trash():
    """Confirm and permanently delete all files in the Trash subfolder."""
    import time

    clear_screen()
    header("VLC Menu - Clean Up Trash", VERSION)

    if not check_base_path_accessible():
        input(color_text("\nPress Enter to return...", fg=YELLOW))
        return

    if not os.path.exists(TRASH_PATH):
        print(color_text(f"\nTrash folder does not exist: {shorten_path(TRASH_PATH)}", fg=YELLOW))
        input(color_text("\nPress Enter to return...", fg=YELLOW))
        return

    # Collect all items in trash
    all_items = []
    total_size = 0
    for entry in os.scandir(TRASH_PATH):
        if entry.is_file(follow_symlinks=False):
            try:
                size = entry.stat().st_size
            except OSError:
                size = 0
            all_items.append(('file', entry.path, size))
            total_size += size
        elif entry.is_dir(follow_symlinks=False):
            all_items.append(('dir', entry.path, 0))

    file_count = sum(1 for kind, _, _ in all_items if kind == 'file')

    if file_count == 0 and not all_items:
        print(color_text("\nTrash folder is already empty.", fg=GREEN))
        input(color_text("\nPress Enter to return...", fg=YELLOW))
        return

    width = shutil.get_terminal_size().columns
    print()
    print(f"  Trash folder: {color_text(shorten_path(TRASH_PATH), fg=CYAN)}")
    print(f"  Files to delete: {color_text(str(file_count), fg=RED, style=BOLD)}")
    print(f"  Total size: {color_text(format_size(total_size), fg=RED, style=BOLD)}")
    print()
    print("-" * width)
    print(color_text("  This will permanently delete all files in the Trash folder.", fg=RED, style=BOLD))
    print("-" * width)
    print()
    print(f"  {color_text('Y', fg=BRIGHT_YELLOW, style=BOLD)} = Yes, permanently delete all trash files")
    print(f"  {color_text('N/ESC', fg=BRIGHT_YELLOW, style=BOLD)} = Cancel")

    choice = get_menu_input("\nConfirm: ")
    if choice != 'Y':
        print(color_text("\nCancelled. No files were deleted.", fg=YELLOW))
        time.sleep(1)
        return

    # Delete all files; remove empty subdirectories afterward
    deleted = 0
    failed = 0
    print()
    for kind, path, _ in all_items:
        if kind == 'file':
            try:
                os.remove(path)
                deleted += 1
            except Exception as e:
                print(color_text(f"  Failed to delete {os.path.basename(path)}: {e}", fg=RED))
                failed += 1

    # Remove leftover empty directories
    for kind, path, _ in all_items:
        if kind == 'dir':
            try:
                shutil.rmtree(path)
            except Exception:
                pass

    print()
    if failed == 0:
        print(color_text(f"  Deleted {deleted} file(s) successfully.", fg=GREEN, style=BOLD))
    else:
        print(color_text(f"  Deleted {deleted} file(s). {failed} failed.", fg=YELLOW, style=BOLD))

    time.sleep(1.5)


def duplicate_finder_menu():
    """Main duplicate finder menu."""
    if not check_base_path_accessible():
        input(color_text("\nPress Enter to return...", fg=YELLOW))
        return

    # Load config to get folders
    config = load_json_config(CONFIG_PATH)
    if not config or 'profiles' not in config:
        print(color_text("Error: Could not load config.", fg=RED))
        input(color_text("\nPress Enter to return...", fg=YELLOW))
        return

    # Collect all unique folders from all profiles
    all_folders = set()
    all_extra_paths = set()
    root = None
    for profile in config['profiles']:
        if root is None:
            root = profile.get('FOLDER_ROOT', BASE_PATH)
        for folder in profile.get('FOLDER_NAME_ARRAY', []):
            all_folders.add(folder)
        for ep in profile.get('EXTRA_PATHS', []):
            all_extra_paths.add(os.path.expanduser(ep))

    if not all_folders and not all_extra_paths:
        print(color_text("Error: No folders found in profiles.", fg=RED))
        input(color_text("\nPress Enter to return...", fg=YELLOW))
        return

    width = shutil.get_terminal_size().columns

    # Phase 1: Hash-based duplicate detection
    clear_screen()
    header("VLC Menu - Duplicate Finder", VERSION)

    print(color_text("\n=== PHASE 1: Find Exact Duplicates (by file hash) ===", fg=CYAN, style=BOLD))
    print(f"\nScanning {len(all_folders) + len(all_extra_paths)} folders...")
    print(f"Root: {root}")

    files = scan_media_files(list(all_folders), root)
    # Also scan extra absolute paths from all profiles
    if all_extra_paths:
        files.extend(scan_media_files(list(all_extra_paths), ""))
    print(color_text(f"\nFound {len(files)} media files.", fg=GREEN))

    if len(files) < 2:
        print(color_text("Not enough files to check for duplicates.", fg=YELLOW))
        input(color_text("\nPress Enter to return...", fg=YELLOW))
        return

    print(color_text("\nSearching for exact duplicates (same content)...", fg=YELLOW))
    hash_duplicates = find_duplicates_by_hash(files)

    if hash_duplicates:
        print(color_text(f"\nFound {len(hash_duplicates)} group(s) of exact duplicates!", fg=RED, style=BOLD))
        input(color_text("\nPress Enter to review and delete...", fg=YELLOW))
        deleted = display_and_delete_duplicates(hash_duplicates, "EXACT DUPLICATES (identical files)")
        print(color_text(f"\nDeleted {deleted} file(s) in Phase 1.", fg=CYAN))
    else:
        print(color_text("\nNo exact duplicates found.", fg=GREEN))

    # Phase 2: Ask about filename similarity search
    print("\n" + "-" * width)
    print(color_text("\n=== PHASE 2: Find Similar Filenames ===", fg=CYAN, style=BOLD))
    print("\nThis will find files with similar names (e.g., movie.mp4 vs movie1.mp4)")
    print(f"\n{color_text('Y', fg=BRIGHT_YELLOW)} = Yes, search for similar filenames")
    print(f"{color_text('N/ESC', fg=BRIGHT_YELLOW)} = No, exit duplicate finder")

    choice = get_menu_input("\nOption: ")

    if choice != 'Y':
        print(color_text("\nDuplicate finder complete.", fg=GREEN))
        input(color_text("\nPress Enter to return...", fg=YELLOW))
        return

    # Re-scan files (in case some were deleted)
    clear_screen()
    header("VLC Menu - Duplicate Finder", VERSION)
    print(color_text("\n=== PHASE 2: Find Similar Filenames ===", fg=CYAN, style=BOLD))

    print(f"\nRe-scanning folders...")
    files = scan_media_files(list(all_folders), root)
    if all_extra_paths:
        files.extend(scan_media_files(list(all_extra_paths), ""))
    print(color_text(f"Found {len(files)} media files.", fg=GREEN))

    print(color_text("\nSearching for similar filenames...", fg=YELLOW))
    similar_groups = find_similar_filenames(files)

    if similar_groups:
        print(color_text(f"\nFound {len(similar_groups)} group(s) with similar filenames!", fg=YELLOW, style=BOLD))
        input(color_text("\nPress Enter to review...", fg=YELLOW))
        deleted = display_and_delete_duplicates(similar_groups, "SIMILAR FILENAMES (possibly same content)")
        print(color_text(f"\nDeleted {deleted} file(s) in Phase 2.", fg=CYAN))
    else:
        print(color_text("\nNo similar filenames found.", fg=GREEN))

    print(color_text("\n=== Duplicate Finder Complete ===", fg=GREEN, style=BOLD))
    input(color_text("\nPress Enter to return to menu...", fg=YELLOW))

def display_current_file() -> int:
    """Display current VLC status in compact format. Returns number of lines printed."""
    fileInfo = get_vlc_current_file()
    lines = 0

    if fileInfo["status"] == "not_running":
        print(color_text("CURRENT: VLC is not running", fg=YELLOW))
        lines = 1
    elif fileInfo["status"] == "no_file":
        print(color_text("CURRENT: VLC running — no file playing", fg=YELLOW))
        lines = 1
    elif fileInfo["status"] == "playing":
        print(color_text(f"CURRENT: {fileInfo['filename']}", fg=GREEN))
        lines = 1
        if fileInfo['path']:
            folder_path = os.path.dirname(fileInfo['path'])
            print(color_text(f"    {shorten_path(folder_path)}", fg=GREEN))
            lines += 1
        info = vlc_get_playback_info()
        parts = []
        if info and info['duration'] > 0:
            pos = _format_seconds(info['current_time'])
            dur = _format_seconds(info['duration'])
            parts.append(f"Length: {color_text(pos, fg=CYAN)} / {color_text(dur, fg=CYAN)}")
        fs_state = vlc_get_fullscreen_state()
        fs_label = color_text("On", fg=BRIGHT_YELLOW, style=BOLD) if fs_state else color_text("Off", fg=WHITE)
        parts.append(f"Fullscreen: {fs_label}")
        parts.append(f"Port: {color_text(str(HTTP_PORT), fg=CYAN)}")
        print(" | ".join(parts))
        lines += 1
    else:
        print(color_text(f"CURRENT: Error — {fileInfo.get('error', 'Unknown error')}", fg=RED))
        lines = 1

    return lines

def check_base_path_accessible() -> bool:
    """Check if the base path (volume) is accessible/mounted."""
    if not BASE_PATH:
        print(color_text("\nError: Base path not configured.", fg=RED, style=BOLD))
        return False

    if not os.path.exists(BASE_PATH):
        print(color_text(f"\nError: Base path not accessible: {BASE_PATH}", fg=RED, style=BOLD))
        print(color_text("The volume may not be mounted.", fg=YELLOW))
        print(color_text("\nPlease ensure the volume is mounted and try again.", fg=YELLOW))
        return False

    return True

def management_mode():
    """Management mode: compact status at top, menu pinned to bottom of terminal."""
    import time

    menu_expanded = False  # Shift+L toggles between compact and full menu

    while True:
        check_resize()

        term_size = shutil.get_terminal_size()
        width = term_size.columns
        height = term_size.lines

        # header() calls clear_screen() internally and prints 3 lines (=, title, =)
        header("VLC Menu - Management Mode", VERSION)

        # Compact status block — returns number of lines printed
        status_lines = display_current_file()

        # feedback_row: where action messages will appear (right below status)
        feedback_row = 4 + status_lines  # 3 header lines + status_lines, 1-indexed

        # --- Build menu strings ---
        menu_compact = (
            color_text("[R]", fg=BRIGHT_YELLOW, style=BOLD) + " Refresh  " +
            color_text("[D]", fg=BRIGHT_YELLOW, style=BOLD) + " Delete  " +
            color_text("[F]", fg=BRIGHT_YELLOW, style=BOLD) + " Fav  " +
            color_text("[S]", fg=BRIGHT_YELLOW, style=BOLD) + " Save  " +
            color_text("[I]", fg=BRIGHT_YELLOW, style=BOLD) + " Move  " +
            color_text("[Shift+M]", fg=BRIGHT_YELLOW, style=BOLD) + " Menu Toggle"
        )
        exp_line1 = menu_compact
        exp_line2 = (
            color_text("[O]", fg=BRIGHT_YELLOW, style=BOLD) + " Open in Finder  " +
            color_text("[W]", fg=BRIGHT_YELLOW, style=BOLD) + " Fullscreen  " +
            color_text("[Space]", fg=BRIGHT_YELLOW, style=BOLD) + " Pause"
        )
        exp_line3 = (
            color_text("[→]", fg=BRIGHT_YELLOW, style=BOLD) + " Next  " +
            color_text("[←]", fg=BRIGHT_YELLOW, style=BOLD) + " Prev  " +
            color_text("[↑]", fg=BRIGHT_YELLOW, style=BOLD) + " +15s  " +
            color_text("[↓]", fg=BRIGHT_YELLOW, style=BOLD) + " -15s  " +
            color_text("[Shift+↑/↓]", fg=BRIGHT_YELLOW, style=BOLD) + " Volume  " +
            color_text("[Tab]", fg=BRIGHT_YELLOW, style=BOLD) + " Shuffle  " +
            color_text("[Q]", fg=BRIGHT_YELLOW, style=BOLD) + " Quit"
        )
        exp_line4 = (
            color_text("[L]", fg=BRIGHT_YELLOW, style=BOLD) + " Later  " +
            color_text("[I]", fg=BRIGHT_YELLOW, style=BOLD) + " Move  " +
            color_text("[H]", fg=BRIGHT_YELLOW, style=BOLD) + " Help  " +
            color_text("[E]", fg=BRIGHT_YELLOW, style=BOLD) + " Exit All"
        )

        # compact = separator + 1 line; expanded = separator + 4 lines + separator
        menu_height = 6 if menu_expanded else 2

        # Pin menu to bottom; never overlap the status block
        menu_start_row = max(height - menu_height + 1, feedback_row + 1)

        sys.stdout.write(f"\033[{menu_start_row};1H")
        sys.stdout.flush()
        print("-" * width)
        if menu_expanded:
            print(exp_line1)
            print(exp_line2)
            print(exp_line3)
            print(exp_line4)
            print("-" * width)
        else:
            print(menu_compact)

        # Park cursor at feedback row so action messages don't disturb the menu
        sys.stdout.write(f"\033[{feedback_row};1H")
        sys.stdout.flush()

        choice = get_key()

        if choice is None or check_resize():
            continue

        if choice == "\x1b":
            show_exit_screen()

        # Shift+M (uppercase M) = menu toggle; L/l = Later
        if choice == "M":
            action = "menu_toggle"
        elif choice in ("l", "L"):
            action = "later"
        else:
            choice_upper = choice.upper() if choice else ""
            if choice_upper == "Q":
                action = "quit"
            elif choice_upper == "R":
                action = "refresh"
            elif choice_upper == "D":
                action = "delete"
            elif choice_upper == "F":
                action = "fav"
            elif choice_upper == "S":
                action = "save"
            elif choice_upper == "O":
                action = "open_finder"
            elif choice_upper == "W":
                action = "fullscreen"
            elif choice_upper == "H":
                action = "help"
            elif choice_upper == "E":
                action = "exit_all"
            elif choice_upper == "I":
                action = "move_to_folder"
            elif choice == " ":
                action = "pause"
            elif choice == "\t":
                action = "shuffle"
            elif choice == "\x1b[C":
                action = "next"
            elif choice == "\x1b[D":
                action = "previous"
            elif choice == "\x1b[A":
                action = "seek_forward"
            elif choice == "\x1b[B":
                action = "seek_back"
            elif choice == "\x1b[1;2A":
                action = "volume_up"
            elif choice == "\x1b[1;2B":
                action = "volume_down"
            else:
                continue

        # Execute the action
        if action == "menu_toggle":
            menu_expanded = not menu_expanded
            continue

        elif action == "quit":
            clear_screen()
            header("VLC Menu", VERSION)
            print(color_text("VLC Menu exiting...\n", fg=CYAN))
            print(color_text(f"Copyright © 2026 Cloud Box 9 Inc. All rights reserved.\n", fg=GREEN))
            sys.exit(0)

        elif action == "refresh":
            continue

        elif action == "pause":
            print(color_text("Toggling pause/play...", fg=CYAN))
            vlc_pause()
            time.sleep(0.5)
            continue

        elif action == "next":
            print(color_text("Next track...", fg=CYAN))
            vlc_next_track()
            time.sleep(0.5)
            continue

        elif action == "previous":
            print(color_text("Previous track...", fg=CYAN))
            vlc_previous_track()
            time.sleep(0.5)
            continue

        elif action == "seek_forward":
            vlc_seek(15)
            info = vlc_get_playback_info()
            if info:
                pos = _format_seconds(info['current_time'])
                dur = _format_seconds(info['duration'])
                print(color_text(f"  ⏩ +15s  →  {pos} / {dur}  —  {info['title']}", fg=CYAN))
            continue

        elif action == "seek_back":
            vlc_seek(-15)
            info = vlc_get_playback_info()
            if info:
                pos = _format_seconds(info['current_time'])
                dur = _format_seconds(info['duration'])
                print(color_text(f"  ⏪ -15s  →  {pos} / {dur}  —  {info['title']}", fg=CYAN))
            continue

        elif action == "volume_up":
            new_vol = vlc_volume_adjust(VOLUME_STEP)
            if new_vol >= 0:
                print(color_text(f"  🔊 Volume: {round(new_vol / 256 * 100)}%", fg=CYAN))
            continue

        elif action == "volume_down":
            new_vol = vlc_volume_adjust(-VOLUME_STEP)
            if new_vol >= 0:
                print(color_text(f"  🔉 Volume: {round(new_vol / 256 * 100)}%", fg=CYAN))
            continue

        elif action == "shuffle":
            print(color_text("Toggling shuffle...", fg=CYAN))
            vlc_shuffle()
            time.sleep(0.5)
            continue

        elif action == "fullscreen":
            vlc_fullscreen()
            time.sleep(0.3)
            fs_state = vlc_get_fullscreen_state()
            print(color_text(f"Fullscreen: {'On' if fs_state else 'Off'}", fg=CYAN))
            time.sleep(0.5)
            continue

        elif action == "open_finder":
            fileInfo = get_vlc_current_file()
            if fileInfo["status"] == "playing" and fileInfo["path"]:
                print(color_text(f"Opening in Finder: {fileInfo['filename']}", fg=CYAN))
                open_in_finder(fileInfo["path"])
                time.sleep(0.5)
            else:
                print(color_text("No file currently playing.", fg=RED, style=BOLD))
                time.sleep(1)
            continue

        elif action == "delete":
            if not check_base_path_accessible():
                time.sleep(2)
                continue

            fileInfo = get_vlc_current_file()
            if fileInfo["status"] == "playing" and fileInfo["path"]:
                print(color_text(f"Deleting: {fileInfo['filename']}", fg=YELLOW, style=BOLD))
                print(color_text(f"Path: {shorten_path(fileInfo['path'])}", fg=YELLOW))
                print(color_text("Advancing to next track...", fg=CYAN))
                vlc_next_track()
                time.sleep(0.5)

                if delete_current_file(fileInfo["path"]):
                    remove_from_playlist(fileInfo["path"])
                    print(color_text("File moved to trash successfully!", fg=GREEN, style=BOLD))
                    time.sleep(1.5)
                else:
                    print(color_text("Failed to move file to trash.", fg=RED, style=BOLD))
                    time.sleep(1.5)
            else:
                print(color_text("No file currently playing to delete.", fg=RED, style=BOLD))
                time.sleep(1.5)

        elif action == "fav":
            if not check_base_path_accessible():
                time.sleep(2)
                continue

            fileInfo = get_vlc_current_file()
            if fileInfo["status"] == "playing" and fileInfo["path"]:
                print(color_text(f"Moving to Favorites: {fileInfo['filename']}", fg=YELLOW, style=BOLD))
                print(color_text(f"Path: {shorten_path(fileInfo['path'])}", fg=YELLOW))
                print(color_text("Advancing to next track...", fg=CYAN))
                vlc_next_track()
                time.sleep(0.5)

                if move_to_fav(fileInfo["path"]):
                    remove_from_playlist(fileInfo["path"])
                    print(color_text("File moved to fav folder successfully!", fg=GREEN, style=BOLD))
                    time.sleep(1.5)
                else:
                    print(color_text("Failed to move file to fav folder.", fg=RED, style=BOLD))
                    time.sleep(1.5)
            else:
                print(color_text("No file currently playing to move.", fg=RED, style=BOLD))
                time.sleep(1.5)

        elif action == "save":
            if not check_base_path_accessible():
                time.sleep(2)
                continue

            fileInfo = get_vlc_current_file()
            if fileInfo["status"] == "playing" and fileInfo["path"]:
                print(color_text(f"Saving: {fileInfo['filename']}", fg=YELLOW, style=BOLD))
                print(color_text(f"Path: {shorten_path(fileInfo['path'])}", fg=YELLOW))
                print(color_text("Advancing to next track...", fg=CYAN))
                vlc_next_track()
                time.sleep(0.5)

                if move_to_saved(fileInfo["path"]):
                    # Remove from playlist files
                    remove_from_playlist(fileInfo["path"])
                    print(color_text("File moved to saved folder successfully!", fg=GREEN, style=BOLD))
                    time.sleep(1.5)
                else:
                    print(color_text("Failed to move file to saved folder.", fg=RED, style=BOLD))
                    time.sleep(1.5)
            else:
                print(color_text("No file currently playing to save.", fg=RED, style=BOLD))
                time.sleep(1.5)

        elif action == "later":
            if not check_base_path_accessible():
                time.sleep(2)
                continue

            fileInfo = get_vlc_current_file()
            if fileInfo["status"] == "playing" and fileInfo["path"]:
                print(color_text(f"Moving to Later: {fileInfo['filename']}", fg=YELLOW, style=BOLD))
                print(color_text(f"Path: {shorten_path(fileInfo['path'])}", fg=YELLOW))
                print(color_text("Advancing to next track...", fg=CYAN))
                vlc_next_track()
                time.sleep(0.5)

                if move_to_saved_for_later(fileInfo["path"]):
                    remove_from_playlist(fileInfo["path"])
                    print(color_text("File moved to savedForLater successfully!", fg=GREEN, style=BOLD))
                    time.sleep(1.5)
                else:
                    print(color_text("Failed to move file to savedForLater.", fg=RED, style=BOLD))
                    time.sleep(1.5)
            else:
                print(color_text("No file currently playing to move.", fg=RED, style=BOLD))
                time.sleep(1.5)

        elif action == "move_to_folder":
            if not check_base_path_accessible():
                time.sleep(2)
                continue

            fileInfo = get_vlc_current_file()
            if fileInfo["status"] == "playing" and fileInfo["path"]:
                destFolder = show_move_folder_menu()
                if destFolder is None:
                    # User cancelled — redraw management mode
                    continue
                print(color_text(f"Moving: {fileInfo['filename']}", fg=YELLOW, style=BOLD))
                print(color_text(f"  To: {shorten_path(destFolder)}", fg=YELLOW))
                print(color_text("Advancing to next track...", fg=CYAN))
                vlc_next_track()
                time.sleep(0.5)
                if move_to_subfolder(fileInfo["path"], destFolder):
                    remove_from_playlist(fileInfo["path"])
                    print(color_text(f"File moved to {os.path.basename(destFolder)} successfully!", fg=GREEN, style=BOLD))
                    time.sleep(1.5)
                else:
                    print(color_text("Failed to move file.", fg=RED, style=BOLD))
                    time.sleep(1.5)
            else:
                print(color_text("No file currently playing to move.", fg=RED, style=BOLD))
                time.sleep(1.5)

        elif action == "help":
            show_help()
            continue

        elif action == "exit_all":
            stop_vlc()
            show_exit_screen()

# -----------------------------------------------------------------------------
# Load Configuration
# -----------------------------------------------------------------------------

def load_config():
    """Load vlcmenuconfig.json configuration."""
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

# -----------------------------------------------------------------------------
# XSPF Playlist Creation
# -----------------------------------------------------------------------------

def create_xspf_playlist(media_files, playlist_path):
    """Create XSPF playlist file for VLC."""
    import xml.etree.ElementTree as ET
    from urllib.parse import quote

    # Create XSPF structure
    playlist = ET.Element('playlist', version="1", xmlns="http://xspf.org/ns/0/")
    title = ET.SubElement(playlist, 'title')
    title.text = os.path.basename(playlist_path)

    trackList = ET.SubElement(playlist, 'trackList')

    for file_path in media_files:
        track = ET.SubElement(trackList, 'track')
        location = ET.SubElement(track, 'location')
        # Convert file path to file:// URI
        location.text = f"file://{quote(file_path)}"

    # Write to file
    tree = ET.ElementTree(playlist)
    ET.indent(tree, space="  ")
    tree.write(playlist_path, encoding='utf-8', xml_declaration=True)

# -----------------------------------------------------------------------------
# VLC Profile Runner
# -----------------------------------------------------------------------------

def run_profile(profile):
    """
    Run VLC with media files from profile configuration.
    Creates XSPF playlist and opens it with VLC.
    Saves playlist to the configured base path (PLAYLIST_DIR global).

    Note: Only folders explicitly listed in FOLDER_NAME_ARRAY are scanned.
    The 'fav' folder is only included if it's in FOLDER_NAME_ARRAY.
    Hidden files and files starting with . are excluded from playlists.
    """
    # Check if base path (volume) is accessible before proceeding
    if not check_base_path_accessible():
        input(color_text("\nPress Enter to return to menu...", fg=YELLOW))
        return

    root = profile['FOLDER_ROOT']
    folders = profile['FOLDER_NAME_ARRAY']
    extra_paths = profile.get('EXTRA_PATHS', [])
    playlist_name = profile.get('PLAYLIST_NAME', 'playlist.xspf')

    # Ensure playlist directory exists
    ensure_folder(PLAYLIST_DIR)
    playlist_path = os.path.join(PLAYLIST_DIR, playlist_name)

    media_files = []
    # Only scan folders explicitly listed in FOLDER_NAME_ARRAY
    for folder in folders:
        full_path = os.path.join(root, folder)
        if os.path.exists(full_path):
            # Collect all files in the targeted folder, excluding hidden files
            files = [os.path.join(full_path, f) for f in os.listdir(full_path)
                    if os.path.isfile(os.path.join(full_path, f)) and not f.startswith('.')]
            media_files.extend(files)

    # Scan extra absolute paths (EXTRA_PATHS)
    for extra_path in extra_paths:
        full_path = os.path.expanduser(extra_path)
        if os.path.exists(full_path):
            files = [os.path.join(full_path, f) for f in os.listdir(full_path)
                    if os.path.isfile(os.path.join(full_path, f)) and not f.startswith('.')]
            media_files.extend(files)

    if not media_files:
        print(color_text("\nNo files found in specified folders.", fg=RED, style=BOLD))
        return

    # Shuffle the media files before building the playlist
    random.shuffle(media_files)

    print(color_text(f"\nCreating playlist with {len(media_files)} items (shuffled)...", fg=YELLOW))

    # Create XSPF playlist file
    create_xspf_playlist(media_files, playlist_path)

    print(color_text(f"Playlist saved to: {shorten_path(playlist_path)}", fg=CYAN))
    print(color_text(f"Opening playlist in VLC...", fg=YELLOW))

    # Launch VLC with HTTP interface for this session's port
    global _vlc_process
    _vlc_process = subprocess.Popen(
        [
            VLC_PATH,
            '--extraintf', 'http',
            '--http-host',     HTTP_HOST,
            '--http-port',     str(HTTP_PORT),
            '--http-password', HTTP_PASSWORD,
            playlist_path
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    # Wait for VLC HTTP interface to come up, then resize and return focus
    import time
    if not wait_for_vlc_http(timeout=10.0):
        print(color_text("Warning: VLC HTTP interface did not respond in time.", fg=YELLOW))
    time.sleep(0.3)

    # Enable shuffle before playback begins
    vlc_shuffle()
    print(color_text("Shuffle enabled.", fg=CYAN))

    focus_terminal()

    print(color_text(f"Loaded {len(media_files)} items into VLC.", fg=GREEN, style=BOLD))

# -----------------------------------------------------------------------------
# Display Profiles
# -----------------------------------------------------------------------------

def display_profiles(profiles, selected_index=None):
    """Display all available VLC profiles using CB9Lib colors.

    Profiles with "hidden": true are not displayed but can still be selected by number.
    """
    header("VLC Menu", VERSION, "Available VLC Profiles")

    width = shutil.get_terminal_size().columns
    displayed_count = 0

    for i, profile in enumerate(profiles):
        # Skip hidden profiles in display (but they're still selectable by number)
        if profile.get('hidden', False):
            continue

        displayed_count += 1

        # Highlight the selected profile
        if selected_index is not None and i == selected_index:
            arrow = color_text("▶", fg=BRIGHT_YELLOW, style=BOLD)
            profile_num = color_text(str(i + 1), fg=BRIGHT_YELLOW, style=BOLD)
            profile_title = color_text(profile['title'], fg=BRIGHT_YELLOW, style=BOLD)
            print(f"{arrow} {profile_num}. {profile_title} → {color_text(', '.join(profile['FOLDER_NAME_ARRAY']), fg=BRIGHT_YELLOW)}")

        else:
            profile_num = color_text(str(i + 1), fg=BRIGHT_YELLOW, style=BOLD)
            profile_title = color_text(profile['title'], fg=WHITE, style=BOLD)
            print(f"  {profile_num}. {profile_title} → {', '.join(profile['FOLDER_NAME_ARRAY'])}")

    # Separator line after the last visible item
    if displayed_count > 0:
        print("-" * width)

# -----------------------------------------------------------------------------
# Profile Info Display
# -----------------------------------------------------------------------------

def show_profile_info(profile):
    """Display detailed profile information."""
    clear_screen()
    header("VLC Menu", VERSION, "Profile Information")

    print(f"\n{color_text(profile.get('title', 'N/A'), fg=BRIGHT_YELLOW, style=BOLD)}\n")

    print(f"{color_text('Folder Root:', fg=YELLOW, style=BOLD)} {shorten_path(profile.get('FOLDER_ROOT', 'N/A'))}")
    print(f"{color_text('Folders:', fg=YELLOW, style=BOLD)} {', '.join(profile.get('FOLDER_NAME_ARRAY', []))}")
    extra_paths = profile.get('EXTRA_PATHS', [])
    if extra_paths:
        print(f"{color_text('Extra Paths:', fg=YELLOW, style=BOLD)}")
        for ep in extra_paths:
            print(f"  {shorten_path(ep)}")
    print(f"{color_text('Playlist Name:', fg=YELLOW, style=BOLD)} {profile.get('PLAYLIST_NAME', 'N/A')}")

    # Count files if possible
    root = profile.get('FOLDER_ROOT', '')
    folders = profile.get('FOLDER_NAME_ARRAY', [])
    file_count = 0
    for folder in folders:
        full_path = os.path.join(root, folder)
        if os.path.exists(full_path):
            files = [f for f in os.listdir(full_path)
                    if os.path.isfile(os.path.join(full_path, f)) and not f.startswith('.')]
            file_count += len(files)
    for ep in extra_paths:
        full_path = os.path.expanduser(ep)
        if os.path.exists(full_path):
            files = [f for f in os.listdir(full_path)
                    if os.path.isfile(os.path.join(full_path, f)) and not f.startswith('.')]
            file_count += len(files)

    print(f"{color_text('Total Files:', fg=YELLOW, style=BOLD)} {file_count}")

# -----------------------------------------------------------------------------
# Interactive Menu
# -----------------------------------------------------------------------------

def show_exit_screen():
    """Display the exit screen and exit the script."""
    clear_screen()
    header("VLC Menu", VERSION)
    print(color_text("VLC Menu exiting...\n", fg=CYAN))
    print(color_text("Copyright © 2026 Cloud Box 9 Inc. All rights reserved.\n", fg=GREEN))
    sys.exit(0)


def collect_input(first_char: str = "") -> str:
    """Collect input characters until Enter. Exits script if ESC pressed."""
    input_str = first_char
    if first_char:
        print(first_char, end='', flush=True)

    while True:
        k = get_key()
        if k == "\r" or k == "\n":
            print()  # New line after Enter
            return input_str
        elif k == "\x1b":  # ESC exits script immediately
            show_exit_screen()
        elif k == "\x7f" or k == "\b":  # Backspace
            if input_str:
                input_str = input_str[:-1]
                print("\b \b", end='', flush=True)
        elif k and k.isprintable():
            input_str += k
            print(k, end='', flush=True)

    return input_str


def get_menu_input(prompt: str = "Option: ") -> str:
    """Get menu input with instant ESC detection. Prints prompt and waits for input."""
    print(prompt, end='', flush=True)
    k = get_key()

    # ESC exits immediately
    if k == "\x1b":
        show_exit_screen()

    # Enter returns empty string
    if k == "\r" or k == "\n":
        print()
        return ""

    # For other keys, collect the rest of input
    if k and k.isprintable():
        return collect_input(k).strip().upper()

    return ""


def get_next_visible_index(profiles, current_index, direction):
    """Get the next visible (non-hidden) profile index.

    Args:
        profiles: List of profile dictionaries
        current_index: Current selected index
        direction: 1 for next, -1 for previous

    Returns:
        Index of next visible profile, or current if none found
    """
    total = len(profiles)
    if total == 0:
        return current_index

    # Count visible profiles
    visible_count = sum(1 for p in profiles if not p.get('hidden', False))
    if visible_count == 0:
        return current_index

    # Find next visible profile
    new_index = current_index
    for _ in range(total):
        new_index = (new_index + direction) % total
        if not profiles[new_index].get('hidden', False):
            return new_index

    return current_index


def get_first_visible_index(profiles):
    """Get the index of the first visible (non-hidden) profile."""
    for i, profile in enumerate(profiles):
        if not profile.get('hidden', False):
            return i
    return 0


def find_profile_by_id(profiles, profile_id):
    """Find a profile by its custom ID.

    Args:
        profiles: List of profile dictionaries
        profile_id: The custom ID to search for

    Returns:
        The profile dictionary if found, None otherwise
    """
    for profile in profiles:
        if profile.get('id') == profile_id:
            return profile
    return None


def interactive_menu(config):
    """Interactive menu using CB9Lib UI components with hybrid input."""
    profiles = config["profiles"]
    # Start at first visible profile
    selected_index = get_first_visible_index(profiles)

    while True:
        # Check for resize and redraw
        check_resize()

        width = shutil.get_terminal_size().columns
        clear_screen()
        display_profiles(profiles, selected_index)

        # Single-line colorized legend using CB9Lib colors
        legend = (
            color_text("[↑/↓]", fg=BRIGHT_YELLOW, style=BOLD) + " Select  " +
            color_text("[Enter]", fg=BRIGHT_YELLOW, style=BOLD) + " Run  " +
            color_text("[#]", fg=BRIGHT_YELLOW, style=BOLD) + " Profile #  " +
            color_text("[E]", fg=BRIGHT_YELLOW, style=BOLD) + " Edit  " +
            color_text("[D]", fg=BRIGHT_YELLOW, style=BOLD) + " Duplicates  " +
            color_text("[C]", fg=BRIGHT_YELLOW, style=BOLD) + " Clean Up  " +
            color_text("[A]", fg=BRIGHT_YELLOW, style=BOLD) + " Admin  " +
            color_text("[Q/ESC]", fg=BRIGHT_YELLOW, style=BOLD) + " Quit"
        )
        print(legend)
        print("-" * width)
        print("Option: ", end='', flush=True)

        # Use get_key() for instant keypress detection
        k = get_key()

        # Handle resize (get_key returns None on interrupt)
        if k is None or check_resize():
            continue

        # ESC exits immediately
        if k == "\x1b":
            show_exit_screen()

        # Arrow keys for navigation (instant, skips hidden profiles)
        elif k == "\x1b[A":  # Up arrow
            selected_index = get_next_visible_index(profiles, selected_index, -1)
            continue
        elif k == "\x1b[B":  # Down arrow
            selected_index = get_next_visible_index(profiles, selected_index, 1)
            continue

        # Enter runs selected profile
        elif k == "\r" or k == "\n":
            clear_screen()
            header("VLC Menu", VERSION)
            run_profile(profiles[selected_index])
            # Go directly to management mode
            management_mode()

        # All other keys: collect full input then process
        else:
            user_input = collect_input(k).strip().lower()

            if not user_input:
                continue

            # Q quits
            if user_input == "q":
                show_exit_screen()

            # Edit JSON
            elif user_input == "e":
                clear_screen()
                header("VLC Menu", VERSION)
                print(color_text(f"Opening {CONFIG_PATH} in default editor...", fg=YELLOW))
                os.system(f'open "{CONFIG_PATH}"')
                print(color_text("\nNote: Restart the script to load changes.", fg=CYAN))
                input(color_text("\nPress Enter to return to menu...", fg=YELLOW))

            # Duplicate Finder
            elif user_input == "d":
                duplicate_finder_menu()

            # Clean Up Trash
            elif user_input == "c":
                clean_up_trash()

            # Admin menu (Media File Organizer + Media Optimize)
            elif user_input == "a":
                admin_menu()

            # Numeric selection (check custom ID first, then positional index)
            elif user_input.isdigit():
                num = int(user_input)

                # First, check if this matches a custom profile ID
                profile_by_id = find_profile_by_id(profiles, num)
                if profile_by_id:
                    clear_screen()
                    header("VLC Menu", VERSION)
                    run_profile(profile_by_id)
                    management_mode()
                # Otherwise, use as positional index (1-based)
                elif 1 <= num <= len(profiles):
                    clear_screen()
                    header("VLC Menu", VERSION)
                    run_profile(profiles[num - 1])
                    management_mode()
                else:
                    clear_screen()
                    header("VLC Menu", VERSION)
                    print(color_text(f"Invalid profile number: {num}. Valid range: 1-{len(profiles)}", fg=RED))
                    input(color_text("\nPress Enter to return to menu...", fg=YELLOW))

# =============================================================================
# ADMIN MENU — Media File Organizer (ported from organizeMedia.py v1.17)
# -----------------------------------------------------------------------------
# Self-contained port. Reads its settings from the "organizeMedia" section of
# vlcmenuConfig.json. Screens are rebranded to the "VLC Menu" header. The source
# organizeMedia.py is NOT modified or imported. get_key() is reused from above.
# =============================================================================

def load_organize_config():
    """Build the Media File Organizer config dict from vlcmenuConfig.json['organizeMedia']."""
    full = load_json_config(CONFIG_PATH) or {}
    config = full.get("organizeMedia")
    if not config:
        return None
    config = dict(config)  # shallow copy so we can add derived keys
    config["sourceDirectory"] = os.path.expanduser(config.get("sourceDirectory", ""))
    if "targetDirectories" in config:
        dirs = [os.path.expanduser(d) for d in config["targetDirectories"] if d][:5]
    elif "targetDirectory" in config:
        dirs = [os.path.expanduser(config["targetDirectory"])]
    else:
        dirs = [config["sourceDirectory"]]
    config["_targetDirectories"] = dirs
    config["targetDirectory"] = dirs[0] if dirs else config["sourceDirectory"]
    if config.get("cacheFile"):
        config["cacheFile"] = os.path.expanduser(config["cacheFile"])
    return config


def shortenPath(path):
    """Replace the user's home directory with ~ for cleaner display."""
    home = os.path.expanduser("~")
    return path.replace(home, "~") if home else path

def formatFileSize(sizeBytes):
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if sizeBytes < 1024.0:
            return f"{sizeBytes:.2f} {unit}"
        sizeBytes /= 1024.0
    return f"{sizeBytes:.2f} TB"

def writeLog(logFile, message):
    """Write message to log file with timestamp."""
    try:
        logPath = os.path.expanduser(logFile)
        os.makedirs(os.path.dirname(logPath), exist_ok=True)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(logPath, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        print(color_text(f"⚠️  Failed to write to log: {e}", fg=YELLOW))


def getTargetDirectories(config):
    """Return list of target directories (up to 5). Always returns at least one."""
    return config.get("_targetDirectories") or [os.path.expanduser(config["targetDirectory"])]


def resolveTargetFolder(subfolder, targetDirectories):
    """Return the full path for a subfolder using first-match-wins across target dirs."""
    for targetDir in targetDirectories:
        candidate = os.path.join(targetDir, subfolder)
        if os.path.isdir(candidate):
            return candidate
    return os.path.join(targetDirectories[0], subfolder)


def calculateFileHash(filePath):
    """Calculate MD5 hash of file for duplicate detection."""
    try:
        md5Hash = hashlib.md5()
        with open(filePath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b""):
                md5Hash.update(chunk)
        return md5Hash.hexdigest()
    except Exception as e:
        print(color_text(f"   ⚠️  Failed to hash {shortenPath(filePath)}: {e}", fg=YELLOW))
        return None

def scanAllFolders(config):
    """Scan ALL subdirectories (except import/deleted) to build/rebuild cache."""
    sourceDir = config["sourceDirectory"]
    extensions = [ext.lower() for ext in config["extensions"]]
    importFolder = config.get("prioritySubfolder", "import")
    deletedFolder = config.get("deletedFolder", "deleted")
    logFile = config.get("logFile")

    if not folder_exists(sourceDir):
        print(color_text(f"❌ Source directory does not exist: {shortenPath(sourceDir)}", fg=BRIGHT_YELLOW, style=BOLD))
        return []

    mediaFiles = []
    print(color_text(f"📁 Scanning ALL subdirectories: {shortenPath(sourceDir)}\n", fg=CYAN))

    if logFile:
        writeLog(logFile, f"Starting full scan of: {sourceDir}")

    for root, dirs, files in os.walk(sourceDir):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in [importFolder, deletedFolder]]
        relPath = os.path.relpath(root, sourceDir)
        if relPath != ".":
            print(color_text(f"   Scanning: {relPath}/", fg=CYAN), end='\r')
        for filename in files:
            if filename.startswith('.'):
                continue
            fileExt = os.path.splitext(filename)[1].lower()
            if fileExt in extensions:
                filePath = os.path.join(root, filename)
                fileSize = os.path.getsize(filePath)
                mediaFiles.append({"path": filePath, "filename": filename, "size": fileSize, "hash": None})

    print()
    print(color_text(f"✓ Found {len(mediaFiles)} media files across all folders\n", fg=GREEN))
    if logFile:
        writeLog(logFile, f"Full scan complete: Found {len(mediaFiles)} media files")
    return mediaFiles

def scanMediaFiles(config):
    """Scan ONLY the import folder for media files to process."""
    sourceDir = config["sourceDirectory"]
    extensions = [ext.lower() for ext in config["extensions"]]
    importFolder = config.get("prioritySubfolder", "import")
    logFile = config.get("logFile")

    importPath = os.path.join(sourceDir, importFolder)

    if not folder_exists(importPath):
        print(color_text(f"❌ Import folder does not exist: {shortenPath(importPath)}", fg=BRIGHT_YELLOW, style=BOLD))
        print(color_text(f"   Creating import folder...\n", fg=YELLOW))
        ensure_folder(importPath)
        if logFile:
            writeLog(logFile, f"Created import folder: {importPath}")
        return []

    mediaFiles = []
    print(color_text(f"📁 Scanning import folder: {shortenPath(importPath)}\n", fg=CYAN))
    if logFile:
        writeLog(logFile, f"Scanning import folder: {importPath}")

    for root, dirs, files in os.walk(importPath):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for filename in files:
            if filename.startswith('.'):
                continue
            fileExt = os.path.splitext(filename)[1].lower()
            if fileExt in extensions:
                filePath = os.path.join(root, filename)
                fileSize = os.path.getsize(filePath)
                mediaFiles.append({"path": filePath, "filename": filename, "size": fileSize, "hash": None})

    print(color_text(f"✓ Found {len(mediaFiles)} media files in import folder\n", fg=GREEN))
    if logFile:
        writeLog(logFile, f"Import scan complete: Found {len(mediaFiles)} media files")
    return mediaFiles


def detectCategory(filename, categoryMatching):
    """Detect category based on filename keywords with priority-based matching."""
    filenameLower = filename.lower()
    sortedCategories = sorted(categoryMatching, key=lambda x: x.get('priority', 999))
    for categoryEntry in sortedCategories:
        folder = categoryEntry.get('folder')
        keywords = categoryEntry.get('keywords', [])
        for keyword in keywords:
            keywordLower = keyword.lower()
            if '&' in keywordLower:
                parts = [part.strip() for part in keywordLower.split('&')]
                if all(part in filenameLower for part in parts):
                    return folder
            else:
                if keywordLower in filenameLower:
                    return folder
    return None

def extractMetadata(filePath):
    """Extract metadata from video file using ffprobe."""
    try:
        cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', filePath]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return {}
        data = json.loads(result.stdout)
        metadata = {}
        if 'format' in data and 'tags' in data['format']:
            tags = data['format']['tags']
            for key, value in tags.items():
                keyLower = key.lower()
                if keyLower in ['title', 'description', 'comment', 'tags', 'keywords', 'genre', 'artist', 'album']:
                    metadata[keyLower] = value.lower() if isinstance(value, str) else str(value).lower()
        if 'streams' in data:
            for stream in data['streams']:
                if 'tags' in stream:
                    for key, value in stream['tags'].items():
                        keyLower = key.lower()
                        if keyLower in ['title', 'description', 'comment', 'tags', 'keywords', 'genre']:
                            if keyLower not in metadata:
                                metadata[keyLower] = value.lower() if isinstance(value, str) else str(value).lower()
        return metadata
    except subprocess.TimeoutExpired:
        return {}
    except Exception:
        return {}

def detectCategoryFromMetadata(metadata, categoryMatching):
    """Try to detect category by matching keywords against video metadata."""
    if not metadata:
        return None
    metadataText = ' '.join(metadata.values()).lower()
    if not metadataText.strip():
        return None
    sortedCategories = sorted(categoryMatching, key=lambda x: x.get('priority', 999))
    for categoryEntry in sortedCategories:
        folder = categoryEntry.get('folder')
        keywords = categoryEntry.get('keywords', [])
        for keyword in keywords:
            keywordLower = keyword.lower()
            if '&' in keywordLower:
                parts = [part.strip() for part in keywordLower.split('&')]
                if all(part in metadataText for part in parts):
                    return folder
            else:
                if keywordLower in metadataText:
                    return folder
    return None


def loadCache(cacheFile):
    """Load file cache from disk."""
    if not file_exists(cacheFile):
        return {}
    try:
        with open(cacheFile, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(color_text(f"⚠️  Failed to load cache: {e}", fg=YELLOW))
        return {}

def saveCache(cache, cacheFile):
    """Save file cache to disk."""
    try:
        with open(cacheFile, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2)
        return True
    except Exception as e:
        print(color_text(f"⚠️  Failed to save cache: {e}", fg=YELLOW))
        return False

def getFileMetadata(filePath):
    """Get file metadata for cache comparison."""
    try:
        stats = os.stat(filePath)
        return {"size": stats.st_size, "mtime": stats.st_mtime}
    except Exception:
        return None


def findDuplicates(mediaFiles, logFile=None, cacheFile=None):
    """Find duplicate files based on MD5 hash with caching and size pre-filtering."""
    print(color_text("🔍 Finding duplicates (using cache and size filtering)...\n", fg=CYAN))
    if logFile:
        writeLog(logFile, "Starting duplicate detection with cache")

    cache = {}
    if cacheFile:
        cache = loadCache(cacheFile)
        print(color_text(f"📦 Loaded cache with {len(cache)} entries\n", fg=CYAN))
        if logFile:
            writeLog(logFile, f"Loaded cache: {len(cache)} entries")

    sizeMap = defaultdict(list)
    for fileInfo in mediaFiles:
        sizeMap[fileInfo['size']].append(fileInfo)

    filesToHash = []
    for size, files in sizeMap.items():
        if len(files) > 1:
            filesToHash.extend(files)

    print(color_text(f"📊 {len(mediaFiles)} total files, {len(filesToHash)} need hashing (same size groups)\n", fg=CYAN))
    if logFile:
        writeLog(logFile, f"Size filtering: {len(filesToHash)}/{len(mediaFiles)} files need hashing")

    hashMap = defaultdict(list)
    cacheHits = cacheMisses = cacheUpdates = 0

    for idx, fileInfo in enumerate(filesToHash, start=1):
        filePath = fileInfo['path']
        filename = fileInfo['filename']
        print(color_text(f"[{idx}/{len(filesToHash)}] ", fg=CYAN) + f"Checking: {color_text(filename, fg=WHITE)}", end='\r')
        metadata = getFileMetadata(filePath)
        if not metadata:
            continue
        fileHash = None
        if filePath in cache:
            cachedEntry = cache[filePath]
            if (cachedEntry.get('size') == metadata['size'] and cachedEntry.get('mtime') == metadata['mtime']):
                fileHash = cachedEntry.get('hash')
                cacheHits += 1
        if not fileHash:
            fileHash = calculateFileHash(filePath)
            cacheMisses += 1
            if fileHash and cacheFile:
                cache[filePath] = {'size': metadata['size'], 'mtime': metadata['mtime'], 'hash': fileHash}
                cacheUpdates += 1
        if fileHash:
            fileInfo['hash'] = fileHash
            hashMap[fileHash].append(fileInfo)

    print()
    if cacheFile and cacheUpdates > 0:
        if saveCache(cache, cacheFile):
            print(color_text(f"💾 Cache updated: {cacheHits} hits, {cacheMisses} misses, {cacheUpdates} updates\n", fg=GREEN))
            if logFile:
                writeLog(logFile, f"Cache stats: {cacheHits} hits, {cacheMisses} misses, {cacheUpdates} updates")

    duplicates = []
    for fileHash, files in hashMap.items():
        if len(files) > 1:
            duplicates.append({"hash": fileHash, "files": files, "count": len(files)})

    totalDuplicates = sum(d['count'] - 1 for d in duplicates)
    print(color_text(f"✓ Found {len(duplicates)} duplicate groups ({totalDuplicates} duplicate files)\n", fg=GREEN))
    if logFile:
        writeLog(logFile, f"Duplicate detection complete: {len(duplicates)} groups, {totalDuplicates} duplicate files")
    return duplicates


def normalizeFilename(filename):
    """Normalize filename by stripping common duplicate suffixes."""
    baseName, ext = os.path.splitext(filename)
    patterns = [
        r'[\s_-]?copy(\s?\d+)?$',
        r'\s?\(\d+\)$',
        r'\s?\[\d+\]$',
        r'_\d+$',
        r'-\d+$',
        r'\s\d+$',
    ]
    normalized = baseName
    for pattern in patterns:
        normalized = re.sub(pattern, '', normalized, flags=re.IGNORECASE)
    return normalized.strip()


def findSimilarNameDuplicates(mediaFiles, sizeTolerance=0.10, logFile=None):
    """Find files with similar names and similar sizes (potential duplicates)."""
    print(color_text("🔍 Finding similar-name duplicates...\n", fg=CYAN))
    if logFile:
        writeLog(logFile, f"Starting similar-name duplicate detection (tolerance: {sizeTolerance*100}%)")

    nameGroups = defaultdict(list)
    for fileInfo in mediaFiles:
        normalizedName = normalizeFilename(fileInfo['filename'])
        nameGroups[normalizedName].append(fileInfo)

    duplicates = []
    for normalizedName, files in nameGroups.items():
        if len(files) < 2:
            continue
        sortedBySize = sorted(files, key=lambda f: f['size'], reverse=True)
        largestSize = sortedBySize[0]['size']
        similarSizeFiles = []
        for f in sortedBySize:
            if largestSize == 0:
                continue
            sizeDiff = abs(largestSize - f['size']) / largestSize
            if sizeDiff <= sizeTolerance:
                similarSizeFiles.append(f)
        if len(similarSizeFiles) > 1:
            duplicates.append({"normalizedName": normalizedName, "files": similarSizeFiles, "count": len(similarSizeFiles)})

    totalDuplicates = sum(d['count'] - 1 for d in duplicates)
    print(color_text(f"✓ Found {len(duplicates)} similar-name groups ({totalDuplicates} potential duplicates)\n", fg=GREEN))
    if logFile:
        writeLog(logFile, f"Similar-name detection complete: {len(duplicates)} groups, {totalDuplicates} potential duplicates")
    return duplicates


def moveFile(sourceFile, targetFolder, dryRun=False):
    """Move file to target folder."""
    sourcePath = sourceFile['path']
    filename = sourceFile['filename']
    if not dryRun and not folder_exists(targetFolder):
        ensure_folder(targetFolder)
    targetPath = os.path.join(targetFolder, filename)
    if file_exists(targetPath) and not dryRun:
        baseName, ext = os.path.splitext(filename)
        counter = 1
        while file_exists(targetPath):
            newFilename = f"{baseName}_{counter}{ext}"
            targetPath = os.path.join(targetFolder, newFilename)
            counter += 1
    if dryRun:
        return True, targetPath
    else:
        try:
            shutil.move(sourcePath, targetPath)
            return True, targetPath
        except Exception as e:
            return False, str(e)

def deleteDuplicateFiles(duplicates, targetDir, deletedFolder, strategy="keep_first", dryRun=False, logFile=None, pauseEvery=50, pauseDuration=5):
    """Move duplicate files to deleted folder based on strategy."""
    movedCount = 0
    totalSize = 0
    totalProcessed = 0
    deletedPath = os.path.join(targetDir, deletedFolder)
    if not dryRun and not folder_exists(deletedPath):
        ensure_folder(deletedPath)
    if logFile:
        writeLog(logFile, f"Starting duplicate removal (strategy: {strategy}, dry_run: {dryRun})")

    for dupGroup in duplicates:
        files = dupGroup['files']
        filesToMove = files[1:]
        for fileInfo in filesToMove:
            filePath = fileInfo['path']
            fileName = fileInfo['filename']
            fileSize = fileInfo['size']
            targetPath = os.path.join(deletedPath, fileName)
            if file_exists(targetPath) and not dryRun:
                baseName, ext = os.path.splitext(fileName)
                counter = 1
                while file_exists(targetPath):
                    newFilename = f"{baseName}_{counter}{ext}"
                    targetPath = os.path.join(deletedPath, newFilename)
                    counter += 1
            if dryRun:
                print(color_text(f"   [DRY RUN] Would move to deleted: {shortenPath(filePath)} ({formatFileSize(fileSize)})", fg=YELLOW))
                if logFile:
                    writeLog(logFile, f"DRY RUN: Would move {filePath} to deleted folder")
            else:
                try:
                    shutil.move(filePath, targetPath)
                    print(color_text(f"   ✓ Moved to deleted: {shortenPath(filePath)} ({formatFileSize(fileSize)})", fg=GREEN))
                    movedCount += 1
                    totalSize += fileSize
                    totalProcessed += 1
                    if logFile:
                        writeLog(logFile, f"MOVED TO DELETED: {filePath} → {targetPath} ({formatFileSize(fileSize)})")
                    if pauseEvery > 0 and totalProcessed % pauseEvery == 0:
                        print(color_text(f"\n⏸️  Pausing for {pauseDuration} seconds to cool drive...", fg=CYAN))
                        time.sleep(pauseDuration)
                        print()
                except Exception as e:
                    print(color_text(f"   ✗ Failed to move {shortenPath(filePath)}: {e}", fg=BRIGHT_YELLOW))
                    if logFile:
                        writeLog(logFile, f"ERROR: Failed to move {filePath}: {e}")

    if logFile:
        writeLog(logFile, f"Duplicate removal complete: {movedCount} files moved to deleted folder, {formatFileSize(totalSize)} total size")
    return movedCount, totalSize


def organizeFiles(config, dryRun=False):
    """Main organization function."""
    logFile = config.get("logFile")
    maxFiles = config.get("maxFilesToProcess", 0)
    pauseEvery = config.get("pauseEvery", 50)
    pauseDuration = config.get("pauseDuration", 5)

    if logFile:
        mode = "DRY RUN" if dryRun else "ORGANIZE"
        writeLog(logFile, f"=== Starting {mode} ===")

    mediaFiles = scanMediaFiles(config)
    if not mediaFiles:
        print(color_text("No media files found to organize.\n", fg=YELLOW))
        if logFile:
            writeLog(logFile, "No media files found")
        return

    if maxFiles > 0 and len(mediaFiles) > maxFiles:
        print(color_text(f"⚠️  Limiting to {maxFiles} files (out of {len(mediaFiles)} found)\n", fg=YELLOW))
        mediaFiles = mediaFiles[:maxFiles]
        if logFile:
            writeLog(logFile, f"Limited processing to {maxFiles} files")

    results = {"categorized": defaultdict(list), "uncategorized": [], "moved": 0, "failed": []}
    targetDirectories  = getTargetDirectories(config)
    primaryTargetDir   = targetDirectories[0]
    categoryMatching   = config["categoryMatching"]
    uncategorizedFolder = config["uncategorizedFolder"]

    if len(targetDirectories) > 1:
        print(color_text(f"📂 Target directories: {len(targetDirectories)}", fg=CYAN))
        for i, d in enumerate(targetDirectories, 1):
            print(color_text(f"   {i}. {shortenPath(d)}", fg=CYAN))
        print()

    print(color_text(f"\n📦 Organizing {len(mediaFiles)} files...\n", fg=CYAN))

    for idx, fileInfo in enumerate(mediaFiles, start=1):
        filename = fileInfo['filename']
        sourcePath = fileInfo['path']
        category = detectCategory(filename, categoryMatching)
        matchedBy = "filename"
        if not category:
            fileExt = os.path.splitext(filename)[1].lower()
            videoExtensions = ['.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm']
            if fileExt in videoExtensions:
                metadata = extractMetadata(sourcePath)
                if metadata:
                    category = detectCategoryFromMetadata(metadata, categoryMatching)
                    if category:
                        matchedBy = "metadata"
        if category:
            targetFolder = resolveTargetFolder(category, targetDirectories)
            categoryName = category
        else:
            targetFolder = os.path.join(primaryTargetDir, uncategorizedFolder)
            categoryName = uncategorizedFolder
            matchedBy = "none"

        success, result = moveFile(fileInfo, targetFolder, dryRun)
        if success:
            matchIndicator = ""
            if matchedBy == "metadata":
                matchIndicator = color_text(" [meta]", fg=MAGENTA)
            elif matchedBy == "filename":
                matchIndicator = color_text(" [file]", fg=CYAN)
            print(color_text(f"[{idx}/{len(mediaFiles)}] ", fg=CYAN) +
                  f"{color_text('✓', fg=GREEN)} {filename} " +
                  color_text(f"→ {categoryName}", fg=BRIGHT_YELLOW) + matchIndicator)
            if category:
                results["categorized"][category].append(filename)
            else:
                results["uncategorized"].append(filename)
            results["moved"] += 1
            if logFile:
                if dryRun:
                    writeLog(logFile, f"DRY RUN: Would move {sourcePath} → {categoryName}/{filename} (matched by: {matchedBy})")
                else:
                    writeLog(logFile, f"MOVED: {sourcePath} → {categoryName}/{filename} (matched by: {matchedBy})")
        else:
            print(color_text(f"[{idx}/{len(mediaFiles)}] ", fg=CYAN) +
                  f"{color_text('✗', fg=BRIGHT_YELLOW)} {filename} - Error: {result}")
            results["failed"].append((filename, result))
            if logFile:
                writeLog(logFile, f"ERROR: Failed to move {sourcePath}: {result}")

        if not dryRun and pauseEvery > 0 and idx % pauseEvery == 0 and idx < len(mediaFiles):
            print(color_text(f"\n⏸️  Pausing for {pauseDuration} seconds to cool drive...", fg=CYAN))
            time.sleep(pauseDuration)
            print()

    if logFile:
        writeLog(logFile, f"Organization complete: {results['moved']} files processed")
    return results


def getFolderCounts(config):
    """Get file counts for import, uncategorized, and category folders."""
    sourceDir = config["sourceDirectory"]
    extensions = [ext.lower() for ext in config["extensions"]]
    importFolder = config.get("prioritySubfolder", "import")
    uncategorizedFolder = config.get("uncategorizedFolder", "uncategorized")
    categoryMatching = config["categoryMatching"]
    uniqueFolders = set(entry.get('folder') for entry in categoryMatching if entry.get('folder'))
    counts = {"import": 0, "uncategorized": 0, "categories": 0}

    importPath = os.path.join(sourceDir, importFolder)
    if folder_exists(importPath):
        for root, dirs, files in os.walk(importPath):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for filename in files:
                if not filename.startswith('.'):
                    if os.path.splitext(filename)[1].lower() in extensions:
                        counts["import"] += 1
                        if counts["import"] % 100 == 0:
                            print('.', end='', flush=True)

    uncategorizedPath = os.path.join(sourceDir, uncategorizedFolder)
    if folder_exists(uncategorizedPath):
        for root, dirs, files in os.walk(uncategorizedPath):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for filename in files:
                if not filename.startswith('.'):
                    if os.path.splitext(filename)[1].lower() in extensions:
                        counts["uncategorized"] += 1
                        if counts["uncategorized"] % 100 == 0:
                            print('.', end='', flush=True)

    targetDirectories = getTargetDirectories(config)
    countedPaths = set()
    for folderName in uniqueFolders:
        categoryPath = resolveTargetFolder(folderName, targetDirectories)
        if categoryPath in countedPaths:
            continue
        countedPaths.add(categoryPath)
        if folder_exists(categoryPath):
            for root, dirs, files in os.walk(categoryPath):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                for filename in files:
                    if not filename.startswith('.'):
                        if os.path.splitext(filename)[1].lower() in extensions:
                            counts["categories"] += 1
                            if counts["categories"] % 100 == 0:
                                print('.', end='', flush=True)
    return counts

def checkUnknownFolders(config):
    """Check for folders in source directory that aren't in categories list."""
    sourceDir = config["sourceDirectory"]
    importFolder = config.get("prioritySubfolder", "import")
    uncategorizedFolder = config.get("uncategorizedFolder", "uncategorized")
    deletedFolder = config.get("deletedFolder", "deleted")
    categoryMatching = config["categoryMatching"]
    uniqueFolders = set(entry.get('folder') for entry in categoryMatching if entry.get('folder'))
    ignoreFolders = {importFolder, uncategorizedFolder, deletedFolder, "fav", "trash"}
    unknownFolders = []
    if not folder_exists(sourceDir):
        return unknownFolders
    try:
        for item in os.listdir(sourceDir):
            itemPath = os.path.join(sourceDir, item)
            if os.path.isdir(itemPath) and not item.startswith('.'):
                if item not in uniqueFolders and item not in ignoreFolders:
                    unknownFolders.append(item)
    except Exception as e:
        print(color_text(f"⚠️  Failed to scan directory: {e}", fg=YELLOW))
    return unknownFolders


def previewOrganization(config):
    """Preview organization without moving files."""
    clear_screen()
    header("VLC Menu", VERSION, "Preview Mode (Dry Run)")
    print(color_text("Running in DRY RUN mode - no files will be moved\n", fg=YELLOW, style=BOLD))
    results = organizeFiles(config, dryRun=True)
    if results:
        displayOrganizationSummary(results, dryRun=True)
    input(color_text("\nPress Enter to return to menu...", fg=CYAN))

def runOrganization(config):
    """Run file organization."""
    clear_screen()
    header("VLC Menu", VERSION, "Organize Files")
    confirm = input(color_text("\n⚠️  This will move files. Continue? (Y/n): ", fg=YELLOW))
    if confirm.lower() == 'n':
        print(color_text("Cancelled.\n", fg=YELLOW))
        input(color_text("Press Enter to return to menu...", fg=CYAN))
        return
    results = organizeFiles(config, dryRun=False)
    if results:
        displayOrganizationSummary(results, dryRun=False)
    input(color_text("\nPress Enter to return to menu...", fg=CYAN))

def findAndDeleteDuplicates(config):
    """Find and delete duplicate files (import folder)."""
    clear_screen()
    header("VLC Menu", VERSION, "Find Duplicates")
    logFile = config.get("logFile")
    cacheFile = config.get("cacheFile")
    mediaFiles = scanMediaFiles(config)
    if not mediaFiles:
        print(color_text("No media files found.\n", fg=YELLOW))
        input(color_text("Press Enter to return to menu...", fg=CYAN))
        return
    duplicates = findDuplicates(mediaFiles, logFile, cacheFile)
    if not duplicates:
        print(color_text("No duplicates found!\n", fg=GREEN))
        input(color_text("Press Enter to return to menu...", fg=CYAN))
        return
    print(color_text("Duplicate Groups:", fg=WHITE, style=BOLD))
    print("-" * 80)
    for idx, dupGroup in enumerate(duplicates, start=1):
        print(color_text(f"\nGroup {idx}: {dupGroup['count']} files", fg=BRIGHT_YELLOW))
        for fileInfo in dupGroup['files']:
            print(f"   • {shortenPath(fileInfo['path'])} ({formatFileSize(fileInfo['size'])})")
    print("\n" + "-" * 80)
    confirm = input(color_text(f"\n⚠️  Delete {sum(d['count'] - 1 for d in duplicates)} duplicate files? (Y/n): ", fg=YELLOW))
    if confirm.lower() != 'n':
        strategy = config.get("duplicateStrategy", "keep_first")
        targetDir = getTargetDirectories(config)[0]
        deletedFolder = config.get("deletedFolder", "deleted")
        pauseEvery = config.get("pauseEvery", 50)
        pauseDuration = config.get("pauseDuration", 5)
        movedCount, totalSize = deleteDuplicateFiles(duplicates, targetDir, deletedFolder, strategy, dryRun=False, logFile=logFile, pauseEvery=pauseEvery, pauseDuration=pauseDuration)
        print(color_text(f"\n✓ Moved {movedCount} duplicate files to deleted folder", fg=GREEN))
        print(color_text(f"✓ Total size: {formatFileSize(totalSize)}\n", fg=GREEN))
    else:
        print(color_text("\nCancelled.\n", fg=YELLOW))
        if logFile:
            writeLog(logFile, "Duplicate deletion cancelled by user")
    input(color_text("Press Enter to return to menu...", fg=CYAN))

def findDuplicatesAllFolders(config):
    """Find duplicates across ALL subfolders (not just import)."""
    clear_screen()
    header("VLC Menu", VERSION, "Find Duplicates (All Folders)")
    logFile = config.get("logFile")
    cacheFile = config.get("cacheFile")
    print(color_text("This will scan ALL category folders for duplicates.\n", fg=CYAN))
    print(color_text("Useful for finding duplicates across your entire library.\n", fg=WHITE))
    mediaFiles = scanAllFolders(config)
    if not mediaFiles:
        print(color_text("No media files found.\n", fg=YELLOW))
        input(color_text("Press Enter to return to menu...", fg=CYAN))
        return
    duplicates = findDuplicates(mediaFiles, logFile, cacheFile)
    if not duplicates:
        print(color_text("No duplicates found!\n", fg=GREEN))
        input(color_text("Press Enter to return to menu...", fg=CYAN))
        return
    print(color_text("Duplicate Groups:", fg=WHITE, style=BOLD))
    print("-" * 80)
    for idx, dupGroup in enumerate(duplicates, start=1):
        print(color_text(f"\nGroup {idx}: {dupGroup['count']} files", fg=BRIGHT_YELLOW))
        for fileInfo in dupGroup['files']:
            print(f"   • {shortenPath(fileInfo['path'])} ({formatFileSize(fileInfo['size'])})")
    print("\n" + "-" * 80)
    confirm = input(color_text(f"\n⚠️  Delete {sum(d['count'] - 1 for d in duplicates)} duplicate files? (Y/n): ", fg=YELLOW))
    if confirm.lower() != 'n':
        strategy = config.get("duplicateStrategy", "keep_first")
        targetDir = getTargetDirectories(config)[0]
        deletedFolder = config.get("deletedFolder", "deleted")
        pauseEvery = config.get("pauseEvery", 50)
        pauseDuration = config.get("pauseDuration", 5)
        movedCount, totalSize = deleteDuplicateFiles(duplicates, targetDir, deletedFolder, strategy, dryRun=False, logFile=logFile, pauseEvery=pauseEvery, pauseDuration=pauseDuration)
        print(color_text(f"\n✓ Moved {movedCount} duplicate files to deleted folder", fg=GREEN))
        print(color_text(f"✓ Total size: {formatFileSize(totalSize)}\n", fg=GREEN))
    else:
        print(color_text("\nCancelled.\n", fg=YELLOW))
        if logFile:
            writeLog(logFile, "Duplicate deletion cancelled by user")
    input(color_text("Press Enter to return to menu...", fg=CYAN))

def findSimilarNameDuplicatesMenu(config):
    """Find duplicates based on similar filenames (e.g., file.mp4 and file_1.mp4)."""
    clear_screen()
    header("VLC Menu", VERSION, "Similar Name Duplicates")
    logFile = config.get("logFile")
    print(color_text("This scan detects files with similar names and similar sizes.\n", fg=CYAN))
    print(color_text("Examples of patterns detected:", fg=WHITE, style=BOLD))
    print("  • video.mp4 and video_1.mp4")
    print("  • file.mp4 and file-copy.mp4")
    print("  • movie.mp4 and movie (1).mp4")
    print("  • clip.mp4 and clip [2].mp4\n")
    print(color_text("Scanning all folders...\n", fg=CYAN))
    mediaFiles = scanAllFolders(config)
    if not mediaFiles:
        print(color_text("No media files found.\n", fg=YELLOW))
        input(color_text("Press Enter to return to menu...", fg=CYAN))
        return
    duplicates = findSimilarNameDuplicates(mediaFiles, sizeTolerance=0.10, logFile=logFile)
    if not duplicates:
        print(color_text("No similar-name duplicates found!\n", fg=GREEN))
        input(color_text("Press Enter to return to menu...", fg=CYAN))
        return
    print(color_text("Similar Name Groups:", fg=WHITE, style=BOLD))
    print("-" * 80)
    for idx, dupGroup in enumerate(duplicates, start=1):
        print(color_text(f"\nGroup {idx}: {dupGroup['count']} files (base: {dupGroup['normalizedName']})", fg=BRIGHT_YELLOW))
        for fileInfo in dupGroup['files']:
            print(f"  • {fileInfo['filename']} ({formatFileSize(fileInfo['size'])})")
            print(f"    {fileInfo['path']}")
    print("\n" + "-" * 80)
    totalToDelete = sum(d['count'] - 1 for d in duplicates)
    confirm = input(color_text(f"\n⚠️  Delete {totalToDelete} duplicate files (keep largest)? (Y/n): ", fg=YELLOW))
    if confirm.lower() != 'n':
        strategy = config.get("duplicateStrategy", "keep_first")
        targetDir = getTargetDirectories(config)[0]
        deletedFolder = config.get("deletedFolder", "deleted")
        pauseEvery = config.get("pauseEvery", 50)
        pauseDuration = config.get("pauseDuration", 5)
        for dupGroup in duplicates:
            dupGroup['files'] = sorted(dupGroup['files'], key=lambda f: f['size'], reverse=True)
        movedCount, totalSize = deleteDuplicateFiles(duplicates, targetDir, deletedFolder, strategy, dryRun=False, logFile=logFile, pauseEvery=pauseEvery, pauseDuration=pauseDuration)
        print(color_text(f"\n✓ Moved {movedCount} duplicate files to deleted folder", fg=GREEN))
        print(color_text(f"✓ Total size recovered: {formatFileSize(totalSize)}\n", fg=GREEN))
    else:
        print(color_text("\nCancelled.\n", fg=YELLOW))
        if logFile:
            writeLog(logFile, "Similar-name duplicate deletion cancelled by user")
    input(color_text("Press Enter to return to menu...", fg=CYAN))

def rescanAllFoldersMenu(config):
    """Rescan all subdirectories and rebuild cache."""
    clear_screen()
    header("VLC Menu", VERSION, "Rescan All Folders")
    logFile = config.get("logFile")
    cacheFile = config.get("cacheFile")
    print(color_text("This will scan ALL category folders and rebuild the cache.\n", fg=CYAN))
    print(color_text("Useful for:", fg=WHITE, style=BOLD))
    print("  • Building initial cache of existing organized files")
    print("  • Finding duplicates across all folders")
    print("  • Updating cache after manual file organization\n")
    confirm = input(color_text("Continue? (Y/n): ", fg=YELLOW))
    if confirm.lower() == 'n':
        print(color_text("\nCancelled.\n", fg=YELLOW))
        input(color_text("Press Enter to return to menu...", fg=CYAN))
        return
    mediaFiles = scanAllFolders(config)
    if not mediaFiles:
        print(color_text("No media files found.\n", fg=YELLOW))
        input(color_text("Press Enter to return to menu...", fg=CYAN))
        return
    print(color_text("\n🔨 Rebuilding cache...\n", fg=CYAN))
    if cacheFile and file_exists(cacheFile):
        os.remove(cacheFile)
        print(color_text("   Cleared old cache\n", fg=YELLOW))
    duplicates = findDuplicates(mediaFiles, logFile, cacheFile)
    print(color_text("\n" + "=" * 80, fg=CYAN))
    print(color_text("Rescan Complete", fg=GREEN, style=BOLD))
    print(color_text("=" * 80, fg=CYAN))
    print(f"\n  • Total files scanned: {len(mediaFiles)}")
    print(f"  • Duplicate groups found: {len(duplicates)}")
    if duplicates:
        totalDupes = sum(d['count'] - 1 for d in duplicates)
        print(f"  • Total duplicate files: {totalDupes}")
    print(f"  • Cache rebuilt successfully\n")
    input(color_text("Press Enter to return to menu...", fg=CYAN))

def clearCacheFile(config):
    """Clear the file cache."""
    clear_screen()
    header("VLC Menu", VERSION, "Clear Cache")
    cacheFile = config.get("cacheFile")
    if not cacheFile:
        print(color_text("No cache file configured.\n", fg=YELLOW))
        input(color_text("Press Enter to return to menu...", fg=CYAN))
        return
    if not file_exists(cacheFile):
        print(color_text("Cache file does not exist.\n", fg=YELLOW))
        input(color_text("Press Enter to return to menu...", fg=CYAN))
        return
    cache = loadCache(cacheFile)
    cacheSize = os.path.getsize(cacheFile)
    print(color_text(f"📦 Current cache:", fg=CYAN))
    print(f"   • Entries: {len(cache)}")
    print(f"   • Size: {formatFileSize(cacheSize)}")
    print(f"   • Location: {shortenPath(cacheFile)}\n")
    confirm = input(color_text("⚠️  Delete cache file? (Y/n): ", fg=YELLOW))
    if confirm.lower() != 'n':
        try:
            os.remove(cacheFile)
            print(color_text("\n✓ Cache cleared successfully\n", fg=GREEN))
            logFile = config.get("logFile")
            if logFile:
                writeLog(logFile, f"Cache cleared: {len(cache)} entries deleted")
        except Exception as e:
            print(color_text(f"\n✗ Failed to clear cache: {e}\n", fg=BRIGHT_YELLOW))
    else:
        print(color_text("\nCancelled.\n", fg=YELLOW))
    input(color_text("Press Enter to return to menu...", fg=CYAN))

def createMissingFolders(config):
    """Create any category folders that don't exist."""
    clear_screen()
    header("VLC Menu", VERSION, "Create Missing Folders")
    targetDirectories = getTargetDirectories(config)
    primaryTargetDir  = targetDirectories[0]
    categoryMatching  = config["categoryMatching"]
    logFile           = config.get("logFile")
    uniqueFolders = set(entry.get('folder') for entry in categoryMatching if entry.get('folder'))
    print(color_text("Checking for missing category folders...\n", fg=CYAN))
    if len(targetDirectories) > 1:
        print(color_text(f"  Checking across {len(targetDirectories)} target directories:", fg=CYAN))
        for d in targetDirectories:
            print(color_text(f"    • {shortenPath(d)}", fg=CYAN))
        print()
    missingFolders = []
    existingFolders = []
    for folderName in sorted(uniqueFolders):
        resolved = resolveTargetFolder(folderName, targetDirectories)
        if folder_exists(resolved):
            existingFolders.append(folderName)
        else:
            categoryPath = os.path.join(primaryTargetDir, folderName)
            missingFolders.append((folderName, categoryPath))
    if existingFolders:
        print(color_text(f"✓ Found {len(existingFolders)} existing folders:", fg=GREEN))
        for folder in sorted(existingFolders):
            print(f"  • {folder}")
        print()
    if not missingFolders:
        print(color_text("✓ All category folders exist!\n", fg=GREEN))
        input(color_text("Press Enter to return to menu...", fg=CYAN))
        return
    print(color_text(f"⚠️  Found {len(missingFolders)} missing folders:", fg=YELLOW))
    for folder, path in missingFolders:
        print(f"  • {folder}")
    print()
    confirm = input(color_text(f"Create {len(missingFolders)} missing folders? (Y/n): ", fg=YELLOW))
    if confirm.lower() != 'n':
        print()
        created = 0
        for folder, path in missingFolders:
            try:
                ensure_folder(path)
                print(color_text(f"✓ Created: {folder}", fg=GREEN))
                created += 1
                if logFile:
                    writeLog(logFile, f"Created category folder: {path}")
            except Exception as e:
                print(color_text(f"✗ Failed to create {folder}: {e}", fg=BRIGHT_YELLOW))
                if logFile:
                    writeLog(logFile, f"ERROR: Failed to create folder {path}: {e}")
        print()
        print(color_text(f"✓ Created {created} of {len(missingFolders)} folders\n", fg=GREEN))
    else:
        print(color_text("\nCancelled.\n", fg=YELLOW))
    input(color_text("Press Enter to return to menu...", fg=CYAN))

def selectCategoryFolder(config):
    """Display list of category folders and let user select one. Returns folder name or None."""
    categoryMatching = config["categoryMatching"]
    uniqueFolders = sorted(set(entry.get('folder') for entry in categoryMatching if entry.get('folder')))
    if not uniqueFolders:
        print(color_text("⚠️  No category folders defined in configuration.\n", fg=YELLOW))
        return None
    clear_screen()
    header("VLC Menu", VERSION, "Select Category Folder")
    print(color_text("Available Category Folders:", fg=CYAN, style=BOLD))
    print("-" * 80)
    print()
    for idx, folder in enumerate(uniqueFolders, start=1):
        print(f"  {color_text(f'[{idx}]', fg=BRIGHT_YELLOW, style=BOLD)} {folder}")
    print()
    print("-" * 80)
    print()
    while True:
        selection = input(color_text("Select folder number (or 'Q' to cancel): ", fg=CYAN))
        if selection.lower() == 'q':
            return None
        try:
            folderIdx = int(selection)
            if 1 <= folderIdx <= len(uniqueFolders):
                return uniqueFolders[folderIdx - 1]
            else:
                print(color_text(f"⚠️  Please enter a number between 1 and {len(uniqueFolders)}\n", fg=YELLOW))
        except ValueError:
            print(color_text("⚠️  Please enter a valid number\n", fg=YELLOW))

def validateFolderContents(config, folderName):
    """Validate files in a specific folder and find mismatches."""
    sourceDir = config["sourceDirectory"]
    extensions = [ext.lower() for ext in config["extensions"]]
    categoryMatching = config["categoryMatching"]
    logFile = config.get("logFile")
    folderPath = os.path.join(sourceDir, folderName)
    if not folder_exists(folderPath):
        print(color_text(f"❌ Folder does not exist: {shortenPath(folderPath)}", fg=BRIGHT_YELLOW, style=BOLD))
        return []
    print(color_text(f"\n📁 Scanning folder: {shortenPath(folderPath)}\n", fg=CYAN))
    if logFile:
        writeLog(logFile, f"Starting validation of folder: {folderPath}")
    mediaFiles = []
    for root, dirs, files in os.walk(folderPath):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for filename in files:
            if filename.startswith('.'):
                continue
            if os.path.splitext(filename)[1].lower() in extensions:
                mediaFiles.append({"path": os.path.join(root, filename), "filename": filename})
    print(color_text(f"✓ Found {len(mediaFiles)} media files in folder\n", fg=GREEN))
    if not mediaFiles:
        return []
    print(color_text("🔍 Validating file categories...\n", fg=CYAN))
    mismatches = []
    for idx, fileInfo in enumerate(mediaFiles, start=1):
        filename = fileInfo['filename']
        filePath = fileInfo['path']
        print(color_text(f"[{idx}/{len(mediaFiles)}] ", fg=CYAN) + f"Checking: {filename}", end='\r')
        detectedCategory = detectCategory(filename, categoryMatching)
        matchedBy = "filename"
        if not detectedCategory:
            fileExt = os.path.splitext(filename)[1].lower()
            videoExtensions = ['.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm']
            if fileExt in videoExtensions:
                metadata = extractMetadata(filePath)
                if metadata:
                    detectedCategory = detectCategoryFromMetadata(metadata, categoryMatching)
                    if detectedCategory:
                        matchedBy = "metadata"
        if detectedCategory != folderName:
            mismatches.append({
                "path": filePath, "filename": filename, "currentFolder": folderName,
                "suggestedFolder": detectedCategory if detectedCategory else "uncategorized",
                "matchedBy": matchedBy if detectedCategory else "none"
            })
    print()
    print(color_text(f"✓ Validation complete: {len(mismatches)} potential mismatches found\n", fg=GREEN))
    if logFile:
        writeLog(logFile, f"Validation complete for {folderName}: {len(mismatches)} mismatches found")
    return mismatches

def writeMismatchesToFile(mismatches, folderName):
    """Write mismatched files to a text file in the configured report folder."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    reportFolder = (load_organize_config() or {}).get("reportFolder", "~/Desktop")
    outputPath = os.path.expanduser(os.path.join(reportFolder, f"validation_{folderName}_{timestamp}.txt"))
    try:
        with open(outputPath, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"Validation Report for folder: {folderName}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total mismatches found: {len(mismatches)}\n")
            f.write("=" * 80 + "\n\n")
            for idx, mismatch in enumerate(mismatches, start=1):
                f.write(f"{idx}. {mismatch['filename']}\n")
                f.write(f"   Current Folder: {mismatch['currentFolder']}\n")
                f.write(f"   Suggested Folder: {mismatch['suggestedFolder']}\n")
                f.write(f"   Matched By: {mismatch['matchedBy']}\n")
                f.write(f"   Path: {mismatch['path']}\n\n")
        return outputPath
    except Exception as e:
        print(color_text(f"\n✗ Failed to write file: {e}\n", fg=BRIGHT_YELLOW))
        return None

def moveMismatchedFiles(config, mismatches, dryRun=False):
    """Move mismatched files to their suggested folders."""
    targetDirectories   = getTargetDirectories(config)
    primaryTargetDir    = targetDirectories[0]
    uncategorizedFolder = config.get("uncategorizedFolder", "uncategorized")
    logFile             = config.get("logFile")
    movedCount = 0
    failedCount = 0
    print(color_text(f"\n{'[DRY RUN] ' if dryRun else ''}Moving mismatched files...\n", fg=CYAN))
    for idx, mismatch in enumerate(mismatches, start=1):
        sourcePath = mismatch['path']
        filename = mismatch['filename']
        suggestedFolder = mismatch['suggestedFolder']
        if suggestedFolder == "uncategorized":
            targetFolder = os.path.join(primaryTargetDir, uncategorizedFolder)
        else:
            targetFolder = resolveTargetFolder(suggestedFolder, targetDirectories)
        if not dryRun and not folder_exists(targetFolder):
            ensure_folder(targetFolder)
        targetPath = os.path.join(targetFolder, filename)
        if file_exists(targetPath) and not dryRun:
            baseName, ext = os.path.splitext(filename)
            counter = 1
            while file_exists(targetPath):
                newFilename = f"{baseName}_{counter}{ext}"
                targetPath = os.path.join(targetFolder, newFilename)
                counter += 1
        if dryRun:
            print(color_text(f"[{idx}/{len(mismatches)}] ", fg=CYAN) +
                  f"Would move: {filename} " + color_text(f"→ {suggestedFolder}", fg=BRIGHT_YELLOW))
            movedCount += 1
        else:
            try:
                shutil.move(sourcePath, targetPath)
                print(color_text(f"[{idx}/{len(mismatches)}] ", fg=CYAN) +
                      color_text(f"✓ ", fg=GREEN) + f"Moved: {filename} " +
                      color_text(f"→ {suggestedFolder}", fg=BRIGHT_YELLOW))
                movedCount += 1
                if logFile:
                    writeLog(logFile, f"VALIDATION MOVE: {sourcePath} → {targetPath}")
            except Exception as e:
                print(color_text(f"[{idx}/{len(mismatches)}] ", fg=CYAN) +
                      color_text(f"✗ ", fg=BRIGHT_YELLOW) + f"Failed: {filename} - {e}")
                failedCount += 1
                if logFile:
                    writeLog(logFile, f"ERROR: Failed to move {sourcePath}: {e}")
    return movedCount, failedCount

def validateFolderMenu(config):
    """Menu function for validating folder contents."""
    folderName = selectCategoryFolder(config)
    if not folderName:
        print(color_text("\nCancelled.\n", fg=YELLOW))
        input(color_text("Press Enter to return to menu...", fg=CYAN))
        return
    clear_screen()
    header("VLC Menu", VERSION, f"Validating: {folderName}")
    mismatches = validateFolderContents(config, folderName)
    if not mismatches:
        print(color_text(f"✓ All files in '{folderName}' are correctly categorized!\n", fg=GREEN))
        input(color_text("Press Enter to return to menu...", fg=CYAN))
        return
    print(color_text("Mismatched Files Found:", fg=WHITE, style=BOLD))
    print("-" * 80)
    print()
    for idx, mismatch in enumerate(mismatches, start=1):
        matchIndicator = ""
        if mismatch['matchedBy'] == "metadata":
            matchIndicator = color_text(" [meta]", fg=MAGENTA)
        elif mismatch['matchedBy'] == "filename":
            matchIndicator = color_text(" [file]", fg=CYAN)
        print(f"{idx}. {color_text(mismatch['filename'], fg=WHITE)}")
        print(f"   Current: {color_text(mismatch['currentFolder'], fg=YELLOW)} → " +
              f"Suggested: {color_text(mismatch['suggestedFolder'], fg=GREEN)}{matchIndicator}")
        if idx == 10 and len(mismatches) > 10:
            remaining = len(mismatches) - 10
            print(f"\n   ... and {remaining} more files\n")
            break
    print()
    print("-" * 80)
    print()
    print(color_text("What would you like to do?", fg=WHITE, style=BOLD))
    print()
    print(color_text("  [W]", fg=BRIGHT_YELLOW, style=BOLD) + " Write to file (saves to Desktop)")
    print(color_text("  [M]", fg=BRIGHT_YELLOW, style=BOLD) + " Move files to suggested folders")
    print(color_text("  [Q]", fg=BRIGHT_YELLOW, style=BOLD) + " Return to main menu")
    print()
    k = get_key()
    if k and k.lower() == 'w':
        outputPath = writeMismatchesToFile(mismatches, folderName)
        if outputPath:
            print(color_text(f"\n✓ Report saved to: {shortenPath(outputPath)}\n", fg=GREEN))
        input(color_text("Press Enter to return to menu...", fg=CYAN))
    elif k and k.lower() == 'm':
        print()
        confirm = input(color_text(f"⚠️  Move {len(mismatches)} files to suggested folders? (Y/n): ", fg=YELLOW))
        if confirm.lower() != 'n':
            movedCount, failedCount = moveMismatchedFiles(config, mismatches, dryRun=False)
            print(color_text(f"\n✓ Moved {movedCount} files", fg=GREEN))
            if failedCount > 0:
                print(color_text(f"⚠️  Failed to move {failedCount} files\n", fg=YELLOW))
        else:
            print(color_text("\nCancelled.\n", fg=YELLOW))
        input(color_text("Press Enter to return to menu...", fg=CYAN))
    else:
        return

def getVideoDuration(filePath):
    """Get duration of video file in seconds using ffprobe. Returns seconds or None."""
    try:
        cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', filePath]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return None
        data = json.loads(result.stdout)
        if 'format' in data and 'duration' in data['format']:
            try:
                return float(data['format']['duration'])
            except (ValueError, TypeError):
                return None
        return None
    except (subprocess.TimeoutExpired, Exception):
        return None

def listCategories(config):
    """Display all categories in CSV format."""
    clear_screen()
    header("VLC Menu", VERSION, "Categories")
    print(color_text("\nCategory List - CSV Format\n", fg=CYAN, style=BOLD))
    print("=" * 80)
    categoryMatching = config.get('categoryMatching', [])
    if not categoryMatching:
        print(color_text("\nNo categories defined.\n", fg=YELLOW))
        input(color_text("Press Enter to return to menu...", fg=CYAN))
        return
    print(f"\n{color_text('Priority,Folder,Keywords', fg=WHITE, style=BOLD)}")
    print("-" * 80)
    sortedCategories = sorted(categoryMatching, key=lambda x: x.get('priority', 999))
    for entry in sortedCategories:
        priority = entry.get('priority', 999)
        folder = entry.get('folder', 'Unknown')
        keywords = entry.get('keywords', [])
        keywordsStr = "; ".join(keywords)
        print(f"{color_text(str(priority), fg=CYAN)},{color_text(folder, fg=BRIGHT_YELLOW)},\"{keywordsStr}\"")
    print()
    print("=" * 80)
    print(f"{color_text('Total Categories:', fg=WHITE, style=BOLD)} {len(categoryMatching)}")
    uniqueFolders = len(set(entry.get('folder') for entry in categoryMatching if entry.get('folder')))
    print(f"{color_text('Unique Folders:', fg=WHITE, style=BOLD)} {uniqueFolders}")
    print()
    input(color_text("Press Enter to return to menu...", fg=CYAN))

def findShortClips(config):
    """Find video clips under 10 seconds and move to trash folder."""
    clear_screen()
    header("VLC Menu", VERSION, "Short Clips")
    print(color_text("\nFinding Short Clips (< 10 seconds)\n", fg=CYAN, style=BOLD))
    print("-" * 80)
    targetDirectories = getTargetDirectories(config)
    primaryTargetDir  = targetDirectories[0]
    trashFolder       = os.path.join(primaryTargetDir, 'trash')
    maxDuration       = 10.0
    if not os.path.exists(trashFolder):
        os.makedirs(trashFolder)
        print(color_text(f"✓ Created trash folder: {shortenPath(trashFolder)}\n", fg=GREEN))
    videoExtensions = ('.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm', '.m4v', '.mpg', '.mpeg')
    shortClips = []
    totalScanned = 0
    print(color_text("Scanning folders for video files...\n", fg=YELLOW))
    foldersToScan = []
    seenPaths = set()
    categoryMatching = config.get('categoryMatching', [])
    uniqueFolders = set()
    for entry in categoryMatching:
        folder = entry.get('folder')
        if folder:
            uniqueFolders.add(folder)
    for folder in uniqueFolders:
        folderPath = resolveTargetFolder(folder, targetDirectories)
        if os.path.exists(folderPath) and folderPath not in seenPaths:
            seenPaths.add(folderPath)
            foldersToScan.append((folder, folderPath))
    for folder in ['uncategorized', 'import']:
        folderPath = os.path.join(primaryTargetDir, folder)
        if os.path.exists(folderPath) and folderPath not in seenPaths:
            seenPaths.add(folderPath)
            foldersToScan.append((folder, folderPath))
    for folderName, folderPath in foldersToScan:
        print(color_text(f"  Scanning: {folderName}", fg=WHITE), end='', flush=True)
        try:
            files = [f for f in os.listdir(folderPath) if f.lower().endswith(videoExtensions)]
            for filename in files:
                totalScanned += 1
                if totalScanned % 10 == 0:
                    print('.', end='', flush=True)
                filePath = os.path.join(folderPath, filename)
                duration = getVideoDuration(filePath)
                if duration is not None and duration < maxDuration:
                    shortClips.append({'filename': filename, 'folder': folderName, 'path': filePath, 'duration': duration})
            print(f" ({len(files)} files)")
        except Exception as e:
            print(color_text(f" [ERROR: {e}]", fg=BRIGHT_YELLOW))
    print()
    print("=" * 80)
    print(color_text(f"Scan Complete", fg=CYAN, style=BOLD))
    print("=" * 80)
    print(f"\n{color_text('Total files scanned:', fg=WHITE, style=BOLD)} {totalScanned}")
    print(f"{color_text('Short clips found:', fg=WHITE, style=BOLD)} {len(shortClips)}")
    if not shortClips:
        print(color_text("\n✓ No short clips found!\n", fg=GREEN))
        input(color_text("Press Enter to return to menu...", fg=CYAN))
        return
    print(f"\n{color_text('Files under 10 seconds:', fg=BRIGHT_YELLOW, style=BOLD)}")
    print()
    for i, clip in enumerate(shortClips[:20], 1):
        durationStr = f"{clip['duration']:.1f}s"
        print(f"  {i}. {color_text(clip['filename'][:50], fg=WHITE)} ({durationStr}) [{clip['folder']}]")
    if len(shortClips) > 20:
        print(f"\n  ... and {len(shortClips) - 20} more")
    print()
    print("-" * 80)
    print(color_text("  [M]", fg=BRIGHT_YELLOW, style=BOLD) + " Move to trash folder")
    print(color_text("  [W]", fg=BRIGHT_YELLOW, style=BOLD) + " Write list to file")
    print(color_text("  [Q]", fg=BRIGHT_YELLOW, style=BOLD) + " Return to main menu")
    print()
    k = get_key()
    if k and k.lower() == 'm':
        print()
        confirm = input(color_text(f"⚠️  Move {len(shortClips)} short clips to trash? (Y/n): ", fg=YELLOW))
        if confirm.lower() != 'n':
            movedCount = 0
            failedCount = 0
            print()
            for clip in shortClips:
                try:
                    destPath = os.path.join(trashFolder, clip['filename'])
                    if os.path.exists(destPath):
                        base, ext = os.path.splitext(clip['filename'])
                        counter = 1
                        while os.path.exists(destPath):
                            destPath = os.path.join(trashFolder, f"{base}_{counter}{ext}")
                            counter += 1
                    shutil.move(clip['path'], destPath)
                    movedCount += 1
                    print(color_text(f"  ✓ Moved: {clip['filename']}", fg=GREEN))
                except Exception as e:
                    failedCount += 1
                    print(color_text(f"  ✗ Failed: {clip['filename']} ({e})", fg=BRIGHT_YELLOW))
            print()
            print(color_text(f"✓ Moved {movedCount} files to trash", fg=GREEN, style=BOLD))
            if failedCount > 0:
                print(color_text(f"⚠️  Failed to move {failedCount} files", fg=YELLOW))
        else:
            print(color_text("\nCancelled.\n", fg=YELLOW))
        input(color_text("\nPress Enter to return to menu...", fg=CYAN))
    elif k and k.lower() == 'w':
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reportFolder = (load_organize_config() or {}).get("reportFolder", "~/Desktop")
        outputPath = os.path.expanduser(os.path.join(reportFolder, f"short_clips_{timestamp}.txt"))
        try:
            with open(outputPath, 'w', encoding='utf-8') as f:
                f.write(f"Short Clips Report (< {maxDuration} seconds)\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total files scanned: {totalScanned}\n")
                f.write(f"Short clips found: {len(shortClips)}\n")
                f.write("\n" + "=" * 80 + "\n\n")
                for clip in shortClips:
                    f.write(f"{clip['filename']}\n")
                    f.write(f"  Duration: {clip['duration']:.2f}s\n")
                    f.write(f"  Folder: {clip['folder']}\n")
                    f.write(f"  Path: {clip['path']}\n\n")
            print(color_text(f"\n✓ Report saved to: {shortenPath(outputPath)}\n", fg=GREEN))
        except Exception as e:
            print(color_text(f"\n✗ Failed to write file: {e}\n", fg=BRIGHT_YELLOW))
        input(color_text("Press Enter to return to menu...", fg=CYAN))
    else:
        return

def displayOrganizationSummary(results, dryRun=False):
    """Display summary of organization results."""
    width = 80
    print("\n" + "=" * width)
    title = "Organization Preview" if dryRun else "Organization Complete"
    print(color_text(title, fg=CYAN, style=BOLD).center(width + 20))
    print("=" * width)
    print(f"\n{color_text('Files Moved:', fg=WHITE, style=BOLD)} {results['moved']}")
    if results['categorized']:
        print(f"\n{color_text('By Category:', fg=WHITE, style=BOLD)}")
        for category, files in sorted(results['categorized'].items()):
            print(f"  • {color_text(category, fg=BRIGHT_YELLOW)}: {len(files)} files")
    if results['uncategorized']:
        print(f"\n{color_text('Uncategorized:', fg=WHITE, style=BOLD)} {len(results['uncategorized'])} files")
    if results['failed']:
        print(f"\n{color_text('Failed:', fg=BRIGHT_YELLOW, style=BOLD)} {len(results['failed'])} files")
        for filename, error in results['failed'][:5]:
            print(f"  • {filename}: {error}")
    print("\n" + "=" * width)


def admin_help():
    """Help screen for the Administration menu."""
    clear_screen()
    header("VLC Menu", VERSION, "Administration - Help")
    width = shutil.get_terminal_size().columns
    print()
    lines = [
        ("[P] Preview",        "Dry-run organize of the import folder (no files moved)."),
        ("[O] Organize",       "Move import-folder files into category folders by keyword."),
        ("[D] Duplicates",     "[I] import (hash), [A] all folders (hash), [N] similar names."),
        ("[R] Rescan All",     "Scan every category folder and rebuild the hash cache."),
        ("[F] Fix Folders",    "Create any category folders that are missing."),
        ("[V] Validate",       "Check a folder's files match its category; move or report."),
        ("[S] Short Clips",    "Find videos under 10s and move them to trash."),
        ("[L] Categories",     "List all categories / keywords in CSV form."),
        ("[M] Media Optimize", "Convert non-MP4 videos to MP4 (ffmpeg) by profile."),
        ("[C] Clear Cache",    "Delete the duplicate-detection hash cache."),
        ("[E] Edit",           "Open vlcmenuConfig.json in your editor."),
        ("[Q/ESC]",            "Return to the VLC main menu."),
    ]
    for key, desc in lines:
        print("  " + color_text(f"{key:<20}", fg=BRIGHT_YELLOW, style=BOLD) + desc)
    print()
    print("-" * width)
    input(color_text("Press Enter to return to menu...", fg=CYAN))


def admin_menu():
    """[A] Administration menu — Media File Organizer tools + [M] Media Optimize.

    [Q/ESC/Enter] returns to the VLC main menu.
    """
    config = load_organize_config()
    if not config:
        clear_screen()
        header("VLC Menu", VERSION, "Administration")
        print(color_text("\nNo 'organizeMedia' section found in vlcmenuConfig.json.\n", fg=RED, style=BOLD))
        input(color_text("Press Enter to return...", fg=CYAN))
        return

    while True:
        check_resize()
        width = shutil.get_terminal_size().columns
        clear_screen()
        header("VLC Menu", VERSION, "Administration")
        print()

        print(color_text("Counting files", fg=CYAN), end='', flush=True)
        counts = getFolderCounts(config)
        print("\r" + " " * 50 + "\r", end='', flush=True)
        print(color_text("Folder Summary", fg=CYAN, style=BOLD))
        print("-" * width)
        importCount = f"{counts['import']:,}"
        uncategorizedCount = f"{counts['uncategorized']:,}"
        categoriesCount = f"{counts['categories']:,}"
        print(f"  Import folder:       {color_text(importCount, fg=BRIGHT_YELLOW)} files")
        print(f"  Uncategorized:       {color_text(uncategorizedCount, fg=BRIGHT_YELLOW)} files")
        print(f"  Category folders:    {color_text(categoriesCount, fg=BRIGHT_YELLOW)} files")
        print()

        unknownFolders = checkUnknownFolders(config)
        if unknownFolders:
            print(color_text("⚠️  Warning: Unknown Folders Detected", fg=YELLOW, style=BOLD))
            print("-" * width)
            print(color_text("  The following folders exist but are NOT in your categories list:", fg=YELLOW))
            for folder in sorted(unknownFolders):
                print(f"    • {color_text(folder, fg=BRIGHT_YELLOW)}")
            print()

        legend = (
            color_text(" [P]", fg=BRIGHT_YELLOW, style=BOLD) + " Preview  " +
            color_text("[O]", fg=BRIGHT_YELLOW, style=BOLD) + " Organize  " +
            color_text("[D]", fg=BRIGHT_YELLOW, style=BOLD) + " Duplicates  " +
            color_text("[R]", fg=BRIGHT_YELLOW, style=BOLD) + " Rescan All\n" +
            color_text(" [F]", fg=BRIGHT_YELLOW, style=BOLD) + " Fix Folders  " +
            color_text("[V]", fg=BRIGHT_YELLOW, style=BOLD) + " Validate  " +
            color_text("[S]", fg=BRIGHT_YELLOW, style=BOLD) + " Short Clips  " +
            color_text("[L]", fg=BRIGHT_YELLOW, style=BOLD) + " Categories\n" +
            color_text(" [M]", fg=BRIGHT_YELLOW, style=BOLD) + " Media Optimize " +
            color_text("[C]", fg=BRIGHT_YELLOW, style=BOLD) + " Clear Cache  " +
            color_text("[H]", fg=BRIGHT_YELLOW, style=BOLD) + " Help " +
            color_text("[Q/ESC]", fg=BRIGHT_YELLOW, style=BOLD) + " Quit/Back"
        )
        print("=" * width)
        print(legend)
        print("=" * width)
        print(color_text(" Copyright © 2026 Cloud Box 9 Inc. All rights reserved.", fg=DIM))

        k = get_key()
        if k is None or check_resize():
            continue
        if k == "\x1b" or k in ("\r", "\n"):
            return
        kl = k.lower()
        if kl == "q":
            return
        elif kl == "p":
            previewOrganization(config)
        elif kl == "o":
            runOrganization(config)
        elif kl == "d":
            print()
            print(color_text("\nDuplicate Scan Options:", fg=CYAN, style=BOLD))
            print(color_text("  [I]", fg=BRIGHT_YELLOW, style=BOLD) + " Import folder only (hash-based)")
            print(color_text("  [A]", fg=BRIGHT_YELLOW, style=BOLD) + " All folders (hash-based)")
            print(color_text("  [N]", fg=BRIGHT_YELLOW, style=BOLD) + " Similar Names (file_1.mp4 pattern)")
            print(color_text("  [Q]", fg=BRIGHT_YELLOW, style=BOLD) + " Cancel")
            print()
            subKey = get_key()
            if subKey and subKey.lower() == "i":
                findAndDeleteDuplicates(config)
            elif subKey and subKey.lower() == "a":
                findDuplicatesAllFolders(config)
            elif subKey and subKey.lower() == "n":
                findSimilarNameDuplicatesMenu(config)
        elif kl == "r":
            rescanAllFoldersMenu(config)
        elif kl == "f":
            createMissingFolders(config)
        elif kl == "v":
            validateFolderMenu(config)
        elif kl == "s":
            findShortClips(config)
        elif kl == "l":
            listCategories(config)
        elif kl == "m":
            moProfiles = (load_json_config(CONFIG_PATH) or {}).get("mediaOptimize", {}).get("profiles", [])
            media_optimize_menu(moProfiles)
        elif kl == "c":
            clearCacheFile(config)
        elif kl == "h":
            admin_help()
        elif kl == "e":
            clear_screen()
            header("VLC Menu", VERSION, "Administration")
            print(color_text(f"\nOpening {CONFIG_PATH} in default editor...", fg=YELLOW))
            os.system(f'open "{CONFIG_PATH}"')
            print(color_text("\nNote: Restart the script to load changes.", fg=CYAN))
            input(color_text("\nPress Enter to return to menu...", fg=YELLOW))


# =============================================================================
# MEDIA OPTIMIZE — convert non-MP4 → MP4 (ported from mediaOptimize.py v1.06)
# -----------------------------------------------------------------------------
# Self-contained port. Reads profiles from vlcmenuConfig.json['mediaOptimize'].
# Screens are rebranded to "VLC Menu". The source mediaOptimize.py is NOT
# modified or imported. Entry point: media_optimize_menu(profiles).
# =============================================================================

MO_SCRIPT_NAME = "VLC Menu"
MO_LOG_FILE    = os.path.expanduser(
    (load_json_config(CONFIG_PATH) or {}).get("mediaOptimize", {}).get("logFile")
    or "~/Documents/log/mediaOptimize.log"
)
MO_SOUND_SUCCESS = os.path.join(SCRIPT_DIR, "audio", "success.mp3")
MO_SOUND_FAILURE = os.path.join(SCRIPT_DIR, "audio", "failure.wav")

MO_PHASES = ['Scan', 'Convert', 'Validate', 'Clean Up']
MO_DEFAULT_EXTENSIONS = [
    '.mov', '.avi', '.mkv', '.wmv', '.flv', '.m4v',
    '.mpeg', '.mpg', '.3gp', '.webm', '.ts', '.mts',
    '.m2ts', '.vob', '.asf', '.rm', '.rmvb', '.dv'
]

# Execution-screen layout (rows frozen by ANSI scroll region)
MO_HEADER_LINES = 7
MO_FOOTER_LINES = 3
MO_MIN_HEIGHT   = 14

# Module-level state
_mo_term_cols       = 80
_mo_term_rows       = 24
_mo_current_phase   = ''
_mo_done_phases     = []
_mo_failed_phases   = []
_mo_run_start_time  = None
_mo_run_end_time    = None
_mo_current_profile = ''
_mo_timer_thread    = None
_mo_timer_stop      = None
_mo_current_mode    = 'select'
_mo_sigwinch_draw_fn = None
_mo_is_paused       = False

_MO_ANSI_RE = re.compile(r'\033\[[0-9;]*[A-Za-z]|\0337|\0338')


def _mo_mv(row, col=1):   return f"\033[{row};{col}H"
def _mo_el():             return "\033[2K"
def _mo_set_sr(t, b):     return f"\033[{t};{b}r"
def _mo_rst_sr():         return "\033[r"
def _mo_clr():            return "\033[2J"
def _mo_hide_cur():       return "\033[?25l"
def _mo_show_cur():       return "\033[?25h"
def _mo_save_cur():       return "\0337"
def _mo_rest_cur():       return "\0338"


def _mo_read_key():
    """Read one keypress. Returns 'UP','DOWN','ENTER','SPACE','ESC', or char. (cbreak mode)"""
    fd  = sys.stdin.fileno()
    ch  = os.read(fd, 1).decode('utf-8', errors='replace')
    if ch == '\x1b':
        ready, _, _ = select.select([fd], [], [], 0.1)
        if ready:
            ch2 = os.read(fd, 1).decode('utf-8', errors='replace')
            if ch2 == '[':
                r2, _, _ = select.select([fd], [], [], 0.1)
                if r2:
                    ch3 = os.read(fd, 1).decode('utf-8', errors='replace')
                    if ch3 == 'A': return 'UP'
                    if ch3 == 'B': return 'DOWN'
                    if ch3 == 'C': return 'RIGHT'
                    if ch3 == 'D': return 'LEFT'
                return 'ESC'
            return 'ESC'
        return 'ESC'
    if ch in ('\r', '\n'): return 'ENTER'
    if ch == ' ':           return 'SPACE'
    return ch


def _mo_reset_terminal():
    sys.stdout.write(_mo_rst_sr() + _mo_show_cur() + _mo_clr() + _mo_mv(1))
    sys.stdout.flush()


def _mo_build_phase_bar():
    parts = []
    for p in MO_PHASES:
        if p in _mo_done_phases:
            parts.append(f"{GREEN}✓ {p}{RESET}")
        elif p in _mo_failed_phases:
            parts.append(f"{RED}✗ {p}{RESET}")
        elif p == _mo_current_phase:
            parts.append(f"{BOLD}{BRIGHT_YELLOW}▶ {p}{RESET}")
        else:
            parts.append(f"{DIM}{WHITE}○ {p}{RESET}")
    return f" {' | '.join(parts)}"


def _mo_build_exec_legend():
    if _mo_is_paused:
        return (f" {BOLD}{BRIGHT_YELLOW}⏸  PAUSED{RESET}"
                f"   {BRIGHT_YELLOW}[P]{RESET} Resume"
                f"   {BRIGHT_YELLOW}[ESC]{RESET} Quit")
    return (f" {BRIGHT_YELLOW}[P]{RESET} Pause"
            f"   {BRIGHT_YELLOW}[ESC]{RESET} Quit")


def _mo_update_exec_legend():
    ft  = (_mo_term_rows - MO_FOOTER_LINES + 1) if _mo_term_rows else 20
    out = _mo_save_cur() + _mo_mv(ft + 1) + _mo_el() + _mo_build_exec_legend() + _mo_rest_cur()
    sys.stdout.write(out)
    sys.stdout.flush()


def _mo_setup_exec_display():
    global _mo_term_cols, _mo_term_rows
    size       = shutil.get_terminal_size()
    cols, rows = size.columns, size.lines
    _mo_term_cols = cols
    _mo_term_rows = rows

    if rows < MO_MIN_HEIGHT:
        sys.stdout.write(_mo_clr() + _mo_mv(1) + color_text(
            f" Terminal too small — need at least {MO_MIN_HEIGHT} rows (current: {rows}).", fg=YELLOW
        ) + "\r\n")
        sys.stdout.flush()
        return

    w, out = cols, []
    out.append(_mo_rst_sr() + _mo_clr() + _mo_hide_cur())
    prof = _mo_current_profile or 'Unknown Profile'
    out.append(_mo_mv(1) + _mo_el() + "=" * w)
    out.append(_mo_mv(2) + _mo_el() +
               f" {BOLD}{CYAN}{MO_SCRIPT_NAME}{RESET} {MAGENTA}{VERSION}{RESET}"
               f"  {DIM}{WHITE}[Profile: {prof}]{RESET}")
    out.append(_mo_mv(3) + _mo_el() + "=" * w)

    if _mo_run_start_time:
        st   = _mo_run_start_time.strftime('%I:%M:%S %p').lstrip('0')
        secs = ((_mo_run_end_time or datetime.now()) - _mo_run_start_time).total_seconds()
        h, m, s = int(secs // 3600), int((secs % 3600) // 60), int(secs % 60)
        rt   = f"{h:02d}:{m:02d}:{s:02d}"
        et   = _mo_run_end_time.strftime('%I:%M:%S %p').lstrip('0') if _mo_run_end_time else 'Running...'
    else:
        st, rt, et = '--:--:--', '00:00:00', '--'

    out.append(_mo_mv(4) + _mo_el() +
               f" Start Time: {WHITE}{st}{RESET}   End Time  : {WHITE}{et}{RESET}")
    out.append(_mo_mv(5) + _mo_el() + f" Run Time  : {BRIGHT_YELLOW}{rt}{RESET}")
    out.append(_mo_mv(6) + _mo_el() + _mo_build_phase_bar())
    out.append(_mo_mv(7) + _mo_el() + "=" * w)

    ft = rows - MO_FOOTER_LINES + 1
    out.append(_mo_mv(ft)     + _mo_el() + "=" * w)
    out.append(_mo_mv(ft + 1) + _mo_el() + _mo_build_exec_legend())
    out.append(_mo_mv(ft + 2) + _mo_el() +
               f" {DIM}{WHITE}Copyright © 2026 Cloud Box 9 Inc. All rights reserved.{RESET}")

    scroll_top    = MO_HEADER_LINES + 1
    scroll_bottom = rows - MO_FOOTER_LINES
    out.append(_mo_set_sr(scroll_top, scroll_bottom))
    out.append(_mo_mv(scroll_top))
    sys.stdout.write("".join(out))
    sys.stdout.flush()


def _mo_update_phase_row():
    out = _mo_save_cur() + _mo_mv(6) + _mo_el() + _mo_build_phase_bar() + _mo_rest_cur()
    sys.stdout.write(out)
    sys.stdout.flush()


def _mo_update_time_rows():
    if _mo_run_start_time:
        st   = _mo_run_start_time.strftime('%I:%M:%S %p').lstrip('0')
        secs = ((_mo_run_end_time or datetime.now()) - _mo_run_start_time).total_seconds()
        h, m, s = int(secs // 3600), int((secs % 3600) // 60), int(secs % 60)
        rt   = f"{h:02d}:{m:02d}:{s:02d}"
        et   = _mo_run_end_time.strftime('%I:%M:%S %p').lstrip('0') if _mo_run_end_time else 'Running...'
    else:
        st, rt, et = '--:--:--', '00:00:00', '--'
    out = (_mo_save_cur()
           + _mo_mv(4) + _mo_el() +
           f" Start Time: {WHITE}{st}{RESET}   End Time  : {WHITE}{et}{RESET}"
           + _mo_mv(5) + _mo_el() + f" Run Time  : {BRIGHT_YELLOW}{rt}{RESET}"
           + _mo_rest_cur())
    sys.stdout.write(out)
    sys.stdout.flush()


def _mo_print_line(text):
    w       = _mo_term_cols or get_width()
    visible = _MO_ANSI_RE.sub('', text)
    if len(visible) >= w:
        print(visible[:w - 4] + '...')
    else:
        print(text)


def _mo_timer_loop():
    while _mo_timer_stop and not _mo_timer_stop.is_set():
        _mo_update_time_rows()
        time.sleep(1.0)


def _mo_start_timer():
    global _mo_timer_thread, _mo_timer_stop
    _mo_timer_stop   = threading.Event()
    _mo_timer_thread = threading.Thread(target=_mo_timer_loop, daemon=True)
    _mo_timer_thread.start()


def _mo_stop_timer():
    global _mo_timer_thread, _mo_timer_stop
    if _mo_timer_stop:
        _mo_timer_stop.set()
    if _mo_timer_thread and _mo_timer_thread.is_alive():
        _mo_timer_thread.join(timeout=2.0)
    _mo_timer_thread = None
    _mo_timer_stop   = None
    _mo_update_time_rows()


class _MO_KeyboardListener:
    """Background thread reading stdin in cbreak mode during execution.
    Plain ESC → quit_event; P/p → toggle pause_flag; arrows swallowed."""

    def __init__(self):
        self.quit_event    = threading.Event()
        self.pause_flag    = threading.Event()
        self._stop_flag    = threading.Event()
        self._thread       = None
        self._old_settings = None

    def start(self):
        self._stop_flag.clear()
        self.quit_event.clear()
        self.pause_flag.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_flag.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self._thread = None
        self._restore()

    def _set_cbreak(self):
        fd = sys.stdin.fileno()
        self._old_settings = termios.tcgetattr(fd)
        tty.setcbreak(fd)

    def _restore(self):
        if self._old_settings is not None:
            try:
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self._old_settings)
            except Exception:
                pass
            self._old_settings = None

    def _run(self):
        global _mo_is_paused
        self._set_cbreak()
        fd = sys.stdin.fileno()
        try:
            while not self._stop_flag.is_set():
                ready, _, _ = select.select([fd], [], [], 0.1)
                if not ready:
                    continue
                ch = os.read(fd, 1).decode('utf-8', errors='replace')
                if ch == '\x1b':
                    r2, _, _ = select.select([fd], [], [], 0.05)
                    if r2:
                        ch2 = os.read(fd, 1).decode('utf-8', errors='replace')
                        if ch2 == '[':
                            r3, _, _ = select.select([fd], [], [], 0.05)
                            if r3:
                                os.read(fd, 1)
                    else:
                        self.quit_event.set()
                elif ch in ('p', 'P'):
                    if self.pause_flag.is_set():
                        self.pause_flag.clear()
                        _mo_is_paused = False
                    else:
                        self.pause_flag.set()
                        _mo_is_paused = True
                    _mo_update_exec_legend()
        finally:
            self._restore()


def _mo_sigwinch(signum, frame):
    if _mo_current_mode == 'execute':
        _mo_setup_exec_display()
    elif _mo_sigwinch_draw_fn:
        _mo_sigwinch_draw_fn()


def mo_get_extensions(profile):
    result = []
    for ext in profile.get('extensions', MO_DEFAULT_EXTENSIONS):
        ext = ext.strip().lower()
        if not ext.startswith('.'):
            ext = '.' + ext
        result.append(ext)
    return result


def mo_scan_for_videos(profile):
    """Recursively scan profile directories for non-MP4 video files."""
    extensions = mo_get_extensions(profile)
    found      = []
    for raw_dir in profile.get('directories', []):
        directory = os.path.expanduser(raw_dir)
        if not os.path.isdir(directory):
            continue
        for root, dirs, files in os.walk(directory):
            dirs[:] = sorted(d for d in dirs if not d.startswith('.'))
            for fname in sorted(files):
                if fname.startswith('.'):
                    continue
                _, ext = os.path.splitext(fname)
                if ext.lower() in extensions:
                    full_path = os.path.join(root, fname)
                    try:
                        size = os.path.getsize(full_path)
                    except OSError:
                        size = 0
                    found.append({'path': full_path, 'size': size, 'rel_dir': raw_dir})
    return found


def _mo_fmt_size(n):
    for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def _mo_get_output_path(source_path, profile):
    base    = os.path.splitext(os.path.basename(source_path))[0]
    out_dir = profile.get('outputDirectory')
    if out_dir:
        out_dir = os.path.expanduser(out_dir)
        os.makedirs(out_dir, exist_ok=True)
    else:
        out_dir = os.path.dirname(source_path)
    return os.path.join(out_dir, base + '.mp4')


def mo_convert_file(source_path, output_path, quit_event=None, pause_flag=None):
    """Convert source to MP4 (H.264/AAC) via ffmpeg. Returns (success, error_msg)."""
    cmd = [
        'ffmpeg', '-y', '-i', source_path,
        '-c:v', 'libx264', '-crf', '23', '-preset', 'medium',
        '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', output_path
    ]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stderr_bytes = b''
        while True:
            try:
                _, stderr_bytes = proc.communicate(timeout=0.3)
                break
            except subprocess.TimeoutExpired:
                if pause_flag and pause_flag.is_set():
                    proc.send_signal(signal.SIGSTOP)
                    while pause_flag and pause_flag.is_set():
                        if quit_event and quit_event.is_set():
                            proc.send_signal(signal.SIGCONT)
                            proc.kill()
                            proc.communicate()
                            return False, 'Aborted by user'
                        time.sleep(0.1)
                    proc.send_signal(signal.SIGCONT)
                elif quit_event and quit_event.is_set():
                    proc.kill()
                    proc.communicate()
                    return False, 'Aborted by user'
        if proc.returncode == 0:
            return True, ''
        err = stderr_bytes.decode('utf-8', errors='replace')[-500:] if stderr_bytes else 'ffmpeg failed'
        return False, err
    except FileNotFoundError:
        return False, 'ffmpeg not found — run: brew install ffmpeg'
    except Exception as e:
        return False, str(e)


def mo_validate_file(output_path):
    """Verify converted file via ffprobe. Returns (valid, error_msg)."""
    if not os.path.exists(output_path):
        return False, 'Output file not found'
    if os.path.getsize(output_path) == 0:
        return False, 'Output file is empty'
    cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', '-show_format', output_path]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return False, 'ffprobe could not read file'
        data      = json.loads(result.stdout)
        has_video = any(s.get('codec_type') == 'video' for s in data.get('streams', []))
        duration  = float(data.get('format', {}).get('duration', 0))
        if not has_video:
            return False, 'No video stream found'
        if duration <= 0:
            return False, 'Duration is zero or unknown'
        return True, ''
    except (json.JSONDecodeError, ValueError):
        return False, 'Could not parse ffprobe output'
    except subprocess.TimeoutExpired:
        return False, 'ffprobe timed out'
    except FileNotFoundError:
        return False, 'ffprobe not found — run: brew install ffmpeg'
    except Exception as e:
        return False, str(e)


def _mo_ensure_log_dir():
    os.makedirs(os.path.dirname(os.path.expanduser(MO_LOG_FILE)), exist_ok=True)


def _mo_write_log(message):
    _mo_ensure_log_dir()
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(os.path.expanduser(MO_LOG_FILE), 'a') as f:
        f.write(f"[{ts}] {message}\n")


def _mo_write_log_header(profile_name, file_count):
    _mo_ensure_log_dir()
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(os.path.expanduser(MO_LOG_FILE), 'a') as f:
        f.write(f"\n{'=' * 80}\n")
        f.write(f"  {MO_SCRIPT_NAME} {VERSION}  |  Profile: {profile_name}  |  {ts}\n")
        f.write(f"  Files to convert: {file_count}\n")
        f.write(f"{'=' * 80}\n")


def _mo_write_log_footer(success_cnt, fail_cnt, elapsed_sec, orig_bytes=0, new_bytes=0):
    h = int(elapsed_sec // 3600)
    m = int((elapsed_sec % 3600) // 60)
    s = int(elapsed_sec % 60)
    saved = max(0, orig_bytes - new_bytes)
    pct   = (saved / orig_bytes * 100) if orig_bytes > 0 else 0.0
    with open(os.path.expanduser(MO_LOG_FILE), 'a') as f:
        f.write(f"{'=' * 80}\n")
        f.write(f"  Completed  |  Success: {success_cnt}"
                f"  |  Failed: {fail_cnt}  |  Run Time: {h:02d}:{m:02d}:{s:02d}\n")
        if orig_bytes > 0:
            f.write(
                f"  Original: {_mo_fmt_size(orig_bytes)}"
                f"  |  Converted: {_mo_fmt_size(new_bytes)}"
                f"  |  Total Saved: {_mo_fmt_size(saved)} ({pct:.1f}%)\n"
            )
        f.write(f"{'=' * 80}\n\n")


def _mo_draw_profile_selection(profiles, cursor):
    """Full-screen profile selection. cursor is a list [int] for mutable closure."""
    w   = get_width()
    out = []
    out.append("=" * w)
    out.append(f" {BOLD}{CYAN}{MO_SCRIPT_NAME}{RESET} {MAGENTA}{VERSION}{RESET}"
               f"  {DIM}{WHITE}[Media Optimise - Profiles]{RESET}")
    out.append("=" * w)
    out.append("")
    for i, p in enumerate(profiles):
        is_cur   = (i == cursor[0])
        arrow    = f"{BOLD}{BRIGHT_YELLOW}▶{RESET}" if is_cur else " "
        name_str = (f"{BOLD}{WHITE}{p['name']}{RESET}" if is_cur
                    else f"{DIM}{WHITE}{p['name']}{RESET}")
        out.append(f" {arrow} {name_str}")
        dirs = p.get('directories', [])
        for d in dirs[:3]:
            out.append(f"      {DIM}{WHITE}{os.path.expanduser(d)}{RESET}")
        if len(dirs) > 3:
            out.append(f"      {DIM}{WHITE}... and {len(dirs) - 3} more{RESET}")
        dm_map  = {'none': 'Keep originals', 'after_each': 'Delete after each',
                   'after_all': 'Delete after all'}
        dm      = dm_map.get(p.get('deleteMode', 'none'), p.get('deleteMode', 'none'))
        out.append(f"      {DIM}Delete mode: {dm}{RESET}")
        out.append("")
    out.append("=" * w)
    out.append(f" {BRIGHT_YELLOW}[↑↓]{RESET} Navigate  "
               f"{BRIGHT_YELLOW}[Enter]{RESET} Select  "
               f"{BRIGHT_YELLOW}[H]{RESET} Help  "
               f"{BRIGHT_YELLOW}[Q/ESC]{RESET} Quit/Back")
    out.append("=" * w)
    out.append(f" {DIM}{WHITE}Copyright © 2026 Cloud Box 9 Inc. All rights reserved.{RESET}")
    sys.stdout.write("\033[H\033[2J" + "\n".join(out) + "\n")
    sys.stdout.flush()


def _mo_help():
    """Brief help for the Media Optimize screens (cbreak-safe; waits for a key)."""
    w = get_width()
    sys.stdout.write("\033[H\033[2J")
    print("=" * w)
    print(f" {BOLD}{CYAN}{MO_SCRIPT_NAME}{RESET} {MAGENTA}{VERSION}{RESET}  {DIM}{WHITE}[Media Optimise - Help]{RESET}")
    print("=" * w)
    print()
    print(f"  Media Optimize converts non-MP4 video files to MP4 (H.264/AAC) via ffmpeg.")
    print()
    print(f"  {BRIGHT_YELLOW}Profile screen:{RESET}  [↑↓] move   [Enter] choose   [Q/ESC] back to Admin")
    print(f"  {BRIGHT_YELLOW}File screen:{RESET}     [↑↓] move   [Space] toggle   [A] all   [N] none   [Enter] convert")
    print(f"  {BRIGHT_YELLOW}While running:{RESET}   [P] pause / resume   [ESC] abort")
    print()
    print(f"  Delete mode (per profile): Keep originals / Delete after each / Delete after all.")
    print(f"  Each converted file is validated with ffprobe before its original is removed.")
    print()
    print("=" * w)
    print(f" {BRIGHT_YELLOW}Press any key to return...{RESET}")
    print("=" * w)
    print(f" {DIM}{WHITE}Copyright © 2026 Cloud Box 9 Inc. All rights reserved.{RESET}")
    sys.stdout.flush()
    _mo_read_key()


def _mo_run_profile_selection(profiles):
    """Arrow-key profile selection. Returns chosen profile dict, or None on quit/back."""
    global _mo_sigwinch_draw_fn
    cursor = [0]
    fd, old = sys.stdin.fileno(), termios.tcgetattr(sys.stdin.fileno())
    tty.setcbreak(fd)
    _mo_sigwinch_draw_fn = lambda: _mo_draw_profile_selection(profiles, cursor)
    try:
        while True:
            _mo_draw_profile_selection(profiles, cursor)
            key = _mo_read_key()
            if key == 'UP'    and cursor[0] > 0:                   cursor[0] -= 1
            elif key == 'DOWN' and cursor[0] < len(profiles) - 1:  cursor[0] += 1
            elif key in ('h', 'H'):                                _mo_help()
            elif key == 'ENTER':                                    return profiles[cursor[0]]
            elif key in ('q', 'Q', 'ESC'):                         return None
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
        _mo_sigwinch_draw_fn = None


class _MO_FileItem:
    __slots__ = ('path', 'size', 'rel_dir', 'checked')

    def __init__(self, r):
        self.path    = r['path']
        self.size    = r['size']
        self.rel_dir = r['rel_dir']
        self.checked = True


def _mo_file_view_size():
    rows = shutil.get_terminal_size().lines
    return min(max(5, rows - 16), 100)


def _mo_draw_file_selection(items, cursor_idx, view_start_idx, profile_name):
    """Full-screen file selection with scrollable viewport."""
    w          = get_width()
    total_cnt  = len(items)
    total_size = sum(it.size for it in items)
    chk_cnt    = sum(1 for it in items if it.checked)
    chk_size   = sum(it.size for it in items if it.checked)
    vs         = view_start_idx
    view_size  = _mo_file_view_size()
    visible    = items[vs : vs + view_size]

    out = []
    out.append("=" * w)
    out.append(f" {BOLD}{CYAN}{MO_SCRIPT_NAME}{RESET} {MAGENTA}{VERSION}{RESET}"
               f"  {DIM}{WHITE}[File Selection — {profile_name}]{RESET}")
    out.append("=" * w)
    if total_cnt > view_size:
        range_tag = (f"  {DIM}[showing {vs + 1}–{min(vs + view_size, total_cnt)}"
                     f" of {total_cnt}]{RESET}")
    else:
        range_tag = ""
    out.append(
        f" Found {WHITE}{total_cnt}{RESET} files ({_mo_fmt_size(total_size)})"
        f"  |  {GREEN}{chk_cnt} selected ({_mo_fmt_size(chk_size)}){RESET}"
        + range_tag
    )
    out.append("")
    if vs > 0:
        out.append(f"  {DIM}{BRIGHT_YELLOW}↑  {vs} file{'s' if vs != 1 else ''} above{RESET}")
    last_dir = None
    for j, it in enumerate(visible):
        idx    = vs + j
        is_cur = (idx == cursor_idx)
        if it.rel_dir != last_dir:
            last_dir = it.rel_dir
            out.append(f"  {BOLD}{CYAN}{os.path.expanduser(it.rel_dir)}{RESET}")
            out.append(f"  {DIM}{'─' * min(60, w - 4)}{RESET}")
        arrow    = f"{BOLD}{BRIGHT_YELLOW}▶{RESET}" if is_cur else " "
        box      = f"{GREEN}[✓]{RESET}" if it.checked else f"{DIM}[ ]{RESET}"
        fname    = os.path.basename(it.path)
        max_name = w - 24
        if len(fname) > max_name:
            fname = fname[:max_name - 3] + '...'
        label = (f"{BOLD}{WHITE}{fname}{RESET}" if is_cur
                 else (f"{WHITE}{fname}{RESET}" if it.checked
                       else f"{DIM}{WHITE}{fname}{RESET}"))
        out.append(f" {arrow} {box} {label}  {DIM}{_mo_fmt_size(it.size)}{RESET}")
    below = total_cnt - (vs + len(visible))
    if below > 0:
        out.append(f"  {DIM}{BRIGHT_YELLOW}↓  {below} file{'s' if below != 1 else ''} below{RESET}")
    out.append("")
    if chk_cnt == 0:
        out.append(f"  {YELLOW}⚠  No files selected — press [A] to select all.{RESET}")
        out.append("")
    out.append("=" * w)
    out.append(f" {BRIGHT_YELLOW}[↑↓]{RESET} Navigate  "
               f"{BRIGHT_YELLOW}[Space]{RESET} Toggle  "
               f"{BRIGHT_YELLOW}[A]{RESET} All  "
               f"{BRIGHT_YELLOW}[N]{RESET} None  "
               f"{BRIGHT_YELLOW}[Enter]{RESET} Convert  "
               f"{BRIGHT_YELLOW}[Q/ESC]{RESET} Back")
    out.append("=" * w)
    out.append(f" {DIM}{WHITE}Copyright © 2026 Cloud Box 9 Inc. All rights reserved.{RESET}")
    sys.stdout.write("\033[H\033[2J" + "\n".join(out) + "\n")
    sys.stdout.flush()


def _mo_run_file_selection(items, profile_name):
    """Arrow-key + space file selection. Returns list of selected items, or None if backed out."""
    if not items:
        return []
    global _mo_sigwinch_draw_fn
    cursor     = [0]
    view_start = [0]

    def _scroll_to_cursor():
        vs = _mo_file_view_size()
        if cursor[0] < view_start[0]:
            view_start[0] = cursor[0]
        elif cursor[0] >= view_start[0] + vs:
            view_start[0] = cursor[0] - vs + 1
        view_start[0] = max(0, view_start[0])

    def _redraw():
        _scroll_to_cursor()
        _mo_draw_file_selection(items, cursor[0], view_start[0], profile_name)

    fd, old = sys.stdin.fileno(), termios.tcgetattr(sys.stdin.fileno())
    tty.setcbreak(fd)
    _mo_sigwinch_draw_fn = _redraw
    try:
        while True:
            _redraw()
            key = _mo_read_key()
            if key == 'UP' and cursor[0] > 0:
                cursor[0] -= 1
            elif key == 'DOWN' and cursor[0] < len(items) - 1:
                cursor[0] += 1
            elif key == 'SPACE':
                items[cursor[0]].checked = not items[cursor[0]].checked
            elif key in ('a', 'A'):
                for it in items: it.checked = True
            elif key in ('n', 'N'):
                for it in items: it.checked = False
            elif key == 'ENTER':
                selected = [it for it in items if it.checked]
                if selected:
                    return selected
            elif key in ('q', 'Q', 'ESC', 'b', 'B'):
                return None
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
        _mo_sigwinch_draw_fn = None


def mo_run_conversion(profile, selected_files):
    """Convert selected files, validate, and delete originals per delete mode.
    Returns (success_count, fail_count, results)."""
    global _mo_current_phase, _mo_run_start_time, _mo_run_end_time, _mo_current_profile
    global _mo_done_phases, _mo_failed_phases, _mo_current_mode, _mo_is_paused

    delete_mode  = profile.get('deleteMode', 'none')
    profile_name = profile.get('name', 'Unknown')
    total        = len(selected_files)
    success_cnt  = 0
    fail_cnt     = 0
    results      = []
    aborted      = False
    total_orig_bytes = 0
    total_new_bytes  = 0

    _mo_write_log_header(profile_name, total)

    _mo_current_profile = profile_name
    _mo_current_mode    = 'execute'
    _mo_done_phases     = []
    _mo_failed_phases   = []
    _mo_run_start_time  = datetime.now()
    _mo_run_end_time    = None
    _mo_current_phase   = 'Scan'
    _mo_is_paused       = False
    _mo_setup_exec_display()
    _mo_start_timer()

    _kb = _MO_KeyboardListener()
    _kb.start()

    try:
        _mo_done_phases.append('Scan')
        _mo_current_phase = 'Convert'
        _mo_update_phase_row()
        _mo_print_line(f" Starting conversion of {total} file(s)...")
        _mo_print_line("")

        for i, file_item in enumerate(selected_files):
            if _kb and _kb.pause_flag.is_set():
                while _kb.pause_flag.is_set():
                    if _kb.quit_event.is_set():
                        break
                    time.sleep(0.1)
            if _kb and _kb.quit_event.is_set():
                aborted = True
                _mo_write_log("Aborted by user before remaining files")
                break

            src      = file_item.path
            src_size = file_item.size
            out      = _mo_get_output_path(src, profile)
            name     = os.path.basename(src)

            _mo_print_line(f" [{i + 1}/{total}] Converting: {name}  ({_mo_fmt_size(src_size)})")
            _mo_write_log(f"[{i + 1}/{total}] {name}  ({_mo_fmt_size(src_size)})")

            ok, err = mo_convert_file(src, out,
                                      quit_event=(_kb.quit_event if _kb else None),
                                      pause_flag=(_kb.pause_flag if _kb else None))

            if err == 'Aborted by user':
                aborted = True
                if os.path.exists(out):
                    try:
                        os.remove(out)
                        _mo_print_line(f"   {DIM}Removed partial file: {os.path.basename(out)}{RESET}")
                        _mo_write_log(f"  Removed partial file: {out}")
                    except OSError as e:
                        _mo_print_line(f"   {YELLOW}⚠ Could not remove partial file: {e}{RESET}")
                        _mo_write_log(f"  ⚠ Could not remove partial file: {e}")
                _mo_print_line(f"   {YELLOW}⚠ Conversion aborted{RESET}")
                _mo_write_log("Aborted by user")
                break

            if ok:
                _mo_print_line(f"   {DIM}→ Validating...{RESET}")
                valid, verr = mo_validate_file(out)
                if valid:
                    out_bytes = os.path.getsize(out)
                    saved     = max(0, src_size - out_bytes)
                    pct       = (saved / src_size * 100) if src_size > 0 else 0.0
                    total_orig_bytes += src_size
                    total_new_bytes  += out_bytes
                    run_saved = max(0, total_orig_bytes - total_new_bytes)
                    run_pct   = (run_saved / total_orig_bytes * 100) if total_orig_bytes > 0 else 0.0
                    _mo_print_line(
                        f"   {GREEN}✓ {os.path.basename(out)} ({_mo_fmt_size(out_bytes)})"
                        f"  |  Saved: {_mo_fmt_size(saved)} ({pct:.1f}%){RESET}"
                    )
                    _mo_write_log(
                        f"  ✓  {os.path.basename(out)}  ({_mo_fmt_size(out_bytes)})"
                        f"  |  Saved: {_mo_fmt_size(saved)} ({pct:.1f}%)"
                        f"  |  Running: {_mo_fmt_size(total_orig_bytes)} → {_mo_fmt_size(total_new_bytes)}"
                        f"  |  Total saved: {_mo_fmt_size(run_saved)} ({run_pct:.1f}%)"
                    )
                    success_cnt += 1
                    results.append({'src': src, 'out': out, 'success': True,
                                    'src_size': src_size, 'out_size': out_bytes})
                    if delete_mode == 'after_each':
                        try:
                            os.remove(src)
                            _mo_print_line(f"   {DIM}Deleted original: {name}{RESET}")
                            _mo_write_log(f"  Deleted: {src}")
                        except OSError as e:
                            _mo_print_line(f"   {YELLOW}⚠ Could not delete original: {e}{RESET}")
                            _mo_write_log(f"  ⚠ Could not delete: {e}")
                else:
                    _mo_print_line(f"   {RED}✗ Validation failed: {verr}{RESET}")
                    _mo_write_log(f"  ✗ Validation failed: {verr}")
                    try:
                        os.remove(out)
                    except OSError:
                        pass
                    fail_cnt += 1
                    results.append({'src': src, 'out': None, 'success': False,
                                    'error': f"Validation: {verr}", 'src_size': src_size, 'out_size': 0})
            else:
                _mo_print_line(f"   {RED}✗ Conversion failed: {err[:100]}{RESET}")
                _mo_write_log(f"  ✗ Conversion failed: {err[:200]}")
                fail_cnt += 1
                results.append({'src': src, 'out': None, 'success': False,
                                'error': err[:100], 'src_size': src_size, 'out_size': 0})
            _mo_print_line("")

        if aborted:
            _mo_failed_phases.extend(['Convert', 'Validate'])
        elif fail_cnt == 0:
            _mo_done_phases.extend(['Convert', 'Validate'])
        else:
            if success_cnt > 0:
                _mo_done_phases.append('Convert')
            _mo_failed_phases.append('Validate')
        _mo_current_phase = 'Clean Up'
        _mo_update_phase_row()

        if not aborted and delete_mode == 'after_all':
            deleted = 0
            for r in results:
                if r['success']:
                    try:
                        os.remove(r['src'])
                        deleted += 1
                        _mo_print_line(f" {DIM}Deleted: {os.path.basename(r['src'])}{RESET}")
                        _mo_write_log(f"Deleted: {r['src']}")
                    except OSError as e:
                        _mo_print_line(f" {YELLOW}⚠ Could not delete: {e}{RESET}")
                        _mo_write_log(f"⚠ Could not delete: {e}")
            if deleted:
                _mo_print_line(f" {DIM}Deleted {deleted} original file(s).{RESET}")

        if 'Clean Up' not in _mo_done_phases and 'Clean Up' not in _mo_failed_phases:
            _mo_done_phases.append('Clean Up')
        _mo_current_phase = ''
        _mo_update_phase_row()
        if _mo_run_end_time is None:
            _mo_run_end_time = datetime.now()
        _mo_stop_timer()
    finally:
        if _mo_run_end_time is None:
            _mo_run_end_time = datetime.now()
            _mo_stop_timer()
        elapsed = 0
        if _mo_run_start_time:
            elapsed = ((_mo_run_end_time or datetime.now()) - _mo_run_start_time).total_seconds()
        _mo_write_log_footer(success_cnt, fail_cnt, elapsed, total_orig_bytes, total_new_bytes)
        if _kb:
            _kb.stop()

    return success_cnt, fail_cnt, results


def _mo_show_scanning(profile):
    w = get_width()
    sys.stdout.write("\033[H\033[2J")
    print("=" * w)
    print(f" {BOLD}{CYAN}{MO_SCRIPT_NAME}{RESET} {MAGENTA}{VERSION}{RESET}  {DIM}{WHITE}[Scanning...]{RESET}")
    print("=" * w)
    print()
    print(f" Scanning profile: {CYAN}{profile['name']}{RESET}")
    for d in profile.get('directories', []):
        print(f"   {DIM}{os.path.expanduser(d)}{RESET}")
    print()
    sys.stdout.flush()


def _mo_show_no_files_screen(profile_name):
    w = get_width()
    sys.stdout.write("\033[H\033[2J")
    print("=" * w)
    print(f" {BOLD}{CYAN}{MO_SCRIPT_NAME}{RESET} {MAGENTA}{VERSION}{RESET}")
    print("=" * w)
    print()
    print(f" {YELLOW}No non-MP4 video files found in profile: {BOLD}{profile_name}{RESET}")
    print()
    print(f" {DIM}All videos may already be MP4, or the directories are empty.{RESET}")
    print()
    print(f" Press any key to return to profile selection...")
    print()
    print("=" * w)
    print(f" {DIM}{WHITE}Copyright © 2026 Cloud Box 9 Inc. All rights reserved.{RESET}")
    sys.stdout.flush()


def _mo_show_summary(profile_name, success_cnt, fail_cnt, results):
    w = get_width()
    sys.stdout.write("\033[H\033[2J")
    print("=" * w)
    print(f" {BOLD}{CYAN}{MO_SCRIPT_NAME}{RESET} {MAGENTA}{VERSION}{RESET}  {DIM}{WHITE}[Complete — {profile_name}]{RESET}")
    print("=" * w)
    print()
    total = success_cnt + fail_cnt
    print(f"  Results: {GREEN}{success_cnt} succeeded{RESET}  {RED}{fail_cnt} failed{RESET}  (of {total} files)")
    print()
    for r in results:
        icon = f"{GREEN}✓{RESET}" if r['success'] else f"{RED}✗{RESET}"
        src_name = os.path.basename(r['src'])
        if r['success']:
            out_name = os.path.basename(r['out'])
            print(f"  {icon}  {DIM}{src_name:<40}{RESET}  →  {WHITE}{out_name}{RESET}")
        else:
            err = r.get('error', 'Unknown error')
            print(f"  {icon}  {DIM}{src_name:<40}{RESET}  {RED}({err[:55]}){RESET}")
    print()
    print(f"  Log: {DIM}{MO_LOG_FILE}{RESET}")
    print()
    print("=" * w)
    print(f" {BRIGHT_YELLOW}[Enter]{RESET} New Profile  {BRIGHT_YELLOW}[Q/ESC]{RESET} Quit/Back")
    print("=" * w)
    print(f" {DIM}{WHITE}Copyright © 2026 Cloud Box 9 Inc. All rights reserved.{RESET}")
    sys.stdout.flush()


def media_optimize_menu(profiles):
    """[M] Media Optimize — profile selection + full convert flow.

    Ported from mediaOptimize.py run_interactive(); reads profiles from
    vlcmenuConfig.json['mediaOptimize']['profiles']. Returns to the Admin menu.
    """
    global _mo_current_mode
    if not profiles:
        clear_screen()
        header("VLC Menu", VERSION, "Media Optimise - Profiles")
        print(color_text("\nNo Media Optimize profiles found in vlcmenuConfig.json.\n", fg=RED, style=BOLD))
        input(color_text("Press Enter to return...", fg=CYAN))
        return

    old_handler = signal.getsignal(signal.SIGWINCH)
    signal.signal(signal.SIGWINCH, _mo_sigwinch)
    try:
        while True:
            _mo_current_mode = 'select'
            profile = _mo_run_profile_selection(profiles)
            if profile is None:
                break

            _mo_show_scanning(profile)
            scan_results = mo_scan_for_videos(profile)
            if not scan_results:
                _mo_show_no_files_screen(profile['name'])
                fd, old = sys.stdin.fileno(), termios.tcgetattr(sys.stdin.fileno())
                tty.setcbreak(fd)
                try:
                    _mo_read_key()
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old)
                continue

            file_items = [_MO_FileItem(r) for r in scan_results]
            selected   = _mo_run_file_selection(file_items, profile['name'])
            if selected is None:
                continue

            try:
                success_cnt, fail_cnt, results = mo_run_conversion(profile, selected)
            finally:
                _mo_reset_terminal()
                _mo_current_mode = 'select'

            if fail_cnt == 0:
                play_sound(get_project_sound(MO_SCRIPT_NAME, 'successAudio', MO_SOUND_SUCCESS))
            else:
                play_sound(get_project_sound(MO_SCRIPT_NAME, 'failureAudio', MO_SOUND_FAILURE))

            _mo_show_summary(profile['name'], success_cnt, fail_cnt, results)
            fd, old = sys.stdin.fileno(), termios.tcgetattr(sys.stdin.fileno())
            tty.setcbreak(fd)
            try:
                key = _mo_read_key()
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)
            if key in ('q', 'Q', 'ESC'):
                break
    finally:
        signal.signal(signal.SIGWINCH, old_handler)
        _mo_reset_terminal()


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description='VLC Menu')
    parser.add_argument('--port', type=int, default=None,
                        help='VLC HTTP port to connect to (overrides config, e.g. 8081 for second instance)')
    args, _ = parser.parse_known_args()

    # Load paths configuration (also loads HTTP settings from config)
    load_paths_config()

    # Command-line port overrides config (allows second instance on different port)
    if args.port is not None:
        global HTTP_PORT
        HTTP_PORT = args.port

    clear_screen()

    # Check if vlcmenuconfig.json exists
    if not file_exists(CONFIG_PATH):
        header("VLC Menu", VERSION)
        print(color_text(f"Error: vlcmenuconfig.json not found at {CONFIG_PATH}", fg=RED, style=BOLD))
        print(color_text("\nPlease create a vlcmenuconfig.json file with your VLC profiles.", fg=YELLOW))
        return

    # Check if VLC is already running and prompt user
    vlc_action = check_vlc_and_prompt()
    if vlc_action == 'exit':
        return  # User chose to exit
    elif vlc_action == 'management':
        # Go directly to management mode
        management_mode()
        return

    config = load_config()
    interactive_menu(config)

if __name__ == "__main__":
    main()
