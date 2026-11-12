# 发布纪律

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
