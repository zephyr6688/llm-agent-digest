"""SQLite 存储层：选题库（冷启动阶段用本地库，后续可换飞书多维表格）。"""
import datetime
import pathlib
import sqlite3

ROOT = pathlib.Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "db.sqlite"

SCHEMA = """
CREATE TABLE IF NOT EXISTS items(
    guid         TEXT PRIMARY KEY,
    title        TEXT NOT NULL,
    url          TEXT,
    author       TEXT,
    source       TEXT,
    published    TEXT,
    summary      TEXT,
    fetched_at   TEXT NOT NULL,
    score        REAL,
    score_reason TEXT,
    status       TEXT DEFAULT 'new'   -- new/scored/selected/published
);
CREATE INDEX IF NOT EXISTS idx_items_score ON items(score);
CREATE INDEX IF NOT EXISTS idx_items_published ON items(published);
"""


def connect(path=None):
    conn = sqlite3.connect(str(path or DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def now_utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def upsert_item(conn, item: dict, source: str) -> bool:
    """插入一条内容，已存在（按 guid/url 去重）则忽略。返回是否新增。"""
    guid = item.get("guid") or item.get("url") or item.get("title", "")
    if not guid:
        return False
    cur = conn.execute(
        "INSERT OR IGNORE INTO items(guid,title,url,author,source,published,summary,fetched_at) "
        "VALUES(?,?,?,?,?,?,?,?)",
        (str(guid), item.get("title", "(untitled)"), item.get("url", ""),
         item.get("author", ""), source, item.get("published"),
         item.get("summary", ""), now_utc()),
    )
    return cur.rowcount > 0
