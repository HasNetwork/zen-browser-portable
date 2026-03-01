<!--
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at http://mozilla.org/MPL/2.0/.
   -->

<img src="./docs/assets/zen-dark.svg" width="100px" align="left">

### `Zen Browser Portable`

[![Latest Portable Release](https://img.shields.io/github/v/release/HasNetwork/zen-browser-portable?label=portable&color=blue)](https://github.com/HasNetwork/zen-browser-portable/releases/latest)
[![Portable Build](https://github.com/HasNetwork/zen-browser-portable/actions/workflows/portable-build.yml/badge.svg)](https://github.com/HasNetwork/zen-browser-portable/actions/workflows/portable-build.yml)
[![Upstream](https://img.shields.io/badge/upstream-zen--browser%2Fdesktop-purple)](https://github.com/zen-browser/desktop)

An **unofficial portable build** of [Zen Browser](https://zen-browser.app) for Windows. Run it from a USB drive, external SSD, or any folder — no installation, no admin rights, no data left behind.

<br>

---

## ⬇️ Download

> Download the latest portable build from [**Releases**](https://github.com/HasNetwork/zen-browser-portable/releases/latest).

| File | Platform |
|---|---|
| `ZenBrowserPortable-x86_64.zip` | Windows x64 (Intel/AMD) |
| `ZenBrowserPortable-arm64.zip` | Windows ARM64 (Snapdragon) |

## 🚀 Getting Started

1. **Download** the ZIP for your platform from [Releases](https://github.com/HasNetwork/zen-browser-portable/releases/latest)
2. **Extract** the ZIP to any folder (local drive, USB, external SSD, etc.)
3. **Double-click** `zen-portable.exe` — that's it!

All your data (bookmarks, history, passwords, extensions) is stored inside the `Data/` folder. Move the entire `ZenBrowserPortable/` folder anywhere and everything comes with it.

## 📁 Folder Structure

```
ZenBrowserPortable/
├── zen-portable.exe       ← Launch this!
├── portable.ini           ← Portable mode marker
├── README.txt             ← Quick reference
├── App/                   ← Zen Browser engine (do not modify)
│   ├── zen.exe
│   ├── xul.dll
│   └── ...
└── Data/                  ← Your personal data (portable)
    ├── profile/           ← Bookmarks, history, extensions, settings
    ├── temp/              ← Temporary files (redirected here)
    └── cache/             ← Cache files
```

## 💡 Key Features

| Feature | Details |
|---|---|
| **True portability** | Profile, temp, and cache all live inside the portable folder |
| **USB / pendrive ready** | Drive letter changes handled automatically |
| **Zero footprint** | No files left on the host PC (temp redirected locally) |
| **No admin required** | Runs from any user-writable folder |
| **Coexists with installed Zen** | Uses `--no-remote` — won't interfere with an existing installation |
| **Auto-updated builds** | New portable builds are published automatically when Zen releases a new version |

## 🔄 Updating

1. Close Zen Browser completely
2. Download the latest ZIP from [Releases](https://github.com/HasNetwork/zen-browser-portable/releases/latest)
3. Delete the contents of the `App/` folder
4. Extract the new ZIP's `App/` folder into your existing one
5. Your `Data/` folder (bookmarks, history, etc.) is preserved

> [!TIP]
> Auto-updates are disabled in portable mode. Check this repo's [Releases](https://github.com/HasNetwork/zen-browser-portable/releases) page for new versions.

## ⚙️ Portable Mode Defaults

The portable launcher applies these preferences via `Data/profile/user.js` (editable):

- 🚫 **Disk cache disabled** — uses RAM cache (256 MB) for USB performance
- 🚫 **Auto-updates disabled** — update manually by replacing `App/`
- 🚫 **Default browser check disabled** — portable apps shouldn't register as default
- 🚫 **Telemetry & crash reporter disabled** — no data sent
- ✅ **`zen.portable.mode = true`** — signals portable mode to Zen

You can change any of these in `about:config` or by editing `Data/profile/user.js`.

## 🏗️ How It Works

The portable launcher (`zen-portable.exe`) is a small Go program (~2 MB) that:

1. Resolves its own directory at runtime (handles drive letter changes)
2. Creates `Data/profile/`, `Data/temp/`, and `Data/cache/` if missing
3. Seeds a `user.js` with portable-mode preferences on first run
4. Redirects `TEMP`/`TMP` environment variables into `Data/temp/`
5. Launches `App/zen.exe --profile Data/profile --no-remote`

No modifications are made to the Zen Browser engine itself — it's the exact same build from the [official releases](https://github.com/zen-browser/desktop/releases).

## 🔨 Building From Source

**Requirements:** Go, Python 3, 7-Zip

```bash
# 1. Compile the portable launcher
cd build/portable/launcher
go build -ldflags="-s -w -H=windowsgui" -o zen-portable.exe .

# 2. Download the latest Zen installer from GitHub releases
#    (zen.installer.exe or zen.installer-arm64.exe)

# 3. Package everything
python build/portable/package.py \
  --installer zen.installer.exe \
  --launcher  build/portable/launcher/zen-portable.exe \
  --assets-dir build/portable/assets \
  --output ZenBrowserPortable-x86_64.zip
```

Or just push to GitHub and the [Portable Build workflow](.github/workflows/portable-build.yml) will handle everything automatically.

## 📋 Upstream

This project is a fork of [zen-browser/desktop](https://github.com/zen-browser/desktop). The portable build system lives in `build/portable/` and does **not** modify any upstream source code.

- **Zen Browser**: [zen-browser.app](https://zen-browser.app)
- **Upstream repo**: [zen-browser/desktop](https://github.com/zen-browser/desktop)
- **Firefox version**: `148.0`

## 📄 License

[Mozilla Public License 2.0](./LICENSE)
