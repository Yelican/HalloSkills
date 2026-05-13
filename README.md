# HalloSkills

基于 Claude Code 的自建自用 Skills 集合。覆盖工具发现、对话提炼等场景。

## 已有的 Skills

### 🛠 HalloTools — 工具雷达

每天自动从多个信息源挖掘新工具和开源项目，内置经典好工具推荐库。

**数据源：** GitHub Trending · Hacker News Show HN · 少数派 · GitHub Search（全部零认证，无需 API Key）

**触发方式：**
- 「今天有什么新工具」→ 拉取每日热门项目
- 「推荐几个笔记软件」→ 查询经典工具库
- 「搜一下 xxx 的开源项目」→ 按需全网搜索

[查看完整文档 →](./hallotools/SKILL.md)

---

### 💎 HalloChatGold — 对话淘金术

基于 6 个被验证思维模型（DIKW 金字塔、Kirkpatrick 评估、Peirce 洞察金字塔、Pearl 反事实因果、RACI 矩阵、复利效应评估）有机整合的 7 步对话价值提炼管道。

**方法论：** 收集 → 过滤 → 评估 → 提炼 → 验证 → 落地 → 预测

**触发方式：**
- 「帮我总结这次讨论」→ 完整 7 步提炼
- 「这次讨论有什么洞见」→ 精简洞察输出
- 「帮我把这段聊天结构化」→ 外部文本提炼

[查看完整文档 →](./hallochatgold/SKILL.md) | [诞生原理 →](./hallochatgold/BIRTH.md)

---

## 安装

### 方式一：git clone（推荐，可自动更新）

```bash
# 克隆整个仓库到本地
git clone https://github.com/Yelican/HalloSkills.git ~/.claude/skills-repo/HalloSkills

# 将需要的 skill 目录链接/复制到 Claude Code skills 目录
# Windows (PowerShell):
New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills\hallotools-1.0.0" -Target (Get-Item ".\hallotools").FullName
New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills\hallochatgold-1.0.0" -Target (Get-Item ".\hallochatgold").FullName

# macOS / Linux:
cp -r ~/.claude/skills-repo/HalloSkills/hallotools ~/.claude/skills/hallotools-1.0.0
cp -r ~/.claude/skills-repo/HalloSkills/hallochatgold ~/.claude/skills/hallochatgold-1.0.0
```

更新：
```bash
cd ~/.claude/skills-repo/HalloSkills && git pull
# 所有已复制的 skill 目录需手动同步
```

### 方式二：手动下载单个 Skill

1. 点击仓库页面的 Code → Download ZIP
2. 解压需要的 `hallotools/` 或 `hallochatgold/` 文件夹到 `~/.claude/skills/<name>-<version>/`

---

## 什么是 Claude Code Skill？

Skill 是 Claude Code 的扩展机制——一个 SKILL.md 文件定义触发条件和执行工作流，AI 读到后自动执行。不需要编程，只需要写清楚"什么时候触发、怎么做、输出什么"。

想自己写一个？参考 [skill-creator](https://github.com/anthropics/claude-code) 和本仓库的 SKILL.md 格式。

---

## License

MIT
