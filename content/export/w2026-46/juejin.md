# Agent 工程周报 · 第 1 期（2026 年第 46 周）

<!-- 掘金标题建议工程化：如『本周 Agent 工程圈值得读的 15 篇』 -->

标签：`人工智能` `LLM` `Agent`

本期速览：15 条精选（近 7 天，相关度 ≥ 6）。

本周两条主线：**小模型价格战进入"agent 执行单元"阶段**——Muse Ember 上市即贴着 Artificial Analysis 效率前沿的 Pareto 线打，但长上下文定价藏着 3 倍跳价陷阱；**"为 agent 造界面与评测"持续升温**——浏览器厂商联合下场给 coding agent 喂知识、邮件 API 靠 AEO 吃到推荐位、湿实验基准示范了什么叫认真的 agent 评测。本期最值得读的一条是斯坦福 CS146S：当 agent 一个 prompt 就能写完去年的作业，大学课程应该教什么。

## Introducing Our Smallest, Most Efficient Model: Muse Ember

Simon Willison · 2026-11-10

Introducing Our Smallest, Most Efficient Model: Muse Ember Meta AI just launched their entry in the Claude Haiku/GPT Luna category: Muse Ember, which they describe as: [...] our smallest and most efficient model designed for complex reasoning execution and the work agents repeat all day: tool calls, coding subtasks, routing, extraction, and long document parsing. For shorter prompts it's priced the same as GPT-6 Luna and Claude Haiku 5.5 - both are $0.10/million input tokens and $0.50/million output. Today's other big model release, Claude Fable 5.2, is 80x that price at $8/$40. The pricing is

原文：https://simonwillison.net/2026/Nov/10/muse-ember/

## CodeRabbit scales agentic software development and ships 20x more

OpenAI Research · 2026-11-09

CodeRabbit uses OpenAI models to govern and trust AI-generated code and Codex to ship 20 times more software with the same engineering team.

原文：https://openai.com/index/coderabbit-codex-daybreak

## llm-anthropic 0.31

Simon Willison · 2026-11-09

Release: llm-anthropic 0.31 Anthropic released Fable 5.2 and Mythos 5.2 today. Fable 5.2 is currently ranked first on Artificial Analysis . Anthropic say it "solved two open problems in the physics of black holes", so clearly their internal benchmarks have become more ambitious! I've added the new models to llm-anthropic , so you can now run prompts through Fable 5.2 like this: uv tool install llm llm install llm-anthropic llm keys set anthropic # paste key here llm -m claude-fable-5.2 "Generate an SVG of a pelican riding a bicycle" I ran pelicans at all five reasoning levels - low , medium ,

原文：https://simonwillison.net/2026/Nov/9/llm-anthropic/

## datasette-llm 0.1a10

Simon Willison · 2026-11-04

Release: datasette-llm 0.1a10 Fixes a bug that affected my agent.datasette.io demo site, where the set of available LLM models was not correctly restricted to just those in the configuration. Tags: llm , datasette

原文：https://simonwillison.net/2026/Nov/4/datasette-llm/

## [One Million AI Engineer Special] How Stanford Teaches AI-Native Engineering — Mihail Eric, Monaco

Latent Space · 2026-11-08

What do you assign when a coding agent can finish last year's homework in one prompt? In the second run of Stanford's CS146S, Mihail Eric brought open-source maintainers into the course. Students have to to learn an unfamiliar repo, propose a change, and ...

原文：https://latent.space/p/one_million_ai_engineer_special_how_stanford_teaches_ai-native_engineering_mihail_eric_monaco/

## Quoting Nilay Patel

Simon Willison · 2026-11-06

The products aren't good enough to sell people on the costs. You cannot tell people that you have to listen to the whine of a data center in their backyard for AI overviews and some of the most hilarious deep fake slop in history. It's not worth it. It just isn't worth it to anyone. And agents aren't real and they might not be being used the way that anyone wants them to yet. All these companies are spending more than they're making on these products. Refrigerators holding blood storage in Europe are being hacked. The costs are too high. The benefits are not real. And if you connect that to co

原文：https://simonwillison.net/2026/Nov/6/nilay-patel/

## Measuring how AI agents handle everyday wet-lab science

OpenAI Research · 2026-11-06

OpenAI introduces BioBasicsBench, a 100-task benchmark measuring how well AI agents interpret raw experimental data and handle everyday wet-lab science.

原文：https://openai.com/index/measuring-how-ai-agents-handle-wet-lab-science

## ChatGPT Desktop forwards your SSH agent to remote machines

Hacker News

HN 热帖 · 216 points · 78 comments

原文：https://news.ycombinator.com/item?id=50422628

## Show HN: Get your coding agent off ~2019 JavaScript, onto modern web primitives

Hacker News

HN 热帖 · 354 points · 106 comments

原文：https://github.com/GoogleChrome/modern-web-guidance

## 6 Hours of YouTube and 85 handtyped pages of notes on LLM Inference – Start here

Hacker News

HN 热帖 · 79 points · 12 comments

原文：https://github.com/samir-sarwar/samir-vllm

## Designing for Agents — Zeno Rocha, Resend

Latent Space · 2026-11-10

Where does answer engine optimization (AEO) end and agent experience begin? Inside Resend, from the docs that help Claude Code pick an email API to the tools it uses to send.

原文：https://latent.space/p/resend/

## Introducing AlphaProof Code: a breakthrough in verifying complex software at depth

Google DeepMind Blog · 2026-11-10

AlphaProof Code agents wrote three million lines of proofs in Lean to verify Signal's core encryption.

原文：https://deepmind.google/blog/introducing-alphaproof-code/

## Yonkers Rises

Simon Willison · 2026-11-10

Tool: Yonkers Rises I realized I didn't know where Yonkers was, so I looked it up on Google Maps and then, to help embed its location and shape in my head (and to try out Claude Fable 5.2's 3D modeling and animation skills), I prompted Fable 5.2 Medium to: Make a three js animation where yonkers stands up as a big mech (cool stand up motion) and átomos around manhattan and queens and Brooklyn, use openstreetmap mapping data It correctly deduced that "átomos" was a mobile keyboard typo for "stomps": Tags: three-js , llms , ai , generative-ai , claude-mythos-fable

原文：https://simonwillison.net/2026/Nov/10/yonkers-rises/

## Cogent and OpenAI build cyber defense factories for enterprises

OpenAI Research · 2026-11-10

Cogent combines OpenAI models with enterprise context to help automatically remediate vulnerabilities with agents.

原文：https://openai.com/index/cogent-security

## Hide your slop PR descriptions behind

Simon Willison · 2026-11-09

Most of the changes I make to my projects these days come in the form of PRs opened for me by Claude Code or Codex. The PR is my unit of work - I use them to bundle commits together, iterating on them until a feature is complete, document decisions and then merge the finished result. Today's coding agents are great at writing PR descriptions. They're too good at describing the work The problem is that they are too good. An agent-written PR description is accurate and comprehensive. It describes the problem, the detailed solution, and the steps taken to verify it. That's a lot of information to

原文：https://simonwillison.net/2026/Nov/9/details-summary/


---

*《Agent 工程周报》· 每周一发布*
