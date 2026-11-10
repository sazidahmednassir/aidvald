---
name: aid-validation-report
description: Phase 7 of AID validation. Use after the screen-by-screen comparison is done, to write one report per target device under the reports/aid-validation build folder, each covering exactly one device and never mentioning the other platform's results. Each report is visual: per screen it embeds the annotated (all-AIDs-highlighted) screenshot and a documented inventory of every accessibility ID found, each non-Found AID gets a focused colour-coded highlight next to its Figma reference, and dynamic {children[]} patterns get one grouped highlight. States explicit coverage (proposed AIDs checked vs total). Delivers a Word (**.docx**) report with embedded visuals by default, rendered by the bundled assets/md2docx.py helper (python-docx; no pandoc or network needed, pandoc an optional fallback) with the Markdown kept as the editable source; before writing, confirms the build this report is for and composes a readable report name (app + version + environment + platform). Runs the final silent self-check before handing back the report path(s) and totals.
---

# AID Validation — Reporting (Phase 7)

Restate the session state line first. Create **one report per target device**. Each report covers **only that device** — never mention the other platform's results in it. Read `assets/report-template.md` for the full structure.

## Step 1 — Confirm the build and compose a readable report name

Before writing anything, confirm **which build this report is for** and build a plain-language file name from it. Do not reuse the technical device hash in the name.

1. Gather the four naming parts from what the session already knows (Phase 1 `.env` + the user's platform/environment choice):
   - **App** — a short display name, not the package. Propose one from the package/bundle ID (e.g. `com.portonics.mygp.debug` → `MyGP`) and **ask the user to confirm or correct it**.
   - **Version** — the installed build/app version from `.env` (e.g. `6.0.1`), without the environment suffix.
   - **Environment** — in title case: `stage` → `Staging`, `prod` → `Production`, `dev` → `Dev`.
   - **Platform** — `Android` or `iOS` (this report's device).
2. Show the proposed name and let the user adjust it:
   - `AID Validation Report - <App> <Version> <Environment> (<Platform>) - <YYYY-MM-DD>.docx`
   - Example: `AID Validation Report - MyGP 6.0.1 Staging (Android) - 2026-11-10.docx`
3. **STOP and wait** for the user to confirm the name before writing the report.

The confirmed base name (without extension) is used for **both** the Markdown source and the rendered `.docx`, written side by side in the evidence build folder:

```
reports/aid-validation/<build>/AID Validation Report - <App> <Version> <Environment> (<Platform>) - <date>.md   ← editable source
reports/aid-validation/<build>/AID Validation Report - <App> <Version> <Environment> (<Platform>) - <date>.docx  ← the deliverable
```

(`<build>` stays the technical build-string folder, e.g. `6.0.1-stage`, so the Phase 6 evidence and relative image paths keep resolving.)

The report is **visual-first**: the screen imagery and the per-screen AID inventory carry the findings; the tables back them up. Every image embedded here is produced in Phase 6 by `annotate_aids.py` — do not hand-draw or hand-list. Link all images with **relative paths** so the report opens correctly from the reports folder.

## Each per-device report includes

1. **Summary** — platform, device name & model, OS version, app ID, installed build, environment, login state, date, and totals per result type (Found / Mismatch / Wrong attribute / Duplicate / Missing / Not checked). Include:
   - a **Coverage** line that proves nothing was dropped: `Coverage: N/N proposed AIDs checked` (the proposed-AID count comes from the Phase 3 doc; it must equal the result-table rows). If any were Not checked, say so and why.
   - the short **colour legend** (green Found, orange Mismatch, amber Wrong attribute, purple Duplicate, red Missing, grey Not checked; blue = all-AID overlay).
2. **Per screen (in Phase 2 order)** — one block per screen validated on this device:
   - Embed the **callout figure** `screen-<N>-callout.png` — the numbered screenshot with the AID names listed beside it (no pixel bounds). This is the business-readable map of every accessibility ID against where it sits on the screen; it replaces a coordinates table in the report body.
   - One line stating the unique-AID count and pointing engineers to `screen-<N>-aids.csv` for element type + bounds. Do **not** paste the bounds table into the report — coordinates are not meaningful to business readers. (`screen-<N>-aids.md` remains available if a text table is specifically wanted.) Note that instances of a documented `{children[]}` array pattern are expected, not undocumented.
3. **Issues** — one entry per AID that is **not Found**, plus an entry per dynamic pattern to show it validated:
   - Element name (exactly as in the proposed doc), screen (Phase 2 number), proposed AID **as the full pattern from the doc**, actual value(s) found (or "none"), result type, short dev note.
   - **Side-by-side images**: the **Figma** highlight, and the **focused live highlight** `screen-<N>-issue-*.png` (colour-coded; all occurrences boxed for a Duplicate; all instances boxed for an array pattern).
4. **Documentation issues** from Phase 3 (naming problems; highlighted Figma elements with no proposed AID; AIDs the app exposes that are genuinely not in the proposed doc — exclude matched `{children[]}` instances).
5. **Full results table** — every proposed AID with the **full pattern**, its result, and the live value(s). One row per proposed AID: this table is the coverage proof.
6. **Not checked** and **Not in scope for this device** lists, with reasons.

## Render the .docx deliverable (always — this is the output the user receives)

The deliverable the user wants is the **Word document**, not the raw evidence. The per-screen PNGs (annotated/callout screenshots) and the XML (page source) from Phase 6 are **internal evidence that get embedded into / referenced by the report** — they are never handed over as the output on their own. Keep the Markdown as the editable source of truth, then always render it to `.docx`.

### Default renderer — the bundled `md2docx.py` (no pandoc, no network)

Render with the bundled `assets/md2docx.py` helper. It uses `python-docx` only (no pandoc, no large download — so it works on locked-down machines where a pandoc install fails), embeds the screenshots, and is not affected by pandoc's old-version table bug. Run it **from inside the evidence build folder** so the relative image paths resolve; the names have spaces, so **quote them**:

```bash
cd "reports/aid-validation/<build>"
python3 "$OLDPWD/.claude/skills/aid-validation-report/assets/md2docx.py" \
  "AID Validation Report - <App> <Version> <Environment> (<Platform>) - <date>.md" \
  "AID Validation Report - <App> <Version> <Environment> (<Platform>) - <date>.docx"
# (use the absolute path to md2docx.py from the project root — $OLDPWD points there if you cd'd in from it)
```

It prints `WROTE <file>` and `EMBEDDED_IMAGES <n>`; confirm `n` equals the number of images in the Markdown. If `python-docx` is missing, install it (tiny, pure-Python): `pip3 install python-docx`.

### Optional higher-fidelity fallback — pandoc

Only if the user explicitly wants pandoc (e.g. for richer Markdown features), and it is installed, render from the same folder:

```bash
cd "reports/aid-validation/<build>"
pandoc "AID Validation Report - <App> <Version> <Environment> (<Platform>) - <date>.md" \
  -o   "AID Validation Report - <App> <Version> <Environment> (<Platform>) - <date>.docx"
```

- **Install only if asked.** Per the orchestrator's "Ask before installing" rule, do not install pandoc silently. (`brew install pandoc` on macOS; note Homebrew bottle downloads may fail on restricted networks — the default `md2docx.py` path avoids this entirely.)
- **Pandoc version caveat.** Pandoc < 2.11 writes a malformed table width (`w:w="0.0"`) that collapses every table to its first column in Word/LibreOffice. Use 2.11+, and after rendering sanity-check that the Summary/Totals tables show their value columns.
- **PDF:** add a PDF engine (weasyprint / wkhtmltopdf) and `--pdf-engine=weasyprint -o "<same base name>.pdf"`.

### Image widths

Tall phone screenshots are large, so in the Markdown give each embedded image an explicit width for print, e.g. `![alt](path){width=2.4in}` (annotated full-screen) and `{width=2.6in}` (side-by-side issue cells), so a screen fits on a page — both renderers honour `{width=Xin}`. Deliver the rendered `.docx` and keep the `.md` beside it.

## If both platforms were validated
Produce one `.docx` per device (each with its own `(Android)` / `(iOS)` name), **and** a short combined summary rendered to `.docx` too: `AID Validation Summary - <App> <Version> <Environment> - <date>.docx` (Markdown source beside it), with one totals + coverage row per device and links to the two device reports. **Do not merge the issue lists.**

## Final silent self-check (before handing back)

Apply `superpowers:verification-before-completion` — confirm all of this silently before claiming the report is done:
- Only the selected platform(s)/device(s) were checked, and each report covers exactly one device.
- **Coverage holds:** every proposed AID from the Phase 3 doc has exactly one result row; the Coverage line's N/N matches the table.
- Every **Found** is backed by the saved page source; every **Missing** was checked after scrolling; array-pattern instances are grouped, not flagged as duplicates/undocumented.
- Every screen block embeds its `-annotated.png` and its `-aids.md` inventory, and every image path resolves (relative to the report file). The **.docx** rendered successfully via `md2docx.py` and its `EMBEDDED_IMAGES` count equals the number of images in the Markdown (verify the .docx, not just the .md).
- Every issue has the element name from the proposed doc, the screen number, and **both** images (Figma + focused live).
- The report name was confirmed with the user and reads in plain language (`AID Validation Report - <App> <Version> <Environment> (<Platform>) - <date>`), with no leftover device hash.
- No secrets appear in the report or the chat.

Finish by telling the user the **.docx** report path(s) (the deliverable), the coverage (N/N), and the totals for each device. The PNG/XML evidence stays in the build folder as backup — do not present it as the output. **Do not paste the whole report into the chat.**
