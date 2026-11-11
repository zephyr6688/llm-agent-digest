"""渠道适配层：冷启动四渠道 + 扩展预留。

设计约定（后续新增渠道照此三步）：
  1. 继承 Channel，实现 render(article) -> list[dict(filename, content)]
  2. 在 CHANNELS 注册表中登记
  3. 在根目录 channels.json 的 enabled 数组中启用

article 结构（由 export.py 从周报草稿解析）：
  {"issue": "w2026-46", "issue_no": 3, "title": "...",
   "intro": "...", "items": [ {"title","url","meta","summary","comment"} ], "footer": "..."}
"""
import re

# ---- 解析周报草稿 ----
ITEM_RE = re.compile(
    r"^- \*\*\[(.+?)\]\((\S+?)\)\*\* · (.+?) · 相关度 (\d+)/10\n"
    r"  - 摘要：(.*)\n"
    r"  - 点评：(.*)$",
    re.M,
)


def parse_draft(md_text: str) -> dict:
    title_m = re.search(r"^# (.+)$", md_text, re.M)
    intro_m = re.search(r"^> (.+)$", md_text, re.M)
    footer_m = re.search(r"^---\n(\*\*.+\*)$", md_text, re.M | re.S)
    items = []
    for m in ITEM_RE.finditer(md_text):
        comment = re.sub(r"<!--.*?-->", "", m.group(6), flags=re.S).strip()
        items.append({
            "title": m.group(1),
            "url": m.group(2),
            "meta": m.group(3),
            "score": m.group(4),
            "summary": m.group(5),
            "comment": comment,
        })
    return {
        "title": title_m.group(1) if title_m else "Agent 工程周报",
        "intro": intro_m.group(1) if intro_m else "",
        "items": items,
        "footer": (footer_m.group(1).strip() if footer_m
                   else "*《Agent 工程周报》· 每周一发布*"),
    }


class Channel:
    name = "base"
    label = "基础"
    filename = "base.md"

    def render(self, article: dict):
        raise NotImplementedError


# ---- 冷启动渠道 1：微信公众号（主阵地，首发） ----
class WechatChannel(Channel):
    name = "wechat"
    label = "微信公众号"
    filename = "wechat.md"

    def render(self, article):
        items_md = []
        for it in article["items"]:
            comment = it["comment"] or "<!-- TODO 点评未写，发布前必须补 -->"
            items_md.append(
                f"### {it['title']}\n\n"
                f"{it['meta']} · 相关度 {it['score']}/10\n\n"
                f"{it['summary']}\n\n"
                f"**点评**：{comment}\n\n"
                f"原文：{it['url']}\n"
            )
        content = (
            f"# {article['title']}\n\n"
            f"<!-- TODO 导读（3-5 句，本期趋势与最值得读的一条） -->\n\n"
            f"<!-- 署名纪律：每条编译内容保留作者与原文链接；"
            f"自己写作占比足够再声明原创 -->\n\n"
            + "\n".join(items_md)
            + f"\n---\n\n{article['footer']}\n\n"
            "<!-- 尾部引导：关注 + 回复关键词进读者群 -->\n"
        )
        return [{"filename": self.filename, "content": content}]


# ---- 冷启动渠道 2：知乎（回答式开头 + 专栏同步） ----
class ZhihuChannel(Channel):
    name = "zhihu"
    label = "知乎"
    filename = "zhihu.md"

    def render(self, article):
        items_md = "\n".join(
            f"**[{it['title']}]({it['url']})** · {it['meta']}\n\n"
            f"{it['summary']}\n\n{('点评：' + it['comment']) if it['comment'] else ''}\n"
            for it in article["items"]
        )
        content = (
            f"# {article['title']}\n\n"
            f"> 本文首发于公众号，同步发布于知乎。\n\n"
            f"{article['intro']}\n\n"
            f"<!-- TODO 知乎打法：除专栏同步外，找 1-2 个已有高流量相关问题"
            f"（如『如何设计 agent 评测』），把本期内容量身改写成回答 -->\n\n"
            f"{items_md}\n\n---\n\n{article['footer']}\n"
        )
        return [{"filename": self.filename, "content": content}]


# ---- 冷启动渠道 3：掘金（工程师社区，Markdown 直发） ----
class JuejinChannel(Channel):
    name = "juejin"
    label = "掘金"
    filename = "juejin.md"

    def render(self, article):
        items_md = "\n".join(
            f"## {it['title']}\n\n{it['meta']}\n\n{it['summary']}\n\n"
            f"原文：{it['url']}\n"
            for it in article["items"]
        )
        content = (
            f"# {article['title']}\n\n"
            f"<!-- 掘金标题建议工程化：如『本周 Agent 工程圈值得读的 {len(article['items'])} 篇』 -->\n\n"
            f"标签：`人工智能` `LLM` `Agent`\n\n"
            f"{article['intro']}\n\n{items_md}\n\n---\n\n{article['footer']}\n"
        )
        return [{"filename": self.filename, "content": content}]


# ---- 冷启动渠道 4：即刻（周报拆条，碎片引流） ----
class JikeChannel(Channel):
    name = "jike"
    label = "即刻（拆条）"
    filename = "jike.md"

    def render(self, article):
        posts = [
            f"【{article['title']}】本周 {len(article['items'])} 条精选，"
            "完整版在公众号，这里拆条发最值得看的几条。"
        ]
        for it in article["items"][:5]:
            one = f"{it['title']}｜{it['meta']}"
            if it["comment"]:
                one += f"｜{it['comment']}"
            one += f"\n{it['url']}"
            posts.append(one[:500])
        content = (
            "# 即刻拆条（每条单独发，间隔 2-3 小时）\n\n"
            + "\n\n---\n\n".join(posts)
            + "\n"
        )
        return [{"filename": self.filename, "content": content}]


# ---- 注册表：新增渠道在此登记 ----
CHANNELS = {
    c.name: c
    for c in [WechatChannel, ZhihuChannel, JuejinChannel, JikeChannel]
}

# 预留路线（尚未实现，冷启动跑通后按三步法补充）：
#   bilibili_column   B 站专栏（图文同步，零边际成本）
#   wechat_channels   视频号（公众号一键同步）
#   xiaohongshu       小红书图文卡片
#   weibo             微博摘要卡片
#   email_digest      邮件订阅
