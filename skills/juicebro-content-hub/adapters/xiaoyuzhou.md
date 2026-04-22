# 小宇宙适配器

## 目标

小宇宙是果汁哥播客内容的首选平台，RSS 支持完善，数据获取稳定。作为播客查询的首选数据源，优先于喜马拉雅。

## 官方账号

- **账号名**：果汁哥
- **平台**：小宇宙（xiaoyuzhoufm.com）
- **播客主页**：`https://www.xiaoyuzhoufm.com/podcast/{podcast_id}`（需先确认播客 ID）
- **搜索入口**：`https://www.xiaoyuzhoufm.com/search?q=果汁哥`
- **RSS（若有）**：`https://feed.xiaoyuzhoufm.com/podcasts/{podcast_id}.xml`
- **内容类别**：播客

## 查询策略

### 主要查询路径

1. **RSS 订阅**（首选）：小宇宙支持 RSS 导出，可获取节目列表和完整元数据
2. **播客主页**：访问 `xiaoyuzhoufm.com/podcast/{id}`，获取节目列表
3. **搜索确认**：通过搜索确认播客名称和 ID

### RSS 优势

使用 RSS 方式可以获取：
- 完整节目列表（无分页限制）
- 标准 `<pubDate>` 字段（ISO 格式时间）
- 节目描述（`<description>`）
- 音频文件 URL（`<enclosure>`）
- 节目时长（`<itunes:duration>`）

### 内容类型识别

| 小宇宙内容 | content_type |
|-----------|-------------|
| 播客节目（音频） | `audio` |

## 适合提取的字段

| 字段 | 可用性 | 提取说明 |
|------|--------|---------|
| `publish_time` | ✅ 高 | RSS `<pubDate>` 字段，标准 RFC822 格式 |
| `title` | ✅ 高 | RSS `<title>` 字段 |
| `summary` | ✅ 高 | RSS `<description>` 字段 |
| `content_type` | ✅ 高 | 固定为 audio |
| `source_locator` | ✅ 高 | 格式：`https://www.xiaoyuzhoufm.com/episode/{episode_id}` |
| `duration` | ✅ 高 | `<itunes:duration>` 字段（HH:MM:SS 格式） |
| `episode_number` | ✅ 中 | `<itunes:episode>` 字段（如有） |
| `audio_url` | ✅ 高 | `<enclosure url="...">` 字段 |

## "今天"查询处理

1. **RSS 方式**：解析 RSS Feed，筛选 `<pubDate>` 为当日的节目
2. **Web 方式**：访问播客主页节目列表，筛选当日发布
3. 小宇宙播客通常为周更或双周更，今日无更新属正常情况
4. RSS 时间格式示例：`Wed, 15 Jan 2024 18:00:00 +0800`，需转换为 ISO8601

## 跨平台去重

- **与喜马拉雅**：内容高度重叠
- 去重依据：节目标题 + 时长相似（±30秒）
- 小宇宙版本为首选保留版本，喜马拉雅标注 `also_posted_on`

## 失败处理

| 失败场景 | 处理方式 |
|----------|----------|
| RSS 不可用 | 降级为 Web 主页访问 |
| Web 主页无法加载 | 提示用户在小宇宙 App 搜索"果汁哥" |
| 播客 ID 未确认 | 通过搜索重新定位，不得使用猜测 ID |
| 节目详情无法访问 | 仅提取 RSS 摘要信息，标注"详情页暂不可访问" |

## 注意事项

- 小宇宙播客 ID 格式为字母数字串，需要通过主页 URL 提取
- RSS Feed URL 格式：`https://feed.xiaoyuzhoufm.com/podcasts/{id}.xml`（需验证是否可用）
- 小宇宙的 Web 端对未登录用户访问能力较好，优先使用 Web 或 RSS
- 播客时长字段有两种格式：纯秒数或 HH:MM:SS，提取时统一转换为 HH:MM:SS
