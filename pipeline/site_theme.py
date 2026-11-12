"""知识库站点主题：终端/IDE 风格 HTML 模板（GitHub Pages docs/ 用）。

设计要点：
- 深蓝黑基底 + 语法高亮语义色（链接青、高分绿、中分琥珀、注释暗绿）；
- 终端窗口 chrome 作为页面骨架，hero 是一段可读的终端会话；
- 等宽字体承担 UI 层（提示符/标签/徽章/日期），正文用系统无衬线保证中文可读；
- 窄屏优先；动效仅一处闪烁光标并尊重 prefers-reduced-motion。
"""
import html


def _esc(s: str) -> str:
    return html.escape(str(s or ""), quote=True)


FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
           "viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' "
           "fill='%230a0f16'/%3E%3Cpath d='M7 11l7 5-7 5' stroke='%2356c8f2' "
           "stroke-width='2.6' fill='none' stroke-linecap='round' "
           "stroke-linejoin='round'/%3E%3Cpath d='M16 22h9' stroke='%235ee08a' "
           "stroke-width='2.6' stroke-linecap='round'/%3E%3C/svg%3E")

CSS = """
:root{
  --bg:#0a0f16; --surface:#0f1621; --surface2:#141e2b; --line:#1e2c3d;
  --ink:#d8e3f0; --muted:#768aa1;
  --cyan:#56c8f2; --green:#5ee08a; --amber:#e2b45f; --note:#3f8f63;
  --mono:ui-monospace,'SF Mono','JetBrains Mono',Menlo,Consolas,monospace;
  --sans:-apple-system,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{
  margin:0;padding:0 14px 64px;
  background:var(--bg) ;
  background-image:
    linear-gradient(rgba(86,200,242,.035) 1px,transparent 1px),
    linear-gradient(90deg,rgba(86,200,242,.035) 1px,transparent 1px);
  background-size:34px 34px;
  color:var(--ink);font-family:var(--sans);font-size:15.5px;line-height:1.75;
}
a{color:var(--cyan);text-decoration:none}
a:hover{text-decoration:underline}
.term{
  max-width:860px;margin:28px auto 0;
  background:var(--surface);
  border:1px solid var(--line);border-radius:10px;overflow:hidden;
  box-shadow:0 18px 50px rgba(2,6,12,.55);
}
.bar{
  display:flex;align-items:center;gap:8px;
  padding:9px 14px;background:var(--surface2);
  border-bottom:1px solid var(--line);
}
.dot{width:11px;height:11px;border-radius:50%;flex:none}
.d1{background:#e0656a}.d2{background:#e2b45f}.d3{background:#5ee08a}
.bar .path{
  font-family:var(--mono);font-size:12.5px;color:var(--muted);
  margin-left:6px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;
}
.shell{padding:22px 20px 26px}
@media (min-width:768px){.shell{padding:30px 36px 36px}}
.prompt{font-family:var(--mono);font-size:13.5px;margin:0 0 4px;color:var(--muted)}
.prompt .u{color:var(--green)}
.prompt .cwd{color:var(--cyan)}
.prompt .cmd{color:var(--ink)}
.out{margin:2px 0 18px;color:var(--ink)}
.cursor{
  display:inline-block;width:9px;height:17px;vertical-align:-3px;
  background:var(--cyan);
}
@media (prefers-reduced-motion:no-preference){
  .cursor{animation:blink 1.1s steps(1) infinite}
  @keyframes blink{50%{opacity:0}}
}
h1.site{
  font-family:var(--mono);font-size:26px;letter-spacing:.5px;
  margin:14px 0 6px;color:var(--ink);font-weight:700;
}
h1.site .g{color:var(--green)}
.tagline{color:var(--muted);margin:0 0 26px;max-width:64ch}
.kicker{font-family:var(--mono);font-size:12.5px;color:var(--cyan);
  margin:26px 0 10px}
h2.sec{font-family:var(--mono);font-size:15px;color:var(--muted);
  margin:26px 0 12px;font-weight:500;border-bottom:1px dashed var(--line);
  padding-bottom:8px}
/* 期次列表 */
.issue{
  display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 14px;
  font-family:var(--mono);font-size:13.5px;
  padding:11px 12px;margin:0 0 8px;border:1px solid var(--line);
  border-radius:6px;background:var(--surface2);
  transition:border-color .15s;
}
.issue:hover{border-color:var(--cyan);text-decoration:none}
.issue .id{color:var(--green);flex:none}
.issue .t{color:var(--ink);flex:1 1 auto;min-width:0;overflow:hidden;
  text-overflow:ellipsis;white-space:nowrap;font-family:var(--sans);font-size:14px}
.issue .n{color:var(--muted);flex:none}
/* 条目卡片 */
.entry{
  border:1px solid var(--line);border-radius:8px;
  background:var(--surface2);padding:16px 18px;margin:0 0 14px;
}
.entry:hover{border-color:#2b4258}
.ehead{display:flex;flex-wrap:wrap;align-items:center;gap:6px 12px;
  font-family:var(--mono);font-size:12.5px;margin:0 0 8px}
.src{color:var(--muted)}
.src::before{content:"[";color:var(--line)}
.src::after{content:"]";color:var(--line)}
.date{color:var(--muted)}
.score{padding:1px 8px;border-radius:4px;font-weight:600}
.s-hi{color:#0a0f16;background:var(--green)}
.s-mid{color:#0a0f16;background:var(--amber)}
.s-lo{color:var(--ink);background:#2a3a4d}
.entry h3{margin:0 0 8px;font-size:16.5px;line-height:1.5;font-weight:600}
.entry h3 a{color:var(--ink)}
.entry h3 a:hover{color:var(--cyan)}
.entry p{margin:0 0 10px;color:#b3c2d4;font-size:14.5px}
.note{
  font-family:var(--mono);font-size:13px;color:var(--note);
  background:rgba(94,224,138,.05);border-left:2px solid var(--note);
  padding:8px 12px;margin:0;border-radius:0 6px 6px 0;
}
.foot{
  margin-top:30px;padding-top:18px;border-top:1px dashed var(--line);
  color:var(--muted);font-size:13px;
}
.foot .fr{font-family:var(--mono);font-size:12px;color:var(--note)}
.back{font-family:var(--mono);font-size:13px;margin:22px 0 0;display:inline-block}
"""

_HEAD_TMPL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<link rel="icon" href="{fav}">
<title>{title}</title>
<style>{css}</style>
</head>
<body>
"""

_TERM_OPEN = """<div class="term" aria-label="content window">
<div class="bar"><span class="dot d1"></span><span class="dot d2"></span><span class="dot d3"></span><span class="path">{path}</span></div>
<div class="shell">
"""


def _page(title: str, desc: str, path: str, body: str) -> str:
    return (_HEAD_TMPL.format(title=_esc(title), desc=_esc(desc),
                              path=_esc(path), fav=FAVICON, css=CSS)
            + _TERM_OPEN.format(path=_esc(path))
            + body
            + "</div></div>\n</body>\n</html>\n")


def _score_class(score: str) -> str:
    try:
        v = int(float(score))
    except (TypeError, ValueError):
        return "s-lo"
    return "s-hi" if v >= 8 else ("s-mid" if v >= 6 else "s-lo")


def _split_meta(meta: str):
    parts = [p.strip() for p in (meta or "").split("·")]
    if len(parts) >= 2:
        return parts[0], parts[1]
    return (parts[0] if parts else "", "")


def _entry_html(it: dict) -> str:
    src, date = _split_meta(it.get("meta"))
    comment = ""
    if it.get("comment"):
        comment = f'<p class="note">// 点评：{_esc(it["comment"])}</p>'
    return f"""<article class="entry">
<div class="ehead"><span class="src">{_esc(src)}</span><span class="date">{_esc(date)}</span><span class="score {_score_class(it.get("score"))}">{_esc(it.get("score"))}/10</span></div>
<h3><a href="{_esc(it["url"])}" rel="noopener">{_esc(it["title"])}</a></h3>
<p>{_esc(it.get("summary"))}</p>
{comment}
</article>"""


def render_index(issues: list) -> str:
    rows = []
    for iss in sorted(issues, key=lambda x: x["issue"], reverse=True):
        rows.append(
            f'<a class="issue" href="posts/{_esc(iss["issue"])}.html">'
            f'<span class="id">{_esc(iss["issue"])}</span>'
            f'<span class="t">{_esc(iss.get("title", ""))}</span>'
            f'<span class="n">{_esc(iss.get("count", 0))} 条</span></a>'
        )
    body = f"""
<p class="prompt"><span class="u">zephyr@digest</span>:<span class="cwd">~</span>$ <span class="cmd">cat ./mission.txt</span></p>
<p class="out">面向动手做 Agent 的人的一手工程情报站。<br>
采集 40+ 海外一手信源 → 相关度初筛 → 独占性人工选题 → 每周编译成报。<br>
打破语言差、时差和视角差，只发国内没有的增量内容。</p>
<h1 class="site">agent-digest<span class="g">_</span></h1>
<p class="tagline">LLM / Agent 工程内容中文编译存档，每周一更新。所有条目保留作者与原文链接。</p>
<p class="prompt"><span class="u">zephyr@digest</span>:<span class="cwd">~</span>$ <span class="cmd">ls -1 ./issues/</span></p>
{''.join(rows)}
<p class="foot"><span class="fr">// pipeline: 采集→评分→选题→编译→分发，全自动生成</span><br>
源仓库：<a href="https://github.com/zephyr6688/llm-agent-digest" rel="noopener">github.com/zephyr6688/llm-agent-digest</a> · 每周一发布 · 公众号「Agent 工程周报」<br>
zephyr@digest:~$ <span class="cursor"></span></p>
"""
    return _page("agent-digest · LLM/Agent 工程情报站",
                 "海外一手 LLM/Agent 工程内容中文编译存档，每周一更新",
                 "~/agent-digest", body)


def render_post(article: dict) -> str:
    items = "".join(_entry_html(it) for it in article.get("items", []))
    issue = article.get("issue", "")
    body = f"""
<p class="prompt"><span class="u">zephyr@digest</span>:<span class="cwd">~/issues</span>$ <span class="cmd">cat {_esc(issue)}.md</span></p>
<p class="out">{_esc(article.get("intro", ""))}</p>
<h1 class="site">{_esc(article.get("title", ""))}</h1>
<h2 class="sec">## 本期条目（{len(article.get("items", []))} 条，按相关度排序）</h2>
{items}
<p class="foot"><span class="fr">// 点评由编辑人工撰写，摘要来自原文 RSS，版权归原作者所有</span><br>
{_esc(article.get("footer", ""))}<br>
zephyr@digest:~/issues$ <span class="cursor"></span></p>
<p><a class="back" href="../index.html">&lt;- cd ..（返回总目录）</a></p>
"""
    return _page(f"{article.get('title', '周报')} · agent-digest",
                 "Agent 工程周报 · 海外一手内容中文编译",
                 f"~/issues/{issue}", body)
