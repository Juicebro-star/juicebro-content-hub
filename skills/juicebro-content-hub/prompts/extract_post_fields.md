# 提示模板：从原始内容中提取规范化字段

**用途**：指导 Agent 将平台原始内容（文本/HTML 片段）解析为 `NormalizedPost` 格式，用于内容规范化层。

---

## 使用场景

- 当 Agent 直接访问平台页面并获取原始内容后，使用本模板完成字段提取
- 在辅助脚本 `normalize_results.py` 中作为提示参考

---

## 提示正文

```
你是内容字段提取专家，负责将平台原始内容解析为标准化结构。

## 任务

从以下原始内容中提取规范化字段，输出严格符合 NormalizedPost Schema 的 JSON 对象。

## 原始内容

- 来源平台：{{platform_id}}
- 账号名：{{account_name}}
- 原始内容（可能为文本、HTML 摘要或结构化片段）：

```
{{raw_content}}
```

## 字段提取规则

### platform（string，必填）
直接使用输入的 platform_id 值：{{platform_id}}

### account（string，必填）
直接使用输入的 account_name 值：{{account_name}}

### publish_time（string，必填，ISO8601 格式）
- 提取原始内容中的发布时间
- 转换为 ISO8601 格式：`YYYY-MM-DDTHH:mm:ss+08:00`（默认北京时间）
- 若为相对时间（"3分钟前"、"2小时前"、"昨天"），根据当前时间 {{current_datetime}} 反推绝对时间
- 若时间完全无法确定，设为 null 并在 notes 中说明

### title（string | null）
- 长文、视频、播客通常有标题，提取并清理
- 短帖（微博、雪球动态）通常无标题，设为 null
- 不得自行创作标题

### summary（string，必填，不超过 150 字）
- 提取内容的核心摘要
- 若原文不超过 150 字，直接使用原文
- 若原文超过 150 字，截取关键句子，保持语义完整
- 不得添加个人理解或推断

### content_type（enum，必填）
根据以下规则判断：
- `video`：视频内容（包含时长、视频链接、视频缩略图等线索）
- `article`：长文章（超过 500 字，有标题，通常来自头条/公众号/B站专栏）
- `audio`：音频/播客（来自喜马拉雅/小宇宙，或包含音频时长字段）
- `short_post`：短文字动态（微博、雪球动态、通常无标题，文字较短）
- `image_post`：图文内容（主体为图片+说明文字，通常来自小红书）

若无法判断，使用 `short_post` 作为默认值。

### topic_tags（string[]）
对照以下主题关键词匹配，列出所有命中的 topic_id：
- bitcoin：比特币、BTC
- gold：黄金、金价
- us_stock：美股、纳指、标普
- a_stock：A股、上证、深证
- ai：AI、人工智能、大模型、ChatGPT
- trump：特朗普、川普、关税
- macro：宏观、通胀、降息、利率
- crypto：加密货币、以太坊、ETH
- investment_strategy：投资、资产配置、仓位
- tech_stock：科技股、NVIDIA、苹果、特斯拉
- real_estate：房产、楼市
- finance：理财、基金、ETF
若无匹配，返回空数组 []

### source_locator（string | null）
- 提取内容的直接访问链接
- 若无链接但有唯一 ID，返回 `{{platform_base_url}}/{id}` 格式
- 若完全无法确定链接，设为 null

### raw_content（string | null）
- 若原始内容字数不超过 2000 字，完整保留
- 若超过 2000 字，截取前 2000 字
- 设计用于 Agent 进一步语义分析

### dedupe_hash（string | null）
- 生成方式：MD5(title + "_" + summary[:200])
- 若 title 为 null，使用 MD5(summary[:200])
- 格式：16位十六进制字符串

## 输出格式

严格输出合法 JSON，不添加任何说明文字：

```json
{
  "platform": "...",
  "account": "...",
  "publish_time": "...",
  "title": null,
  "summary": "...",
  "content_type": "...",
  "topic_tags": [],
  "source_locator": null,
  "raw_content": null,
  "dedupe_hash": null,
  "also_posted_on": [],
  "extraction_notes": "..."
}
```

`extraction_notes` 用于记录提取过程中的疑难点（如时间推算依据、字段缺失说明），正常情况下为空字符串。

## 批量提取

若输入包含多条内容，输出 JSON 数组：
```json
[
  { ...post1... },
  { ...post2... }
]
```
```
