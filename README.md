# Mobile Accessibility ID (AID) Validation Skills

A comprehensive suite of agentic skills for validating proposed mobile Accessibility IDs (AIDs) / testTags against live mobile applications on Android and iOS devices using Appium and live page source analysis.

## Overview

Validating mobile accessibility IDs manually or through ad-hoc inspection is error-prone. This workflow enforces strict, phased validation with verification gates to ensure:
- Proposed AIDs conform to mobile test automation naming conventions (no raw database IDs, lowercase snake_case, standardized element suffixes).
- Every proposed AID is verified against the live UIAutomator2 (Android) or XCUITest (iOS) page source.
- Naming mismatches, duplicate IDs across screens, and wrong attribute placements are identified before automation tests break.

---

## Phased Workflow Structure

| Phase | Responsibility | Skill |
|:---|:---|:---|
| **Phase 1** | Environment check & target device selection (parses `.env`, identifies active devices) | `aid-validation-references` |
| **Phase 2** | Design reference intake (captures and numbers Figma screenshots & API specs) | `aid-validation-references` |
| **Phase 3** | Documentation reference & proposed AID checklist creation with convention checks | `aid-validation-references` |
| **Phase 4** | Device & app verification (confirms device connectivity, installed build version, Appium server) | `aid-validation-device-check` |
| **Phase 5** | Environment (VPN) & login state verification | `aid-validation-device-check` |
| **Phase 6** | Screen-by-screen page source comparison (`content-desc`, `resource-id`, `name`) | `aid-validation-compare` |
| **Phase 7** | Detailed report generation with side-by-side Figma vs live screenshots and issue breakdown | `aid-validation-report` |

---

## Directory Structure

```text
.
├── .claude/
│   └── skills/
│       ├── aid-validation/              # Master Orchestrator skill
│       ├── aid-validation-references/   # Phases 1–3 (Env, Design, Doc checklists)
│       ├── aid-validation-device-check/ # Phases 4–5 (Device, App, VPN, Login)
│       ├── aid-validation-compare/      # Phase 6 (Live source comparison)
│       └── aid-validation-report/       # Phase 7 (Per-device reporting & assets)
├── .env.example                         # Environment configuration template
├── .gitignore                           # Excludes sensitive data, reports, and assets
└── README.md
```

---

## Setup & Prerequisites

1. Copy `.env.example` to `.env` and fill in your device details:
   ```bash
   cp .env.example .env
   ```
2. Ensure `adb` (for Android) and/or `xcrun` / `libimobiledevice` (for iOS) are installed and available on your `PATH`.
3. Start your Appium server with the required driver (`uiautomator2` or `xcuitest`).

