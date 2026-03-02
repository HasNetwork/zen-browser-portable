// Zen Browser Portable - Default Portable Preferences
// These are copied to Data/profile/user.js on first launch

// ── Portable mode flag ────────────────────────────────────────────
user_pref("zen.portable.mode", true);

// ── Cache: use RAM to reduce USB wear ─────────────────────────────
user_pref("browser.cache.disk.enable", false);
user_pref("browser.cache.disk.capacity", 0);
user_pref("browser.cache.memory.enable", true);
user_pref("browser.cache.memory.capacity", 262144);

// ── Disable auto-updates (update manually) ────────────────────────
user_pref("app.update.enabled", false);
user_pref("app.update.auto", false);
user_pref("app.update.mode", 0);
user_pref("app.update.service.enabled", false);

// ── Don't check for default browser ───────────────────────────────
user_pref("browser.shell.checkDefaultBrowser", false);
user_pref("browser.shell.didSkipDefaultBrowserCheckOnFirstRun", true);

// ── Disable telemetry & crash reporting ───────────────────────────
user_pref("toolkit.telemetry.enabled", false);
user_pref("toolkit.telemetry.unified", false);
user_pref("toolkit.telemetry.archive.enabled", false);
user_pref("datareporting.healthreport.uploadEnabled", false);
user_pref("datareporting.policy.dataSubmissionEnabled", false);
user_pref("breakpad.reportURL", "");
user_pref("browser.tabs.crashReporting.sendReport", false);
user_pref("browser.crashReports.unsubmittedCheck.autoSubmit2", false);

// ── Privacy: no tracking ──────────────────────────────────────────
user_pref("privacy.donottrackheader.enabled", true);
user_pref("privacy.trackingprotection.enabled", true);
user_pref("privacy.trackingprotection.socialtracking.enabled", true);

// ── Disable extension and blocklist auto-update checks ────────────
user_pref("extensions.update.enabled", false);
user_pref("extensions.blocklist.enabled", false);

// ── Disable "What's New" and first-run pages ──────────────────────
user_pref("browser.startup.homepage_override.mstone", "ignore");
user_pref("startup.homepage_welcome_url", "");
user_pref("startup.homepage_override_url", "");

// ── Disable captive portal detection ──────────────────────────────
user_pref("network.captive-portal-service.enabled", false);

// ── Disable network connectivity checks ───────────────────────────
user_pref("network.connectivity-service.enabled", false);
