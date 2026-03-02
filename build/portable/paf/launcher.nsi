; ------------------------------------------------------------------
; Zen Browser Portable - NSIS Launcher
; Generates: ZenBrowserPortable.exe
;
; What it does:
;   1. Resolves its own directory
;   2. Seeds Data\profile from App\DefaultData on first run
;   3. Sets TEMP/TMP environment variables
;   4. Launches zen.exe --profile "Data\profile" --no-remote
;   5. Waits for the browser to exit
;   6. Cleans up the temp directory
; ------------------------------------------------------------------

!include "FileFunc.nsh"
!include "LogicLib.nsh"

; -- Metadata ------------------------------------------------------
Name "Zen Browser Portable"
OutFile "ZenBrowserPortable.exe"
RequestExecutionLevel user
SilentInstall silent

; -- Main ----------------------------------------------------------
Section "Main"
    ; Get our own directory
    ${GetParent} "$EXEPATH" $0
    StrCpy $INSTDIR "$0"

    ; -- Seed Data\profile from DefaultData on first run -----------
    IfFileExists "$INSTDIR\Data\profile\*.*" SkipSeed
        CreateDirectory "$INSTDIR\Data\profile"
        CopyFiles /SILENT "$INSTDIR\App\DefaultData\profile\*.*" "$INSTDIR\Data\profile"
    SkipSeed:

    ; -- Create temp directory -------------------------------------
    CreateDirectory "$INSTDIR\Data\temp"

    ; -- Set environment variables ---------------------------------
    System::Call 'Kernel32::SetEnvironmentVariable(t "TEMP", t "$INSTDIR\Data\temp")i'
    System::Call 'Kernel32::SetEnvironmentVariable(t "TMP", t "$INSTDIR\Data\temp")i'
    System::Call 'Kernel32::SetEnvironmentVariable(t "MOZ_CRASHREPORTER_DISABLE", t "1")i'

    ; -- Find and launch zen.exe -----------------------------------
    StrCpy $1 "$INSTDIR\App\zen\zen.exe"

    IfFileExists "$1" LaunchApp
        MessageBox MB_OK|MB_ICONSTOP "Could not find zen.exe. Please reinstall Zen Browser Portable."
        Quit
    LaunchApp:

    ; Launch the browser and wait for it to exit
    ExecWait '"$1" --profile "$INSTDIR\Data\profile" --no-remote'

    ; -- Cleanup temp directory ------------------------------------
    RMDir /r "$INSTDIR\Data\temp"
SectionEnd
