#!/usr/bin/env python3
"""Render the report Markdown to print-ready HTML, then to PDF via headless Chrome.

Mermaid blocks are replaced with the SVGs pre-rendered by mermaid-cli, so the
diagrams appear as figures rather than as source listings.
"""
import re
import sys
import pathlib
import markdown

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parent
DIAG = HERE / "diagrams"
HTML = HERE / "html"
HTML.mkdir(exist_ok=True)

CSS = """
@page { size: A4; margin: 20mm 18mm 20mm 18mm; }
@page :first { margin-top: 24mm; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body {
  font-family: "Charter", "Georgia", "Times New Roman", serif;
  font-size: 10.5pt; line-height: 1.52; color: #14171a; margin: 0;
  hyphens: auto; text-align: justify;
}
h1, h2, h3 { font-family: "Helvetica Neue", Arial, sans-serif; color: #0b0d0f; text-align: left; }
h1 { font-size: 19pt; line-height: 1.2; margin: 0 0 1.1em; padding-bottom: .35em;
     border-bottom: 2px solid #14171a; break-after: avoid; }
h2 { font-size: 13pt; margin: 1.7em 0 .55em; break-after: avoid; }
h3 { font-size: 11pt; margin: 1.3em 0 .45em; break-after: avoid; }
p { margin: 0 0 .75em; orphans: 3; widows: 3; }
strong { font-weight: 600; }
a { color: #14171a; text-decoration: none; }

/* Tables */
table { border-collapse: collapse; width: 100%; margin: 1em 0 1.2em;
        font-size: 9.2pt; break-inside: avoid; font-family: "Helvetica Neue", Arial, sans-serif; }
thead { background: #f2f4f6; }
th, td { border: 1px solid #ccd2d8; padding: 5px 8px; text-align: left; vertical-align: top; }
th { font-weight: 600; }
tbody tr:nth-child(even) { background: #fafbfc; }

/* Code */
code { font-family: "SF Mono", "Menlo", monospace; font-size: 8.8pt;
       background: #f4f6f8; padding: 1px 4px; border-radius: 3px; }
pre { background: #f7f9fa; border: 1px solid #e2e7ec; border-left: 3px solid #8b98a5;
      padding: 9px 12px; border-radius: 3px; overflow-x: auto; break-inside: avoid;
      font-size: 8.6pt; line-height: 1.42; text-align: left; }
pre code { background: none; padding: 0; font-size: inherit; }

/* Figure / screenshot callouts */
blockquote { margin: .9em 0; padding: .6em .9em; background: #fffdf3;
             border-left: 3px solid #d9b23a; font-size: 9.4pt; break-inside: avoid;
             font-family: "Helvetica Neue", Arial, sans-serif; text-align: left; }
blockquote p { margin: 0 0 .35em; }
blockquote p:last-child { margin-bottom: 0; }

/* Rendered mermaid diagrams */
figure.diagram { margin: 1.2em 0; text-align: center; break-inside: avoid; page-break-inside: avoid; }
figure.diagram svg { max-width: 100%; height: auto; }
figure.diagram figcaption { font-size: 8.6pt; color: #5b6770; margin-top: .5em;
                            font-family: "Helvetica Neue", Arial, sans-serif; }

hr { border: none; border-top: 1px solid #dde2e7; margin: 1.6em 0; }
ul, ol { margin: 0 0 .8em; padding-left: 1.4em; }
li { margin-bottom: .22em; }
.section-break { break-before: page; }
"""

MD_EXT = ["tables", "fenced_code", "sane_lists", "attr_list", "toc", "footnotes"]

CAPTIONS = {
    "11_architecture_diagram_0": "Fig. 11.1 — Deployment and data-flow architecture. "
                                 "Solid edges are runtime paths; the dashed edge is an offline artefact dependency.",
    "11_architecture_diagram_1": "Fig. 11.2 — Sequence diagram for POST /assessment.",
    "17_database_design_0": "Fig. 17.1 — Entity–relationship diagram.",
}


def strip_svg_header(svg: str) -> str:
    svg = re.sub(r"<\?xml[^>]*\?>", "", svg)
    svg = re.sub(r"<!DOCTYPE[^>]*>", "", svg)
    return svg.strip()


def convert(md_path: pathlib.Path) -> str:
    text = md_path.read_text()

    # Swap mermaid fences for the pre-rendered SVG, in document order.
    counter = {"i": 0}

    def repl(_m):
        key = f"{md_path.stem}_{counter['i']}"
        counter["i"] += 1
        svg_file = DIAG / f"{key}.svg"
        if not svg_file.exists():
            return _m.group(0)
        svg = strip_svg_header(svg_file.read_text())
        cap = CAPTIONS.get(key, "")
        cap_html = f"<figcaption>{cap}</figcaption>" if cap else ""
        return f'\n<figure class="diagram">{svg}{cap_html}</figure>\n'

    text = re.sub(r"```mermaid\n(.*?)```", repl, text, flags=re.S)

    body = markdown.markdown(text, extensions=MD_EXT)
    return body


def page(body: str, title: str) -> str:
    return (f"<!doctype html><html><head><meta charset='utf-8'>"
            f"<title>{title}</title><style>{CSS}</style></head>"
            f"<body>{body}</body></html>")


def main():
    files = sorted(SRC.glob("*.md"))
    combined = []
    for i, f in enumerate(files):
        body = convert(f)
        (HTML / f"{f.stem}.html").write_text(page(body, f.stem))
        cls = ' class="section-break"' if i else ""
        combined.append(f"<div{cls}>{body}</div>")
        print("html:", f.stem)

    (HTML / "_full_report.html").write_text(
        page("".join(combined), "Behavioural Risk Assessment — Full Report"))
    print("html: _full_report  (%d sections)" % len(files))


if __name__ == "__main__":
    main()
