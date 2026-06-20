#!/usr/bin/env python3
"""
Build Zen Browser Portable in PortableApps.com Format (PAF).

This script:
  1. Sets up the PAF directory structure
  2. Extracts Zen Browser from the NSIS installer
  3. Copies PAF config files (appinfo.ini, launcher.ini, icons, etc.)
  4. Generates icons from the Zen logo using ImageMagick
  5. Compiles ZenBrowserPortable.exe from launcher.nsi using makensis
  6. Compiles the final .paf.exe from installer.nsi using makensis

Usage:
    python build_paf.py \
        --installer zen.installer.exe \
        --paf-template build/portable/paf \
        --icon logo128.png \
        --version 1.19b \
        --output ZenBrowserPortable_1.19b.paf.exe
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


def run(cmd: list[str], label: str) -> None:
    """Run a command, print output, and exit on failure."""
    print(f"  > {' '.join(cmd)}")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.stdout.strip():
        print(r.stdout.strip())
    if r.returncode != 0:
        # For 7z, exit code 1 = warnings (OK to continue)
        if cmd[0] in ("7z", "7z.exe") and r.returncode == 1:
            print(f"  {label}: 7z warning (exit 1), continuing...")
            return
        print(f"ERROR in {label} (exit {r.returncode}):\n{r.stderr}", file=sys.stderr)
        sys.exit(1)


def generate_icons(source_png: str, appinfo_dir: str) -> None:
    """Generate required PAF icon sizes from a source PNG using ImageMagick."""
    sizes = {
        "appicon_16.png": 16,
        "appicon_32.png": 32,
        "appicon_75.png": 75,
        "appicon_128.png": 128,
        "appicon_256.png": 256,
    }

    for filename, size in sizes.items():
        out = os.path.join(appinfo_dir, filename)
        run(["magick", source_png, "-resize", f"{size}x{size}", out],
            f"generate {filename}")
        print(f"  OK: {filename} ({size}x{size})")

    # Generate ICO with multiple sizes
    ico_path = os.path.join(appinfo_dir, "appicon.ico")
    run(["magick", source_png,
         "-define", "icon:auto-resize=256,48,32,16",
         ico_path],
        "generate appicon.ico")
    print(f"  OK: appicon.ico (multi-size)")


def build_paf(args: argparse.Namespace) -> None:
    # Use a local build dir instead of system temp (avoids Windows path issues)
    tmp = os.path.abspath(args.build_dir)
    if args.installer_only:
        _compile_paf_installer(args, tmp)
        return

    if os.path.exists(tmp):
        shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp, exist_ok=True)

    try:
        _build_paf_inner(args, tmp)
    finally:
        # Best-effort cleanup
        if not args.keep_build_dir:
            shutil.rmtree(tmp, ignore_errors=True)


def _build_paf_inner(args: argparse.Namespace, tmp: str) -> None:
    paf_root = os.path.join(tmp, "ZenBrowserPortable")
    app_dir = os.path.join(paf_root, "App")
    zen_dir = os.path.join(app_dir, "zen")
    appinfo_dir = os.path.join(app_dir, "AppInfo")
    staging = os.path.join(tmp, "_staging")

    # -- 1. Copy PAF template files --------------------------------
    print("\n[1/6] Copying PAF template ...")
    template = args.paf_template
    shutil.copytree(template, paf_root, dirs_exist_ok=True)

    # -- 2. Extract browser from NSIS installer --------------------
    print("\n[2/6] Extracting Zen Browser ...")
    os.makedirs(staging, exist_ok=True)
    run(["7z", "x", "-y", f"-o{staging}", args.installer], "NSIS extraction")

    zen_root = find_file(staging, "zen.exe")
    if not zen_root:
        print("ERROR: zen.exe not found after extraction!", file=sys.stderr)
        sys.exit(1)

    os.makedirs(zen_dir, exist_ok=True)
    for item in os.listdir(zen_root):
        s = os.path.join(zen_root, item)
        d = os.path.join(zen_dir, item)
        if os.path.isdir(s):
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)

    # Remove installer-only files
    for unwanted in UNWANTED_FILES:
        target = os.path.join(zen_dir, unwanted)
        if os.path.exists(target):
            if os.path.isdir(target):
                shutil.rmtree(target)
            else:
                os.remove(target)

    print(f"  OK: Extracted to App/zen/ ({len(os.listdir(zen_dir))} items)")

    # -- 3. Generate icons -----------------------------------------
    print("\n[3/6] Generating icons ...")
    if args.icon and os.path.isfile(args.icon):
        generate_icons(args.icon, appinfo_dir)
    else:
        # Try to get icon from the browser itself
        browser_icon = os.path.join(zen_dir, "browser", "chrome", "icons", "default", "default128.png")
        if os.path.isfile(browser_icon):
            generate_icons(browser_icon, appinfo_dir)
        else:
            print("  WARN: No icon source found, skipping icon generation")

    # -- 4. Update appinfo.ini version -----------------------------
    print("\n[4/6] Updating version info ...")
    appinfo_path = os.path.join(appinfo_dir, "appinfo.ini")
    if os.path.isfile(appinfo_path):
        with open(appinfo_path, "r") as f:
            content = f.read()
        # Update PackageVersion (needs 4-part dotted format)
        version_parts = args.version.lstrip("v").replace("-", ".").split(".")
        # Pad to 4 parts
        while len(version_parts) < 4:
            version_parts.append("0")
        # Replace only numeric parts (strip alpha suffixes for PackageVersion)
        pkg_clean = []
        for p in version_parts[:4]:
            nums = ""
            for c in p:
                if c.isdigit():
                    nums += c
                else:
                    break
            pkg_clean.append(nums if nums else "0")
        pkg_version = ".".join(pkg_clean)

        content = content.replace("PackageVersion=1.0.0.0", f"PackageVersion={pkg_version}")
        content = content.replace("DisplayVersion=1.0.0", f"DisplayVersion={args.version}")
        with open(appinfo_path, "w") as f:
            f.write(content)
        print(f"  OK: PackageVersion={pkg_version}, DisplayVersion={args.version}")

    # -- 5. Compile ZenBrowserPortable.exe (launcher) --------------
    print("\n[5/6] Compiling launcher (NSIS) ...")
    launcher_nsi = os.path.join(paf_root, "launcher.nsi")
    if os.path.isfile(launcher_nsi):
        orig_dir = os.getcwd()
        os.chdir(paf_root)
        run(["makensis", "/V2", launcher_nsi], "launcher compilation")
        os.chdir(orig_dir)
        launcher_exe = os.path.join(paf_root, "ZenBrowserPortable.exe")
        if os.path.isfile(launcher_exe):
            size_kb = os.path.getsize(launcher_exe) // 1024
            print(f"  OK: ZenBrowserPortable.exe ({size_kb} KB)")
        else:
            print("  WARN: Launcher exe not found after compilation")
        # Remove the .nsi source from the final package
        os.remove(launcher_nsi)
    else:
        print("  WARN: launcher.nsi not found, skipping")

    if args.prepare_only:
        print(f"\nPrepared PAF tree for signing: {paf_root}")
        return

    _compile_paf_installer(args, tmp)


def _compile_paf_installer(args: argparse.Namespace, tmp: str) -> None:
    paf_root = os.path.join(tmp, "ZenBrowserPortable")

    # -- 6. Compile .paf.exe (installer) --------------------------
    print("\n[6/6] Compiling installer (NSIS) ...")
    installer_nsi = os.path.join(paf_root, "installer.nsi")
    output_path = os.path.abspath(args.output)
    if os.path.isfile(installer_nsi):
        orig_dir = os.getcwd()
        os.chdir(paf_root)
        run(["makensis", "/V2",
             f"/DVERSION={args.version}",
             f"/DPACKAGE_DIR={paf_root}",
             f"/DOUTPUT={output_path}",
             installer_nsi],
            "installer compilation")
        os.chdir(orig_dir)
        # Remove the .nsi source from package
        os.remove(installer_nsi)
    else:
        print("  WARN: installer.nsi not found, falling back to ZIP")

    # -- Check result ----------------------------------------------
    if os.path.isfile(output_path):
        size_mb = os.path.getsize(output_path) / 1048576
        print(f"\nDONE: {output_path} ({size_mb:.1f} MB)")
    else:
        # Fallback to ZIP
        print("\n  Falling back to ZIP output ...")
        zip_path = output_path.replace(".paf.exe", "")
        shutil.make_archive(zip_path, "zip", tmp, "ZenBrowserPortable")
        final = zip_path + ".zip"
        if os.path.isfile(final):
            size_mb = os.path.getsize(final) / 1048576
            print(f"\nDONE: {final} ({size_mb:.1f} MB)")
        else:
            print("\nFAILED: Could not create output!")
            sys.exit(1)


def main() -> None:
    p = argparse.ArgumentParser(description="Build Zen Browser Portable (PAF)")
    p.add_argument("--installer", required=True, help="Windows NSIS installer (.exe)")
    p.add_argument("--paf-template", required=True, help="PAF template directory")
    p.add_argument("--icon", help="Source PNG for icon generation")
    p.add_argument("--version", default="0.0.0", help="Version string (e.g. 1.19b)")
    p.add_argument("--output", required=True, help="Output .paf.exe path")
    p.add_argument("--build-dir", default="_paf_build", help="Working directory for the staged PAF tree")
    p.add_argument("--keep-build-dir", action="store_true", help="Keep the staged PAF tree after building")
    p.add_argument("--prepare-only", action="store_true",
                   help="Stop after compiling ZenBrowserPortable.exe so it can be signed before creating the installer")
    p.add_argument("--installer-only", action="store_true",
                   help="Create the final installer from an existing staged PAF tree")
    args = p.parse_args()

    if not os.path.isfile(args.installer):
        print(f"ERROR: Installer not found: {args.installer}", file=sys.stderr)
        sys.exit(1)

    build_paf(args)


if __name__ == "__main__":
    main()
