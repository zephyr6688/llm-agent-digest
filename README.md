# blog_reposting · LLM/Agent 方向博客引进管线

打破信息差的冷启动工程：海外一手信源 → 自动采集 → 初筛评分 → 周报草稿 → 多渠道导出。
整体方案见 `方案.md` / `方案.html`；本 README 只讲怎么跑。

## 快速开始（3 条命令跑通全流程）

```bash
python3 pipeline/fetch.py --prio P0 --hn   # ① 采集：P0 信源 + Hacker News 雷达
python3 pipeline/score.py                  # ② 评分：有 LLM_API_KEY 走 LLM，否则关键词启发式
python3 pipeline/report.py --weekly        # ③ 生成本周周报草稿 content/weekly/wYYYY-WW.md
python3 pipeline/export.py                 # ④ 导出六渠道版本 content/export/wYYYY-WW/
python3 pipeline/export.py --publish       # ⑤ 发布支持 API 的渠道（邮件 + GitHub Pages）
```

纯 Python 标准库实现，无第三方依赖。数据落在 `db.sqlite`（选题库）。

## 冷启动发布流程（每周一，约 2-3 小时）

1. **人工选题**：看 `content/inbox.md`（自动刷新的高分待选题清单），执行独占性判断——
   国内已有译本的放弃，无译本的抢时效；
2. **补写**：打开当周周报草稿，补每条点评和导读（TODO 标记清零）；
3. **导出**：`python3 pipeline/export.py`，得到四渠道版本 + `CHECKLIST.md`；
4. **发布**（按顺序纪律）：
   - 公众号首发（周一 8:00 前，用 `wechat.md`，mdnice 排版）
   - 24 小时后同步知乎（`zhihu.md`，注明首发）+ 掘金（`juejin.md`）
   - 即刻拆条（`jike.md`，每条间隔 2-3 小时，引流公众号）
5. **回填**：发布后在草稿头部记录各渠道数据（阅读/在看/涨粉），供月度复盘。

## 全自动渠道（--publish 触发）

两个支持 API 发布的渠道已实现，`export.py --publish` 时自动执行，
未配置凭据时会打印对应的三步配置指引：

- **邮件订阅**（email_digest）：向 `content/subscribers.txt`（每行一个邮箱）
  通过阿里云邮件推送 `SingleSendMail` 发送本期周报 HTML。
  配置：① 阿里云开通『邮件推送』并创建验证发信地址；② `channels.json` 的
  `config.email_digest.from_address` 填入发信地址；③ 设置环境变量
  `ALIYUN_ACCESS_KEY_ID` / `ALIYUN_ACCESS_KEY_SECRET`。
- **GitHub Pages 知识库**（github_pages）：render 时写入 `docs/`
  （index.md + posts/wYYYY-WW.md），`--publish` 时 git 提交并推送。
  首次使用：GitHub 仓库 Settings → Pages 选择 **main 分支 /docs 目录**。

## LLM 评分模式（推荐，替代关键词启发式）

```bash
export LLM_API_KEY=sk-xxx
export LLM_API_BASE=https://api.deepseek.com/v1   # 任意 OpenAI 兼容端点
export LLM_MODEL=deepseek-chat
python3 pipeline/score.py
```

## 自动化（GitHub Actions，每小时）

1. 推到 GitHub 私有仓库；
2. 仓库 Settings → Secrets 添加 `LLM_API_KEY`（可选，不配则启发式），
   Variables 添加 `LLM_API_BASE` / `LLM_MODEL`（可选）；
3. `.github/workflows/ingest.yml` 每小时自动：采集 P0+P1 → 评分 → 刷新 inbox.md 并提交。
   在 Actions 上跑还能绕开本地网络对部分信源的访问限制。

## 目录结构

```
├── sources.csv          # 信源清单（含 RSS 地址；地址列留空会自动发现）
├── glossary.json        # 术语表（翻译/改写阶段做一致性约束，暂未接入管线）
├── channels.json        # 渠道启停配置（扩展入口）
├── db.sqlite            # 选题库（SQLite）
├── pipeline/
│   ├── db.py            #   存储层
│   ├── feeds.py         #   RSS/Atom 解析 + 自动发现（仅标准库）
│   ├── fetch.py         #   采集入口
│   ├── score.py         #   评分（LLM / 启发式）
│   ├── report.py        #   周报草稿 + inbox
│   ├── channels.py      #   渠道适配层（六渠道：四手动 + 邮件/Pages 全自动）
│   ├── aliyun_dm.py     #   阿里云邮件推送签名与发信（仅标准库）
│   └── export.py        #   多渠道导出 + --publish 发布
├── content/
│   ├── inbox.md         #   高分待选题清单（自动生成）
│   ├── weekly/          #   周报草稿归档（人工编辑的主体）
│   ├── subscribers.txt  #   邮件订阅者（每行一个邮箱）
│   └── export/          #   各渠道发布版本（自动生成，勿手编）
├── docs/                # GitHub Pages 知识库（github_pages 渠道产物）
├── 信源清单.csv          # 人类可读版信源主档（pipeline 读 sources.csv）
├── 方案.md / 方案.html   # 全流程方案文档
└── _diagrams/           # 方案配图（mermaid 源 + SVG）
```

## 渠道扩展（冷启动跑通后）

三步法，无需改 export.py：

1. `pipeline/channels.py` 继承 `Channel`，实现 `render(article)`；
   需要自动发布能力则再实现 `publish(article)`（不支持则保持基类默认，
   `--publish` 时自动降级为手动指引）；
2. 在 `CHANNELS` 注册表登记；
3. `channels.json` 的 `enabled` 数组中加入（渠道参数放 `config`）。

预留路线（2026-11-12 已核实 API 可用性）：
- `bilibili_column`（B 站专栏）：有官方 API，需入驻开放平台 + 专栏管理权限报备；
- `weibo`：有官方 `statuses/update` API，需应用审核 + OAuth；
- `xiaohongshu`：开放平台内容接口需企业资质，个人拿不到权限；
- `wechat_channels`（视频号）：官方未开放内容发布 API。
后两个保持手动。

## 当前状态与已知边界

- 冷启动验证：2026-11-11 实测 P0 信源 10/19 在线可采（其余为网络波动或无 RSS，
  在 GitHub Actions 上会更好）；
- 启发式评分偏召回（初筛漏报少、误报交给人工选题层）；配 LLM Key 后质量明显更好；
- 授权台账（auth_ledger.csv）暂缓——按当前决策以跑通冷启动为第一任务，
  深度编译（全文翻译）上线前需补合规流程，见 `方案.md` 第 2 节。
