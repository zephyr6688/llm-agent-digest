#!/usr/bin/env python3
"""Build offline self-contained HTML from 方案.md + rendered SVGs."""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path("/Users/zephyr/Desktop/AI/blog_reposting")
MD = ROOT / "方案.md"
DIAG = ROOT / "_diagrams"
OUT = ROOT / "方案.html"

DIAGRAM_NAMES = ["pipeline", "matrix", "roadmap"]  # in document order

md_text = MD.read_text(encoding="utf-8")

# 1. Extract mermaid blocks, replace with placeholders
blocks = []

def repl(m):
    blocks.append(m.group(1))
    return f"<!--DIAGRAM:{len(blocks) - 1}-->"

md_text = re.sub(r"```mermaid\n(.*?)```", repl, md_text, flags=re.S)
assert len(blocks) == len(DIAGRAM_NAMES), f"expected {len(DIAGRAM_NAMES)} mermaid blocks, got {len(blocks)}"

# 2. Convert markdown body to HTML fragment via marked
frag = subprocess.run(
    ["npx", "-y", "marked"],
    input=md_text, capture_output=True, text=True, check=True,
).stdout

# 3. Load, clean and id-rename SVGs
def load_svg(name: str) -> str:
    svg = (DIAG / f"{name}.svg").read_text(encoding="utf-8")
    uid = f"svg-{name}"
    svg = svg.replace("my-svg", uid)
    # make responsive within content column, drop fixed max-width
    svg = re.sub(r'style="max-width:\s*[\d.]+px;?\s*background-color:\s*white;?"',
                 'style="background-color:white"', svg)
    svg = svg.replace('width="100%"', 'width="100%"')
    return svg

for i, name in enumerate(DIAGRAM_NAMES):
    svg = load_svg(name)
    fig = f'<figure class="diagram">{svg}</figure>'
    frag = frag.replace(f"<!--DIAGRAM:{i}-->", fig)

# 4. Wrap in template
html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>打破信息差：LLM / Agent 方向博客引进与分发全流程落地方案</title>
<style>
  :root { --ink:#1c2b3a; --muted:#5b6b7b; --accent:#0f8b8d; --line:#e3e9ef; --bg:#fbfcfd; }
  * { box-sizing: border-box; }
  body {
    margin: 0; padding: 0 20px 80px;
    background: var(--bg); color: var(--ink);
    font-family: 'PingFang SC','Hiragino Sans GB','Microsoft YaHei','Noto Sans CJK SC',sans-serif;
    font-size: 16px; line-height: 1.75;
  }
  main { max-width: 940px; margin: 0 auto; }
  h1 { font-size: 1.7em; line-height: 1.35; margin: 2.2em 0 0.4em; }
  h2 { font-size: 1.32em; margin: 2.4em 0 0.6em; padding-bottom: 0.3em;
       border-bottom: 2px solid var(--accent); }
  h3 { font-size: 1.1em; margin: 1.8em 0 0.5em; }
  p { margin: 0.7em 0; }
  a { color: var(--accent); text-decoration: none; }
  a:hover { text-decoration: underline; }
  blockquote {
    margin: 1.2em 0; padding: 0.6em 1.1em; border-left: 4px solid var(--accent);
    background: #fff; border-radius: 0 8px 8px 0; color: var(--muted);
  }
  blockquote p { margin: 0.3em 0; }
  table { border-collapse: collapse; width: 100%; margin: 1.1em 0; background: #fff;
          font-size: 0.93em; }
  th, td { border: 1px solid var(--line); padding: 8px 11px; text-align: left;
           vertical-align: top; }
  th { background: #eef6f6; color: #12324d; }
  tr:nth-child(even) td { background: #f7fafb; }
  code { font-family: 'SF Mono', Menlo, Consolas, monospace; font-size: 0.88em;
         background: #eef2f5; padding: 2px 5px; border-radius: 4px; }
  pre { background: #f4f6f8; border: 1px solid var(--line); border-radius: 10px;
        padding: 14px 16px; overflow-x: auto; line-height: 1.55; }
  pre code { background: none; padding: 0; font-size: 0.85em; }
  figure.diagram {
    margin: 1.6em 0; padding: 10px; background: #fff;
    border: 1px solid var(--line); border-radius: 12px;
    overflow-x: auto;
  }
  figure.diagram svg { display: block; margin: 0 auto; height: auto; }
  hr { border: none; border-top: 1px solid var(--line); margin: 2.6em 0; }
  ul, ol { padding-left: 1.5em; }
  li { margin: 0.3em 0; }
  strong { color: #12324d; }
  @media print { body { background: #fff; } figure.diagram { break-inside: avoid; } }
  @media (max-width: 640px) {
    body { font-size: 15px; }
    table { display: block; overflow-x: auto; }
    figure.diagram svg { min-width: 620px; }
  }
</style>
</head>
<body>
<main>
""" + frag + """
</main>
</body>
</html>
"""

OUT.write_text(html, encoding="utf-8")
print(f"OK -> {OUT} ({len(html)} bytes, {len(blocks)} diagrams inlined)")
