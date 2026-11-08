# AID Validation — Checklist Templates

Copy these tables into the working notes. Fill one row per item.

## Target device list (Phase 1)

| # | Platform | Device | UDID | App ID |
|:--|:--|:--|:--|:--|
| 1 | Android | Pixel 7 | `emulator-5554` / serial | `com.example.app` |

## .env summary (Phase 1) — mask secrets

| Key | Value | Notes |
|:--|:--|:--|
| Android device / UDID | Pixel 7 / `<serial>` | |
| iOS device / UDID | iPhone 14 / `<udid>` | |
| Android package | `com.example.app` | |
| iOS bundle ID | `com.example.app` | |
| App / build version | 6.0.12 (512) | |
| Appium host:port | `127.0.0.1:4723` | |
| Environment | stage | |
| Any secret (token/pwd/key) | `****` | never print the real value |

## Screen inventory (Phase 2)

- **Screen N: <what it shows>**
  - Highlighted element — visible text — position — API source (endpoint → object → attribute) — state condition — dynamic? — platform scope

## AID checklist (Phase 3) — target device(s) only

| # | Element name (as in proposed doc) | Screen (Phase 2 #) | Proposed AID | Type (static/dynamic) | Dynamic parts & source | Applies to target device? |
|:--|:--|:--|:--|:--|:--|:--|

### Naming-convention problems (documentation issues, not app bugs)

| Proposed AID | Problem | Convention rule broken |
|:--|:--|:--|

### Mapping gaps

- Highlighted Figma elements with **no proposed AID**:
- Proposed AIDs with **no highlighted element**:

### Not in scope for this device

| Element name | Proposed AID | Platform it belongs to |
|:--|:--|:--|
