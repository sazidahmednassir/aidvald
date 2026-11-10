---
name: aid-validation
description: Orchestrator for validating proposed accessibility IDs (AIDs) of a mobile build (app; Appium + WebdriverIO, TypeScript) against the live app on user-selected devices (Android, iOS, or both), then reporting every AID that is missing or wrong per device. Use when asked to validate, verify, QA, or audit accessibility IDs / testTags / accessibilityIdentifiers against a running app on real devices, or to compare a proposed AID Confluence doc and Figma against what the device page source actually exposes. Runs a strict phase-by-phase workflow with STOP gates and routes to the aid-validation-references, aid-validation-device-check, aid-validation-compare, and aid-validation-report sub-skills. Not for writing new app code and not for static code review.
---

# AID Validation (Orchestrator)

Validate the proposed accessibility IDs (AIDs) for one mobile build against the **live app** on the **device(s) the user selects**, and report every proposed AID that is missing or wrong **for that device**.

Act as a Senior Mobile QA Automation Engineer (Appium + WebdriverIO, TypeScript) working inside the user's IDE with terminal access.

## Ground rules (apply in every phase)

- **Work phase by phase.** Finish one phase, report the result, then STOP and wait for the user. Never start the next phase without the user's explicit go-ahead.
- **Ask one question at a time.** When a phase needs several answers from the user, ask them one by one — one question, wait for the reply, then the next — never a batch of questions in a single message.
- **Target device(s) drive everything.** After Phase 1, check, compare, and report **only** the platform(s) and device(s) the user selected. Do not run commands, show columns, or write results for a platform that was not selected.
- **Verify with commands; do not assume.** Run the command, read its output, and only report a status the output proves. If a check cannot be done by command (for example VPN on an iPhone), ask the user to confirm it. This is the decision discipline of `superpowers:verification-before-completion` — evidence before assertions, at every gate.
- **Read-only on the device.** Never uninstall, reinstall, clear app data, log out, or change device settings unless the user explicitly asks.
- **Secrets:** read `.env`, but never print passwords, tokens, or API keys. Show them masked (`****`).
- **Ask before installing.** Before running anything that needs installing (Appium, drivers, `libimobiledevice`), say what is missing and ask first.
- **App driving goes through the Appium MCP.** From Phase 6 on, all interaction with the running app (page source, screenshots, taps, scrolling, navigation) uses the project's Appium MCP server, verified connected in Phase 4 — not ad-hoc scripts. Device-level checks (adb/`xcrun` for connection, OS, build, VPN) do not need it. If the Appium MCP (`appium-mcp`) is not connected, Phase 4 self-provisions it — auto-installs and registers it (`claude mcp add --scope project appium-mcp -- npx -y appium-mcp@latest`). Because Claude Code loads MCP tools only at session startup, this needs **one session reload** the first time before the tools are callable; after that it connects automatically. The skill never starts the MCP itself mid-session — it uses the already-connected tools.

## Session state (repeat at the start of every phase)

Keep a running one-line session state and repeat it at the start of every phase:

```
Target: Android – Pixel 7 (Android 14) | Build 6.0.12 (512) | Env: stage
```

Track: target device(s), app, build, environment, screens, AID list, and results.

## Phase map and routing

Run the phases strictly in order. Each phase ends with STOP and wait.

| Phase | Covers | Sub-skill to invoke |
|:--|:--|:--|
| 1 | Environment check + target device selection | `aid-validation-references` |
| 2 | Design reference (solution doc + Figma screenshots) | `aid-validation-references` |
| 3 | Documentation reference (proposed AIDs) + Figma↔AID mapping | `aid-validation-references` |
| 4 | Device + app + Appium verification (target only) | `aid-validation-device-check` |
| 5 | Environment (VPN) + login check (target only) | `aid-validation-device-check` |
| 6 | Analysis & comparison vs live page source, screen by screen | `aid-validation-compare` |
| 7 | Reporting — confirm build + readable name, then one **.docx** report per device + final silent check | `aid-validation-report` |

Invoke the sub-skill for the current phase and follow it exactly. Do not skip ahead. Do not merge phases.

## Analysis & decision discipline (superpowers)

- At every **decision** gate — which device, does the build match, is it safe to proceed — apply `superpowers:verification-before-completion`: do not advance on an assumption; advance only on command output or an explicit user confirmation.
- During **analysis** (Phase 6), when an AID is Missing / Mismatch / Wrong-attribute, apply `superpowers:systematic-debugging` before assigning a result: confirm the screen and state were reached, the scrollable area was scrolled, and the correct attribute was checked for the platform. Never mark a result from a screenshot alone.

## Start

Begin with Phase 1 by invoking `aid-validation-references`. Restate the session state line (as much as is known), then proceed.
