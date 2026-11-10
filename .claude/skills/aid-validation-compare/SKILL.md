---
name: aid-validation-compare
description: Phase 6 of AID validation. Use after device readiness is confirmed, to compare the proposed AIDs against the live app page source screen by screen on the target device(s). For each screen it captures page source plus a screenshot (through the project's Appium MCP server) to reports/aid-validation, runs the annotate_aids.py helper to produce a highlighted screenshot and a documented inventory of every accessibility ID present on that screen, scrolls scrollable areas before judging, and assigns each AID exactly one result — Found, Mismatch, Wrong attribute, Duplicate, Missing, or Not checked — matching Android content-desc/resource-id or iOS name, with static AIDs by exact match and dynamic AIDs by expected value or pattern wildcard. Handles {children[]} array patterns as multiple expected instances, never marks a result from a screenshot alone, and guarantees every proposed AID gets a result. When a target screen or section is not on the currently open page, it first scrolls to try to locate it and, if it still cannot be found, prompts the user for where the element lives and how to navigate there, then drives the app to that screen with the Appium MCP before judging. If both platforms are selected it finishes one device fully before the next. Stops whenever the device state must change.
---

# AID Validation — Analysis & Comparison (Phase 6)

Restate the session state line first. Go **screen by screen, in Phase 2 order**. If both platforms are selected, finish one device completely, then do the other — ask the user which to do first.

**Coverage is mandatory.** Every proposed AID on the Phase 3 checklist gets **exactly one result** — none is silently dropped. At the end, the count of proposed AIDs in the doc must equal the number of result rows. Carry that count so the report can state it.

Before assigning any non-Found result, apply `superpowers:systematic-debugging`: was the screen and its required state actually reached? was every scrollable area scrolled? was the correct attribute checked for this platform? Only after those are confirmed does a Missing / Mismatch / Wrong-attribute / Duplicate stand.

## Driving the device — the Appium MCP

All interaction with the running app in this phase — capturing page source, taking screenshots, tapping, and scrolling/navigating — goes through the **project's Appium MCP server** (verified connected in Phase 4), not ad-hoc WebdriverIO scripts.

- **Find the tools at runtime.** The server's tools appear as `mcp__<appium-server>__*` (if deferred, load them with `ToolSearch` first). Discover the exact names from the tool list — typically something like *list devices / select device*, *get page source*, *take screenshot*, *find element*, *tap / click*, *send keys*, and *scroll / swipe*. Use the server's own tool for each action; do not assume a tool name that isn't listed.
- **Capture** (page source + screenshot) uses the MCP's source/screenshot tools; save their output to the Phase-6 paths below.
- **Fallback for gestures the MCP can't do:** `adb` on Android (`adb -s <id> shell input swipe/tap/keyevent`) and the equivalent on iOS — read-only interaction only (navigation and scrolling; never log out, clear data, or change settings).
- **If the Appium MCP is not connected**, stop and go back to Phase 4's "Auto-provision the Appium MCP" step (it installs/registers `appium-mcp` and needs a one-time session reload) — do not silently fall back to hand-driving the device.

## Per screen, on the current device

1. Ask the user to open that screen (or navigate with the Appium MCP if allowed), and to set any state the screen needs (zero balance, not enrolled, etc.). **If the screen or section is not already on the open page, follow "Reaching a screen/section that isn't on the open page" below before capturing.**
2. Capture the **page source** and a **screenshot** with the Appium MCP's source/screenshot tools. Save both to:
   `reports/aid-validation/<build>/<platform>-<device>/screen-<N>.(xml|png)`
3. If a list/carousel element is off-screen, **scroll inside it and capture again**. Do not mark an AID missing until the scrollable area has been checked.
4. **Build the visual + documented evidence for the screen.** Run the annotate helper on the captured pair:

   ```bash
   python3 .claude/skills/aid-validation-compare/scripts/annotate_aids.py \
     --screenshot reports/aid-validation/<build>/<platform>-<device>/screen-<N>.png \
     --xml       reports/aid-validation/<build>/<platform>-<device>/screen-<N>.xml \
     --out-dir   reports/aid-validation/<build>/<platform>-<device> \
     --base screen-<N> --screen <N> \
     --checklist <checklist.json>   # optional: JSON array of the proposed AID strings for this screen
   ```

   This writes, next to the capture:
   - `screen-<N>-annotated.png` — **every accessibility ID on the screen boxed (blue) and numbered**, matching the highlighted-Figma style. Numbers map to the inventory.
   - `screen-<N>-callout.png` — the **business-readable view**: the numbered screenshot with a legend of number → AID name beside it (green = in the proposed doc), and **no pixel bounds**. This is the figure to put in the report body; bounds coordinates are not meaningful to non-engineers.
   - `screen-<N>-aids.md` / `screen-<N>-aids.csv` — the **"Accessibility IDs identified on screen"** inventory: number, AID value (content-desc / name), element type, occurrence count, every bounds, secondary resource-id, and — when `--checklist` is passed — whether each AID was documented (so **undocumented AIDs the app exposes are flagged**). Pixel bounds live in the `.csv` (engineer view) only — keep them out of the business-facing report.

   The helper reads bounds directly from the page source, so the boxes are exact. It is the source of the **"document every AID identified on the screen"** requirement — do not hand-list AIDs; use its output.
5. Look up each proposed AID for that screen using the platform rule:
   - **Android:** match `content-desc` and `resource-id` (Compose `testTag` with `testTagsAsResourceId` shows as `resource-id`).
   - **iOS:** match `name` (`accessibilityIdentifier`). If the value appears only in `label`, that is **Wrong attribute**.
   - **Static AID:** exact match.
   - **Dynamic AID:** resolve the pattern. Fixed segments must match literally; a `{placeholder}` matches any value of the right shape. Report the live value(s) found.
6. Give each AID exactly one result:
   - **Found** — the pattern/value matches in the page source. For a dynamic pattern, Found if at least one valid live instance matches and none break the format.
   - **Mismatch** — a similar ID exists but differs (case, spaces, suffix, order, extra/missing part). Show proposed vs. actual.
   - **Wrong attribute** — value exists but in the wrong place (iOS `label` instead of `name`; Android `text` instead of `content-desc`).
   - **Duplicate** — the **same resolved AID string** is on more than one element on the screen (the inventory `Count` column makes these obvious). A static AID, or a dynamic AID whose discriminator does not actually vary, that lands on several elements is a Duplicate.
   - **Missing** — not found after scrolling the screen (and the screen was reached — see "Reaching a screen/section that isn't on the open page").
   - **Not checked** — screen/state could not be reached **even after scrolling and following the user's navigation directions**. Give the reason.

   **Dynamic `{children[]}` (array) patterns — do not mis-flag.** When a pattern contains an array placeholder such as `{children[]}` (e.g. `..._home_appbar_{children[]}_card`), the app is **expected** to expose one AID per array item, each with a different value (`..._39808_card`, `..._39807_card`, …). Match and list **every** such instance under that one checklist row and mark it **Found** — the multiple values are correct, **not** Duplicate and **not** undocumented. Only report a problem if (a) an instance breaks the pattern/convention (e.g. a raw DB id where the convention forbids it — a Phase 3 documentation issue), or (b) the same resolved value repeats on multiple elements. Contrast with a sibling AID on the same elements that has **no** discriminator (e.g. `..._home_appbar_bnnr`): that one collides across the instances and **is** a Duplicate — a useful signal that the sibling AID is missing the `{children[]}` part the card AID has.
7. **Produce a focused highlight for each reported AID**, coloured by result, to embed in the report. Write the issues for this screen to a small JSON file and re-run the helper with `--issues`:

   ```bash
   # Single AID:  {"aid":"slide_..._bnnr","name":"Top-Bar Megabanner","result":"Duplicate"}
   # Array pattern (group all live instances into ONE image):
   #   {"aids":["..._39808_card","..._39807_card","..._39890_card"],
   #    "name":"Top-Bar Megabanner Child Card","result":"Found","slug":"children-card-pattern"}
   python3 .claude/skills/aid-validation-compare/scripts/annotate_aids.py \
     --screenshot <...>/screen-<N>.png --xml <...>/screen-<N>.xml \
     --out-dir <...> --base screen-<N> --screen <N> --issues issues.json
   ```

   Each entry yields `screen-<N>-issue-<k>-<slug>.png`: the whole screen dimmed, the matched element(s) restored and boxed in the result colour (red=Missing, orange=Mismatch, amber=Wrong attribute, purple=Duplicate, green=Found), with a caption bar. For a **Duplicate** every colliding occurrence is boxed; for an **array pattern** every instance is boxed in one image; for a **Missing** the AID is not on screen, so the image is the dimmed screen with a "not present" caption. Produce one per non-Found AID, plus one per dynamic pattern to show it validated across its instances.
8. Also list any **unexpected AIDs** on the screen that are close to a proposed one (possible renames) — the inventory's undocumented rows are where to look. Exclude array-pattern instances already matched in step 6.
9. Show the result table for that screen and device, then move to the next screen. **If the user must change device state, STOP and wait.**

## Reaching a screen/section that isn't on the open page

Before an AID can get a Missing or Not-checked result, its screen/section must actually be reached. When the expected screen or section is **not visible on the page currently open**, work through this in order — do not jump straight to Missing:

1. **Scroll the open page to locate it.** Scroll the page/container up and down to its ends (and sideways for carousels/tabs), re-capturing page source as you go, looking for the section's identifying elements (its heading text, a known AID, or elements from the solution doc). Treat this as part of the mandatory scroll discipline — a section below the fold is **present**, not missing.
2. **If it still cannot be found, STOP and ask the user** — one clear question: *"I can't find **\<screen / section name\>** on the current page (\<what is open now\>). Where does it live in the app, and how do I get there from here — which tabs/buttons/menu items do I tap, in order?"* Wait for the answer.
3. **Drive the app there with the Appium MCP, using the user's directions** (navigation by tapping is interaction, not a data change, so it is allowed — but it is still **read-only**: do not log out, change settings, or alter app data). For each step the user gives:
   - Use the MCP's *find element* tool with an accessibility-id or visible-text selector, then its *tap/click* tool; or use its *scroll/swipe* tool for the gesture described (open a drawer, switch tab, scroll to and tap an item). Fall back to `adb shell input` (Android) only if the MCP has no matching gesture tool.
   - Re-capture the page source/screenshot (MCP) after each step and confirm the expected next screen was reached before the next tap.
   - If a step can't be automated (an OS dialog, biometrics, a flow the MCP can't reach), ask the user to perform just that step on the device and tell you when the screen is open.
4. **Once the screen is reached, resume the normal per-screen flow** (capture → annotate → compare). Only if the screen genuinely cannot be reached even with the user's guidance do its AIDs become **Not checked**, with the reason recorded.

Record how each screen was reached (already open / scrolled to / navigated via user steps) so the evidence shows the state was truly reached before judging.

## Result table per screen (current device only)

| # | Element name | Proposed AID (pattern) | Result | Actual value(s) found |
|:--|:--|:--|:--|:--|

Keep, per screen, as the evidence pack: `screen-<N>.xml`, `screen-<N>.png`, `screen-<N>-annotated.png`, `screen-<N>-aids.(md|csv)`, and one `screen-<N>-issue-*.png` per reported AID / pattern.

**Never mark an AID Found from the screenshot alone — it must be in the saved page source.** Keep every captured `.xml` as the evidence backing each Found and each Missing.
