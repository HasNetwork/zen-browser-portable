// Zen Browser Portable Launcher
//
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.
//
// Build (native):  go build -ldflags="-s -w -H=windowsgui" -o zen-portable.exe .
// Build (cross):   GOOS=windows GOARCH=amd64 go build -ldflags="-s -w -H=windowsgui" -o zen-portable.exe .

package main

import (
	_ "embed"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"syscall"
	"unsafe"
)

// Embedded default user.js — written to the profile on first launch.
//
//go:embed defaults/user.js
var defaultUserJS []byte

// ── Windows MessageBox via user32.dll ──────────────────────────────

var (
	modUser32   = syscall.NewLazyDLL("user32.dll")
	procMsgBoxW = modUser32.NewProc("MessageBoxW")
)

const (
	mbOK      = 0x00000000
	mbIconErr = 0x00000010
)

func showError(msg string) {
	title, _ := syscall.UTF16PtrFromString("Zen Browser Portable")
	text, _ := syscall.UTF16PtrFromString(msg)
	procMsgBoxW.Call(
		0,
		uintptr(unsafe.Pointer(text)),
		uintptr(unsafe.Pointer(title)),
		mbIconErr|mbOK,
	)
}

func fatal(msg string) {
	showError(msg)
	os.Exit(1)
}

// ── Main ───────────────────────────────────────────────────────────

func main() {
	// 1. Resolve the launcher's own directory (handles shortcuts, etc.)
	exePath, err := os.Executable()
	if err != nil {
		fatal("Cannot determine launcher location:\n" + err.Error())
	}
	exePath, _ = filepath.EvalSymlinks(exePath)
	root := filepath.Dir(exePath)

	// 2. Define the portable directory layout
	appDir := filepath.Join(root, "App")
	zenExe := filepath.Join(appDir, "zen.exe")
	dataDir := filepath.Join(root, "Data")
	profileDir := filepath.Join(dataDir, "profile")
	tempDir := filepath.Join(dataDir, "temp")
	cacheDir := filepath.Join(dataDir, "cache")

	// 3. Verify zen.exe exists
	if _, err := os.Stat(zenExe); os.IsNotExist(err) {
		fatal(fmt.Sprintf(
			"Zen Browser not found!\n\n"+
				"Expected:\n  %s\n\n"+
				"Make sure the 'App' folder contains the browser files.",
			zenExe,
		))
	}

	// 4. Create data directories
	for _, d := range []string{profileDir, tempDir, cacheDir} {
		if err := os.MkdirAll(d, 0o755); err != nil {
			fatal(fmt.Sprintf("Cannot create directory:\n  %s\n\n%s", d, err.Error()))
		}
	}

	// 5. Seed user.js on first run
	userJS := filepath.Join(profileDir, "user.js")
	if _, err := os.Stat(userJS); os.IsNotExist(err) {
		if err := os.WriteFile(userJS, defaultUserJS, 0o644); err != nil {
			fatal("Cannot write default user.js:\n" + err.Error())
		}
	}

	// 6. Environment - redirect temp and disable crash reporter
	os.Setenv("TEMP", tempDir)
	os.Setenv("TMP", tempDir)
	os.Setenv("MOZ_CRASHREPORTER_DISABLE", "1")

	// 7. Launch zen.exe with portable arguments
	args := []string{"--profile", profileDir, "--no-remote"}
	args = append(args, os.Args[1:]...) // pass-through (URLs, flags, etc.)

	cmd := exec.Command(zenExe, args...)
	cmd.Dir = appDir
	cmd.Env = os.Environ()

	if err := cmd.Start(); err != nil {
		fatal("Failed to start Zen Browser:\n" + err.Error())
	}
	cmd.Wait()
}
