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
exec "$ZEN_EXE" --profile "$PROFILE_DIR" --no-remote "$@"
