#!/usr/bin/env python3
"""Render an AID-validation Markdown report to .docx with python-docx.

Self-contained: no pandoc, no network, no large dependency (only python-docx,
`pip install python-docx` if missing). Use this as the default renderer for the
Phase-7 report; pandoc is an optional higher-fidelity fallback.

Usage:
    python3 md2docx.py <report.md> <output.docx>

Run it from inside the report's folder (or pass absolute paths) so the relative
image paths in the Markdown resolve. Handles: #/##/### headings, > blockquotes,
pipe tables (including image + inline cells and <br>), standalone images with
{width=Xin}, `-` and `N.` lists, `---` rules, and inline **bold** `code`
*italic* ![img](src){..} [text](url). Missing images are flagged inline rather
than aborting the render.
"""
import os, re, sys
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

if len(sys.argv) != 3:
    sys.exit("usage: md2docx.py <report.md> <output.docx>")

md_path, out_path = sys.argv[1], sys.argv[2]
base = os.path.dirname(os.path.abspath(md_path))

doc = Document()
doc.styles['Normal'].font.name = 'Calibri'
doc.styles['Normal'].font.size = Pt(10)

IMG_RE = re.compile(r'!\[(?P<alt>[^\]]*)\]\((?P<src>[^)]+)\)(?:\{width=(?P<w>[0-9.]+)in\})?')
LINK_RE = re.compile(r'\[(?P<txt>[^\]]+)\]\((?P<url>[^)]+)\)')
TOKEN_RE = re.compile(r'(\*\*.+?\*\*|`[^`]+`|\*[^*]+\*)')


def resolve(src):
    return os.path.join(base, src)


def add_image(container_para, src, width_in):
    p = resolve(src)
    run = container_para.add_run()
    if os.path.exists(p):
        try:
            run.add_picture(p, width=Inches(width_in if width_in else 3.0))
            return
        except Exception as e:
            run.text = f'[image error: {src}: {e}]'
    else:
        run.text = f'[missing image: {src}]'


def add_inline(paragraph, text):
    text = LINK_RE.sub(lambda m: m.group('txt'), text)
    pos = 0
    for m in TOKEN_RE.finditer(text):
        if m.start() > pos:
            paragraph.add_run(text[pos:m.start()])
        tok = m.group(0)
        if tok.startswith('**'):
            r = paragraph.add_run(tok[2:-2]); r.bold = True
        elif tok.startswith('`'):
            r = paragraph.add_run(tok[1:-1]); r.font.name = 'Consolas'; r.font.size = Pt(9)
        elif tok.startswith('*'):
            r = paragraph.add_run(tok[1:-1]); r.italic = True
        pos = m.end()
    if pos < len(text):
        paragraph.add_run(text[pos:])


def cell_content(cell, text):
    cell.paragraphs[0].text = ''
    para = cell.paragraphs[0]
    first = True
    for seg in text.split('<br>'):
        if not first:
            para = cell.add_paragraph()
        first = False
        seg = seg.strip()
        img = IMG_RE.search(seg)
        if img:
            before = seg[:img.start()].strip()
            if before:
                add_inline(para, before); para = cell.add_paragraph()
            w = float(img.group('w')) if img.group('w') else 3.0
            add_image(para, img.group('src'), w)
            after = seg[img.end():].strip()
            if after:
                para = cell.add_paragraph(); add_inline(para, after)
        else:
            add_inline(para, seg)


lines = open(md_path, encoding='utf-8').read().split('\n')
i = 0
while i < len(lines):
    line = lines[i]
    stripped = line.strip()

    if stripped.startswith('|') and i + 1 < len(lines) and re.match(r'^\s*\|[:\-\s|]+\|\s*$', lines[i + 1]):
        header = [c.strip() for c in stripped.strip('|').split('|')]
        i += 2
        rows = []
        while i < len(lines) and lines[i].strip().startswith('|'):
            rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')])
            i += 1
        table = doc.add_table(rows=1, cols=len(header))
        table.style = 'Table Grid'
        for j, h in enumerate(header):
            c = table.rows[0].cells[j]
            cell_content(c, h)
            for r in c.paragraphs:
                for run in r.runs:
                    run.bold = True
        for row in rows:
            cells = table.add_row().cells
            for j in range(len(header)):
                cell_content(cells[j], row[j] if j < len(row) else '')
        doc.add_paragraph()
        continue

    if stripped in ('', '---'):
        i += 1; continue

    if stripped.startswith('### '):
        doc.add_heading(stripped[4:], level=3)
    elif stripped.startswith('## '):
        doc.add_heading(stripped[3:], level=2)
    elif stripped.startswith('# '):
        doc.add_heading(stripped[2:], level=1)
    elif stripped.startswith('> '):
        p = doc.add_paragraph(); p.paragraph_format.left_indent = Inches(0.3)
        r = p.add_run(stripped[2:]); r.italic = True; r.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
    elif stripped.startswith('![') and IMG_RE.search(stripped):
        m = IMG_RE.search(stripped)
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        w = float(m.group('w')) if m.group('w') else 3.0
        add_image(p, m.group('src'), w)
    elif re.match(r'^\s*-\s+', line):
        indent = len(line) - len(line.lstrip())
        p = doc.add_paragraph(style='List Bullet')
        if indent >= 2:
            p.paragraph_format.left_indent = Inches(0.5)
        add_inline(p, re.sub(r'^\s*-\s+', '', line))
    elif re.match(r'^\s*\d+\.\s+', line):
        p = doc.add_paragraph(style='List Number')
        p.paragraph_format.left_indent = Inches(0.5)
        add_inline(p, re.sub(r'^\s*\d+\.\s+', '', line))
    else:
        add_inline(doc.add_paragraph(), stripped)
    i += 1

doc.save(out_path)
print('WROTE', out_path)
_imgs = [r for r in Document(out_path).part.rels.values() if 'image' in r.reltype]
print('EMBEDDED_IMAGES', len(_imgs))
