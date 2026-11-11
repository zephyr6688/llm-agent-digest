"""RSS/Atom 解析与 Feed 自动发现（仅标准库，无第三方依赖）。"""
import html
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urljoin

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) blog-repost-pipeline/0.1")

_ATOM = "{http://www.w3.org/2005/Atom}"
_DC_CREATOR = "{http://purl.org/dc/elements/1.1/}creator"

_LINK_TAG_RE = re.compile(
    r"<link[^>]+type=[\"']application/(?:rss|atom)\+xml[\"'][^>]*>", re.I)
_HREF_RE = re.compile(r"href=[\"']([^\"']+)[\"']", re.I)


def http_get(url: str, timeout: int = 15):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read(), resp.geturl()


def discover_feed(home_url: str, timeout: int = 12):
    """从主页 <link rel=alternate> 自动发现 RSS/Atom；失败再试常见路径。"""
    try:
        data, _ = http_get(home_url, timeout=timeout)
        text = data.decode("utf-8", "ignore")
        for tag in _LINK_TAG_RE.finditer(text):
            m = _HREF_RE.search(tag.group(0))
            if m:
                return urljoin(home_url, m.group(1))
    except Exception:
        pass
    for guess in ("feed", "rss", "feed.xml", "rss.xml", "atom.xml", "index.xml"):
        url = home_url.rstrip("/") + "/" + guess
        try:
            data, _ = http_get(url, timeout=8)
            head = data.lstrip()[:200]
            if head.startswith(b"<"):
                return url
        except Exception:
            continue
    return None


def _text(elt) -> str:
    return (elt.text or "").strip() if elt is not None else ""


def _strip_html(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def _parse_date(s: str):
    if not s:
        return None
    s = s.strip()
    try:
        return parsedate_to_datetime(s).astimezone(timezone.utc).isoformat()
    except Exception:
        pass
    try:
        return (datetime.fromisoformat(s.replace("Z", "+00:00"))
                .astimezone(timezone.utc).isoformat())
    except Exception:
        return None


def parse_feed(data: bytes) -> list:
    """解析 RSS 2.0 / Atom，返回 item dict 列表。"""
    root = ET.fromstring(data)
    items = []
    if root.tag.lower().endswith("rss"):
        for it in root.iter("item"):
            items.append({
                "guid": _text(it.find("guid")),
                "title": _strip_html(_text(it.find("title"))) or "(untitled)",
                "url": _text(it.find("link")),
                "summary": _strip_html(_text(it.find("description")))[:600],
                "published": _parse_date(_text(it.find("pubDate"))),
                "author": _text(it.find("author")) or _text(it.find(_DC_CREATOR)),
            })
    elif root.tag.lower().endswith("feed"):
        for e in root.iter(f"{_ATOM}entry"):
            url = ""
            for link in e.findall(f"{_ATOM}link"):
                if link.get("rel") in (None, "alternate"):
                    url = link.get("href") or ""
                    break
            content = e.find(f"{_ATOM}content")
            if content is None:
                content = e.find(f"{_ATOM}summary")
            author = ""
            a = e.find(f"{_ATOM}author")
            if a is not None:
                author = _text(a.find(f"{_ATOM}name"))
            items.append({
                "guid": _text(e.find(f"{_ATOM}id")),
                "title": _strip_html(_text(e.find(f"{_ATOM}title"))) or "(untitled)",
                "url": url,
                "summary": _strip_html(_text(content))[:600],
                "published": _parse_date(_text(e.find(f"{_ATOM}updated"))
                                          or _text(e.find(f"{_ATOM}published"))),
                "author": author,
            })
    return items
