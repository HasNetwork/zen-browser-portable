#!/usr/bin/env python3
"""
Build Zen Browser Portable in PortableApps.com Format (PAF).

This script:
  1. Sets up the PAF directory structure
  2. Extracts Zen Browser from the NSIS installer
  3. Copies PAF config files (appinfo.ini, launcher.ini, etc.)
  4. Generates icons from the Zen logo
  5. Runs the PAL Generator to compile ZenBrowserPortable.exe
  6. Runs the PA.c Installer to create the final .paf.exe

Usage:
    python build_paf.py \
        --installer zen.installer.exe \
        --paf-template build/portable/paf \
        --icon configs/branding/release/logo128.png \
        --pal-dir /path/to/PortableApps.comLauncher \
        --pai-dir /path/to/PortableApps.comInstaller \
        --output ZenBrowserPortable_1.0.0.paf.exe

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


UNWANTED_FILES = {
    "uninstall", "uninstall.exe", "Uninstall.exe",
    "maintenanceservice.exe", "maintenanceservice_installer.exe",
    "updater.exe", "updater.ini",
    "update-settings.ini", "precomplete",
}


def find_file(search_dir: str, filename: str) -> str | None:
    """Walk tree to find a file by name, return its parent directory."""
    for dirpath, _, filenames in os.walk(search_dir):
        if filename in filenames:
            return dirpath
    return None


def extract_nsis(installer: str, dest: str) -> None:
    """Extract a Windows NSIS installer using 7z."""
    print("Extracting NSIS installer with 7z ...")
    r = subprocess.run(["7z", "x", "-y", f"-o{dest}", installer],
                       capture_output=True, text=True)
    if r.returncode >= 2:
        print(f"7z failed (exit {r.returncode}):\n{r.stderr}", file=sys.stderr)
        sys.exit(1)


def generate_icons(source_png: str, appinfo_dir: str) -> None:
    """Generate required PAF icon sizes from a source PNG using magick."""
    sizes = {
        "appicon_16.png": 16,
        "appicon_32.png": 32,
        "appicon_75.png": 75,
        "appicon_128.png": 128,
        "appicon_256.png": 256,
    }
    for filename, size in sizes.items():
        out = os.path.join(appinfo_dir, filename)
        r = subprocess.run(
            ["magick", source_png, "-resize", f"{size}x{size}", out],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            print(f"Warning: Failed to generate {filename}: {r.stderr}")
        else:
            print(f"  Generated {filename} ({size}x{size})")

    # Generate ICO with multiple sizes
    ico_path = os.path.join(appinfo_dir, "appicon.ico")
    ico_sizes = [16, 32, 48, 256]
    args = ["magick", source_png]
    for s in ico_sizes:
        args += ["(", "-clone", "0", "-resize", f"{s}x{s}", ")"]
    args += ["-delete", "0", ico_path]
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"Warning: Failed to generate appicon.ico: {r.stderr}")
        # Fallback: just copy the PNG as-is (won't be a valid ICO but won't crash)
    else:
        print(f"  Generated appicon.ico")


def build_paf(args: argparse.Namespace) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        paf_root = os.path.join(tmp, "ZenBrowserPortable")
        app_dir = os.path.join(paf_root, "App")
        zen_dir = os.path.join(app_dir, "zen")
        appinfo_dir = os.path.join(app_dir, "AppInfo")
        data_dir = os.path.join(paf_root, "Data")
        staging = os.path.join(tmp, "_staging")

        # ── Create directory structure ──────────────────────────────
        for d in [zen_dir, appinfo_dir, data_dir, os.path.join(data_dir, "profile"),
                  os.path.join(data_dir, "temp"), staging]:
            os.makedirs(d, exist_ok=True)

        # ── Copy PAF template files ─────────────────────────────────
        template = args.paf_template
        for item in os.listdir(template):
            src = os.path.join(template, item)
            dst = os.path.join(paf_root, item)
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
        print("Copied PAF template files")

        # ── Extract browser from NSIS installer ─────────────────────
        extract_nsis(args.installer, staging)
        zen_root = find_file(staging, "zen.exe")
        if not zen_root:
            print("ERROR: zen.exe not found after extraction!", file=sys.stderr)
            sys.exit(1)

        for item in os.listdir(zen_root):
            s = os.path.join(zen_root, item)
            d = os.path.join(zen_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)
        print(f"Extracted Zen Browser to App/zen/")

        # ── Remove installer-only files ─────────────────────────────
        for unwanted in UNWANTED_FILES:
            target = os.path.join(zen_dir, unwanted)
            if os.path.exists(target):
                if os.path.isdir(target):
                    shutil.rmtree(target)
                else:
                    os.remove(target)
                print(f"  Removed: {unwanted}")

        # ── Generate icons ──────────────────────────────────────────
        if args.icon and os.path.isfile(args.icon):
            print("Generating PAF icons ...")
            generate_icons(args.icon, appinfo_dir)
        else:
            print("Warning: No icon provided, PAF icons not generated")

        # ── Run PAL Generator ───────────────────────────────────────
        if args.pal_dir:
            pal_gen = os.path.join(args.pal_dir, "PortableApps.comLauncherGenerator.exe")
            if os.path.isfile(pal_gen):
                print("Running PortableApps.com Launcher Generator ...")
                r = subprocess.run([pal_gen, paf_root],
                                   capture_output=True, text=True, timeout=120)
                if r.returncode != 0:
                    print(f"PAL Generator output:\n{r.stdout}\n{r.stderr}")
                    print("Warning: PAL Generator failed, falling back to template launcher")
                else:
                    print("PAL Generator completed successfully")
            else:
                print(f"Warning: PAL Generator not found at {pal_gen}")

        # ── Run PA.c Installer ──────────────────────────────────────
        if args.pai_dir:
            pai_gen = os.path.join(args.pai_dir, "PortableApps.comInstaller.exe")
            if os.path.isfile(pai_gen):
                print("Running PortableApps.com Installer ...")
                r = subprocess.run([pai_gen, paf_root],
                                   capture_output=True, text=True, timeout=300)
                if r.returncode != 0:
                    print(f"PA.c Installer output:\n{r.stdout}\n{r.stderr}")
                    print("Warning: PA.c Installer failed")
                else:
                    print("PA.c Installer completed successfully")

                # Find the generated .paf.exe
                for f in os.listdir(tmp):
                    if f.endswith(".paf.exe"):
                        src_paf = os.path.join(tmp, f)
                        shutil.move(src_paf, args.output)
                        size_mb = os.path.getsize(args.output) / 1048576
                        print(f"Done! {args.output} ({size_mb:.1f} MB)")
                        return
            else:
                print(f"Warning: PA.c Installer not found at {pai_gen}")

        # ── Fallback: create ZIP if installer tools unavailable ─────
        print("Falling back to ZIP output ...")
        shutil.make_archive(args.output.replace(".paf.exe", "").replace(".zip", ""),
                            "zip", tmp, "ZenBrowserPortable")
        output_zip = args.output.replace(".paf.exe", ".zip")
        if not os.path.isfile(output_zip):
            output_zip = args.output.replace(".paf.exe", "") + ".zip"
        if os.path.isfile(output_zip):
            size_mb = os.path.getsize(output_zip) / 1048576
            print(f"Done! {output_zip} ({size_mb:.1f} MB)")
        else:
            print("Warning: Could not create output archive")


def main() -> None:
    p = argparse.ArgumentParser(description="Build Zen Browser Portable (PAF)")
    p.add_argument("--installer", required=True, help="Windows NSIS installer (.exe)")
    p.add_argument("--paf-template", required=True, help="PAF template directory")
    p.add_argument("--icon", help="Source PNG for icon generation")
    p.add_argument("--pal-dir", help="Path to PortableApps.com Launcher")
    p.add_argument("--pai-dir", help="Path to PortableApps.com Installer")
    p.add_argument("--output", required=True, help="Output .paf.exe path")
    args = p.parse_args()

    if not os.path.isfile(args.installer):
        print(f"ERROR: Installer not found: {args.installer}", file=sys.stderr)
        sys.exit(1)

    build_paf(args)


if __name__ == "__main__":
    main()
