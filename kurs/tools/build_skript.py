"""Baut aus encor-1.4.10/wissen/*.md + bilder/*.svg ein einzelnes HTML-Lernskript."""
import html, re, sys, pathlib, datetime

ROOT = pathlib.Path(sys.argv[1])          # .../encor-1.4.10
OUT = pathlib.Path(sys.argv[2])           # Ziel-HTML
WISSEN = ROOT / "wissen"
BILDER = ROOT / "bilder"
LEGACY = {"15", "16", "17", "18", "27", "28"}

def inline(t):
    codes = []
    def keep(m):
        codes.append("<code>" + html.escape(m.group(1)) + "</code>")
        return f"\x00{len(codes)-1}\x00"
    t = re.sub(r"`([^`]+)`", keep, t)
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\*\w])\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<em>\1</em>", t)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"(?<![\"'>=])(https?://[^\s<)]+)", r'<a href="\1">\1</a>', t)
    t = re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], t)
    return t

def slug(s, used):
    b = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "abschnitt"
    s2, i = b, 2
    while s2 in used:
        s2, i = f"{b}-{i}", i + 1
    used.add(s2)
    return s2

def svg_inline(path):
    t = path.read_text(encoding="utf-8")
    t = re.sub(r"<\?xml[^>]*\?>", "", t).strip()
    t = re.sub(r"<svg\b", '<svg class="lernbild"', t, count=1)
    return t

def md_to_html(md, chapter, toc, used):
    lines = md.replace("\r\n", "\n").split("\n")
    out, i, n = [], 0, len(lines)
    in_bilder = False
    list_stack = []          # [(indent, tag)]

    def close_lists(to_indent=-1):
        while list_stack and list_stack[-1][0] > to_indent:
            out.append(f"</li></{list_stack.pop()[1]}>")

    while i < n:
        line = lines[i]
        s = line.strip()
        # Code-Block
        if s.startswith("```"):
            close_lists()
            buf = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i]); i += 1
            out.append("<pre><code>" + html.escape("\n".join(buf)) + "</code></pre>")
            i += 1; continue
        # Überschrift
        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            close_lists()
            lvl, text = len(m.group(1)), m.group(2).strip()
            if lvl == 1:
                num, rest = chapter
                title = f"Kapitel {num}: {text}"
                sid = slug(title, used)
                badge = ' <span class="legacy">Wireless – nicht mehr in ENCOR v1.2</span>' if num in LEGACY else ""
                out.append(f'<h1 id="{sid}" class="kapitel">{inline(title)}{badge}</h1>')
                toc.append((1, title, sid))
            else:
                hl = min(lvl, 4)
                sid = slug(f"{chapter[0]}-{text}", used)
                out.append(f'<h{hl} id="{sid}">{inline(text)}</h{hl}>')
                if lvl == 2:
                    toc.append((2, text, sid))
            in_bilder = (lvl == 2 and text.lower().startswith("bilder"))
            i += 1; continue
        # Bilder-Abschnitt: SVGs einbetten
        if in_bilder:
            mm = re.search(r"(?:bilder/([\w\-]+)/)?([\w\-]+\.svg)", s)
            if mm and s.lstrip().startswith(("-", "*")):
                p = BILDER / (mm.group(1) or chapter[1]) / mm.group(2)
                cap = re.sub(r"^[-*]\s*`?[^`]*\.svg`?\s*[–\-:]*\s*", "", s)
                if p.exists():
                    EMBEDDED.add(p.resolve())
                    out.append('<figure>' + svg_inline(p) + f'<figcaption>{inline(cap)}</figcaption></figure>')
                    i += 1; continue
            if s.startswith("Ordner"):
                i += 1; continue
        # Tabelle
        if s.startswith("|") and i + 1 < n and re.match(r"^\|?\s*:?-{2,}", lines[i+1].strip()):
            close_lists()
            def cells(r):
                r = r.strip().strip("|")
                return [c.strip() for c in re.split(r"(?<!\\)\|", r)]
            head = cells(s); i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append(cells(lines[i])); i += 1
            t = ["<table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>"]
            for r in rows:
                t.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            out.append("".join(t) + "</tbody></table>")
            continue
        # Liste
        m = re.match(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$", line)
        if m:
            ind = len(m.group(1).replace("\t", "    "))
            tag = "ol" if m.group(2)[0].isdigit() else "ul"
            if not list_stack or ind > list_stack[-1][0]:
                out.append(f"<{tag}><li>")
                list_stack.append((ind, tag))
            else:
                close_lists(ind)
                if list_stack and list_stack[-1][0] == ind:
                    out.append("</li><li>")
                else:
                    out.append(f"<{tag}><li>"); list_stack.append((ind, tag))
            out.append(inline(m.group(3)))
            i += 1; continue
        if s == "":
            # Leerzeile beendet Liste nur, wenn danach kein Listenelement folgt
            j = i + 1
            while j < n and lines[j].strip() == "":
                j += 1
            if not (j < n and re.match(r"^\s*([-*+]|\d+[.)])\s+", lines[j])):
                close_lists()
            i += 1; continue
        if list_stack and line.startswith(" "):
            out.append(" " + inline(s)); i += 1; continue
        close_lists()
        if s.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip()[1:].strip()); i += 1
            out.append("<blockquote>" + inline(" ".join(buf)) + "</blockquote>")
            continue
        if re.match(r"^(-{3,}|\*{3,})$", s):
            out.append("<hr>"); i += 1; continue
        buf = [s]; i += 1
        while i < n and lines[i].strip() and not re.match(r"^(#|```|\||\s*([-*+]|\d+[.)])\s|>)", lines[i].strip()):
            buf.append(lines[i].strip()); i += 1
        out.append("<p>" + inline(" ".join(buf)) + "</p>")
    close_lists()
    return "\n".join(out)

files = sorted(WISSEN.glob("*.md"))
toc, used, body = [], set(), []
EMBEDDED = set()
for f in files:
    num = f.stem.split("-")[0]
    part = md_to_html(f.read_text(encoding="utf-8"), (num, f.stem), toc, used)
    rest = [p for p in sorted((BILDER / f.stem).glob("*.svg")) if p.resolve() not in EMBEDDED]
    for p in rest:
        t = re.search(r"<title>(.*?)</title>", p.read_text(encoding="utf-8"), re.S)
        cap = html.escape(t.group(1).strip()) if t else p.stem
        part += '<figure>' + svg_inline(p) + f'<figcaption>{cap}</figcaption></figure>'
        EMBEDDED.add(p.resolve())
    body.append('<section class="chapter">' + part + "</section>")

toc_html = ["<nav class='toc'><h1>Inhalt</h1><ol>"]
open_sub = False
for lvl, title, sid in toc:
    if lvl == 1:
        if open_sub: toc_html.append("</ol></li>"); open_sub = False
        toc_html.append(f'<li><a href="#{sid}">{inline(title)}</a><ol>'); open_sub = True
    else:
        toc_html.append(f'<li><a href="#{sid}">{inline(title)}</a></li>')
if open_sub: toc_html.append("</ol></li>")
toc_html.append("</ol></nav>")

css = """
@page { size: A4; margin: 16mm 14mm 18mm 14mm; }
body { font-family: 'Segoe UI', Arial, sans-serif; font-size: 10.5pt; line-height: 1.45; color: #222; max-width: 190mm; margin: 0 auto; }
h1.kapitel { page-break-before: always; font-size: 20pt; color: #1b4f8a; border-bottom: 3px solid #4a9cff; padding-bottom: 4px; }
h2 { font-size: 14pt; color: #1b4f8a; margin-top: 18pt; border-bottom: 1px solid #cfe0f5; }
h3 { font-size: 12pt; color: #333; } h4 { font-size: 11pt; }
.legacy { font-size: 9pt; background: #fff3cd; color: #7a5a00; padding: 2px 6px; border-radius: 4px; vertical-align: middle; }
table { border-collapse: collapse; width: 100%; margin: 8pt 0; font-size: 9.5pt; page-break-inside: auto; }
th, td { border: 1px solid #c9d3de; padding: 3px 6px; vertical-align: top; text-align: left; }
th { background: #eaf2fc; } tr { page-break-inside: avoid; }
pre { background: #f4f6f8; border: 1px solid #dde3e9; padding: 6px 8px; font-size: 8.8pt; white-space: pre-wrap; word-break: break-word; page-break-inside: avoid; }
code { font-family: Consolas, 'Courier New', monospace; background: #f1f3f5; padding: 0 2px; font-size: 92%; }
pre code { background: none; padding: 0; }
blockquote { border-left: 4px solid #ffd23f; background: #fffbea; margin: 8pt 0; padding: 4px 10px; }
figure { margin: 10pt 0; page-break-inside: avoid; text-align: center; }
svg.lernbild { width: 100%; height: auto; max-height: 120mm; border: 1px solid #e3e8ee; }
figcaption { font-size: 9pt; color: #555; margin-top: 3px; }
.titel { text-align: center; padding-top: 70mm; page-break-after: always; }
.titel h1 { font-size: 30pt; color: #1b4f8a; border: none; }
.toc ol { padding-left: 18px; } .toc > ol > li { margin-top: 4px; font-weight: 600; } .toc ol ol { font-weight: normal; font-size: 9.5pt; }
.toc { page-break-after: always; } a { color: #1b4f8a; text-decoration: none; }
"""
datum = datetime.date.today().strftime("%d.%m.%Y")
titel = f"""<div class="titel"><h1>ENCOR 350-401 – Lernskript</h1>
<p style="font-size:14pt">Wissensbasis zu „Implementing and Operating Cisco Enterprise Network Core Technologies“ (Kurs 1.4.10)</p>
<p>32 Kapitel · {sum(1 for _ in BILDER.rglob('*.svg'))} Lernbilder · Stand {datum}</p>
<p style="font-size:9pt;color:#666;max-width:140mm;margin:40mm auto 0">Eigene Zusammenfassungen und eigene Zeichnungen, fachlich gegen Cisco-Dokumentation und RFCs geprüft.
Wireless-Kapitel sind markiert, da sie im aktuellen Blueprint v1.2 nicht mehr geprüft werden. Nur zum persönlichen Lernen.</p></div>"""
doc = f"""<!DOCTYPE html><html lang="de"><head><meta charset="utf-8"><title>ENCOR 350-401 – Lernskript</title><style>{css}</style></head>
<body>{titel}{''.join(toc_html)}{''.join(body)}</body></html>"""
OUT.write_text(doc, encoding="utf-8")
print(f"OK: {OUT} ({OUT.stat().st_size//1024} KB), Kapitel {len(files)}, TOC-Einträge {len(toc)}")
