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

### 💎 HalloChatGold — 对话淘金术（v1.2）

基于 6 个被验证思维模型（DIKW 金字塔、Kirkpatrick 五级评估、Peirce 洞察金字塔、Pearl 反事实因果、RACI 矩阵、复利效应评估）有机整合的 7 步对话价值提炼管道。**不只是记笔记，是把讨论价值榨干。**

**方法论：** 收集 → 过滤 → 评估 → 提炼 → 验证 → 落地 → 预测

**v1.2 亮点：**
- 评分标准全面重构——从 0 起评、证据锚定、扣分项独立检查、审计触发，终结高分膨胀
- 每步新增质量检查清单（DIKW 分类红线、洞察肥皂剧测试、反事实三角验证、RACI 周一早测试）
- 复利评估从 1-10 改为 0-2 分，与 Kirkpatrick 全篇统一
- 知识半衰期来源修正为 Samuel Arbesman (2012)
- 导出排版规范落地（LaTeX/Chrome/Python 三档可选）

**触发方式：**
- 「帮我总结这次讨论」「提炼一下刚才聊的」→ 完整 7 步管道
- 「这段对话有什么洞见」「值得回顾吗」→ 精简输出
- 「感觉聊了很多但记不住」→ AI 主动提议提炼

[查看完整文档 →](./hallochatgold/SKILL.md) | [诞生原理 →](./hallochatgold/BIRTH.md)

---

## 安装

一行搞定，或者让你的 AI 帮你跑：

**Windows (PowerShell):**
```powershell
git clone https://github.com/Yelican/HalloSkills.git $env:TEMP\HalloSkills; Copy-Item "$env:TEMP\HalloSkills\hallotools" "$env:USERPROFILE\.claude\skills\hallotools-1.0.0" -Recurse; Copy-Item "$env:TEMP\HalloSkills\hallochatgold" "$env:USERPROFILE\.claude\skills\hallochatgold-1.2" -Recurse
```

**macOS / Linux:**
```bash
git clone https://github.com/Yelican/HalloSkills.git /tmp/HalloSkills && cp -r /tmp/HalloSkills/hallotools ~/.claude/skills/hallotools-1.0.0 && cp -r /tmp/HalloSkills/hallochatgold ~/.claude/skills/hallochatgold-1.2
```

**也可以直接对你的 AI 说：**
> 「去 github.com/Yelican/HalloSkills 把 hallochatgold 装到我的 skills 目录」

更新：重新跑上面的命令或者 `git pull` 后复制。

---

## 什么是 Claude Code Skill？

Skill 是 Claude Code 的扩展机制——一个 SKILL.md 文件定义触发条件和执行工作流，AI 读到后自动执行。不需要编程，只需要写清楚"什么时候触发、怎么做、输出什么"。

想自己写一个？参考 [skill-creator](https://github.com/anthropics/claude-code) 和本仓库的 SKILL.md 格式。

---

## License

MIT
