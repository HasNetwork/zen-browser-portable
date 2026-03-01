// Zen Browser Portable — Default Preferences
// This file is auto-generated on first launch. You may edit it freely.
// Preferences here override defaults each time the browser starts.
//
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

// ─── Portable Mode ─────────────────────────────────────────────────
user_pref("zen.portable.mode", true);

// ─── Disk Cache ─────────────────────────────────────────────────────
// Disabled to avoid excessive writes on removable media (USB drives).
// Pages are cached in RAM instead. Adjust capacity as needed (in KB).
user_pref("browser.cache.disk.enable", false);
user_pref("browser.cache.memory.enable", true);
user_pref("browser.cache.memory.capacity", 262144); // 256 MB

// ─── Updates ────────────────────────────────────────────────────────
// Portable installs are updated manually by replacing the App folder.
user_pref("app.update.enabled", false);
user_pref("app.update.auto", false);
user_pref("app.update.service.enabled", false);
user_pref("app.update.staging.enabled", false);
user_pref("app.update.background.scheduling.enabled", false);

// ─── Default Browser ────────────────────────────────────────────────
// Never ask — a portable install shouldn't register as default.
user_pref("browser.shell.checkDefaultBrowser", false);
user_pref("browser.shell.didSkipDefaultBrowserCheckOnFirstRun", true);

// ─── Crash Reporter ────────────────────────────────────────────────
user_pref("browser.crashReports.unsubmittedCheck.autoSubmit2", false);
user_pref("browser.crashReports.unsubmittedCheck.enabled", false);
user_pref("breakpad.reportURL", "");

// ─── Telemetry & Data Reporting ─────────────────────────────────────
user_pref("datareporting.policy.dataSubmissionEnabled", false);
user_pref("datareporting.healthreport.uploadEnabled", false);
user_pref("toolkit.telemetry.enabled", false);
user_pref("toolkit.telemetry.unified", false);
user_pref("toolkit.telemetry.archive.enabled", false);

// ─── Experiments / Normandy ─────────────────────────────────────────
user_pref("app.normandy.enabled", false);
user_pref("app.shield.optoutstudies.enabled", false);
