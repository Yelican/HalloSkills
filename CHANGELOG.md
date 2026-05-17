# HalloSkills 更新日志

## 2026-05-17 · v2.0

### 🔥 重大重构

- **hallochatgold + hallogoldchat 合并为 hallogoldchat-v3.0**
  - 旧 hallochatgold（对话淘金术 skill）和旧 hallogoldchat（Python 假分析脚本）已删除
  - 合并后的 v3.0 保持 7 步管道真实分析，新增自动存档 + 聚合看板
  - Claude 在对话中执行真实分析，存档 JSON；build.py 读取生成自包含 HTML 看板
  - SessionEnd hook 自动更新看板，无需手动操作

### ✨ 新增

- **hallogoldchat-v3.0/build.py** — 聚合脚本，零 pip 依赖
  - 读取 `~/.claude/hallo-gold-chat/reports/` 下所有 JSON 报告
  - 生成自包含 HTML 看板（概览统计 + 时间线详情 + 评分趋势）
  - 支持 `python build.py --serve` 启动本地预览服务器
- **SKILL.md 自动存档指令** — 每次复盘后自动写 JSON 到数据目录
- **示例报告** — 3 份测试数据用于验证看板功能

### 📝 更新

- README 重写，v1.2 和旧看板描述替换为 v3.0
- 安装脚本路径更新为 hallogoldchat-v3.0
- SKILL.md frontmatter 从 hallochatgold 修正为 hallogoldchat

### 🗑 删除

- hallochatgold/（被 v3.0 取代）
- hallogoldchat/（含 hellgold-chat-2.0.py 假分析脚本）

---

## 2026-05-16 · v1.1

### ✨ 新增

- **HalloCC v1.0.0** — Claude Code 全量备份工具
  - 一键备份 `~/.claude/` 全部核心数据（配置、对话、Skills、MCP）
  - API Key / token 自动脱敏
  - 可选 HTML 看板生成
  - 跨平台（Windows / macOS / Linux）
  - [查看文档 →](./hallocc-1.0.0/SKILL.md)

- **HalloGoldChat** — 黄金对话管理中心（原 HellGold Chat 2.0）
  - 四合一 AI 对话分析 HTML 看板
  - 模块：会话浏览 / 价值看板 / 提示词审计 / 批判镜
  - 零外部依赖，纯前端，离线即用
  - 数据不出本地，无需 API Key
  - [查看文档 →](./hallogoldchat/README.md)

### 📝 更新

- README 重编，新增 HalloCC 和 HalloGoldChat 介绍
- HellGold Chat 2.0 更名为 hallogoldchat，统一命名风格
- 安装脚本同步更新，支持一键安装全部 Skills
