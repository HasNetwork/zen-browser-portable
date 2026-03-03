#!/usr/bin/env bash
# Zen Browser Portable Launcher (Linux / macOS)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

set -euo pipefail

# ── Resolve the portable directory (handles symlinks) ───────────────
SOURCE="${BASH_SOURCE[0]}"
while [ -L "$SOURCE" ]; do
    DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
    SOURCE="$(readlink "$SOURCE")"
    [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
PORTABLE_DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"

# ── Directory layout ───────────────────────────────────────────────
APP_DIR="$PORTABLE_DIR/App"
DATA_DIR="$PORTABLE_DIR/Data"
PROFILE_DIR="$DATA_DIR/profile"
TEMP_DIR="$DATA_DIR/temp"
CACHE_DIR="$DATA_DIR/cache"

# ── Create data directories ────────────────────────────────────────
mkdir -p "$PROFILE_DIR" "$TEMP_DIR" "$CACHE_DIR"

# ── Seed user.js on first run ──────────────────────────────────────
USER_JS="$PROFILE_DIR/user.js"
DEFAULT_JS="$PORTABLE_DIR/defaults/user.js"
if [ ! -f "$USER_JS" ] && [ -f "$DEFAULT_JS" ]; then
    cp "$DEFAULT_JS" "$USER_JS"
    echo "Zen Portable: created default user.js"
fi

# ── Environment overrides ──────────────────────────────────────────
export TMPDIR="$TEMP_DIR"
export TEMP="$TEMP_DIR"
export TMP="$TEMP_DIR"
export MOZ_CRASHREPORTER_DISABLE=1

# ── Check system dependencies (Linux only) ─────────────────────────
if [ "$(uname)" = "Linux" ]; then
    MISSING=""
    PACKAGES=""

    check_lib() {
        if ! ldconfig -p 2>/dev/null | grep -q "$1"; then
            MISSING="$MISSING  - $1 ($2)\n"
            PACKAGES="$PACKAGES $3"
        fi
    }

    check_lib "libasound.so.2"      "ALSA audio"        "libasound2"
    check_lib "libgtk-3.so.0"       "GTK 3"             "libgtk-3-0"
    check_lib "libdbus-1.so.3"      "D-Bus"             "libdbus-1-3"
    check_lib "libX11.so.6"         "X11"               "libx11-6"
    check_lib "libXt.so.6"          "Xt toolkit"        "libxt6"
    check_lib "libXtst.so.6"        "Xt testing"        "libxtst6"

    if [ -n "$MISSING" ]; then
        echo "Zen Browser Portable: missing system libraries:"
        echo ""
        printf "$MISSING"
        echo ""
        echo "Install them with:"
        echo "  sudo apt install libasound-dev libgtk-3-dev libdbus-1-dev libx11-dev libxt-dev libxtst-dev  # Debian/Ubuntu"
        echo "  sudo dnf install alsa-lib gtk3 dbus-libs libX11 libXt libXtst  # Fedora"
        echo "  sudo pacman -S alsa-lib gtk3 dbus libx11 libxt libxtst         # Arch"
        echo ""
        echo "Then try again."
        exit 1
    fi
fi

# ── Find zen executable ────────────────────────────────────────────
ZEN_EXE=""

if [ -f "$APP_DIR/zen" ]; then
    # Linux: binary directly in App/
    ZEN_EXE="$APP_DIR/zen"
elif [ -f "$APP_DIR/zen-bin" ]; then
    # Linux: some builds use zen-bin
    ZEN_EXE="$APP_DIR/zen-bin"
fi

# macOS: look for .app bundle
if [ -z "$ZEN_EXE" ]; then
    for app in "$APP_DIR"/*.app; do
        if [ -d "$app" ]; then
            candidate="$app/Contents/MacOS/zen"
            if [ -f "$candidate" ]; then
                ZEN_EXE="$candidate"
                break
            fi
        fi
    done
fi

if [ -z "$ZEN_EXE" ] || [ ! -f "$ZEN_EXE" ]; then
    echo "Error: Zen Browser executable not found!"
    echo ""
    echo "Expected one of:"
    echo "  $APP_DIR/zen          (Linux)"
    echo "  $APP_DIR/*.app/       (macOS)"
    echo ""
    echo "Make sure the 'App' folder contains the Zen Browser files."
    exit 1
fi

# ── Launch ──────────────────────────────────────────────────────────
# Ensure execute permission (may be lost on FAT32/exFAT or after extract)
chmod +x "$ZEN_EXE" 2>/dev/null || true
exec "$ZEN_EXE" --profile "$PROFILE_DIR" --no-remote "$@"
