"""渠道适配层：冷启动四渠道 + 扩展预留。

设计约定（后续新增渠道照此三步）：
  1. 继承 Channel，实现 render(article) -> list[dict(filename, content)]
  2. 在 CHANNELS 注册表中登记
  3. 在根目录 channels.json 的 enabled 数组中启用

article 结构（由 export.py 从周报草稿解析）：
  {"issue": "w2026-46", "title": "...", "intro": "...",
   "items": [ {"title","url","meta","summary","comment"} ], "footer": "..."}

发布能力约定：
  - render() 只产出文件，永不产生外部副作用；
  - publish() 由 export.py --publish 显式触发；
  - 不支持 API 发布的渠道保持基类默认（ManualPublishRequired，给出手动指引）。
"""
import html
import re
import subprocess

# ---- 解析周报草稿 ----
ITEM_RE = re.compile(
    r"^- \*\*\[(.+?)\]\((\S+?)\)\*\* · (.+?) · 相关度 (\d+)/10\n"
    r"  - 摘要：(.*)\n"
    r"  - 点评：(.*)$",
    re.M,
)


def parse_draft(md_text: str) -> dict:
    title_m = re.search(r"^# (.+)$", md_text, re.M)
    intro_m = re.findall(r"^> (.+)$", md_text, re.M)
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
        "intro": "\n\n".join(intro_m),
        "items": items,
        "footer": (footer_m.group(1).strip() if footer_m
                   else "*《Agent 工程周报》· 每周一发布*"),
    }


class ManualPublishRequired(Exception):
    """该渠道不支持（或尚未配置）API 发布，需要人工操作。message 为操作指引。"""


class Channel:
    name = "base"
    label = "基础"
    filename = "base.md"

    def __init__(self, cfg: dict | None = None):
        self.cfg = cfg or {}

    def render(self, article: dict):
        raise NotImplementedError

    def publish(self, article: dict):
        raise ManualPublishRequired(
            f"{self.label} 暂不支持 API 发布：将导出文件手动粘贴到平台后台完成发布。"
        )


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
        intro = article["intro"] or "<!-- TODO 导读（3-5 句，本期趋势与最值得读的一条） -->"
        content = (
            f"# {article['title']}\n\n"
            f"> {intro}\n\n"
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
            f"<!-- 知乎打法：专栏同步用本文件；回答式改写见 content/zhihu/ 内容包"
            f"（专栏文章 + 回答草稿 + 选题池） -->\n\n"
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


# ---- 全自动渠道 1：邮件订阅（阿里云邮件推送 DirectMail） ----
class EmailDigestChannel(Channel):
    name = "email_digest"
    label = "邮件订阅"
    filename = "email_digest.html"

    def _html(self, article: dict) -> str:
        esc = html.escape
        blocks = []
        for it in article["items"]:
            comment = (
                f'<p style="color:#0f8b8d;margin:8px 0 0;font-size:14px;">'
                f"<b>点评</b>：{esc(it['comment'])}</p>"
                if it["comment"] else ""
            )
            blocks.append(
                f'<div style="margin:0 0 24px;padding:0 0 24px;border-bottom:1px solid #eee;">'
                f'<h3 style="margin:0 0 6px;font-size:16px;">'
                f'<a href="{esc(it["url"])}" style="color:#1c2b3a;text-decoration:none;">'
                f"{esc(it['title'])}</a></h3>"
                f'<p style="color:#888;font-size:12px;margin:0 0 8px;">'
                f"{esc(it['meta'])} · 相关度 {esc(it['score'])}/10</p>"
                f'<p style="color:#333;font-size:14px;line-height:1.7;margin:0;">'
                f"{esc(it['summary'])}</p>{comment}</div>"
            )
        return (
            '<div style="max-width:640px;margin:0 auto;font-family:-apple-system,'
            "'PingFang SC','Microsoft YaHei',sans-serif;\">"
            f'<h2 style="font-size:20px;">{esc(article["title"])}</h2>'
            f'<p style="color:#666;font-size:14px;">{esc(article["intro"])}</p>'
            + "".join(blocks)
            + f'<p style="color:#999;font-size:12px;">{esc(article["footer"])}</p>'
            '<p style="color:#999;font-size:12px;">如不想再收到本邮件，直接回复即可退订。</p>'
            "</div>"
        )

    def _subject(self, article: dict) -> str:
        prefix = self.cfg.get("subject_prefix", "Agent 工程周报")
        return f"{prefix} · {article.get('issue', '')}"

    def render(self, article):
        content = self._html(article)
        return [
            {"filename": "email_digest.html", "content": content},
            {"filename": "email_subject.txt",
             "content": self._subject(article) + "\n"},
        ]

    def publish(self, article: dict):
        import os
        import pathlib
        import sys

        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
        import aliyun_dm

        key_id = os.environ.get("ALIYUN_ACCESS_KEY_ID", "").strip()
        secret = os.environ.get("ALIYUN_ACCESS_KEY_SECRET", "").strip()
        from_addr = (self.cfg.get("from_address") or "").strip()
        if not (key_id and secret and from_addr):
            raise ManualPublishRequired(
                "邮件发布未配置。三步：① 阿里云开通『邮件推送』并创建验证发信地址；"
                "② channels.json 的 config.email_digest.from_address 填入发信地址；"
                "③ 设置环境变量 ALIYUN_ACCESS_KEY_ID / ALIYUN_ACCESS_KEY_SECRET。"
            )
        sub_file = pathlib.Path(self.cfg.get("subscribers_file",
                                             "content/subscribers.txt"))
        if not sub_file.exists():
            raise ManualPublishRequired(
                f"订阅者文件不存在：{sub_file}（每行一个邮箱，# 开头为注释）"
            )
        subs = [ln.strip() for ln in sub_file.read_text(encoding="utf-8").splitlines()
                if ln.strip() and not ln.strip().startswith("#")]
        if not subs:
            raise ManualPublishRequired(f"订阅者为空：{sub_file}")
        body = self._html(article)
        subject = self._subject(article)
        ok = fail = 0
        for to in subs:
            try:
                aliyun_dm.send_mail(to, subject, body, from_addr, key_id, secret)
                ok += 1
            except Exception as e:
                fail += 1
                print(f"  [email-fail] {to}: {e}")
        return f"邮件已发送：成功 {ok} / 失败 {fail}（共 {len(subs)} 位订阅者）"


# ---- 全自动渠道 2：GitHub Pages 知识库（docs/ 目录，git 提交推送） ----
class GithubPagesChannel(Channel):
    name = "github_pages"
    label = "GitHub Pages 知识库"
    filename = "github_pages.md"

    def render(self, article: dict):
        # 产物写入 docs/：issues.json 索引 + 终端风 HTML 页面
        # （GitHub Pages 从 main 分支 /docs 提供），content/export/ 下留说明。
        import json
        import pathlib
        import sys

        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
        import site_theme

        root = pathlib.Path(__file__).resolve().parent.parent
        site = root / (self.cfg.get("site_dir", "docs"))
        posts = site / "posts"
        posts.mkdir(parents=True, exist_ok=True)

        (posts / f"{article['issue']}.html").write_text(
            site_theme.render_post(article), encoding="utf-8")

        index_path = site / "issues.json"
        issues = []
        if index_path.exists():
            try:
                issues = json.loads(index_path.read_text(encoding="utf-8"))
            except Exception:
                issues = []
        entry = {"issue": article["issue"], "title": article["title"],
                 "count": len(article.get("items", []))}
        issues = [i for i in issues if i.get("issue") != article["issue"]]
        issues.append(entry)
        index_path.write_text(json.dumps(issues, ensure_ascii=False, indent=1),
                             encoding="utf-8")
        (site / "index.html").write_text(site_theme.render_index(issues),
                                          encoding="utf-8")
        (site / ".nojekyll").write_text("", encoding="utf-8")
        return [{"filename": self.filename,
                 "content": f"（本渠道产物直接写入 {site}，此处无文件）\n"}]

    def publish(self, article: dict):
        import pathlib
        root = pathlib.Path(__file__).resolve().parent.parent
        site = self.cfg.get("site_dir", "docs")

        def run(*cmd):
            return subprocess.run(cmd, cwd=root, capture_output=True, text=True)

        run("git", "add", site)
        status = run("git", "status", "--porcelain", site)
        if not status.stdout.strip():
            return "docs/ 无变更，无需发布。"
        run("git", "commit", "-m", f"site: publish {article['issue']}")
        push = run("git", "push")
        if push.returncode == 0:
            return f"知识库已发布：docs/ 提交并推送（{article['issue']}）。"
        raise ManualPublishRequired(
            "docs/ 已提交到本地仓库，但推送失败（"
            f"{(push.stderr or push.stdout).strip()[:120]}）。"
            "请配置远端后重试；首次使用请在 GitHub 仓库 "
            "Settings → Pages 选择 main 分支 /docs 目录启用。"
        )


# ---- 注册表：新增渠道在此登记 ----
CHANNELS = {
    c.name: c
    for c in [WechatChannel, ZhihuChannel, JuejinChannel, JikeChannel,
              EmailDigestChannel, GithubPagesChannel]
}

# 预留路线（API 不可用或个人拿不到权限，保持手动）：
#   bilibili_column   B 站专栏（有官方 API，需入驻开放平台+权限报备）
#   weibo             微博（有官方 API，需应用审核+OAuth）
#   xiaohongshu       小红书（开放平台内容接口需企业资质）
#   wechat_channels   视频号（官方未开放内容发布 API）
