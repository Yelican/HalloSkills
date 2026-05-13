---
name: hallotools
description: 工具雷达 —— 每日新工具/项目发现 + 经典好工具推荐。当你问"今天有什么新工具"、"GitHub上有什么好项目"、"推荐几个工具"、"有没有xx类的工具"、"最近有什么好用的"、"我去哪儿找xx"、"什么工具能帮xx"、"效率工具推荐"、"最近在流行什么工具"等任何工具/项目发现类问题时触发。让眼界永远大于能力。
---

# HalloTools Skill

HalloTools 是一个工具发现引擎。每天自动从多个信息源挖掘新工具和项目，同时内置一份经典好工具推荐库。

核心理念：**眼界大于能力** —— 你不知道某个工具存在，就永远无法用它解决你的问题。

## 触发条件

任何关于"找工具/发现项目/推荐软件"的问题都触发。

| 用户问法 | 工作流 |
|---|---|
| "今天有什么新工具"、"工具日报"、"GitHub 有什么好项目"、"最近在流行什么" | **A：每日新鲜货** |
| "推荐几个xx工具"、"有没有xx类的"、"除了xx还有啥替代品" | **B：经典工具查询** |
| "搜一下最近关于xx的项目"、"有没有类似xx的开源替代" | **B/C：经典查找 + 按需搜索** |

---

## 信息源（全部零认证，无需 API Key）

| # | 源 | 获取方式 | 覆盖 |
|---|---|---|---|
| 1 | **GitHub Trending** | curl HTML → Python 解析 | 开源项目/开发者工具 |
| 2 | **Hacker News Show HN** | Algolia REST API → JSON | 独立开发者新产品 |
| 3 | **少数派 RSS** | curl XML → 关键词过滤 | 中文效率工具/数字生活 |
| 4 | **GitHub Search** | 官方 REST API → JSON | 按关键词补漏搜索 |

### 各源速览

**GitHub Trending**
```
https://github.com/trending?since=daily
HTML → <article class="Box-row"> 每个仓库
  提取: h2 a → 仓库名, p → 描述, itemprop → 语言, 数字 → 今日 star 数
```

**HN Show HN (Algolia)**
```
https://hn.algolia.com/api/v1/search_by_date?tags=show_hn&hitsPerPage=30&numericFilters=points>5
JSON → .hits[] → {title, url, points, num_comments, created_at, objectID}
```

**少数派 RSS**
```bash
curl -sL "https://www.sspai.com/feed" -H "User-Agent: Mozilla/5.0"
XML → <item> → <title>, <link>, <description>, <pubDate>
过滤关键词: "App", "工具", "推荐", "评测", "新玩意", "利器", "效率"
```

**GitHub Search**
```
https://api.github.com/search/repositories?q=KEYWORD&sort=stars&order=desc&per_page=20
Header: Accept: application/vnd.github.v3+json
JSON → .items[] → {full_name, html_url, description, stargazers_count, language}
```

---

## 工作流 A：每日新鲜货

**触发：** "今天有什么新工具" / "工具日报" / "最近在流行什么"

### 执行步骤

1. **并发拉取 3 个源**
   ```bash
   # 源1: GitHub Trending (daily)
   curl -s -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
     "https://github.com/trending?since=daily" > /tmp/gh_trending.html

   # 源2: HN Show HN (近 48 小时，>5 分)
   curl -s "https://hn.algolia.com/api/v1/search_by_date?tags=show_hn&hitsPerPage=30&numericFilters=points>5" \
     > /tmp/hn_show.json

   # 源3: 少数派 RSS（最近 10 篇）
   curl -sL -H "User-Agent: Mozilla/5.0" "https://www.sspai.com/feed" \
     > /tmp/sspai_rss.xml
   ```

2. **解析去重** — 提取标题/描述/链接/热度，跨源同名项目去重

3. **排序** — GitHub Trending 按今日 star 数、HN 按 points、少数派按发布时间

4. **输出** — 见下方格式

### 输出格式

```markdown
**🛠 HalloTools 日报 · 2026-05-13**

## 🔥 GitHub Trending 今日热榜
1. **owner/repo** — 🌟 X,XXX stars today
   一句话描述
   https://github.com/owner/repo

## 💡 Hacker News Show HN
2. **Project Name: 一句话介绍** — XXX pts | XX 讨论
   https://...

## 📱 少数派工具推荐
3. **文章标题**
   https://sspai.com/post/...

---
**数据源: GitHub Trending / HN Show HN / 少数派 · 共 N 条**
```

**规则：**
- **全局编号**贯穿全文 (1, 2, 3 ... N)，不在每个版块内重新计数
- 每条**必须有可访问链接**
- 每条有**一句话描述**（原样或精炼）
- 时间转人话（"2 小时前"、"今天上午"、"昨天"），不贴 ISO 时间戳
- 今日数据 < 5 条时，自动扩大到最近 3 天
- 描述不超过 160 字

---

## 工作流 B：经典工具查询

**触发：** "推荐几个xx工具" / "有没有xx类的" / "什么xx好用"

### 执行步骤

1. 读 `references/classic-tools.md`
2. 按分类/关键词匹配
3. 命中 → 排序列出；未命中 → 回退到工作流 C

### 输出格式

```markdown
**🛠 HalloTools · <分类> 推荐**

| 工具 | 介绍 | 网站 | 开源 |
|---|---|---|---|
| **Obsidian** | 本地 Markdown 笔记，插件生态丰富 | obsidian.md | ❌ (核心闭源) |
| **思源笔记** | 国产替代，块级引用 + 本地优先 | b3log.org/siyuan | github.com/siyuan-note/siyuan |
```

经典工具库覆盖 10 个分类：AI/LLM · 效率/自动化 · 笔记/知识管理 · 写作/排版 · 微信/社交管理 · 开发工具 · 文件/传输/备份 · 数据/可视化 · 设计/创意 · 其他神器

---

## 工作流 C：按需搜索

**触发：** 工作流 B 未命中，或用户明确要搜索

```bash
# GitHub 搜索
curl -s "https://api.github.com/search/repositories?q=<KEYWORD>&sort=stars&order=desc&per_page=15" \
  -H "Accept: application/vnd.github.v3+json"

# HN Algolia 搜索
curl -s "https://hn.algolia.com/api/v1/search_by_date?tags=show_hn&query=<KEYWORD>&hitsPerPage=10"
```

---

## 安装与使用

### 安装

```bash
# 克隆到 Claude Code skills 目录
# Windows (PowerShell)
git clone https://github.com/YOUR_USERNAME/HalloSkills.git $env:USERPROFILE\.claude\skills\hallotools-1.0.0

# macOS / Linux
git clone https://github.com/YOUR_USERNAME/HalloSkills.git ~/.claude/skills/hallotools-1.0.0
```

或手动下载 `hallotools/` 文件夹放到 `~/.claude/skills/hallotools-1.0.0/`。

### 定时推送（可选）

通过 Claude Code CronCreate 设置每天自动推送日报：

```
CronCreate cron="37 8 * * *" recurring=true durable=true
  prompt="触发 HalloTools Skill，拉今日工具日报，输出到终端（或写入你常用的笔记软件）"
```

时间选整点过后随机分钟数，避免高峰拥堵。

---

## 常见问题

- **GitHub Trending 403** → 换 User-Agent 重试，或回退到 GitHub Search API
- **HN Algolia 空返回** → 可能限流，等 5 秒重试，或降 `points>5` 到 `points>1`
- **少数派 RSS 301** → 必须用 `-L` 跟随重定向
- **所有源都挂了**（罕见）→ 诚实说明，不要编造数据

---

## 不要做

- 不要推荐无法访问/已下架的工具
- 不要编造描述或评分数据
- 不要向用户暴露 API 参数细节（如 `?tags=show_hn&hitsPerPage=30`）
- 不要把经典工具和每日新鲜货混在同一输出
- 不要在用户问具体分类时返回全库所有条目
- 不要把 HalloTools 和 AIHot（AI 资讯 Skill）搞混
