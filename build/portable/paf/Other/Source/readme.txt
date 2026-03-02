Zen Browser Portable Launcher
==============================

This portable package was created using the PortableApps.com Format
and the PortableApps.com Launcher.

The launcher configuration is located at:
  App\AppInfo\Launcher\ZenBrowserPortable.ini

How it works:
  - Launches App\zen\zen.exe with --profile pointing to Data\profile
  - Passes --no-remote to avoid conflicts with installed copies
  - Redirects TEMP/TMP to Data\temp (cleaned on exit)
  - Backs up and restores any local %APPDATA%\zen data
  - Seeds Data\profile\user.js from App\DefaultData on first run

License:
  Zen Browser is licensed under the Mozilla Public License 2.0.
  The PortableApps.com Launcher is licensed under the GPL.

Source:
  https://github.com/HasNetwork/zen-browser-portable
  https://github.com/zen-browser/desktop
