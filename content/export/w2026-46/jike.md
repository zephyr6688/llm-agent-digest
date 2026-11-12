# 即刻拆条（每条单独发，间隔 2-3 小时）

【Agent 工程周报 · 第 1 期（2026 年第 46 周）】本周 15 条精选，完整版在公众号，这里拆条发最值得看的几条。

---

Introducing Our Smallest, Most Efficient Model: Muse Ember｜Simon Willison · 2026-11-10｜小模型军备竞赛的本质是在抢"agent 一天重复一千次的那些动作"（工具调用、路由、抽取、长文档解析）的单价。Simon 算的账值得抄下来：短 prompt 下 Ember/Luna/Haiku 同价，但超过各自阈值后 Ember 跳到 $0.30/$1.50——比 Haiku 的长文本档还贵，做长上下文 agent 选型时这个细节会直接改变成本结论。
https://simonwillison.net/2026/Nov/10/muse-ember/

---

CodeRabbit scales agentic software development and ships 20x more｜OpenAI Research · 2026-11-09｜案例文营销浓度不低，"20x 吞吐"听听就好；真正值得看的是它的隐含架构：AI 生成代码之后，靠另一套 AI 治理和建立对代码的信任——生成与验证分离成两层，这是做多 agent 生产管线绕不开的模式。
https://openai.com/index/coderabbit-codex-daybreak

---

llm-anthropic 0.31｜Simon Willison · 2026-11-09｜注意 Simon 的工作方式：新模型发布当天，他把模型接进自己的 llm 工具链，然后拿同一个任务（画鹈鹕骑自行车）把各推理档全跑一遍对比。这就是一套人人可抄的"模型快速体检管线"——比看跑分榜快得多，也更接近你的真实负载。
https://simonwillison.net/2026/Nov/9/llm-anthropic/

---

datasette-llm 0.1a10｜Simon Willison · 2026-11-04｜一句话版本新闻，收录理由是它背后那个 agent.datasette.io——把 LLM 配置暴露给 runtime agent 的公开 demo，配置边界出 bug 正说明"agent 能用哪些模型"本身就是一个需要认真治理的权限问题。
https://simonwillison.net/2026/Nov/4/datasette-llm/

---

[One Million AI Engineer Special] How Stanford Teaches AI-Native Engineering — Mihail Eric, Monaco｜Latent Space · 2026-11-08｜本期最值得精读的一篇。当 coding agent 一个 prompt 就能写完去年的作业，CS146S 的回答是把作业换成"学一个陌生开源仓库、提一个变更、向可能合并它的 maintainer 解释你的 patch"——真实开源协作就是课程本身。加上他在 Monaco 团队的落地经验（"买来学，留下来自建"、给 on-call agent 接 Datadog 和 GitHub、让 repo 变得 agent-ready），这是对"AI 时代工程师还该学什么"最认真的一份答案。
https://latent.space/p/one_million_ai_engineer_special_how_stanford_teaches_ai-native_engineering_mihail_eric_monaco/
