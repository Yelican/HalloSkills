# HalloSkills

Claude Code 的开源 Skills 集合。让 AI 成为你最好的工具发现伙伴。

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

## 安装

### 方式一：git clone（推荐，可自动更新）

**Windows (PowerShell):**
```powershell
git clone https://github.com/Yelican/HalloSkills.git $env:USERPROFILE\.claude\skills\hallotools-1.0.0
```

**macOS / Linux:**
```bash
git clone https://github.com/Yelican/HalloSkills.git ~/.claude/skills/hallotools-1.0.0
```

更新：
```bash
cd ~/.claude/skills/hallotools-1.0.0 && git pull
```

### 方式二：手动下载

1. 点击仓库页面的 Code → Download ZIP
2. 解压 `hallotools/` 文件夹到 `~/.claude/skills/hallotools-1.0.0/`

---

## 什么是 Claude Code Skill？

Skill 是 Claude Code 的扩展机制——一个 SKILL.md 文件定义触发条件和执行工作流，AI 读到后自动执行。不需要编程，只需要写清楚"什么时候触发、怎么做、输出什么"。

想自己写一个？参考 [skill-creator](https://github.com/anthropics/claude-code) 和本仓库的 SKILL.md 格式。

---

## 贡献

欢迎 PR 和 Issue。
- 发现好工具 → 编辑 `classic-tools.md` 提交 PR
- 有新的 Skill 想法 → 开 Issue 讨论
- 想把自己的 Skill 加进来 → Fork + PR

---

## License

MIT
