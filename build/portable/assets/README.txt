
  ZEN BROWSER PORTABLE
  ====================

  GETTING STARTED
  ---------------
  Double-click "zen-portable.cmd" to launch Zen Browser in portable mode.

  All your data (bookmarks, history, passwords, extensions)
  is stored in the "Data" folder next to this file.


  FOLDER STRUCTURE
  ----------------
    ZenBrowserPortable/
    |-- zen-portable.cmd     <-- Launch this!
    |-- defaults\user.js     <-- Default portable preferences
    |-- portable.ini         <-- Portable mode marker
    |-- App/                 <-- Browser engine (do not modify)
    |-- Data/                <-- Your personal data
    |   |-- profile/         <-- Bookmarks, history, extensions
    |   |-- temp/            <-- Temporary files
    |   +-- cache/           <-- Cache files
    +-- README.txt           <-- This file


  USB / PENDRIVE USAGE
  --------------------
  * Copy this entire folder to a USB drive.
  * Works on any Windows PC — no installation or admin rights needed.
  * All data stays inside this folder — nothing is left on the host PC.
  * Do NOT unplug the USB drive while the browser is running!


  UPDATING
  --------
  1. Close Zen Browser completely.
  2. Download the latest release ZIP from:
       https://github.com/nkhokhla/zen-browser-portable/releases
  3. Delete the contents of the "App" folder.
  4. Extract the new release ZIP into the "App" folder.
  5. Your data in "Data" is preserved.


  NOTES
  -----
  * Disk cache is disabled by default for USB performance.
    Re-enable in about:config -> browser.cache.disk.enable
  * Auto-updates are disabled. Update manually (see above).
  * Settings are in Data/profile/user.js — edit freely.
  * To reset the browser, delete the "Data" folder.


  LICENSE
  -------
  Zen Browser is licensed under the Mozilla Public License 2.0.
  https://github.com/zen-browser/desktop
