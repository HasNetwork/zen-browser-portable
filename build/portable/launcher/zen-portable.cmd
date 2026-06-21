@echo off
setlocal

set "ROOT=%~dp0"
set "APP_DIR=%ROOT%App"
set "ZEN_EXE=%APP_DIR%\zen.exe"
set "DATA_DIR=%ROOT%Data"
set "PROFILE_DIR=%DATA_DIR%\profile"
set "TEMP_DIR=%DATA_DIR%\temp"
set "CACHE_DIR=%DATA_DIR%\cache"
set "DEFAULT_USER_JS=%ROOT%defaults\user.js"

if not exist "%ZEN_EXE%" (
  echo Zen Browser was not found.
  echo Expected: "%ZEN_EXE%"
  exit /b 1
)

if not exist "%PROFILE_DIR%" mkdir "%PROFILE_DIR%"
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"
if not exist "%CACHE_DIR%" mkdir "%CACHE_DIR%"

if not exist "%PROFILE_DIR%\user.js" if exist "%DEFAULT_USER_JS%" (
  copy /y "%DEFAULT_USER_JS%" "%PROFILE_DIR%\user.js" >nul
)

set "TEMP=%TEMP_DIR%"
set "TMP=%TEMP_DIR%"
set "MOZ_CRASHREPORTER_DISABLE=1"

start "" /wait "%ZEN_EXE%" --profile "%PROFILE_DIR%" --no-remote %*
