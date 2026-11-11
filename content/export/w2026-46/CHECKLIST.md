# 发布纪律（冷启动四渠道）

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
