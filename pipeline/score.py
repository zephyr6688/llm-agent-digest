#!/usr/bin/env python3
"""初筛评分：LLM 打分（有 API Key 时）或关键词启发式（无 Key 兜底）。

用法：
  python3 pipeline/score.py               # 自动：有 LLM_API_KEY 走 LLM，否则启发式
  python3 pipeline/score.py --heuristic   # 强制启发式
  python3 pipeline/score.py --all         # 对全部历史条目重评

LLM 模式环境变量：
  LLM_API_KEY   必填
  LLM_API_BASE  默认 https://api.deepseek.com/v1（OpenAI 兼容协议）
  LLM_MODEL     默认 deepseek-chat
"""
import argparse
import json
import os
import pathlib
import re
import sys
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import db

# ---- 启发式关键词（冷启动无 Key 时兜底；权重即相关度加成） ----
KEYWORDS = {
    "agent": 3, "智能体": 3, "agentic": 3, "multi-agent": 3,
    "llm": 2, "大语言模型": 2, "大模型": 2, "language model": 2,
    "eval": 2, "评测": 2, "benchmark": 1,
    "context engineering": 3, "上下文工程": 3, "context window": 1,
    "tool use": 2, "工具调用": 2, "function calling": 2, "mcp": 2,
    "rag": 1, "检索增强": 1, "fine-tun": 1, "微调": 1,
    "prompt": 1, "提示词": 1, "reasoning": 1, "推理模型": 2,
    "guardrail": 1, "护栏": 1, "observ": 1, "tracing": 1,
    "inference": 1, "kv cache": 1, "token": 1,
}

SYSTEM_PROMPT = (
    "你是一位专注于大语言模型与 Agent 开发领域的技术编辑。"
    "请对下面这条内容按『与 LLM/Agent 工程实践的相关度』打 0-10 分"
    "（10 分=直接讲 agent 构建/评测/上下文工程等实操；5 分=泛 AI 技术；"
    "0 分=与工程无关的纯新闻/融资/八卦），并给一句话中文理由。"
    '只输出 JSON：{"score": <0-10>, "reason": "<一句话>"}'
)


def heuristic_score(title: str, summary: str):
    text = f"{title} {summary}".lower()
    hits = [(kw, w) for kw, w in KEYWORDS.items() if kw in text]
    # 命中即给 3 分基础分（初筛偏召回，误报交给人工选题层过滤）
    score = min(10.0, 3.0 + float(sum(w for _, w in hits))) if hits else 0.0
    reason = "命中关键词: " + ", ".join(kw for kw, _ in hits) if hits else "无关键词命中"
    return score, reason


def llm_score_one(item, api_base, api_key, model):
    user = f"标题：{item['title']}\n摘要：{item['summary'] or '（无）'}\n来源：{item['source']}"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user},
        ],
        "temperature": 0,
    }
    req = urllib.request.Request(
        api_base.rstrip("/") + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {api_key}"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        content = json.loads(resp.read().decode("utf-8"))[
            "choices"][0]["message"]["content"]
    m = re.search(r"\{.*\}", content, re.S)
    if not m:
        return 0.0, "LLM 输出无法解析"
    try:
        obj = json.loads(m.group(0))
        return float(obj.get("score", 0)), str(obj.get("reason", ""))
    except Exception:
        return 0.0, "LLM 输出无法解析"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--heuristic", action="store_true", help="强制关键词启发式")
    ap.add_argument("--all", action="store_true", help="重评全部条目")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    api_key = os.environ.get("LLM_API_KEY", "").strip()
    api_base = os.environ.get("LLM_API_BASE", "https://api.deepseek.com/v1")
    model = os.environ.get("LLM_MODEL", "deepseek-chat")
    use_llm = bool(api_key) and not args.heuristic

    conn = db.connect()
    if args.all:
        rows = conn.execute("SELECT * FROM items ORDER BY published DESC").fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM items WHERE score IS NULL ORDER BY published DESC"
        ).fetchall()
    if args.limit:
        rows = rows[: args.limit]

    mode = f"LLM({model})" if use_llm else "heuristic"
    print(f"== score: {len(rows)} items, mode={mode} ==")
    for r in rows:
        try:
            if use_llm:
                score, reason = llm_score_one(r, api_base, api_key, model)
            else:
                score, reason = heuristic_score(r["title"], r["summary"] or "")
        except Exception as e:
            print(f"  [fail] {r['title'][:40]}: {e}")
            continue
        conn.execute(
            "UPDATE items SET score=?, score_reason=?, status='scored' WHERE guid=?",
            (score, reason, r["guid"]),
        )
    conn.commit()

    print("== top 10 (score desc) ==")
    for r in conn.execute(
            "SELECT title, source, score FROM items "
            "WHERE score IS NOT NULL ORDER BY score DESC, published DESC LIMIT 10"):
        print(f"  {r['score']:>4.1f} | {r['source'][:16]:<16} | {r['title'][:48]}")


if __name__ == "__main__":
    main()
