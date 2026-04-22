# 辅助脚本说明

本目录包含 `juicebro-content-hub` 的可选辅助脚本，用于数据处理管道的各个阶段。

## 重要声明

**这些脚本目前均为"骨架型"实现**，包含完整的类型标注、接口定义和扩展点注释，但不包含真实的平台抓取逻辑。

设计原则：
- 不包含爬虫代码
- 不绕过平台 robots.txt 或反爬机制
- 不存储登录凭证
- 不执行隐蔽的网络请求

## 脚本列表

| 脚本 | 用途 | 当前状态 |
|------|------|----------|
| `optional_fetcher.py` | 可选数据获取接口（骨架） | 骨架 |
| `normalize_results.py` | 将原始数据规范化为 NormalizedPost | 骨架 |
| `dedupe_posts.py` | 跨平台内容去重 | 骨架 |
| `topic_classifier.py` | 内容主题标注 | 骨架 |

## 如何扩展

每个脚本都设计了清晰的扩展点（标注为 `# EXTEND: ...` 注释），V2 阶段可以：

1. 实现 `optional_fetcher.py` 中各平台的 `fetch_*` 方法（接入 RSS 或公开 API）
2. 完善 `normalize_results.py` 中的字段映射逻辑
3. 实现 `dedupe_posts.py` 中的去重算法
4. 扩展 `topic_classifier.py` 中的关键词匹配和 NLP 分析

## 运行环境

```bash
# Python >= 3.9
pip install -r requirements.txt
```

当前 `requirements.txt`（骨架阶段无额外依赖）：
```
# 骨架阶段无需额外依赖
# V2 阶段将添加：
# requests>=2.31.0
# feedparser>=6.0.10
# jieba>=0.42.1
```
