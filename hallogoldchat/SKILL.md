---
name: hallogoldchat
description: 一键生成 HellGold Chat 暗色科技风 AI 对话分析看板（含价值评估、提示词审计、批判镜）。数据与 CC会话管理中心同源，独立运行，零外部依赖，离线即用。
---

# HalloGoldChat · 黄金对话管理中心

**把每一次 AI 对话变成认知资产。** 一键生成暗色科技风 HTML 看板，四个维度审视你的 AI 交互质量。

---

## 触发条件

| 用户问法 | 动作 |
|---------|------|
| "生成对话分析看板" / "更新 HellGold" / "生成看板" | 运行主脚本 |
| "我的提示词有什么问题" / "帮我看看对话质量" | 引导用户打开已有 HTML |
| "安装 HellGold Chat" | 执行安装步骤 |

## 功能模块

| 模块 | 核心能力 |
|------|---------|
| 💬 会话浏览 | 气泡式对话回放、全局搜索、项目分组、仅对话/全部/仅工具筛选 |
| 💎 价值看板 | Kirkpatrick 五级评估 + DIKW 内容分层 + 反事实价值 + 核心洞察 + RACI 行动清单 |
| 🎯 提示词审计 | 10维质量评分 + 逐条可展开分析 + 共性弱项 + 改写示例 |
| 🪞 批判镜 | 盲点检测 + 认知偏误分析 + 逻辑断裂 + 元认知挑战 + 改进路线图 |

## 数据来源

扫描 `~/.claude/projects/` 目录下所有 Claude Code 对话 JSONL 文件，与 CC会话管理中心同源，但完全独立运行。不需要安装任何其他工具。

## 使用方式

```bash
# 命令行直接运行
python hellgold-chat-2.0.py

# 指定输出目录
python hellgold-chat-2.0.py /path/to/output

# 输出文件：HalloGoldChat.html（桌面）
```

在浏览器中打开生成的 HTML 文件即可使用。**零外部依赖、纯 CSS、无 CDN、离线即开即用。**

## 安装

```bash
# 1. 复制脚本到 Claude Code 共享脚本库
cp hellgold-chat-2.0.py ~/.claude/shared-scripts/

# 2. （可选）配置 Claude Code hook 自动更新
# 在 ~/.claude/settings.json 中添加：
# "hooks": {
#   "SessionEnd": [
#     { "command": "python ~/.claude/shared-scripts/hellgold-chat-2.0.py" }
#   ]
# }

# 3. 首次运行
python ~/.claude/shared-scripts/hellgold-chat-2.0.py
```

## 技术特点

- 单文件 HTML 输出（~500KB），数据完全内嵌
- 暗色科技风设计，毛玻璃卡片 + 渐变标题
- 零外部依赖：无 Chart.js / Bootstrap / CDN 引用
- 纯 CSS 可视化：进度条、圆点矩阵、色块图、表格
- 所有评分可展开查看证据链和评分标准
- 明/暗主题一键切换，偏好自动保存

## 设计哲学

不是教你"怎么用 AI"，而是让你**看清自己是怎么用 AI 的**——然后自己决定要不要改。
