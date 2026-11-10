---
name: aid-validation-device-check
description: Phases 4-5 of AID validation. Use after the AID checklist is confirmed, to verify (Phase 4) that each target device is connected and authorized, its OS/model/installed build match the target, and the Appium MCP server (plus the right driver — uiautomator2 for Android, xcuitest for iOS) is connected and can open a session; and (Phase 5, dev/stage only) that the on-device VPN is active and whether the app is pre-login or logged in, proven by a screenshot and page source captured through the Appium MCP. Runs only the block for each selected platform, read-only on the device, and asks before installing anything. Owns the vetted adb/xcrun/ideviceinstaller/appium command references and the device-check script. Ends with a readiness summary and a STOP gate.
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
- **Appium MCP (each selected platform):** the project's Appium MCP server is connected to this session (its `mcp__<appium-server>__*` tools are available — load with `ToolSearch` if deferred) and can open a session on the target device; `appium driver list --installed` shows `uiautomator2` for Android or `xcuitest` for iOS — check only the selected platform's driver. Prove "can open a session" by having the MCP take one screenshot of the target device.

### Auto-provision the Appium MCP (if its tools aren't present)

Phase 6 drives the app only through this MCP. If no `mcp__…appium…` tools are available, **self-provision it** — the user has authorized the skill to install and configure it without asking each time (this is the one exception to the "ask before installing" rule, and it applies only to this Appium-MCP bootstrap). Do it in this order, reporting each step:

1. **Prerequisites.** Confirm `node`/`npx` are on PATH, the Appium server is reachable (the `curl .../status` check above; if the `appium` CLI is missing, install it: `npm i -g appium` and the platform driver `appium driver install uiautomator2` / `xcuitest`), and the target device is connected (adb/`xcrun`). `appium-mcp` wraps a running Appium server — it does not replace it.
2. **Register the MCP server** in the project config so it loads every session:
   ```bash
   claude mcp add --scope project appium-mcp -- npx -y appium-mcp@latest
   ```
   (equivalently, write to `.mcp.json`: `{"mcpServers":{"appium-mcp":{"command":"npx","args":["-y","appium-mcp@latest"]}}}`).
3. **Reload once — the only unavoidable manual step.** Claude Code registers MCP tools at **session startup**, so the newly added server's `mcp__appium-mcp__*` tools are **not** callable in this running session. Tell the user to restart the session (or `/mcp` → reconnect) and approve the server if prompted, then re-run Phase 4. From then on it connects automatically with no further setup.

Do not continue to Phase 6 until the `mcp__appium-mcp__*` tools are actually present. Device-level checks above (adb/`xcrun`) do **not** need the MCP and run regardless. (Tool names come from `appium-mcp` — e.g. `create_session`, `find_element`, `tap`, `swipe`, `take_screenshot`; confirm the exact names from the loaded tool list and use those.)

Report one row per target device:

| Platform | Device | Connected | OS | App installed | Installed build | Matches target build | Appium MCP ready |
|:--|:--|:--|:--|:--|:--|:--|:--|

Apply `superpowers:verification-before-completion`: mark a cell only from command output, never from assumption. If a device is missing, unauthorized, or the build does not match, say exactly what to do (plug in, accept the USB-debugging prompt, trust the computer, install build X) and **do not continue with that device until fixed.**

**STOP. Wait for the user's go-ahead.**

## Phase 5 — Environment and login check (target only)

**Only if the environment is dev or stage — VPN:**
- Android: `adb -s <id> shell dumpsys connectivity | grep -i vpn` and/or `adb -s <id> shell ip addr | grep -E "tun|ppp"`. Report "VPN active" only if the output shows it.
- iOS: no reliable command — **ask the user to confirm** the VPN is connected on the iPhone.
- If VPN is not connected on a target device, STOP and ask the user to connect it.

**Every environment — login state:**
- Using the Appium MCP, open a session on the target device with `noReset: true` (clears nothing), take a screenshot, and read the page source.
- Report whether the app is on the **pre-login** screen or **logged in**, with the screenshot as proof.
- Compare with the Phase 2/3 screens: list which proposed screens need login and which are pre-login, and tell the user which state each screen needs.

Then show a **readiness summary** (target device(s), build, environment, VPN, login state, number of AIDs to check on each device, screens to visit) and ask: **"Ready to start the comparison on <device(s)>?"**

**STOP. Phase 6 starts only after the user confirms.**
