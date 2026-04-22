# 架构设计说明

## 概述

`juicebro-content-hub` 采用"声明式中台 + 适配层扩展 + 提示模板驱动"的三层架构。Agent 不需要自己实现抓取逻辑，而是依赖本 Skill 提供的上下文（账号矩阵、平台规则、意图路由、提示模板）来完成内容查询与汇总任务。

```
用户自然语言请求
        │
        ▼
┌───────────────────┐
│   意图识别层       │  query_intents.json + topic_keywords.json
│  (Intent Router)  │  → 识别：平台、时间范围、主题、内容形态
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│   平台适配层       │  adapters/*.md + platform_rules.json
│  (Platform Layer) │  → 确定查询策略、字段映射、失败处理
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│   内容规范化层     │  schemas/normalized_post.schema.json
│  (Normalizer)     │  → 统一字段：platform/account/publish_time/
└────────┬──────────┘    title/summary/content_type/topic_tags/source_locator
         │
         ▼
┌───────────────────┐
│   去重 & 汇总层    │  dedupe_posts.py (可选) + prompts/*.md
│  (Aggregator)     │  → 跨平台去重 + 多维汇总视角
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│   输出格式化层     │  normalized_result.schema.json + prompts
│  (Formatter)      │  → Markdown 日报 / 平台报告 / 主题摘要
└───────────────────┘
```

---

## 各层说明

### 1. 意图识别层

**输入**：用户自然语言字符串

**核心数据**：
- `data/query_intents.json`：定义支持的意图类型（全平台查询、单平台查询、主题查询、形态查询、汇总报告、导航推荐）
- `data/topic_keywords.json`：主题关键词映射表（比特币、黄金、美股、AI、特朗普……）

**输出**：结构化意图对象
```json
{
  "intent_type": "platform_single",
  "platforms": ["weibo"],
  "time_range": "today",
  "topic": null,
  "content_type": null,
  "output_format": "list"
}
```

---

### 2. 平台适配层

**输入**：结构化意图对象

**核心数据**：
- `data/accounts.json`：账号矩阵（平台 → 账号名、URL、类别、内容类型）
- `data/platform_rules.json`：各平台公开访问规则、查询策略、字段可用性
- `skills/juicebro-content-hub/adapters/*.md`：每个平台的详细适配说明

**规则**：
- 若用户指定平台 → 仅查指定平台
- 若用户未指定平台 → 遍历所有 `is_queryable: true` 的平台
- 若平台公开访问受限 → 返回限制说明，不编造结果

---

### 3. 内容规范化层

所有平台返回的原始内容统一规范化为 `NormalizedPost` 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| `platform` | string | 平台标识（weibo / xiaohongshu / bilibili / …） |
| `account` | string | 账号名 |
| `publish_time` | ISO8601 string | 发布时间 |
| `title` | string \| null | 标题（长文有标题，短帖可为 null） |
| `summary` | string | 内容摘要（100字以内） |
| `content_type` | enum | video / article / audio / short_post / image_post |
| `topic_tags` | string[] | 主题标签（由 topic_classifier.py 或 Agent 推断） |
| `source_locator` | string | 原始内容链接或定位信息 |
| `raw_content` | string \| null | 原始文本（可选，Agent 做进一步分析时使用） |
| `dedupe_hash` | string \| null | 用于跨平台去重的内容指纹 |

完整 Schema 见 [`schemas/normalized_post.schema.json`](../schemas/normalized_post.schema.json)。

---

### 4. 去重 & 汇总层

**去重策略**：
- 相同 `title` + 相似 `publish_time`（±24h）视为疑似重复
- 计算 `dedupe_hash`（基于标题+前200字的 MD5）做精确去重
- 保留最早平台版本，其他版本合并到 `also_posted_on` 字段

**汇总视角**：

| 视角 | 对应提示 |
|------|----------|
| 按时间 | `prompts/summarize_recent_posts.md` |
| 按平台 | `prompts/summarize_by_platform.md` |
| 按主题 | `prompts/summarize_by_topic.md` |
| 字段提取 | `prompts/extract_post_fields.md` |

---

### 5. 输出格式化层

根据用户意图选择输出格式：

| 意图 | 输出格式 |
|------|----------|
| 日常查询 | Markdown 列表，每条包含平台+时间+摘要+链接 |
| 日报生成 | 结构化 Markdown，按平台分组，带统计摘要 |
| 主题摘要 | 按时间排列，标注主题标签，过滤非相关内容 |
| 导航推荐 | 简洁文字推荐 + 平台链接 |

---

## 数据流示意（全平台查询场景）

```
用户："果汁哥今天发了什么"
  │
  ├─ 意图识别 → intent_type=all_platform, time_range=today
  │
  ├─ 平台遍历 → [weibo, xiaohongshu, douyin, bilibili, xueqiu, toutiao, wechat_oa, ximalaya, xiaoyuzhou, ...]
  │
  ├─ 逐平台适配 → 查询策略 + 字段提取
  │
  ├─ 规范化 → NormalizedPost[]
  │
  ├─ 去重 → 合并同源内容
  │
  ├─ 汇总 → 按平台分组 + 统计条数
  │
  └─ 输出 → Markdown 日报
```

---

## 扩展点

1. **新增平台**：在 `data/accounts.json` 添加账号，`adapters/` 添加适配说明，`platform_rules.json` 添加规则
2. **新增主题**：在 `data/topic_keywords.json` 添加关键词映射
3. **新增意图**：在 `data/query_intents.json` 添加意图类型，`prompts/` 添加对应提示模板
4. **接入真实数据源**：实现 `scripts/optional_fetcher.py` 中的各平台 `fetch_*` 方法

---

## 依赖关系图

```
accounts.json ──────────────────────────┐
platform_rules.json ─────────────────── ├──→ adapters/*.md
query_intents.json ──────────────────── ┤
topic_keywords.json ─────────────────── ┘
                                         │
                                         ▼
                              normalized_post.schema.json
                                         │
                          ┌──────────────┴──────────────┐
                          ▼                             ▼
                    prompts/*.md              dedupe_posts.py
                          │
                          ▼
                normalized_result.schema.json
```
