---
name: aid-validation-compare
description: Phase 6 of AID validation. Use after device readiness is confirmed, to compare the proposed AIDs against the live app page source screen by screen on the target device(s). For each screen it captures page source plus a screenshot to reports/aid-validation, runs the annotate_aids.py helper to produce a highlighted screenshot and a documented inventory of every accessibility ID present on that screen, scrolls scrollable areas before judging, and assigns each AID exactly one result — Found, Mismatch, Wrong attribute, Duplicate, Missing, or Not checked — matching Android content-desc/resource-id or iOS name, with static AIDs by exact match and dynamic AIDs by expected value or pattern wildcard. Handles {children[]} array patterns as multiple expected instances, never marks a result from a screenshot alone, and guarantees every proposed AID gets a result. If both platforms are selected it finishes one device fully before the next. Stops whenever the device state must change.
---

# AID Validation — Analysis & Comparison (Phase 6)

Restate the session state line first. Go **screen by screen, in Phase 2 order**. If both platforms are selected, finish one device completely, then do the other — ask the user which to do first.

**Coverage is mandatory.** Every proposed AID on the Phase 3 checklist gets **exactly one result** — none is silently dropped. At the end, the count of proposed AIDs in the doc must equal the number of result rows. Carry that count so the report can state it.

Before assigning any non-Found result, apply `superpowers:systematic-debugging`: was the screen and its required state actually reached? was every scrollable area scrolled? was the correct attribute checked for this platform? Only after those are confirmed does a Missing / Mismatch / Wrong-attribute / Duplicate stand.

## Per screen, on the current device

1. Ask the user to open that screen (or navigate with Appium if allowed), and to set any state the screen needs (zero balance, not enrolled, etc.).
2. Capture the **page source** and a **screenshot**. Save both to:
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
   - **Missing** — not found after scrolling the screen.
   - **Not checked** — screen/state could not be reached. Give the reason.

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

## Result table per screen (current device only)

| # | Element name | Proposed AID (pattern) | Result | Actual value(s) found |
|:--|:--|:--|:--|:--|

Keep, per screen, as the evidence pack: `screen-<N>.xml`, `screen-<N>.png`, `screen-<N>-annotated.png`, `screen-<N>-aids.(md|csv)`, and one `screen-<N>-issue-*.png` per reported AID / pattern.

**Never mark an AID Found from the screenshot alone — it must be in the saved page source.** Keep every captured `.xml` as the evidence backing each Found and each Missing.
