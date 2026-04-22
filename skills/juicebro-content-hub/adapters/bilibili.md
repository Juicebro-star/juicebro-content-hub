# bilibili 适配器

## 目标

bilibili 是果汁哥发布中长视频和专栏文章的核心平台，内容质量高，有公开 API 支持。数据获取稳定性优于其他平台。

## 官方账号

- **账号名**：果汁哥juicebro
- **平台**：bilibili（bilibili.com）
- **用户空间**：`https://space.bilibili.com/{uid}`（UID 需先确认）
- **搜索入口**：`https://search.bilibili.com/all?keyword=果汁哥juicebro&from_source=webtop_search&search_source=2`
- **内容类别**：日常分享

## 查询策略

### 主要查询路径

1. **用户空间视频列表**（推荐）：`https://space.bilibili.com/{uid}/video`
2. **B站公开 API**（V2 扩展点）：
   - 视频列表：`https://api.bilibili.com/x/space/arc/search?mid={uid}&ps=30&pn=1&order=pubdate`
   - 专栏文章：`https://api.bilibili.com/x/space/article?mid={uid}&pn=1&ps=10&sort=publish_time`
3. **RSS 订阅**（需第三方工具）：`https://rsshub.app/bilibili/user/video/{uid}`

### 内容类型识别

| B站内容 | content_type |
|---------|-------------|
| 投稿视频 | `video` |
| 专栏文章 | `article` |
| 动态（短内容） | `short_post` |

## 适合提取的字段

| 字段 | 可用性 | 提取说明 |
|------|--------|---------|
| `publish_time` | ✅ 高 | B站 API 返回 Unix 时间戳，转换为 ISO8601 |
| `title` | ✅ 高 | 视频/文章标题 |
| `summary` | ✅ 高 | 视频简介 / 文章摘要 |
| `content_type` | ✅ 高 | video / article 明确区分 |
| `source_locator` | ✅ 高 | 视频：`https://www.bilibili.com/video/{bvid}`；文章：`https://www.bilibili.com/read/cv{cvid}` |
| `view_count` | ✅ 高 | 播放量（API 直接返回） |
| `like_count` | ✅ 高 | 点赞数 |
| `duration` | ✅ 高 | 视频时长（秒数，需换算为 HH:mm:ss） |
| `thumbnail_url` | ✅ 高 | 封面图 URL（API 返回 pic 字段） |
| `episode_number` | ❌ | B站不维护 episode_number，设为 null |

## "今天"查询处理

1. 通过视频列表 API 获取最近投稿（`order=pubdate` 按发布时间排序）
2. 将 API 返回的 `pubdate`（Unix 时间戳）转换为北京时间
3. 筛选当日（00:00 - 23:59 北京时间）发布的内容
4. 专栏文章同理，检查 `publish_time` 字段

## 跨平台去重

- **与抖音/快手**：部分视频同步，通常 B站版本更长（完整版），抖音/快手为剪辑版
  - 判断规则：标题相似（前20字匹配）且时长 > 5 分钟 → 认为是完整版，保留 B站版本
  - 短视频（< 3 分钟）且抖音/快手也有 → 标注 `also_posted_on`
- **与今日头条/公众号**：专栏文章与文章平台可能重叠，以标题去重

## 失败处理

| 失败场景 | 处理方式 |
|----------|----------|
| UID 未确认 | 通过搜索确认 UID，不得猜测 |
| API 限流（429）| 等待后重试，或降级为 Web 爬取 |
| API 返回空列表 | 输出"近期暂无新内容" |
| Web 端访问正常但 API 失败 | 降级为 Web 端内容提取 |

## 注意事项

- B站 API 为公开接口，无需认证，但有 rate limit，建议每分钟不超过 30 次请求
- BV 号（bvid）是视频的唯一标识，格式为 `BV1xxxxxxxxx`
- 专栏文章（CV 号）和视频是分开的接口，查询时都需要覆盖
- B站 API 的时间字段为 Unix 时间戳（秒），需换算为北京时间（UTC+8）
