#!/usr/bin/env python3
"""
annotate_aids.py — turn an Appium page-source dump + screenshot into visual,
documented AID evidence for the aid-validation report.

For one captured screen it produces:
  1. <base>-annotated.png  — every accessibility ID on the screen boxed and
     numbered (blue), matching the style of the highlighted Figma screens.
  2. <base>-aids.md / .csv — the "Accessibility IDs identified on screen"
     inventory: number, AID value, element type, occurrences, bounds, and
     (when a checklist is given) whether the AID was expected.
  3. <base>-issue-N-<slug>.png — a focused highlight per reported AID, coloured
     by result (red=Missing, orange=Mismatch/Wrong attribute, purple=Duplicate,
     green=Found), with the rest of the screen dimmed and a caption bar.

Platform-agnostic: reads Android bounds="[x1,y1][x2,y2]" (AID = content-desc,
resource-id secondary) and iOS x/y/width/height (AID = name, label secondary).

Usage:
  python3 annotate_aids.py --screenshot screen-1.png --xml screen-1.xml \
      --out-dir . --base screen-1 [--screen 1] \
      [--issues issues.json]

issues.json (optional): [{"aid":"slide_..._bnnr","name":"Top-Bar Megabanner",
"result":"Duplicate"}, ...]  — one focused image is written per entry.
For a dynamic {children[]} pattern, give "aids":[...] (a list of the live values)
instead of "aid" and all their occurrences are boxed in one image; add "slug"
to name the output file.
"""
import argparse, csv, json, os, re, sys
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont

BOUNDS_RE = re.compile(r"\[(-?\d+),(-?\d+)\]\[(-?\d+),(-?\d+)\]")

RESULT_COLORS = {
    "found": (46, 125, 50),          # green
    "mismatch": (245, 124, 0),       # orange
    "wrong attribute": (249, 168, 37),  # amber
    "duplicate": (106, 27, 154),     # purple
    "missing": (198, 40, 40),        # red
    "not checked": (84, 110, 122),   # grey
}
OVERLAY_COLOR = (21, 101, 192)       # blue — matches the Figma highlight

# A value that looks like a proper AID (snake_case + a known UI suffix) vs a
# plain human/system label. Used only to tag rows, never to drop them.
AID_SUFFIXES = ("btn", "txt", "img", "icon", "card", "list", "bnnr", "prgrs",
                "banner", "view", "lbl", "cell", "row", "tab", "field", "input")


def load_font(size):
    for p in (
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


def slugify(s):
    s = re.sub(r"[^A-Za-z0-9]+", "-", s or "").strip("-").lower()
    return (s[:60] or "element")


def looks_like_aid(value):
    v = (value or "").strip()
    if not v or " " in v:
        return False
    return "_" in v and v.lower().endswith(AID_SUFFIXES)


def node_box(attrib):
    """Return (x1,y1,x2,y2) from Android bounds or iOS x/y/width/height."""
    b = attrib.get("bounds")
    if b:
        m = BOUNDS_RE.search(b)
        if m:
            x1, y1, x2, y2 = (int(g) for g in m.groups())
            return (x1, y1, x2, y2)
        return None
    if "x" in attrib and "width" in attrib:
        try:
            x = int(float(attrib["x"])); y = int(float(attrib["y"]))
            w = int(float(attrib["width"])); h = int(float(attrib["height"]))
            return (x, y, x + w, y + h)
        except (ValueError, KeyError):
            return None
    return None


def node_aid(attrib):
    """(aid_value, secondary_resource_id). AID = content-desc (Android) or name (iOS)."""
    aid = attrib.get("content-desc") or attrib.get("name") or ""
    rid = attrib.get("resource-id") or ""
    # strip android package prefix if present (com.x:id/foo -> foo)
    if ":id/" in rid:
        rid = rid.split(":id/", 1)[1]
    return aid.strip(), rid.strip()


def short_type(attrib, tag):
    cls = attrib.get("class") or tag or ""
    return cls.split(".")[-1]


def collect(xml_path, img_w, img_h):
    """Return ordered list of elements that carry an accessibility ID."""
    tree = ET.parse(xml_path)
    elements = []
    for el in tree.iter():
        aid, rid = node_aid(el.attrib)
        if not aid:
            continue
        box = node_box(el.attrib)
        if not box:
            continue
        x1, y1, x2, y2 = box
        # clamp to image and drop degenerate / whole-screen container boxes
        x1 = max(0, min(x1, img_w)); x2 = max(0, min(x2, img_w))
        y1 = max(0, min(y1, img_h)); y2 = max(0, min(y2, img_h))
        if x2 - x1 < 2 or y2 - y1 < 2:
            continue
        elements.append({
            "aid": aid,
            "rid": rid,
            "type": short_type(el.attrib, el.tag),
            "text": (el.attrib.get("text") or el.attrib.get("label") or "").strip(),
            "box": (x1, y1, x2, y2),
        })
    return elements


def group_by_aid(elements):
    """Collapse repeated AIDs into one inventory row with occurrence boxes."""
    order, groups = [], {}
    for e in elements:
        if e["aid"] not in groups:
            groups[e["aid"]] = {
                "aid": e["aid"], "rid": e["rid"], "type": e["type"],
                "text": e["text"], "boxes": [],
            }
            order.append(e["aid"])
        groups[e["aid"]]["boxes"].append(e["box"])
    return [groups[a] for a in order]


def draw_box(draw, box, color, width, label=None, font=None):
    x1, y1, x2, y2 = box
    # white halo for contrast on busy images, then the colour on top
    draw.rectangle([x1 - 1, y1 - 1, x2 + 1, y2 + 1], outline=(255, 255, 255), width=width + 2)
    draw.rectangle([x1, y1, x2, y2], outline=color, width=width)
    if label is not None and font is not None:
        tb = draw.textbbox((0, 0), label, font=font)
        tw, th = tb[2] - tb[0], tb[3] - tb[1]
        pad = max(4, width)
        bx1, by1 = x1, max(0, y1 - th - 2 * pad)
        draw.rectangle([bx1, by1, bx1 + tw + 2 * pad, by1 + th + 2 * pad], fill=color)
        draw.text((bx1 + pad, by1 + pad), label, fill=(255, 255, 255), font=font)


def make_overlay(img, groups, out_path):
    """All AIDs on the screen, boxed in blue and numbered -> numbers map to the inventory."""
    canvas = img.convert("RGB").copy()
    draw = ImageDraw.Draw(canvas)
    w = canvas.width
    line = max(3, w // 360)
    bfont = load_font(max(18, w // 42))
    for i, g in enumerate(groups, 1):
        for box in g["boxes"]:
            draw_box(draw, box, OVERLAY_COLOR, line)
        # numbered badge at the first occurrence's top-left
        x1, y1, _, _ = g["boxes"][0]
        num = str(i)
        tb = draw.textbbox((0, 0), num, font=bfont)
        tw, th = tb[2] - tb[0], tb[3] - tb[1]
        pad = max(5, line + 2)
        bx, by = x1, y1
        draw.rectangle([bx, by, bx + tw + 2 * pad, by + th + 2 * pad], fill=OVERLAY_COLOR)
        draw.text((bx + pad, by + pad), num, fill=(255, 255, 255), font=bfont)
    canvas.save(out_path)
    return canvas


def _wrap_chars(draw, text, font, maxw):
    """Wrap a long AID (which has no spaces) to fit a pixel width."""
    lines, cur = [], ""
    for ch in text:
        if draw.textlength(cur + ch, font=font) <= maxw:
            cur += ch
        else:
            lines.append(cur); cur = ch
    if cur:
        lines.append(cur)
    return lines or [""]


def make_callout(overlay_canvas, groups, expected, screen, out_path):
    """Business-readable figure: the numbered screenshot + a legend of number -> AID name
    beside it, so each accessibility ID is read against where it sits on the screen.
    No pixel bounds — those stay in the engineer CSV."""
    base = overlay_canvas.convert("RGB")
    sw, sh = base.size
    panel_w = max(1100, sw)
    pad = 32
    hfont = load_font(38)
    font = load_font(27)
    small = load_font(22)
    chip = 44
    text_x0 = sw + pad + chip + 16
    text_maxw = panel_w - (pad + chip + 16) - pad
    expected = {e.lower() for e in (expected or [])}

    measure = ImageDraw.Draw(base)
    rows = []
    line_h = font.size + 8
    for i, g in enumerate(groups, 1):
        lines = _wrap_chars(measure, g["aid"], font, text_maxw)
        meta = []
        if len(g["boxes"]) > 1:
            meta.append(f"appears {len(g['boxes'])}x")
        meta.append("in proposed doc" if g["aid"].lower() in expected else "not in doc")
        row_h = max(len(lines) * line_h, chip) + small.size + 16
        rows.append((i, g, lines, "  ·  ".join(meta), row_h))

    legend_h = pad + 56 + sum(r[4] for r in rows) + pad
    canvas_h = max(sh, legend_h)
    canvas = Image.new("RGB", (sw + panel_w, canvas_h), (255, 255, 255))
    canvas.paste(base, (0, 0))
    d = ImageDraw.Draw(canvas)
    x0 = sw
    d.line([(x0, 0), (x0, canvas_h)], fill=(220, 220, 220), width=2)
    d.text((x0 + pad, pad), f"Accessibility IDs — screen {screen}", font=hfont, fill=(20, 20, 20))
    y = pad + 56
    for (i, g, lines, meta, row_h) in rows:
        in_doc = g["aid"].lower() in expected
        d.rectangle([x0 + pad, y, x0 + pad + chip, y + chip], fill=OVERLAY_COLOR)
        num = str(i)
        tb = d.textbbox((0, 0), num, font=small)
        d.text((x0 + pad + (chip - (tb[2] - tb[0])) / 2, y + (chip - (tb[3] - tb[1])) / 2 - tb[1]),
               num, font=small, fill=(255, 255, 255))
        ty = y
        for ln in lines:
            d.text((text_x0, ty), ln, font=font, fill=(15, 15, 15)); ty += line_h
        d.text((text_x0, ty), meta, font=small, fill=(60, 130, 60) if in_doc else (150, 90, 70))
        y += row_h
    canvas.save(out_path)


def make_focus(img, boxes, color, caption, out_path):
    """Dim the whole screen, restore the highlighted region(s), draw a coloured box + caption."""
    base = img.convert("RGB")
    dim = Image.blend(base, Image.new("RGB", base.size, (0, 0, 0)), 0.55)
    for b in boxes:
        x1, y1, x2, y2 = b
        dim.paste(base.crop((x1, y1, x2, y2)), (x1, y1))
    draw = ImageDraw.Draw(dim)
    w = dim.width
    line = max(4, w // 240)
    for b in boxes:
        draw_box(draw, b, color, line)
    # caption bar across the top — auto-fit the font, then ellipsize if still too wide
    margin = max(10, w // 60)
    avail = w - 2 * margin
    size = max(20, w // 36)
    cfont = load_font(size)
    while size > 14 and draw.textlength(caption, font=cfont) > avail:
        size -= 2
        cfont = load_font(size)
    text = caption
    if draw.textlength(text, font=cfont) > avail:
        while text and draw.textlength(text + "…", font=cfont) > avail:
            text = text[:-1]
        text += "…"
    tb = draw.textbbox((0, 0), text, font=cfont)
    th = tb[3] - tb[1]
    barh = th + max(16, w // 40)
    draw.rectangle([0, 0, w, barh], fill=color)
    draw.text((margin, (barh - th) // 2 - tb[1]), text, fill=(255, 255, 255), font=cfont)
    dim.save(out_path)


def write_inventory(groups, base, screen, md_path, csv_path, expected=None):
    expected = {e.lower() for e in (expected or [])}
    header_note = ""
    if expected:
        header_note = " | In checklist?"
    lines = [f"#### Accessibility IDs identified on screen"
             + (f" {screen}" if screen else "") + f"  ({len(groups)} unique)", ""]
    cols = "| # | Accessibility ID (content-desc / name) | Type | Count | Bounds | resource-id / secondary"
    sep = "|:--|:--|:--|:--:|:--|:--|"
    if expected:
        cols += " | In checklist?"
        sep += ":--:|"
    else:
        sep = sep[:-1] + "|"
    lines += [cols + " |", sep]
    for i, g in enumerate(groups, 1):
        bounds = "; ".join(f"[{b[0]},{b[1]}][{b[2]},{b[3]}]" for b in g["boxes"])
        rid = g["rid"] if g["rid"] and g["rid"] != g["aid"] else ("same" if g["rid"] else "—")
        kind = "AID" if looks_like_aid(g["aid"]) else "label/system"
        row = f"| {i} | `{g['aid']}` | {g['type']} ({kind}) | {len(g['boxes'])} | {bounds} | `{rid}`"
        if expected:
            row += " | " + ("yes" if g["aid"].lower() in expected else "**no (undocumented)**")
        lines.append(row + " |")
    with open(md_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    with open(csv_path, "w", newline="") as f:
        wr = csv.writer(f)
        head = ["num", "accessibility_id", "type", "kind", "count", "bounds", "resource_id"]
        if expected:
            head.append("in_checklist")
        wr.writerow(head)
        for i, g in enumerate(groups, 1):
            bounds = "; ".join(f"[{b[0]},{b[1]}][{b[2]},{b[3]}]" for b in g["boxes"])
            kind = "AID" if looks_like_aid(g["aid"]) else "label/system"
            row = [i, g["aid"], g["type"], kind, len(g["boxes"]), bounds, g["rid"]]
            if expected:
                row.append("yes" if g["aid"].lower() in expected else "no")
            wr.writerow(row)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--screenshot", required=True)
    ap.add_argument("--xml", required=True)
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--base", help="output basename (default: screenshot stem)")
    ap.add_argument("--screen", default="", help="screen number/label for captions")
    ap.add_argument("--issues", help="JSON list of {aid,name,result} to highlight")
    ap.add_argument("--checklist", help="JSON list of expected AID strings (marks undocumented AIDs)")
    args = ap.parse_args()

    img = Image.open(args.screenshot)
    base = args.base or os.path.splitext(os.path.basename(args.screenshot))[0]
    os.makedirs(args.out_dir, exist_ok=True)

    elements = collect(args.xml, img.width, img.height)
    groups = group_by_aid(elements)
    by_aid = {g["aid"]: g for g in groups}

    expected = None
    if args.checklist and os.path.exists(args.checklist):
        expected = json.load(open(args.checklist))

    # 1. overlay (numbered boxes on the screenshot)
    overlay_path = os.path.join(args.out_dir, f"{base}-annotated.png")
    overlay_canvas = make_overlay(img, groups, overlay_path)

    # 1b. callout (business view): screenshot + legend of number -> AID name, no bounds
    callout_path = os.path.join(args.out_dir, f"{base}-callout.png")
    make_callout(overlay_canvas, groups, expected, args.screen, callout_path)

    # 2. inventory (engineer view): full table incl. bounds in CSV
    md_path = os.path.join(args.out_dir, f"{base}-aids.md")
    csv_path = os.path.join(args.out_dir, f"{base}-aids.csv")
    write_inventory(groups, base, args.screen, md_path, csv_path, expected)

    produced = [overlay_path, callout_path, md_path, csv_path]

    # 3. focused issue highlights
    if args.issues and os.path.exists(args.issues):
        issues = json.load(open(args.issues))
        for n, iss in enumerate(issues, 1):
            result = (iss.get("result") or "").strip().lower()
            color = RESULT_COLORS.get(result, OVERLAY_COLOR)
            # "aids": [...] groups a dynamic {children[]} pattern's live instances;
            # "aid": single value otherwise.
            aid_list = iss.get("aids") or ([iss["aid"]] if iss.get("aid") else [])
            boxes = []
            for a in aid_list:
                g = by_aid.get(a)
                if g:
                    boxes.extend(g["boxes"])
            name = iss.get("name") or (aid_list[0] if aid_list else "element")
            tag = aid_list[0] if len(aid_list) == 1 else f"{len(aid_list)} instances"
            cap = f"{name} — {iss.get('result','')}  [{tag}]"
            slug = iss.get("slug") or (slugify(aid_list[0]) if aid_list else "element")
            out = os.path.join(args.out_dir, f"{base}-issue-{n}-{slug}.png")
            if boxes:
                make_focus(img, boxes, color, cap, out)
            else:
                # not on screen (e.g. Missing) -> dimmed screen + caption, no box
                make_focus(img, [], color, cap + "  (not present on screen)", out)
            produced.append(out)

    print(json.dumps({
        "screen": args.screen,
        "unique_aids": len(groups),
        "total_elements": len(elements),
        "outputs": [os.path.abspath(p) for p in produced],
    }, indent=2))


if __name__ == "__main__":
    main()
