# iOS — vetted device & app check commands

All read-only. `<udid>` = device UDID from `.env`. `<bundleId>` = app bundle ID. Never uninstall, reset, or change device/trust settings. Some tools need `libimobiledevice` (`idevice*`) — if missing, say so and **ask before installing**.

## Phase 4 — device & app

| Check | Command (pick what is available) | Output must show |
|:--|:--|:--|
| Device connected | `xcrun xctrace list devices` — or — `idevice_id -l` — or — `xcrun devicectl list devices` | the target UDID present and matched to `.env` |
| OS version | `ideviceinfo -u <udid> -k ProductVersion` — or — `devicectl` device details | iOS version, e.g. `17.5` |
| App installed + version/build | `ideviceinstaller -u <udid> -l \| grep <bundleId>` — or — `xcrun devicectl device info apps --device <udid>` | bundle ID present with its CFBundleShortVersionString / build — compare with target |
| XCUITest session can start | confirm WebDriverAgent / Appium `xcuitest` can open a session on this device | needed for Phase 6; if it cannot, resolve before comparing |

If the device is not trusted: ask the user to tap **Trust** on the iPhone and enter the passcode. Do not continue until the UDID is matched and reachable.

## Phase 5 — VPN (dev / stage only)
There is **no reliable command** to read iPhone VPN state. **Ask the user to confirm** the VPN is connected on the device, and record their confirmation.

## Appium (iOS)

| Check | Command | Output must show |
|:--|:--|:--|
| Server reachable | `curl -s http://<host>:<port>/status` | JSON with `"ready": true` / build info |
| Driver installed | `appium driver list --installed` | `xcuitest` listed |

## accessibilityIdentifier note (for Phase 6)
On iOS, match proposed AIDs against `name` (the `accessibilityIdentifier`). If the value appears only in `label` (`accessibilityLabel`), that is a **Wrong attribute** result — note it (dev fix: set `accessibilityIdentifier`, not `accessibilityLabel`).
