# juicebro-content-hub

> 果汁哥内容聚合 Skill —— 让 Agent 能够查询、汇总、导航"果汁哥"全平台公开内容

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Skill Version](https://img.shields.io/badge/skill%20version-0.1.1-blue)](./skills/juicebro-content-hub/SKILL.md)
[![Platform Coverage](https://img.shields.io/badge/platforms-13-green)](./skills/juicebro-content-hub/adapters/)

---

## 这是什么

`juicebro-content-hub` 是一个供 OpenClaw、Hermes、Claude Code 及兼容 AgentSkills 生态使用的果汁哥公开内容聚合 skill。安装后 Agent 可围绕"果汁哥"的全平台公开内容进行自然语言查询、汇总和导航。

**当前阶段说明**：本项目处于 specification-first / skill-package-first 阶段，核心交付物为账号矩阵、意图路由规范、平台适配器文档和标准化 Schema，数据获取依赖 Agent 自身的公开内容访问能力（V2 将引入 RSS/API 数据接入层）。

**这不是一个静态资料展示页**，而是一个内容聚合中台 Skill，能够响应各种自然语言意图，包括：

- 全平台查询（果汁哥今天发了什么？）
- 单平台查询（果汁哥今天微博发了什么？）
- 主题过滤（果汁哥最近关于比特币发了什么？）
- 内容形态筛选（果汁哥最近有哪些视频？）
- 汇总报告（把果汁哥今天更新做成日报）
- 导航推荐（看投资内容去哪个平台？）

---

## 账号矩阵

| 类别 | 平台 | 账号名 | 可查询 |
|------|------|--------|--------|
| 日常分享 | 微博 | 果汁哥6688 | ✅ |
| 日常分享 | 小红书 | guozhige | ✅ |
| 日常分享 | 抖音 | 果汁哥的知识分享 / Roaring_Kitty | ✅ |
| 日常分享 | 快手 | 果汁哥 | ✅ |
| 日常分享 | bilibili | 果汁哥juicebro | ✅ |
| 日常分享 | 元宝 | 果汁哥 | ⚠️ 待确认 |
| 日常分享 | 微信（私域） | guozhige2024 | ❌ 私域 |
| 投资主题 | 雪球 | juicebro | ✅ |
| 投资主题 | 今日头条 | 果汁哥的知识分享 | ✅ |
| 投资主题 | 微信公众号 | 果汁哥的知识分享 | ⚠️ 部分 |
| 投资主题 | 知识星球 | 果汁哥私享圈 | ❌ 付费 |
| 播客 | 喜马拉雅 | 果汁哥juicebro | ✅ |
| 播客 | 小宇宙 | 果汁哥 | ✅ |

---

## 支持的查询类型（示例）

```
果汁哥今天发了什么
果汁哥最近三天发了什么
果汁哥今天微博发了什么
果汁哥最近雪球发了什么
果汁哥最近关于比特币发了什么
果汁哥最近关于黄金发了什么
果汁哥最近有哪些视频
果汁哥最近有哪些文章
果汁哥最近有哪些音频
把果汁哥最近一周内容按平台整理一下
把果汁哥今天更新做成日报
看投资内容去哪个平台
```

完整的支持查询列表见 [docs/supported-queries.md](./docs/supported-queries.md)。

---

## 项目结构

```
juicebro-content-hub/
├── README.md                    # 本文件
├── LICENSE                      # MIT 许可证
├── CHANGELOG.md                 # 版本变更记录
├── .gitignore
├── docs/
│   ├── architecture.md          # 架构设计说明
│   ├── supported-queries.md     # 完整查询意图列表
│   ├── installation.md          # 安装指南
│   ├── safety.md                # 安全声明
│   └── roadmap.md               # 演进路线
├── skills/
│   └── juicebro-content-hub/
│       ├── SKILL.md             # Skill 入口（YAML frontmatter + 描述）
│       ├── data/                # 静态数据（账号、规则、意图、关键词）
│       ├── prompts/             # 可复用提示模板
│       ├── adapters/            # 各平台适配说明
│       ├── examples/            # Skill 内查询示例
│       └── schemas/             # 数据规范 JSON Schema
├── scripts/                     # 可选辅助脚本（占位型骨架，非生产爬虫）
└── examples/                    # 端到端输出样例
```

---

## 快速开始

> **注意**：以下安装命令为参考示例，请按你所使用的 Agent 版本和 CLI 文档确认实际用法。

### Claude Code / npx skills 安装

```bash
npx skills add Juicebro-star/juicebro-content-hub --skill juicebro-content-hub -g -y
```

### OpenClaw 接入

在 OpenClaw 的 skills 配置中添加（请参考当前 OpenClaw 文档确认配置格式）：

```yaml
skills:
  - source: github
    repo: Juicebro-star/juicebro-content-hub
    skill: juicebro-content-hub
```

### Hermes 接入

将本仓库地址作为 GitHub skill 源告知 Hermes：

```
这是一个 GitHub 可安装 Skill：https://github.com/Juicebro-star/juicebro-content-hub
Skill 入口在 skills/juicebro-content-hub/SKILL.md
```

### 通用 AgentSkills 生态

```bash
git clone https://github.com/Juicebro-star/juicebro-content-hub.git
```

将 `skills/juicebro-content-hub/` 目录注册到你的 Agent 框架的 Skill 搜索路径中。

详细安装说明见 [docs/installation.md](./docs/installation.md)。

---

## 设计原则

1. **公开内容优先**：只聚合平台公开可见内容，不做隐蔽抓取，不绕过登录
2. **透明说明限制**：若平台公开访问受限，明确告知，不编造结果
3. **标准化输出**：所有内容统一规范为标准字段（platform / account / publish_time / title / summary / content_type / topic_tags / source_locator）
4. **去重处理**：考虑跨平台重复发布内容的合并
5. **多维汇总**：支持按平台、按时间、按主题、按内容形态的不同聚合视角

---

## 关于辅助脚本

`scripts/` 目录下包含四个辅助脚本（`optional_fetcher.py`、`normalize_results.py`、`dedupe_posts.py`、`topic_classifier.py`），均为**占位型骨架脚本**：设计为可扩展的接口定义，附有类型标注和扩展点注释，不包含真实爬虫逻辑，不包含绕过反爬机制的代码。V2 阶段将基于这些接口扩展真实的 RSS/API 数据接入能力。详见 [scripts/README.md](./scripts/README.md)。

---

## 安全声明

本 Skill 不执行任何危险系统操作，不默认保存私密凭证，不做隐蔽命令执行，不尝试绕过平台登录。
详见 [docs/safety.md](./docs/safety.md)。

---

## 文档导航

| 文档 | 说明 |
|------|------|
| [docs/architecture.md](./docs/architecture.md) | 整体架构与数据流 |
| [docs/supported-queries.md](./docs/supported-queries.md) | 完整查询意图清单 |
| [docs/installation.md](./docs/installation.md) | 安装与接入指南 |
| [docs/safety.md](./docs/safety.md) | 安全与合规声明 |
| [docs/roadmap.md](./docs/roadmap.md) | V1/V2/V3 演进路线 |
| [CHANGELOG.md](./CHANGELOG.md) | 版本变更记录 |

---

## 贡献

欢迎提交 Issue 反馈账号变更、平台访问限制变化，或通过 PR 添加新平台适配器、改进提示模板。详见各文件中的扩展点说明。

## License

MIT © 2025 juicebro-content-hub contributors
