<!--
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at http://mozilla.org/MPL/2.0/.
   -->

<img src="./docs/assets/zen-dark.svg" width="100px" align="left">

### `Zen Browser Portable`

[![Latest Portable Release](https://img.shields.io/github/v/release/nkhokhla/zen-browser-portable?label=portable&color=blue)](https://github.com/nkhokhla/zen-browser-portable/releases/latest)
[![Portable Build](https://github.com/nkhokhla/zen-browser-portable/actions/workflows/portable-build.yml/badge.svg)](https://github.com/nkhokhla/zen-browser-portable/actions/workflows/portable-build.yml)
[![Upstream](https://img.shields.io/badge/upstream-zen--browser%2Fdesktop-purple)](https://github.com/zen-browser/desktop)

An **unofficial portable build** of [Zen Browser](https://zen-browser.app) for Windows, Linux, and macOS. Run it from a USB drive, external SSD, or any folder — no installation, no admin rights, no data left behind.

<br>

---

## ⬇️ Download

> Download the latest popup-free standalone build from [**this fork's Releases**](https://github.com/nkhokhla/zen-browser-portable/releases/latest).

| File                                        | Platform                         | Format           |
| ------------------------------------------- | -------------------------------- | ---------------- |
| `ZenBrowserPortable-windows-x86_64.zip`     | 🪟 Windows x64 (Intel/AMD)       | Standalone ZIP   |
| `ZenBrowserPortable-windows-arm64.zip`      | 🪟 Windows ARM64 (Snapdragon)    | Standalone ZIP   |
| `ZenBrowserPortable-linux-x86_64.tar.gz`    | 🐧 Linux x64                     | Standalone       |
| `ZenBrowserPortable-linux-aarch64.tar.gz`   | 🐧 Linux ARM64                   | Standalone       |
| `ZenBrowserPortable-macos-universal.tar.gz` | 🍎 macOS (Intel + Apple Silicon) | Standalone       |
| `ZenBrowserPortable_*.paf.exe`              | 🪟 Windows x64                   | PortableApps.com, signed builds only |

## 🚀 Getting Started

**Windows (Standalone):**

1. Download the `.zip` → Extract → Double-click **`zen-portable.cmd`**

**Windows (PortableApps.com):**

1. Download the `.paf.exe` only when a signed PAF build is available → Double-click → Choose install location → Run **`ZenBrowserPortable.exe`**
2. Or install via the PortableApps.com Platform for menu integration

**Linux / macOS:**

1. Download the `.tar.gz` → Extract → Run **`./zen-portable`**

```bash
# Linux / macOS
tar xzf ZenBrowserPortable-linux-x86_64.tar.gz
cd ZenBrowserPortable
chmod +x zen-portable    # should already be executable
./zen-portable
```

All your data (bookmarks, history, passwords, extensions) is stored inside the `Data/` folder. Move the entire `ZenBrowserPortable/` folder anywhere and everything comes with it.

## 📁 Folder Structure

```
ZenBrowserPortable/
├── zen-portable.cmd       ← Launch this on Windows
├── zen-portable           ← Launch this on Linux / macOS
├── portable.ini           ← Portable mode marker
├── README.txt             ← Quick reference
├── defaults/              ← Default preferences (Linux/macOS)
│   └── user.js
├── App/                   ← Browser engine (do not modify)
│   ├── zen(.exe)          ← Windows / Linux
│   └── Zen Browser.app/   ← macOS
└── Data/                  ← Your personal data (portable)
    ├── profile/           ← Bookmarks, history, extensions, settings
    ├── temp/              ← Temporary files (redirected here)
    └── cache/             ← Cache files
```

## 💡 Key Features

| Feature                         | Details                                                                         |
| ------------------------------- | ------------------------------------------------------------------------------- |
| **True portability**            | Profile, temp, and cache all live inside the portable folder                    |
| **Cross-platform**              | Windows, Linux, and macOS                                                       |
| **USB / pendrive ready**        | Drive letter and mount point changes handled automatically                      |
| **Zero footprint**              | No files left on the host machine                                               |
| **No admin required**           | Runs from any user-writable folder                                              |
| **Coexists with installed Zen** | Uses `--no-remote` — won't interfere with an existing installation              |
| **Auto-updated builds**         | New portable builds are published automatically when Zen releases a new version |
| **Popup-free Windows ZIP**      | The standalone ZIP avoids fork-built `.exe` launchers that trigger SmartScreen  |
| **PortableApps.com Format**     | Available only for signed builds that integrate with the PortableApps.com Platform |

## 🔄 Updating

1. Close Zen Browser completely
2. Download the latest archive from [Releases](https://github.com/HasNetwork/zen-browser-portable/releases/latest)
3. Delete the contents of the `App/` folder
4. Extract the new archive's `App/` folder into your existing one
5. Your `Data/` folder (bookmarks, history, etc.) is preserved

> **Tip:** Auto-updates are disabled in portable mode. Check this fork's [Releases](https://github.com/nkhokhla/zen-browser-portable/releases) page for new versions.

## ⚙️ Portable Mode Defaults

The portable launcher applies these preferences via `Data/profile/user.js` (editable):

- 🚫 **Disk cache disabled** — uses RAM cache (256 MB) for USB performance
- 🚫 **Auto-updates disabled** — update manually by replacing `App/`
- 🚫 **Default browser check disabled** — portable apps shouldn't register as default
- 🚫 **Telemetry & crash reporter disabled** — no data sent
- ✅ **`zen.portable.mode = true`** — signals portable mode to Zen

You can change any of these in `about:config` or by editing `Data/profile/user.js`.

## 🏗️ How It Works

**Windows (Standalone):** The launcher (`zen-portable.cmd`) resolves its own directory, redirects TEMP/TMP, seeds the portable profile, and launches the upstream `App\zen.exe --profile Data\profile --no-remote`. The standalone ZIP intentionally does not include a fork-built `.exe` launcher, which avoids Microsoft Defender SmartScreen's unrecognized-app warning for the portable wrapper.

**Windows (PAF):** The launcher (`ZenBrowserPortable.exe`) is compiled by the [PortableApps.com Launcher](https://portableapps.com/apps/development/portableapps.com_launcher). It does the same job — redirects profile, temp, and APPDATA — but integrates with the PortableApps.com Platform menu and follows the [PAF spec](https://portableapps.com/development/portableapps.com_format).

**Linux / macOS:** The launcher (`zen-portable`) is a bash script that does the same — finds the `zen` binary or `.app` bundle in `App/`, sets environment variables, and launches with `--profile`.

No modifications are made to the Zen Browser engine — it's the exact same build from the [official releases](https://github.com/zen-browser/desktop/releases).

## 🔨 Building From Source

**Requirements:** Python 3 and 7-Zip for standalone packages. PAF installer builds also require NSIS, ImageMagick, and a valid code-signing setup before publishing.

```bash
# Package (Windows)
python build/portable/package.py \
  --installer zen.installer.exe \
  --windows-launcher build/portable/launcher/zen-portable.cmd \
  --user-js build/portable/launcher/defaults/user.js \
  --assets-dir build/portable/assets \
  --output ZenBrowserPortable-windows-x86_64.zip

# Package (Linux)
python build/portable/package.py \
  --tarball zen.linux-x86_64.tar.xz \
  --shell-launcher build/portable/launcher/zen-portable.sh \
  --user-js build/portable/launcher/defaults/user.js \
  --assets-dir build/portable/assets \
  --output ZenBrowserPortable-linux-x86_64.tar.gz

# Package (macOS — requires 7z for DMG extraction)
python build/portable/package.py \
  --dmg zen.macos-universal.dmg \
  --shell-launcher build/portable/launcher/zen-portable.sh \
  --user-js build/portable/launcher/defaults/user.js \
  --assets-dir build/portable/assets \
  --output ZenBrowserPortable-macos-universal.tar.gz

# PortableApps.com Format (Windows — requires NSIS, 7z, ImageMagick)
python build/portable/build_paf.py \
  --installer zen.installer.exe \
  --paf-template build/portable/paf \
  --icon configs/branding/release/logo128.png \
  --pal-dir /path/to/PortableApps.comLauncher \
  --pai-dir /path/to/PortableApps.comInstaller \
  --output ZenBrowserPortable_1.0.0.paf.exe
```

Or just push to GitHub — the [Portable Build workflow](.github/workflows/portable-build.yml) handles everything automatically.

## 📋 Upstream

This project is a fork of [zen-browser/desktop](https://github.com/zen-browser/desktop). The portable build system lives in `build/portable/` and does **not** modify any upstream source code.

- **Zen Browser**: [zen-browser.app](https://zen-browser.app)
- **Upstream repo**: [zen-browser/desktop](https://github.com/zen-browser/desktop)

## 📄 License

[Mozilla Public License 2.0](./LICENSE)
