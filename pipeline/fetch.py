#!/usr/bin/env python3
"""采集入口：RSS/Atom 订阅 + Hacker News 雷达 → SQLite 选题库。

用法：
  python3 pipeline/fetch.py                 # 默认抓 P0 信源
  python3 pipeline/fetch.py --prio all      # P0+P1+P2 全量
  python3 pipeline/fetch.py --hn            # 附加 Hacker News AI 热帖
  python3 pipeline/fetch.py --limit 5       # 只试前 5 个信源（调试）

说明：单个信源失败不影响整体；无 RSS 地址的信源会自动从主页发现。
"""
import argparse
import csv
import json
import pathlib
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import db
import feeds

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCES_CSV = ROOT / "sources.csv"


def load_sources(prio: str = "P0"):
    want = set(prio.split(","))
    rows = []
    with open(SOURCES_CSV, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            p = (r.get("优先级") or "").strip()
            if "all" not in want and p not in want:
                continue
            if (r.get("类别") or "").strip() == "发现层":
                continue  # 发现层走 --hn 等专用雷达
            rows.append(r)
    return rows


def fetch_source(row, conn) -> tuple:
    name = row["名称"].strip()
    home = row["地址"].strip()
    rss = (row.get("rss") or "").strip()
    note = ""
    if rss in ("", "-"):
        rss = feeds.discover_feed(home) or ""
        note = " (auto-discovered)" if rss else " (no feed found)"
    if not rss:
        return name, 0, 0, "skip: no feed"
    try:
        data, _ = feeds.http_get(rss)
        items = feeds.parse_feed(data)
    except Exception as e:
        return name, 0, 0, f"error: {type(e).__name__}: {e}"
    new = 0
    for it in items:
        if db.upsert_item(conn, it, source=name):
            new += 1
    return name, len(items), new, f"ok{note}: {rss}"


def fetch_hn(conn, min_points=50, hours=72):
    """Hacker News 近 N 小时 AI 相关热帖（Algolia API，多查询合并去重）。"""
    since = int(time.time()) - hours * 3600
    hits = {}
    for q in ("llm", "agent", "large language model", "openai", "anthropic"):
        url = (f"https://hn.algolia.com/api/v1/search_by_date?query={urllib.parse.quote(q)}"
               f"&tags=story&numericFilters=points>{min_points},created_at_i>{since}"
               f"&hitsPerPage=30")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": feeds.UA})
            with urllib.request.urlopen(req, timeout=15) as resp:
                for h in json.loads(resp.read().decode("utf-8")).get("hits", []):
                    hits[h.get("objectID")] = h
        except Exception as e:
            print(f"  [Hacker News] query '{q}' error: {e}")
    new = 0
    for h in hits.values():
        link = h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}"
        item = {
            "guid": f"hn-{h.get('objectID')}",
            "title": h.get("title") or "(untitled)",
            "url": link,
            "summary": f"HN 热帖 · {h.get('points', 0)} points · "
                       f"{h.get('num_comments', 0)} comments",
            "published": None,
            "author": "",
        }
        if db.upsert_item(conn, item, source="Hacker News"):
            new += 1
    print(f"  [Hacker News] hits={len(hits)} new={new}")
    return new


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prio", default="P0",
                    help="P0 / P1 / P2 / all / 逗号组合，默认 P0")
    ap.add_argument("--limit", type=int, default=0, help="只处理前 N 个信源")
    ap.add_argument("--hn", action="store_true", help="附加 Hacker News 雷达")
    args = ap.parse_args()

    sources = load_sources(args.prio)
    if args.limit:
        sources = sources[: args.limit]

    conn = db.connect()
    print(f"== fetch: {len(sources)} sources (prio={args.prio}) ==")
    ok = fail = skip = 0
    for row in sources:
        name, total, new, note = fetch_source(row, conn)
        status = note.split(":")[0]
        if status == "ok":
            ok += 1
        elif status == "skip":
            skip += 1
        else:
            fail += 1
        print(f"  [{status:>4}] {name}: {new}/{total} new | {note}")
        conn.commit()

    if args.hn:
        fetch_hn(conn)
        conn.commit()

    n = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
    print(f"== done: ok={ok} fail={fail} skip={skip}, db total={n} ==")


if __name__ == "__main__":
    main()
