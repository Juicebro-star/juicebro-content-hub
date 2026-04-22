# Changelog

本文件记录 `juicebro-content-hub` 的版本变更历史，格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/) 规范。

---

## [0.1.1] - 2025-04-23

### Fixed
- 替换所有文档中的占位符仓库地址（`yourname/juicebro-content-hub` → `Juicebro-star/juicebro-content-hub`）
- 修正 JSON Schema 文件中的 `$id` 字段为真实仓库 URL

### Changed
- README：新增"当前阶段说明"，明确本项目为 specification-first 阶段；补全账号矩阵可查询状态列；优化安装说明口吻（参考示例，非绝对命令）；新增辅助脚本定性说明
- `docs/installation.md`：安装命令统一替换为真实仓库地址；OpenClaw/Hermes 接入说明改为保守工程化表述，明确"请按当前版本文档调整"；V1 骨架脚本依赖说明更清晰
- `docs/safety.md`：新增整体定位声明（规范包 vs 爬虫系统）；骨架脚本免责声明独立成条；新增元宝/微信公众号平台限制说明；报告地址更新为真实 URL
- `skills/juicebro-content-hub/SKILL.md`：版本更新为 0.1.1；新增 `repository` 字段；账号矩阵表格补全可查询状态列；步骤 2 新增"公开结果不足时不推测内容"约束；重要约束新增"说明访问状态"条目；description 补充阶段说明；平台数量修正为 13
- `PUBLISHING.md`：仓库地址统一替换为真实地址

### Added
- `CHANGELOG.md`（本文件）

---

## [0.1.0] - 2025-04-20

### Added
- 初始化项目结构
- 13 平台账号矩阵（`skills/juicebro-content-hub/data/accounts.json`）
- 6 种查询意图路由规范（`data/query_intents.json`）
- 14 个主题关键词定义（`data/topic_keywords.json`）
- 13 个平台规则配置（`data/platform_rules.json`）
- 12 个平台适配器文档（`adapters/*.md`）
- `NormalizedPost` / `NormalizedResult` JSON Schema
- 5 个可复用提示模板（`prompts/*.md`）
- 4 个骨架辅助脚本（`scripts/*.py`，含类型标注和扩展点注释）
- 完整文档体系（`docs/architecture.md`、`installation.md`、`safety.md`、`supported-queries.md`、`roadmap.md`）
- 端到端输出样例（`examples/*.md`）
