# Android — vetted device & app check commands

All read-only. `<id>` = device serial/UDID from `.env`. `<pkg>` = app package. Never run uninstall, `pm clear`, `am force-stop`, or settings changes.

## Phase 4 — device & app

| Check | Command | Output must show |
|:--|:--|:--|
| Device connected & authorized | `adb devices -l` | the target serial listed as `device` (not `unauthorized` / `offline`) |
| OS version | `adb -s <id> shell getprop ro.build.version.release` | Android release, e.g. `14` |
| Device model | `adb -s <id> shell getprop ro.product.model` | model matching `.env` |
| App installed | `adb -s <id> shell pm list packages \| grep <pkg>` | `package:<pkg>` present |
| Installed build | `adb -s <id> shell dumpsys package <pkg> \| grep -E "versionName\|versionCode"` | `versionName`/`versionCode` — compare with target build |

If `unauthorized`: ask the user to accept the USB-debugging prompt on the phone.
If `offline`: ask the user to replug / re-authorize. Do not continue with that device until it reads `device`.

## Phase 5 — VPN (dev / stage only)

| Check | Command | Report "VPN active" only if |
|:--|:--|:--|
| VPN via connectivity | `adb -s <id> shell dumpsys connectivity \| grep -i vpn` | output shows an established VPN/transport VPN |
| VPN via interface | `adb -s <id> shell ip addr \| grep -E "tun\|ppp"` | a `tun`/`ppp` interface is up with an address |

## Appium (Android)

| Check | Command | Output must show |
|:--|:--|:--|
| Server reachable | `curl -s http://<host>:<port>/status` | JSON with `"ready": true` / build info |
| Driver installed | `appium driver list --installed` | `uiautomator2` listed |

## Compose / testTag note (for Phase 6)
Jetpack Compose `testTag` appears as `resource-id` in the page source **only when** the app sets `testTagsAsResourceId = true`. Match proposed AIDs against both `content-desc` and `resource-id`.
