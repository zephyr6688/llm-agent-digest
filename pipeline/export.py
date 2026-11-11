#!/usr/bin/env python3
"""多渠道导出：把周报草稿渲染成各渠道适配版本。

用法：
  python3 pipeline/export.py                          # 取最新一期周报草稿
  python3 pipeline/export.py --draft content/weekly/w2026-46.md
  python3 pipeline/export.py --channels wechat,jike   # 只导出指定渠道

启用渠道由根目录 channels.json 的 enabled 数组控制（渠道扩展入口）。
"""
import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from channels import CHANNELS, parse_draft

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHANNELS_JSON = ROOT / "channels.json"
EXPORT_DIR = ROOT / "content" / "export"

CHECKLIST = """# 发布纪律（冷启动四渠道）

1. **公众号首发**（周一 8:00 前完成）：使用 wechat.md；
   - 每条点评必须补完，TODO 标记清零后才能发；
   - 署名纪律：保留作者 + 原文链接；自己写作占比足够再声明原创。
2. **24 小时后同步**：知乎（zhihu.md，注明首发）+ 掘金（juejin.md）。
3. **即刻拆条**（jike.md）：每条间隔 2-3 小时，引流公众号。
4. 发布后回填：把 db 中对应条目 status 改为 published，
   并在周报草稿头部记录各渠道数据（阅读/在看/涨粉）。

## 渠道扩展（冷启动跑通后）

在 `pipeline/channels.py` 继承 Channel → 注册 → `channels.json` 的
enabled 中启用。预留路线：bilibili_column / wechat_channels /
xiaohongshu / weibo / email_digest。
"""


def load_enabled():
    cfg = json.loads(CHANNELS_JSON.read_text(encoding="utf-8"))
    return cfg.get("enabled", [])


def latest_draft():
    drafts = sorted((ROOT / "content" / "weekly").glob("w*.md"))
    if not drafts:
        sys.exit("未找到周报草稿，先运行: python3 pipeline/report.py --weekly")
    return drafts[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", help="指定周报草稿路径")
    ap.add_argument("--channels", help="逗号分隔的渠道名，覆盖 channels.json")
    args = ap.parse_args()

    draft = pathlib.Path(args.draft) if args.draft else latest_draft()
    article = parse_draft(draft.read_text(encoding="utf-8"))
    issue = draft.stem
    out_dir = EXPORT_DIR / issue
    out_dir.mkdir(parents=True, exist_ok=True)

    enabled = (args.channels.split(",") if args.channels else load_enabled())
    print(f"== export: {draft.name} -> {out_dir} (channels: {', '.join(enabled)}) ==")
    for name in enabled:
        cls = CHANNELS.get(name)
        if cls is None:
            print(f"  [skip] unknown channel: {name}")
            continue
        for doc in cls().render(article):
            path = out_dir / doc["filename"]
            path.write_text(doc["content"], encoding="utf-8")
            print(f"  [ok] {cls.label} -> {path}")
    (out_dir / "CHECKLIST.md").write_text(CHECKLIST, encoding="utf-8")
    print(f"  [ok] checklist -> {out_dir / 'CHECKLIST.md'}")


if __name__ == "__main__":
    main()
