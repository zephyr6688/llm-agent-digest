#!/usr/bin/env python3
"""周报草稿 / 收件箱生成。

用法：
  python3 pipeline/report.py            # 刷新 content/inbox.md（高分待选题清单）
  python3 pipeline/report.py --weekly   # 生成本周周报草稿 content/weekly/wYYYY-WW.md
  python3 pipeline/report.py --weekly --force   # 覆盖已存在草稿
"""
import argparse
import datetime
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import db

ROOT = pathlib.Path(__file__).resolve().parent.parent
WEEKLY_DIR = ROOT / "content" / "weekly"
INBOX = ROOT / "content" / "inbox.md"

FOOTER = """---

*《Agent 工程周报》· 每周一发布 · 面向动手做 Agent 的人*
*选题池来自 40+ 海外一手信源，经相关度初筛与独占性人工判断后精选。*"""


def pick_items(conn, days, min_score, top):
    cutoff = (datetime.datetime.now(datetime.timezone.utc)
              - datetime.timedelta(days=days)).isoformat()
    rows = conn.execute(
        "SELECT * FROM items WHERE score >= ? "
        "AND COALESCE(published, fetched_at) >= ? "
        "AND (status IS NULL OR status IN ('new','scored','selected')) "
        "ORDER BY score DESC, COALESCE(published, fetched_at) DESC LIMIT ?",
        (min_score, cutoff, top),
    ).fetchall()
    return rows


def render_item(r, idx):
    summary = (r["summary"] or "").replace("\n", " ").strip()
    if not summary:
        summary = "（RSS 未提供摘要，点开原文补写）"
    pub = ""
    if r["published"]:
        m = re.match(r"(\d{4}-\d{2}-\d{2})", r["published"])
        if m:
            pub = f" · {m.group(1)}"
    return (
        f"- **[{r['title']}]({r['url'] or '#'})** · {r['source']}{pub} · "
        f"相关度 {r['score']:.0f}/10\n"
        f"  - 摘要：{summary}\n"
        f"  - 点评：<!-- TODO 人工一句话点评（为什么值得看） -->\n"
    )


def gen_weekly(conn, args):
    now = datetime.datetime.now(datetime.timezone.utc)
    iso = now.isocalendar()
    week_tag = f"w{iso[0]}-{iso[1]:02d}"
    out = WEEKLY_DIR / f"{week_tag}.md"
    if out.exists() and not args.force:
        print(f"exists (use --force to overwrite): {out}")
        return out
    WEEKLY_DIR.mkdir(parents=True, exist_ok=True)
    existing = sorted(WEEKLY_DIR.glob("w*.md"))
    issue_no = len(existing) + (0 if out.exists() else 1)

    rows = pick_items(conn, args.days, args.min_score, args.top)
    date_range = f"{iso[0]} 年第 {iso[1]} 周"
    lines = [
        f"# Agent 工程周报 · 第 {issue_no} 期（{date_range}）\n",
        f"> 本期速览：{len(rows)} 条精选（近 {args.days} 天，相关度 ≥ {args.min_score}）。",
        "> <!-- TODO 导读：3-5 句，本周期整体趋势 / 值得注意的一件事 -->\n",
        "---\n",
    ]
    for i, r in enumerate(rows, 1):
        lines.append(render_item(r, i))
    lines.append(FOOTER)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"weekly draft -> {out} ({len(rows)} items)")
    return out


def gen_inbox(conn, args):
    rows = pick_items(conn, args.days, args.min_score, 50)
    lines = [
        "# 选题收件箱（自动生成，勿手编）\n",
        f"> 近 {args.days} 天相关度 ≥ {args.min_score} 的待选题，按分数排序。"
        "选题后把对应条目状态改为 selected。\n",
    ]
    for r in rows:
        m = re.match(r"(\d{4}-\d{2}-\d{2})", r["published"] or "")
        pub = m.group(1) if m else r["fetched_at"][:10]
        lines.append(
            f"- {r['score']:.0f} | {pub} | {r['source']} | "
            f"[{r['title']}]({r['url'] or '#'}) | {r['score_reason'] or ''}"
        )
    INBOX.parent.mkdir(parents=True, exist_ok=True)
    INBOX.write_text("\n".join(lines), encoding="utf-8")
    print(f"inbox -> {INBOX} ({len(rows)} items)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--weekly", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--min-score", type=float, default=6)
    args = ap.parse_args()
    conn = db.connect()
    if args.weekly:
        gen_weekly(conn, args)
    else:
        gen_inbox(conn, args)


if __name__ == "__main__":
    main()
