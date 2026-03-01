#!/usr/bin/env python3
"""
Package Zen Browser Portable for Windows, Linux, and macOS.

Usage:
    # Windows (NSIS installer → ZIP)
    python package.py --installer zen.installer.exe --launcher zen-portable.exe \
        --output ZenBrowserPortable-x86_64.zip

    # Linux (tar.xz → tar.gz)
    python package.py --tarball zen.linux-x86_64.tar.xz --shell-launcher zen-portable.sh \
        --user-js defaults/user.js --output ZenBrowserPortable-linux-x86_64.tar.gz

    # macOS (DMG → tar.gz, requires 7z)
    python package.py --dmg zen.macos-universal.dmg --shell-launcher zen-portable.sh \
        --user-js defaults/user.js --output ZenBrowserPortable-macos-universal.tar.gz

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

import argparse
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile


# ── Extraction helpers ──────────────────────────────────────────────

def extract_nsis(installer: str, dest: str) -> None:
    """Extract a Windows NSIS installer using 7z."""
    print("Extracting NSIS installer with 7z ...")
    r = subprocess.run(["7z", "x", "-y", f"-o{dest}", installer],
                       capture_output=True, text=True)
    if r.returncode >= 2:
        print(f"7z failed (exit {r.returncode}):\n{r.stderr}", file=sys.stderr)
        sys.exit(1)
    if r.returncode == 1:
        print("  7z warning (non-fatal, continuing)")


def extract_tarball(tarball: str, dest: str) -> None:
    """Extract a .tar.xz / .tar.gz / .tar.bz2 archive."""
    print(f"Extracting {os.path.basename(tarball)} ...")
    with tarfile.open(tarball, "r:*") as tf:
        tf.extractall(dest)


def extract_dmg(dmg: str, dest: str) -> None:
    """Extract a macOS DMG using 7z.

    DMGs typically contain a symlink to /Applications which 7z flags as
    'dangerous' (exit code 1 = warning).  This is expected and harmless —
    we only fail on exit code 2+ (actual errors).
    """
    print("Extracting DMG with 7z ...")
    r = subprocess.run(["7z", "x", "-y", f"-o{dest}", dmg],
                       capture_output=True, text=True)
    if r.returncode >= 2:
        print(f"7z failed (exit {r.returncode}):\n{r.stderr}", file=sys.stderr)
        sys.exit(1)
    if r.returncode == 1:
        print("  7z warning (harmless): dangerous symlink to /Applications ignored")


# ── Finders ─────────────────────────────────────────────────────────

def find_file(search_dir: str, filename: str) -> str | None:
    """Walk tree to find a file by name, return its parent directory."""
    for dirpath, _, filenames in os.walk(search_dir):
        if filename in filenames:
            return dirpath
    return None


def find_app_bundle(search_dir: str) -> str | None:
    """Find a macOS .app bundle directory."""
    for dirpath, dirnames, _ in os.walk(search_dir):
        for d in dirnames:
            if d.endswith(".app"):
                return os.path.join(dirpath, d)
    return None


# ── Packaging ───────────────────────────────────────────────────────

def copy_tree(src: str, dst: str) -> None:
    """Copy directory contents into dst, preserving symlinks."""
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.islink(s):
            link_target = os.readlink(s)
            os.symlink(link_target, d)
        elif os.path.isdir(s):
            shutil.copytree(s, d, symlinks=True)
        else:
            shutil.copy2(s, d)


def create_tar_gz(source_dir: str, output_path: str, root_name: str) -> None:
    """Create a .tar.gz archive preserving permissions and symlinks."""
    print(f"Creating {output_path} ...")
    with tarfile.open(output_path, "w:gz") as tf:
        for dirpath, dirnames, filenames in os.walk(source_dir):
            for name in dirnames + filenames:
                full = os.path.join(dirpath, name)
                arc = os.path.join(root_name, os.path.relpath(full, source_dir))
                tf.add(full, arcname=arc, recursive=False)


def create_zip(source_dir: str, output_path: str, root_name: str) -> None:
    """Create a .zip archive."""
    print(f"Creating {output_path} ...")
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for dirpath, _, filenames in os.walk(source_dir):
            for fn in filenames:
                full = os.path.join(dirpath, fn)
                arc = os.path.join(root_name, os.path.relpath(full, source_dir))
                zf.write(full, arc)


UNWANTED_FILES = {
    "uninstall", "uninstall.exe", "Uninstall.exe",
    "maintenanceservice.exe", "maintenanceservice_installer.exe",
    "updater.exe", "updater.ini",
    "update-settings.ini", "precomplete",
}


def package_portable(args: argparse.Namespace) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = os.path.join(tmp, "ZenBrowserPortable")
        app_dir = os.path.join(root, "App")
        staging = os.path.join(tmp, "_staging")

        os.makedirs(app_dir)
        os.makedirs(os.path.join(root, "Data", "profile"))
        os.makedirs(os.path.join(root, "Data", "temp"))
        os.makedirs(os.path.join(root, "Data", "cache"))
        os.makedirs(staging)

        # ── Extract source ──────────────────────────────────────────
        if args.installer:
            extract_nsis(args.installer, staging)
            zen_root = find_file(staging, "zen.exe")
            if not zen_root:
                print("ERROR: zen.exe not found after extraction!", file=sys.stderr)
                sys.exit(1)
            copy_tree(zen_root, app_dir)
            print(f"Found zen.exe — {os.path.getsize(os.path.join(app_dir, 'zen.exe')) / 1048576:.1f} MB")

        elif args.tarball:
            extract_tarball(args.tarball, staging)
            zen_root = find_file(staging, "zen")
            if not zen_root:
                print("ERROR: 'zen' binary not found after extraction!", file=sys.stderr)
                sys.exit(1)
            copy_tree(zen_root, app_dir)
            # Ensure execute permission
            zen_bin = os.path.join(app_dir, "zen")
            if os.path.isfile(zen_bin):
                os.chmod(zen_bin, 0o755)
                print(f"Found zen — {os.path.getsize(zen_bin) / 1048576:.1f} MB")

        elif args.dmg:
            extract_dmg(args.dmg, staging)
            app_bundle = find_app_bundle(staging)
            if not app_bundle:
                print("ERROR: .app bundle not found after DMG extraction!", file=sys.stderr)
                sys.exit(1)
            bundle_name = os.path.basename(app_bundle)
            shutil.copytree(app_bundle, os.path.join(app_dir, bundle_name), symlinks=True)
            # Ensure execute permission on the main binary
            zen_bin = os.path.join(app_dir, bundle_name, "Contents", "MacOS", "zen")
            if os.path.isfile(zen_bin):
                os.chmod(zen_bin, 0o755)
            print(f"Found {bundle_name}")

        # ── Remove installer-only files ─────────────────────────────
        for unwanted in UNWANTED_FILES:
            target = os.path.join(app_dir, unwanted)
            if os.path.exists(target):
                if os.path.isdir(target):
                    shutil.rmtree(target)
                else:
                    os.remove(target)
                print(f"  Removed: {unwanted}")

        # ── Copy launcher ───────────────────────────────────────────
        if args.launcher:
            # Windows: compiled Go exe
            shutil.copy2(args.launcher, os.path.join(root, "zen-portable.exe"))

        if args.shell_launcher:
            # Linux / macOS: shell script
            dest = os.path.join(root, "zen-portable")
            shutil.copy2(args.shell_launcher, dest)
            os.chmod(dest, 0o755)

        if args.user_js:
            # Ship defaults/user.js for the shell launcher to copy
            defaults_dir = os.path.join(root, "defaults")
            os.makedirs(defaults_dir, exist_ok=True)
            shutil.copy2(args.user_js, os.path.join(defaults_dir, "user.js"))

        # ── Copy static assets ──────────────────────────────────────
        for name in ("portable.ini", "README.txt"):
            src = os.path.join(args.assets_dir, name)
            if os.path.isfile(src):
                shutil.copy2(src, os.path.join(root, name))

        # ── Create output archive ───────────────────────────────────
        output = args.output
        if output.endswith(".tar.gz") or output.endswith(".tgz"):
            create_tar_gz(root, output, "ZenBrowserPortable")
        else:
            create_zip(root, output, "ZenBrowserPortable")

        size_mb = os.path.getsize(output) / 1048576
        print(f"Done! {output} ({size_mb:.1f} MB)")


def main() -> None:
    p = argparse.ArgumentParser(description="Package Zen Browser Portable")

    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--installer", help="Windows NSIS installer (.exe)")
    src.add_argument("--tarball", help="Linux tar archive (.tar.xz)")
    src.add_argument("--dmg", help="macOS disk image (.dmg)")

    p.add_argument("--launcher", help="Compiled Windows launcher (.exe)")
    p.add_argument("--shell-launcher", help="Shell script launcher (Linux/macOS)")
    p.add_argument("--user-js", help="Default user.js to include in defaults/")
    p.add_argument("--output", required=True, help="Output archive path")
    p.add_argument("--assets-dir", default="assets", help="Static assets directory")
    args = p.parse_args()

    # Validate inputs
    source = args.installer or args.tarball or args.dmg
    if not os.path.isfile(source):
        print(f"ERROR: source not found: {source}", file=sys.stderr)
        sys.exit(1)

    package_portable(args)


if __name__ == "__main__":
    main()
