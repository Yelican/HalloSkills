# HalloSkills

基于 Claude Code 的自建自用 Skills 集合。覆盖备份、工具发现、对话提炼、对话分析等场景。

## 已有的 Skills

### 🗄 HalloCC — 全量备份工具（v1.0）

一键备份 Claude Code 全部配置、对话历史、Skills、环境信息，敏感信息自动脱敏，生成 HTML 看板。

**核心能力：**
- 备份 `~/.claude/` 全部核心数据
- 对话 JSONL + Skills + MCP 配置全覆盖
- API Key / token 等敏感信息自动扫描替换
- 可选生成 HTML 可视化看板

**触发方式：**
- `/hallocc` → 备份到桌面
- `/hallocc <路径>` → 备份到指定目录

[查看完整文档 →](./hallocc-1.0.0/SKILL.md)

---

### 🛠 HalloTools — 工具雷达（v1.0）

每天自动从多个信息源挖掘新工具和开源项目，内置经典好工具推荐库。

**数据源：** GitHub Trending · Hacker News Show HN · 少数派 · GitHub Search（全部零认证，无需 API Key）

**触发方式：**
- 「今天有什么新工具」→ 拉取每日热门项目
- 「推荐几个笔记软件」→ 查询经典工具库
- 「搜一下 xxx 的开源项目」→ 按需全网搜索

[查看完整文档 →](./hallotools/SKILL.md)

---

### 💎 HalloGoldChat — 对话淘金术 + 聚合看板（v3.0）

基于 6 个被验证思维模型（DIKW 金字塔、Kirkpatrick 五级评估、Peirce 洞察金字塔、Pearl 反事实因果、RACI 矩阵、复利效应评估）的 7 步对话价值提炼管道 + 自动存档 + 聚合看板。

**架构亮点：**
- Claude 在对话中执行真实 7 步分析（不是 Python 假数据）
- 每次复盘结果自动存档为 JSON 到 `~/.claude/hallo-gold-chat/reports/`
- `build.py` 聚合所有存档生成自包含 HTML 看板，双击即开
- SessionEnd hook 自动更新看板，无需手动操作

**核心流程：**
```
深度讨论 → "凡哥来个复盘" → 报告输出 + 自动存档 JSON → 看板自动更新
```

**触发方式：**
- 「帮我总结这次讨论」「提炼一下刚才聊的」→ 完整 7 步管道
- 「这段对话有什么洞见」「值得回顾吗」→ 精简输出
- 复盘后看板自动更新，桌面 `HalloChatGold 看板.html` 双击查看

[查看完整文档 →](./hallogoldchat-v3.0/SKILL.md) | [诞生原理 →](./hallogoldchat-v3.0/BIRTH.md) | [聚合脚本 →](./hallogoldchat-v3.0/build.py)

---

## 安装

一行搞定，或者让你的 AI 帮你跑：

**Windows (PowerShell):**
```powershell
git clone https://github.com/Yelican/HalloSkills.git $env:TEMP\HalloSkills; Copy-Item "$env:TEMP\HalloSkills\hallotools" "$env:USERPROFILE\.claude\skills\hallotools-1.0.0" -Recurse; Copy-Item "$env:TEMP\HalloSkills\hallogoldchat-v3.0" "$env:USERPROFILE\.claude\skills\hallogoldchat-3.0.0" -Recurse; Copy-Item "$env:TEMP\HalloSkills\hallocc-1.0.0" "$env:USERPROFILE\.claude\skills\hallocc-1.0.0" -Recurse
```

**macOS / Linux:**
```bash
git clone https://github.com/Yelican/HalloSkills.git /tmp/HalloSkills && cp -r /tmp/HalloSkills/hallotools ~/.claude/skills/hallotools-1.0.0 && cp -r /tmp/HalloSkills/hallogoldchat-v3.0 ~/.claude/skills/hallogoldchat-3.0.0 && cp -r /tmp/HalloSkills/hallocc-1.0.0 ~/.claude/skills/hallocc-1.0.0
```

**也可以直接对你的 AI 说：**
> 「去 github.com/Yelican/HalloSkills 把 hallogoldchat-v3.0 装到我的 skills 目录」

更新：重新跑上面的命令或者 `git pull` 后复制。

---

## 什么是 Claude Code Skill？

Skill 是 Claude Code 的扩展机制——一个 SKILL.md 文件定义触发条件和执行工作流，AI 读到后自动执行。不需要编程，只需要写清楚"什么时候触发、怎么做、输出什么"。

想自己写一个？参考 [skill-creator](https://github.com/anthropics/claude-code) 和本仓库的 SKILL.md 格式。

---

## License

MIT
