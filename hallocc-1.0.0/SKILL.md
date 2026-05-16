---
name: hallocc
description: "HalloCC —— Claude Code 全量备份工具。一键备份配置、对话历史、Skills、环境清单到桌面，敏感信息自动脱敏，生成 HTML 看板。跨平台（Windows / macOS / Linux）。"
user-invocable: true
---

# HalloCC —— Claude Code 全量备份

## 触发

- `/hallocc` — 备份到桌面（默认 `~/Desktop/HalloCC-备份-{日期}/`）
- `/hallocc <路径>` — 备份到指定目录

## 备份内容

| 内容 | 说明 |
|------|------|
| `~/.claude/` 核心数据 | CLAUDE.md、对话 JSONL、Skills、shared-scripts、memory、settings.json、.mcp.json |
| 项目配置 | 工作目录下的 `.claude/settings*.json` |
| 环境清单 | 自动探测 node/python/git/gh/curl 版本，记录 MCP 配置 |
| HTML 看板 | 对话历?+ Skills + MCP 可视化（需 python3，可选） |
| 恢复指南 | RESTORE.md + 脱敏标记 |

**不备份**：tool-results 缓存、telemetry、shell-snapshots、sessions 等运行时临时文件。

## 敏感信息处理

自动扫描并替换为占位符（恢复后需重新配置）：
- `sk-xxx` API Key（OpenAI / DeepSeek 等）
- `token`、`apiKey`、`api_key`、`secret`、`password` 字段值
- JWT token

## 执行步骤

当用户输入 `/hallocc` 或 `/hallocc <路径>` 时：

1. **确认输出目录**：用户指定 or 默认桌面
2. **准备备份脚本**：
   - 检查 `~/.claude/shared-scripts/hallocc/backup.sh` 是否存在
   - 如果不存在，从下面的代码块创建它
3. **执行备份**：`bash ~/.claude/shared-scripts/hallocc/backup.sh [输出目录]`
4. **可选看板**：如果有 python3，执行 `~/.claude/shared-scripts/hallocc/dashboard.sh [备份目录]`
5. **报告结果**：输出目录、大小、会话数、Skill 数

## 跨平台说明

- Windows：Git Bash 环境下运行（Claude Code 自带）
- macOS / Linux：原生 bash
- 依赖工具：bash、cp、find、sed、grep、date
- 可选增强：python3（用于 HTML 看板生成）
