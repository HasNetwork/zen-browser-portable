#!/usr/bin/env python3
"""
Package Zen Browser Portable.

Accepts either a release ZIP or an NSIS installer as input.

Usage (ZIP):
    python package.py --release-zip zen.win-x86_64.zip  ...

Usage (NSIS installer — requires 7z on PATH):
    python package.py --installer zen.installer.exe  ...

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile


def extract_nsis(installer: str, dest: str) -> None:
    """Extract an NSIS installer using 7z."""
    print(f"Extracting NSIS installer with 7z ...")
    result = subprocess.run(
        ["7z", "x", "-y", f"-o{dest}", installer],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"7z stderr:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)

    # NSIS extracts into a structure that may include $INSTDIR or
    # sub-directories. Find zen.exe and determine the actual root.
    for dirpath, _, filenames in os.walk(dest):
        if "zen.exe" in filenames:
            return dirpath
    return dest


def extract_zip(zippath: str, dest: str) -> None:
    """Extract a release ZIP."""
    print(f"Extracting ZIP ...")
    with zipfile.ZipFile(zippath, "r") as zf:
        zf.extractall(dest)


def flatten_single_child(directory: str) -> None:
    """If a dir has exactly one child dir, move its contents up."""
    children = os.listdir(directory)
    if len(children) == 1:
        child = os.path.join(directory, children[0])
        if os.path.isdir(child):
            for item in os.listdir(child):
                shutil.move(os.path.join(child, item), directory)
            os.rmdir(child)


def find_zen_root(search_dir: str) -> str:
    """Walk the extracted tree to find the directory containing zen.exe."""
    for dirpath, _, filenames in os.walk(search_dir):
        if "zen.exe" in filenames:
            return dirpath
    return search_dir


def package_portable(
    source_path: str,
    is_installer: bool,
    launcher_exe: str,
    output_zip: str,
    assets_dir: str,
) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = os.path.join(tmp, "ZenBrowserPortable")
        app_dir = os.path.join(root, "App")

        os.makedirs(app_dir)
        os.makedirs(os.path.join(root, "Data", "profile"))
        os.makedirs(os.path.join(root, "Data", "temp"))
        os.makedirs(os.path.join(root, "Data", "cache"))

        # ── Extract browser files into App/ ─────────────────────────
        staging = os.path.join(tmp, "_staging")
        os.makedirs(staging)

        if is_installer:
            extract_nsis(source_path, staging)
        else:
            extract_zip(source_path, staging)

        # Find the actual zen.exe location and move files to App/
        zen_root = find_zen_root(staging)
        for item in os.listdir(zen_root):
            src = os.path.join(zen_root, item)
            dst = os.path.join(app_dir, item)
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)

        # Verify
        zen_exe = os.path.join(app_dir, "zen.exe")
        if not os.path.isfile(zen_exe):
            print(f"ERROR: zen.exe not found after extraction!", file=sys.stderr)
            print("App/ contents:", os.listdir(app_dir), file=sys.stderr)
            sys.exit(1)
        print(f"Found zen.exe — {os.path.getsize(zen_exe) / 1024 / 1024:.1f} MB")

        # Remove installer/uninstaller artifacts that aren't needed
        for unwanted in (
            "uninstall", "uninstall.exe", "Uninstall.exe",
            "maintenanceservice.exe", "maintenanceservice_installer.exe",
            "updater.exe", "updater.ini",
            "update-settings.ini", "precomplete",
        ):
            target = os.path.join(app_dir, unwanted)
            if os.path.exists(target):
                if os.path.isdir(target):
                    shutil.rmtree(target)
                else:
                    os.remove(target)
                print(f"  Removed: {unwanted}")

        # ── Copy launcher + assets ──────────────────────────────────
        shutil.copy2(launcher_exe, os.path.join(root, "zen-portable.exe"))

        for name in ("portable.ini", "README.txt"):
            src = os.path.join(assets_dir, name)
            if os.path.isfile(src):
                shutil.copy2(src, os.path.join(root, name))

        # ── Build output ZIP ────────────────────────────────────────
        print(f"Creating {output_zip} ...")
        with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            for dirpath, dirnames, filenames in os.walk(root):
                for fn in filenames:
                    full = os.path.join(dirpath, fn)
                    arc = os.path.relpath(full, tmp)
                    zf.write(full, arc)

        size_mb = os.path.getsize(output_zip) / (1024 * 1024)
        print(f"Done! {output_zip} ({size_mb:.1f} MB)")


def main() -> None:
    p = argparse.ArgumentParser(description="Package Zen Browser Portable")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--release-zip", help="Zen release ZIP file")
    src.add_argument("--installer", help="Zen NSIS installer (.exe)")
    p.add_argument("--launcher", required=True, help="Compiled zen-portable.exe")
    p.add_argument("--output", required=True, help="Output portable ZIP path")
    p.add_argument("--assets-dir", default="assets", help="Static assets dir")
    args = p.parse_args()

    source = args.release_zip or args.installer
    if not os.path.isfile(source):
        print(f"ERROR: file not found: {source}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(args.launcher):
        print(f"ERROR: launcher not found: {args.launcher}", file=sys.stderr)
        sys.exit(1)

    package_portable(
        source_path=source,
        is_installer=(args.installer is not None),
        launcher_exe=args.launcher,
        output_zip=args.output,
        assets_dir=args.assets_dir,
    )


if __name__ == "__main__":
    main()
