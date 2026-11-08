---
name: aid-validation-device-check
description: Phases 4-5 of AID validation. Use after the AID checklist is confirmed, to verify (Phase 4) that each target device is connected and authorized, its OS/model/installed build match the target, and Appium plus the right driver (uiautomator2 for Android, xcuitest for iOS) are ready; and (Phase 5, dev/stage only) that the on-device VPN is active and whether the app is pre-login or logged in, proven by an Appium screenshot and page source. Runs only the block for each selected platform, read-only on the device, and asks before installing anything. Owns the vetted adb/xcrun/ideviceinstaller/appium command references and the device-check script. Ends with a readiness summary and a STOP gate.
---

# AID Validation — Device & App Check (Phases 4–5)

Restate the session state line first. Run **only** the block for each selected platform; skip the other platform completely. Stay **read-only** on the device. Ask before installing Appium, drivers, or `libimobiledevice`.

Use the vetted commands in:
- `references/android-commands.md` (Android)
- `references/ios-commands.md` (iOS)

`scripts/device-check.sh` runs the Phase-4 connection/OS/model/install/build checks for one platform and prints the status row. Read it before first use; it never modifies the device.

## Phase 4 — Device and app verification (target only)

Run the per-platform checks (see the reference files for exact commands):

- **Android:** device listed as `device` (not `unauthorized`/`offline`); OS version; model matched to `.env`; app package installed; installed `versionName`/`versionCode` compared with the target build.
- **iOS:** device connected and matched to the `.env` UDID; OS version; app installed with its version and build; confirm WebDriverAgent / XCUITest can start a session (needed in Phase 6).
- **Appium (each selected platform):** server reachable at the `.env` host/port (`curl .../status`); `appium driver list --installed` shows `uiautomator2` for Android or `xcuitest` for iOS — check only the selected platform's driver.

Report one row per target device:

| Platform | Device | Connected | OS | App installed | Installed build | Matches target build | Appium ready |
|:--|:--|:--|:--|:--|:--|:--|:--|

Apply `superpowers:verification-before-completion`: mark a cell only from command output, never from assumption. If a device is missing, unauthorized, or the build does not match, say exactly what to do (plug in, accept the USB-debugging prompt, trust the computer, install build X) and **do not continue with that device until fixed.**

**STOP. Wait for the user's go-ahead.**

## Phase 5 — Environment and login check (target only)

**Only if the environment is dev or stage — VPN:**
- Android: `adb -s <id> shell dumpsys connectivity | grep -i vpn` and/or `adb -s <id> shell ip addr | grep -E "tun|ppp"`. Report "VPN active" only if the output shows it.
- iOS: no reliable command — **ask the user to confirm** the VPN is connected on the iPhone.
- If VPN is not connected on a target device, STOP and ask the user to connect it.

**Every environment — login state:**
- Open an Appium session on the target device with `noReset: true` (clears nothing), take a screenshot, and read the page source.
- Report whether the app is on the **pre-login** screen or **logged in**, with the screenshot as proof.
- Compare with the Phase 2/3 screens: list which proposed screens need login and which are pre-login, and tell the user which state each screen needs.

Then show a **readiness summary** (target device(s), build, environment, VPN, login state, number of AIDs to check on each device, screens to visit) and ask: **"Ready to start the comparison on <device(s)>?"**

**STOP. Phase 6 starts only after the user confirms.**
