---
name: juicebro-content-hub
version: 0.1.1
description: >
  果汁哥内容聚合 Skill。让 Agent 能够查询、汇总和导航"果汁哥"在微博、小红书、
  抖音、B站、雪球、头条、公众号、小宇宙等 13 个平台上的公开内容。
  支持全平台总查、单平台查询、主题过滤、内容形态筛选、汇总报告生成和平台导航推荐。
  注意：本 Skill 处于 specification-first 阶段，内容获取依赖 Agent 自身的公开访问能力。
author: juicebro-content-hub contributors
license: MIT
repository: https://github.com/Juicebro-star/juicebro-content-hub
tags:
  - content-aggregation
  - juicebro
  - chinese-social-media
  - multi-platform
  - kol-tracking
triggers:
  - 果汁哥今天发了什么
  - 果汁哥最近发了什么
  - 果汁哥.*平台.*发了什么
  - 果汁哥.*关于.*发了什么
  - 果汁哥.*有哪些.*视频
  - 果汁哥.*有哪些.*文章
  - 果汁哥.*有哪些.*音频
  - 把果汁哥.*整理
  - 果汁哥.*日报
  - 看.*内容去哪个平台
  - 果汁哥在哪.*发
data_dir: ./data
prompts_dir: ./prompts
adapters_dir: ./adapters
schemas_dir: ./schemas
examples_dir: ./examples
requires:
  agent_capabilities:
    - web_browsing         # 访问公开网页内容
    - markdown_output      # 格式化输出
  optional_capabilities:
    - rss_parsing          # V2 新增：RSS 订阅解析
    - local_cache          # V2 新增：本地缓存读写
safety:
  no_system_commands: true
  no_credential_storage: true
  no_login_bypass: true
  public_content_only: true
---

# juicebro-content-hub Skill

## 概述

本 Skill 是"果汁哥内容聚合中台"，安装后 Agent 可以回答以下类型的问题：

- **全平台总查**：今天/最近 N 天/最近一周，全平台有什么更新
- **平台单查**：指定微博/小红书/抖音/B站/雪球/头条/公众号/小宇宙/喜马拉雅等平台的查询
- **主题查询**：过滤比特币、黄金、美股、AI、特朗普等特定主题的内容
- **内容形态查询**：过滤视频/文章/音频/短帖/图文等内容类型
- **汇总报告**：生成日报、周报、按平台/主题/形态的结构化摘要
- **导航推荐**：推荐适合特定内容类型的平台

**重要说明**：本 Skill 依赖 Agent 的公开网页访问能力获取内容，不包含内置数据爬取逻辑。部分平台存在公开索引限制，查询结果因访问环境而异。

---

## 账号矩阵（权威数据源）

加载 `data/accounts.json` 获取完整的账号矩阵。

快速参考：

| 平台 | 账号 | 类别 | 可查询 |
|------|------|------|--------|
| 微博 | 果汁哥6688 | 日常分享 | ✅ |
| 小红书 | guozhige | 日常分享 | ✅ |
| 抖音 | 果汁哥的知识分享 / Roaring_Kitty | 日常分享 | ✅ |
| 快手 | 果汁哥 | 日常分享 | ✅ |
| bilibili | 果汁哥juicebro | 日常分享 | ✅ |
| 元宝 | 果汁哥 | 日常分享 | ⚠️ 待确认 |
| 微信（私域） | guozhige2024 | 日常分享 | ❌ 私域 |
| 雪球 | juicebro | 投资主题 | ✅ |
| 知识星球 | 果汁哥私享圈 | 投资主题（付费）| ❌ 付费 |
| 今日头条 | 果汁哥的知识分享 | 投资主题 | ✅ |
| 微信公众号 | 果汁哥的知识分享 | 投资主题 | ⚠️ 部分 |
| 喜马拉雅 | 果汁哥juicebro | 播客 | ✅ |
| 小宇宙 | 果汁哥 | 播客 | ✅ |

---

## 使用流程

### 步骤 1：意图识别

收到用户查询后，参照 `data/query_intents.json` 识别意图类型：

```
intent_type: all_platform_query | platform_single_query | topic_query |
             content_type_query | aggregation_report | navigation_recommend
```

并提取：
- `platforms`：用户指定的平台（无则全选 is_queryable=true 的平台）
- `time_range`：today / last_3_days / last_7_days / last_30_days
- `topic`：主题标签（参照 `data/topic_keywords.json`）
- `content_type`：video / article / audio / short_post / image_post
- `output_format`：list / digest / report

### 步骤 2：平台适配

对每个目标平台：
1. 查 `data/accounts.json` 获取账号信息
2. 查 `data/platform_rules.json` 确认查询策略
3. 参照 `adapters/{platform}.md` 了解字段提取方式和失败处理
4. 若平台 `is_queryable: false`，直接输出限制说明，跳过该平台
5. 若平台可查询但访问结果不足，明确说明，不推测或补充内容

### 步骤 3：内容规范化

将各平台内容规范化为 `NormalizedPost` 格式（见 `schemas/normalized_post.schema.json`）：

```json
{
  "platform": "weibo",
  "account": "果汁哥6688",
  "publish_time": "2024-01-15T10:30:00+08:00",
  "title": null,
  "summary": "今天聊聊比特币最新走势...",
  "content_type": "short_post",
  "topic_tags": ["bitcoin", "crypto"],
  "source_locator": "https://weibo.com/...",
  "dedupe_hash": "a3f2c1..."
}
```

### 步骤 4：去重与汇总

- 计算 `dedupe_hash`，合并跨平台重复内容
- 根据意图选择汇总提示：
  - 时间汇总 → `prompts/summarize_recent_posts.md`
  - 平台汇总 → `prompts/summarize_by_platform.md`
  - 主题汇总 → `prompts/summarize_by_topic.md`
  - 字段提取 → `prompts/extract_post_fields.md`
  - 无结果或受限 → `prompts/fallback_response.md`

### 步骤 5：输出

按 `schemas/normalized_result.schema.json` 格式输出，使用 Markdown 美化。

---

## 重要约束

1. **不编造内容**：若平台无法访问或公开结果不足，说明原因，不推测或虚构内容
2. **不绕过登录**：付费/需登录内容直接说明受限，不尝试绕过
3. **标注来源**：每条内容必须标注 platform + account + source_locator
4. **去重优先**：跨平台相同内容合并展示，不重复列举
5. **说明访问状态**：每次查询在输出中标注各平台的访问状态（成功/受限/无内容）

---

## 扩展点

- 新增平台：添加 `adapters/{platform}.md` + 更新 `data/accounts.json` 和 `data/platform_rules.json`
- 新增主题：更新 `data/topic_keywords.json`
- 改进输出：优化 `prompts/*.md` 中的提示模板
- 接入真实数据源（V2）：实现 `scripts/optional_fetcher.py` 中的平台方法

---

## 参考文档

- [账号矩阵](./data/accounts.json)
- [平台规则](./data/platform_rules.json)
- [查询意图](./data/query_intents.json)
- [主题关键词](./data/topic_keywords.json)
- [标准化 Schema](./schemas/normalized_post.schema.json)
- [架构说明](../../docs/architecture.md)
- [支持查询列表](../../docs/supported-queries.md)
- [安全声明](../../docs/safety.md)
