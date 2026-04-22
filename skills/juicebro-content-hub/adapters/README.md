# 平台适配器说明

本目录包含 `juicebro-content-hub` Skill 支持的各平台适配文档。每个文件描述一个平台的查询策略、字段提取规范和异常处理方式。

## 文件列表

| 文件 | 平台 | 是否可查 | 主要内容类型 |
|------|------|----------|-------------|
| [weibo.md](./weibo.md) | 微博 | ✅ | 短帖、图文、视频 |
| [xiaohongshu.md](./xiaohongshu.md) | 小红书 | ✅ | 图文、短帖 |
| [douyin.md](./douyin.md) | 抖音 | ✅ | 视频 |
| [kuaishou.md](./kuaishou.md) | 快手 | ✅ | 视频 |
| [bilibili.md](./bilibili.md) | bilibili | ✅ | 视频、文章 |
| [xueqiu.md](./xueqiu.md) | 雪球 | ✅ | 短帖、文章 |
| [toutiao.md](./toutiao.md) | 今日头条 | ✅ | 文章、视频 |
| [wechat_official_account.md](./wechat_official_account.md) | 微信公众号 | ⚠️ 部分 | 文章 |
| [yuanbao.md](./yuanbao.md) | 元宝 | ⚠️ 待确认 | 短帖、文章 |
| [ximalaya.md](./ximalaya.md) | 喜马拉雅 | ✅ | 音频 |
| [xiaoyuzhou.md](./xiaoyuzhou.md) | 小宇宙 | ✅ | 音频 |
| [zhishixingqiu.md](./zhishixingqiu.md) | 知识星球 | ❌ 付费 | - |

## 适配器文档结构

每个适配器文件包含以下章节：

1. **目标**：该平台在聚合中的定位
2. **官方账号**：账号名和 URL
3. **查询策略**：如何访问和获取内容列表
4. **适合提取的字段**：各字段可用性和提取方式
5. **"今天"查询处理**：如何处理时间筛选
6. **跨平台去重**：与其他平台的重叠情况
7. **失败处理**：访问失败或受限时的回退策略

## 添加新平台

1. 复制任一现有适配器文件作为模板
2. 填写所有必要字段
3. 在 `data/accounts.json` 添加账号信息
4. 在 `data/platform_rules.json` 添加规则
5. 提交 PR 并在 README.md 中更新表格
