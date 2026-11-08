# AID Validation Report — {Platform} / {Device}

> One device per report. Do not include the other platform's results here.
> File: `reports/aid-validation/<build>/AID_Validation_Report_<build>_<Platform>_<Device>_<date>.md`
> Every image below is produced by `annotate_aids.py` in Phase 6. Use relative paths.

## 1. Summary

| Field | Value |
|:--|:--|
| Platform | Android / iOS |
| Device (name & model) | Pixel 7 (Pixel 7) |
| OS version | 14 |
| App ID | `com.example.app` |
| Installed build | 6.0.12 (512) |
| Environment | stage |
| Login state | logged in / pre-login |
| Date | YYYY-MM-DD |

**Totals**

| Found | Mismatch | Wrong attribute | Duplicate | Missing | Not checked |
|:--:|:--:|:--:|:--:|:--:|:--:|
| 0 | 0 | 0 | 0 | 0 | 0 |

**Coverage:** N/N proposed AIDs checked (count from the Phase 3 doc = result-table rows; note any Not checked).

**Highlight legend** — 🟩 Found · 🟧 Mismatch · 🟨 Wrong attribute · 🟪 Duplicate · 🟥 Missing · ⬜ Not checked · 🟦 all-AID overlay (every accessibility ID on the screen).

## 2. Screens — accessibility IDs identified on the live app

> One block per screen validated on this device, in Phase 2 order. The annotated image boxes and numbers **every** AID on the screen; the inventory documents each one and flags any the proposed doc does not cover.

### Screen {N} — {screen name}

<!-- business view: numbered screenshot + AID-name legend, no bounds. {width=6.5in} -->
![accessibility IDs mapped to the screen](<relative/path/to/screen-N-callout.png>){width=6.5in}

*{count} unique accessibility IDs on this screen. Full engineer table (type + pixel bounds): `<...>/screen-N-aids.csv`.*

## 3. Issues (one entry per AID that is not "Found")

### Issue N — {Element name (exactly as in proposed doc)}

- **Screen:** {Phase 2 number} — {screen name}
- **Proposed AID:** `{proposed_aid}`
- **Actual value found:** `{actual}` (or "none")
- **Result:** Mismatch / Wrong attribute / Duplicate / Missing / Not checked
- **Dev note:** {e.g. set accessibilityIdentifier, not accessibilityLabel}

| Figma (expected) | Live app ({Device}) — highlighted |
|:--|:--|
| ![figma](<relative/path/to/figma-screen-N.png>) | ![live highlight](<relative/path/to/screen-N-issue-k-slug.png>) |

## 4. Documentation issues (from Phase 3)

- Naming-convention problems:

| Proposed AID | Problem | Convention rule broken |
|:--|:--|:--|

- Highlighted Figma elements with no proposed AID:

- AIDs exposed by the app but **not in the proposed doc** (from the Section 2 inventory "undocumented" rows):

| Accessibility ID | Screen | Note |
|:--|:--|:--|

## 5. Full results table (every AID checked on this device)

| # | Element name | Screen | Proposed AID (full pattern) | Result | Actual value(s) found |
|:--|:--|:--|:--|:--|:--|

## 6. Not checked / Not in scope

**Not checked** (with reason):

| Element name | Proposed AID | Reason |
|:--|:--|:--|

**Not in scope for this device** (belongs to the other platform):

| Element name | Proposed AID | Platform |
|:--|:--|:--|

---

## Cross-device summary (only if both platforms validated)
> File: `reports/aid-validation/<build>/AID_Validation_Summary_<build>_<date>.md`
> One totals row per device + links to each device report. Do NOT merge issue lists.

| Device | Found | Mismatch | Wrong attr | Duplicate | Missing | Not checked | Report |
|:--|:--:|:--:|:--:|:--:|:--:|:--:|:--|
| Android – Pixel 7 | | | | | | | [report](./AID_Validation_Report_...Android...md) |
| iOS – iPhone 14 | | | | | | | [report](./AID_Validation_Report_...iOS...md) |
