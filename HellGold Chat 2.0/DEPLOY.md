---
name: hellgold-chat-2.0-deploy
description: 完整部署 HellGold Chat 2.0 到新设备的 AI 可读指令
---

# HellGold Chat 2.0 · AI 部署指令

你是 Claude Code 实例。请执行以下步骤在本机完整部署 **HellGold Chat 2.0**——一个零外部依赖的 AI 对话分析看板。

## 任务目标

1. 确认环境就绪
2. 从用户提供的打包目录中获取文件
3. 运行主脚本
4. 验证输出
5. （可选）配置自动更新

---

## 第一步：环境检查

```bash
# 确认 Python 3 可用
python --version

# 确认是 Claude Code 用户且有对话数据
ls ~/.claude/projects/*.jsonl 2>/dev/null

# 如果没有对话记录，提醒用户先跟 AI 聊几次
```

如果 `~/.claude/projects/` 下没有 `.jsonl` 文件，提示用户："还没有对话数据，请先使用 Claude Code 进行几次对话。"

## 第二步：定位打包目录

用户提供的打包目录位于桌面：

```bash
ls ~/Desktop/HellGold\ Chat\ 2.0/
```

应包含以下文件：

| 文件 | 必须 | 用途 |
|------|------|------|
| `hellgold-chat-2.0.py` | ✅ | 主脚本（Python 导出 + HTML 生成器） |
| `SKILL.md` | ❌ | Claude Code Skill 定义 |
| `README.md` | ❌ | 使用说明 |

如果缺少 `hellgold-chat-2.0.py`，请让用户从源设备重新拷贝。

## 第三步：运行主脚本

```bash
cd ~/Desktop/HellGold\ Chat\ 2.0/
python hellgold-chat-2.0.py
```

### 预期输出

```
Scanning sessions...
Found N sessions, M messages
Done: ~/Desktop/HellGold Chat 2.0.html
```

### 常见问题处理

- **报错 `No sessions found`**：说明 `~/.claude/projects/` 下没有对话数据。让用户先使用 Claude Code 产生对话。
- **报错 Python 编码问题**：Windows 下如果遇到 GBK 编码错误，用以下方式运行：
  ```bash
  python -X utf8 hellgold-chat-2.0.py
  ```
- **脚本执行超时**：如果对话数据很多（几千条），扫描可能需要 10-30 秒。正常现象。

## 第四步：验证生成结果

```bash
# 确认 HTML 文件生成
ls -lh ~/Desktop/HellGold\ Chat\ 2.0.html

# 确认文件大小在 300KB-2MB 之间
# 确认文件包含预期内容
grep -c "tab-panel\|ALL_SESSIONS\|genAnalysis" ~/Desktop/HellGold\ Chat\ 2.0.html
```

告诉用户打开 `~/Desktop/HellGold Chat 2.0.html`，在浏览器中查看。

如果用户问起，解释四个 Tab 的功能：
- 💬 **会话**：气泡式对话回放，左侧项目分组，可搜索可筛选
- 💎 **价值**：Kirkpatrick 五级评估 + DIKW 内容分层 + 核心洞察 + RACI 行动清单
- 🎯 **提示词**：10 维质量评分，每条可展开看详情，共性强弱项含改写示例
- 🪞 **批判镜**：总体判断 + 盲点检测 + 偏误分析 + 逻辑断裂 + 元认知挑战 + 改进路线

## 第五步：配置自动更新（可选）

每次 Claude Code 对话结束后自动刷新看板。

1. 复制脚本到共享目录：
```bash
cp ~/Desktop/HellGold\ Chat\ 2.0/hellgold-chat-2.0.py ~/.claude/shared-scripts/
```

2. 编辑 `~/.claude/settings.json`，在 `"hooks"` 节点添加：

```json
"SessionEnd": [
  {
    "hooks": [
      {
        "type": "command",
        "command": "python ~/.claude/shared-scripts/hellgold-chat-2.0.py"
      }
    ]
  }
]
```

3. 验证：跟用户说"下次对话结束后桌面的 HTML 就会自动更新"。

## 第六步：通知用户

报告以下信息：

- ✅ 部署完成
- 📄 看板位置：`~/Desktop/HellGold Chat 2.0.html`
- 📊 扫描到 N 个会话，M 条消息
- 🔄 是否配置了自动更新
- 💡 提示：HTML 文件零外部依赖，可以直接复制到其他电脑上打开

---

## 脚本原理简介（如果用户问起）

`hellgold-chat-2.0.py` 是一个自包含 Python 脚本，功能链为：

```
读取 ~/.claude/projects/*.jsonl
  → 解析每条消息（角色 + 时间戳 + 内容）
  → 生成分析数据（Kirkpatrick 评分、10 维提示词打分、偏误检测）
  → 输出单文件 HTML（数据 + CSS + JS 全内嵌）
```

分析引擎运行在浏览器端（JS），采用启发式算法而非 LLM 推理，所以速度很快（秒级），且**不需要 API Key、不需要联网、数据不出本地**。

## 技术约束

- 仅支持 Claude Code JSONL 格式（不兼容 ChatGPT / DeepSeek）
- 分析数据为启发式估算，方向性正确但不精确
- 如需精确 LLM 分析，需要接入 API（当前版本不包含）
