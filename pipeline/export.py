#!/usr/bin/env python3
"""多渠道导出与发布。

用法：
  python3 pipeline/export.py                          # 渲染全部启用渠道（只产文件）
  python3 pipeline/export.py --channels wechat,jike   # 只渲染指定渠道
  python3 pipeline/export.py --publish                # 渲染后触发支持 API 的渠道发布
  python3 pipeline/export.py --draft content/weekly/w2026-46.md

启用渠道与各渠道参数由根目录 channels.json 控制（渠道扩展入口）。
"""
import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from channels import CHANNELS, ManualPublishRequired, parse_draft

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHANNELS_JSON = ROOT / "channels.json"
EXPORT_DIR = ROOT / "content" / "export"

CHECKLIST = """# 发布纪律

## 冷启动四渠道（手动，24 小时节奏）

1. **公众号首发**（周一 8:00 前完成）：使用 wechat.md；
   - 每条点评必须补完，TODO 标记清零后才能发；
   - 署名纪律：保留作者 + 原文链接；自己写作占比足够再声明原创；
   - 也可贴入后台用官方**定时群发**定在周一 8:00。
2. **24 小时后同步**：知乎（zhihu.md，注明首发）+ 掘金（juejin.md）。
3. **即刻拆条**（jike.md）：每条间隔 2-3 小时，引流公众号。
4. 发布后回填：把 db 中对应条目 status 改为 published，
   并在周报草稿头部记录各渠道数据（阅读/在看/涨粉）。

## 全自动渠道（--publish 触发）

- **邮件订阅**（email_digest）：`--publish` 时向 content/subscribers.txt
  中所有订阅者发送本期周报 HTML；未配置阿里云凭据时会打印配置指引。
  首次使用三步：开通阿里云『邮件推送』→ 创建并验证发信地址 →
  channels.json 填 from_address + 设置 ALIYUN_ACCESS_KEY_ID/SECRET 环境变量。
- **GitHub Pages 知识库**（github_pages）：render 时已写入 docs/，
  `--publish` 时提交并推送；首次使用在 GitHub 仓库
  Settings → Pages 选择 main 分支 /docs 目录启用。

## 渠道扩展

在 `pipeline/channels.py` 继承 Channel（可选实现 publish 获得自动发布能力）
→ 注册 → `channels.json` 的 enabled 中启用。
预留路线：bilibili_column（官方 API，需入驻报备）/ weibo（API 可用，需应用审核）/
xiaohongshu / wechat_channels（无 API 或个人无权限，保持手动）。
"""


def load_config():
    return json.loads(CHANNELS_JSON.read_text(encoding="utf-8"))


def latest_draft():
    drafts = sorted((ROOT / "content" / "weekly").glob("w*.md"))
    if not drafts:
        sys.exit("未找到周报草稿，先运行: python3 pipeline/report.py --weekly")
    return drafts[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", help="指定周报草稿路径")
    ap.add_argument("--channels", help="逗号分隔的渠道名，覆盖 channels.json enabled")
    ap.add_argument("--publish", action="store_true",
                    help="渲染后对支持 API 的渠道执行发布")
    args = ap.parse_args()

    draft = pathlib.Path(args.draft) if args.draft else latest_draft()
    article = parse_draft(draft.read_text(encoding="utf-8"))
    article["issue"] = draft.stem
    out_dir = EXPORT_DIR / article["issue"]
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg_all = load_config()
    configs = cfg_all.get("config", {})
    enabled = (args.channels.split(",") if args.channels
               else cfg_all.get("enabled", []))

    print(f"== export: {draft.name} -> {out_dir} (channels: {', '.join(enabled)}) ==")
    for name in enabled:
        cls = CHANNELS.get(name)
        if cls is None:
            print(f"  [skip] unknown channel: {name}")
            continue
        channel = cls(configs.get(name, {}))
        for doc in channel.render(article):
            path = out_dir / doc["filename"]
            path.write_text(doc["content"], encoding="utf-8")
            print(f"  [ok] {channel.label} -> {path}")
        if args.publish:
            try:
                result = channel.publish(article)
                print(f"  [published] {channel.label}: {result}")
            except ManualPublishRequired as e:
                print(f"  [manual] {channel.label}: {e}")
    (out_dir / "CHECKLIST.md").write_text(CHECKLIST, encoding="utf-8")
    print(f"  [ok] checklist -> {out_dir / 'CHECKLIST.md'}")


if __name__ == "__main__":
    main()
