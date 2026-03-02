; ──────────────────────────────────────────────────────────────────
; Zen Browser Portable — PAF Installer
; Generates: ZenBrowserPortable_<version>.paf.exe
;
; A self-extracting installer compatible with PortableApps.com
; Platform. Users double-click, choose a folder, done.
; ──────────────────────────────────────────────────────────────────

!include "MUI2.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"

; ── Passed in from the command line via /D... ─────────────────────
; makensis /DVERSION=1.19b /DPACKAGE_DIR=... /DOUTPUT=... installer.nsi
!ifndef VERSION
    !define VERSION "0.0.0"
!endif
!ifndef PACKAGE_DIR
    !error "PACKAGE_DIR must be defined (path to assembled ZenBrowserPortable folder)"
!endif
!ifndef OUTPUT
    !define OUTPUT "ZenBrowserPortable_${VERSION}.paf.exe"
!endif

; ── Metadata ─────────────────────────────────────────────────────
Name "Zen Browser Portable ${VERSION}"
OutFile "${OUTPUT}"
InstallDir "$DOCUMENTS\ZenBrowserPortable"

; Request user-level execution (no admin needed)
RequestExecutionLevel user

; ── UI ───────────────────────────────────────────────────────────
!define MUI_ICON "${PACKAGE_DIR}\App\AppInfo\appicon.ico"
!define MUI_ABORTWARNING
!define MUI_WELCOMEPAGE_TITLE "Zen Browser Portable ${VERSION}"
!define MUI_WELCOMEPAGE_TEXT "This will install Zen Browser Portable on your computer or USB drive.$\r$\n$\r$\nNo administrator rights are needed.$\r$\n$\r$\nClick Next to choose an install location."
!define MUI_DIRECTORYPAGE_TEXT_TOP "Choose the folder where you want to install Zen Browser Portable. You can install to a USB drive."

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

; ── Installation ─────────────────────────────────────────────────
Section "Install"
    SetOutPath "$INSTDIR"

    ; Copy everything from the assembled package
    File /r "${PACKAGE_DIR}\*.*"

    ; Ensure Data directories exist
    CreateDirectory "$INSTDIR\Data"
    CreateDirectory "$INSTDIR\Data\profile"
    CreateDirectory "$INSTDIR\Data\temp"
SectionEnd

; ── Silent install support ───────────────────────────────────────
; The installer supports /S for silent mode and /D= for destination,
; which is required by the PortableApps.com Platform.
