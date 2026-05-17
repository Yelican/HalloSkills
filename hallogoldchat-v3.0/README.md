# HalloGoldChat v3.0 · 对话淘金 + 聚合看板

合并自 hallochatgold（对话淘金术 skill）+ hallogoldchat（看板构建器）。

## 文件说明

- `SKILL.md` — 对话淘金术 7 步管道定义 + 自动存档指令
- `BIRTH.md` — 6 个底层模型的溯源和整合逻辑
- `build.py` — 聚合脚本，读取存档 JSON 生成自包含 HTML 看板
- `_meta.json` — 技能注册元数据

## 工作流程

1. 和 Claude 进行深度讨论
2. 说「凡哥来个复盘」或「总结一下刚才聊的」
3. hallogoldchat skill 执行 7 步管道 → 输出报告 → 自动存档 JSON
4. 终端跑 `python build.py` → 桌面生成看板
5. 双击 `HalloChatGold 看板.html`，所有历史分析一目了然

## 数据存储

报告 JSON：`~/.claude/hallo-gold-chat/reports/`
