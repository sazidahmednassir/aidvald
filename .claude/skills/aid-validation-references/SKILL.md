---
name: aid-validation-references
description: Phases 1-3 of AID validation. Use after the aid-validation orchestrator starts, to (1) find and parse the .env, report device/app/build/env details with masked secrets, and capture the target device list; (2) intake and number the solution document and Figma screenshots with their highlighted elements; and (3) build the proposed-AID checklist for the target device(s) only from the Confluence doc, resolve dynamic AID patterns, check the naming convention, and map every Figma element to a proposed AID. Produces the target device list, numbered screens, and the confirmed AID checklist. Each phase ends with a STOP gate.
---

# AID Validation — References (Phases 1–3)

Restate the session state line at the start of each phase. Run one phase, report, then STOP and wait. Read `assets/checklist-template.md` for the exact table shapes.

## Phase 1 — Environment check and target device selection

1. Find the `.env` in the project root (also check `.env.local`, `.env.<env>`). If more than one exists, list them and ask which to use.
2. Read it and report, in a short table: device names / UDIDs per platform, platform versions, app package (Android) / bundle ID (iOS), app or build version, Appium host/port, target environment (prod / stage / dev). **Mask all secrets** (`****`) — never print passwords, tokens, or API keys.
3. Flag anything missing or inconsistent (for example an iOS device listed but no iOS bundle ID).
4. Ask the user the following **one question at a time** — ask one, wait for the answer, then ask the next. **Never present them all in a single message.**
   1. Which device(s) to validate on: **Android, iOS, or both?**
   2. If `.env` lists more than one device for a chosen platform, **which device** (by name/UDID)?
   3. **App name check (both platforms).** Confirm the selected platform's app name is in `.env` — Android **app package** (`ANDROID_APP_PACKAGE`) or iOS **bundle ID** (`IOS_APP_BUNDLE_ID`). If it is **missing**, ask the user **which app it is and to provide the app name** — the Android **app package** or the iOS **bundle ID** (for example, "Which app? Please provide the Android app package / iOS bundle ID") — and once given, **write it into the `.env`** under the matching key (`ANDROID_APP_PACKAGE` / `IOS_APP_BUNDLE_ID`) before continuing. If both platforms are in scope, do this for each.
   4. Which **environment**: prod, stage, or dev?

Record the answer as the **target device list**:

| # | Platform | Device | UDID | App ID |
|:--|:--|:--|:--|:--|

If the selected platform has no device in `.env`, ask the user for it before continuing. If its **app name** is missing from `.env`, ask for it and **write it into the `.env`** under the matching key (`ANDROID_APP_PACKAGE` for Android, `IOS_APP_BUNDLE_ID` for iOS) before continuing. **STOP. Wait for the answers.**

## Phase 2 — Design reference (solution + Figma)

1. Ask for the **solution document** and the **Figma screenshots** with the highlighted (boxed) elements.
2. Number the screenshots in upload order (Screen 1, 2, 3…). Keep counting across batches. **Never renumber.**
3. For each screen, list `Screen N: <what it shows>` and every highlighted element with its visible text and position (for example "top bar, under the profile").
4. From the solution document, note the API source for each element where one exists (endpoint → object → attribute), any state conditions (logged-in only, balance = 0), and which values are dynamic.
5. Note any element or screen the documents say exists on **only one platform** — it will be checked only there.
6. End with: **"Are there more screenshots or documents to upload? If any screen label is wrong, tell me now."**

**STOP. Repeat this phase until the user says there is nothing more.**

## Phase 3 — Documentation reference (proposed AIDs)

1. Ask for the **proposed AID Confluence document** (export, copy-paste, or file).
2. Build the **AID checklist for the target device(s) only** — one row per proposed AID (see `assets/checklist-template.md`):

   | # | Element name (as in proposed doc) | Screen (Phase 2 #) | Proposed AID | Type: static / dynamic | Dynamic parts & source | Applies to target device? |

   If the doc gives different AIDs per platform, list only the AID for the selected platform. An AID that applies only to the other platform is listed once under **"Not in scope for this device"** and is not checked.
3. For dynamic AIDs (patterns like `{parentCard.type}_{child.subtype}_title_{title}_txt`), work out the **expected live value** from the solution doc or visible text. If a value cannot be resolved, mark it **"pattern only"** — it will be checked by pattern match.
4. Check the proposed AIDs against the naming convention (lowercase static parts, `_` separator, valid suffix such as `btn`, `txt`, `img`, `icon`, `card`, `list`, `bnnr`, `prgrs`; no indexes or raw DB IDs). List naming problems **separately** — these are documentation issues, not app bugs.
5. Map every highlighted Figma element to a proposed AID. List any highlighted element with **no proposed AID**, and any proposed AID with **no highlighted element**.

Show the checklist and the mapping gaps. **STOP. Ask the user to confirm the checklist before any device work.**
