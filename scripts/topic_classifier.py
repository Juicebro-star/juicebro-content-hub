"""
topic_classifier.py
-------------------
内容主题分类器（骨架实现）。

为 NormalizedPost 的 topic_tags 字段填充主题标签，基于关键词匹配。
V2 阶段可引入 jieba 分词和更复杂的 NLP 分析。

主题定义见：skills/juicebro-content-hub/data/topic_keywords.json
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 主题关键词加载
# ---------------------------------------------------------------------------

# 内联关键词表（避免路径依赖，与 topic_keywords.json 保持同步）
TOPIC_KEYWORDS: dict[str, list[str]] = {
    "bitcoin": [
        "比特币", "BTC", "比特", "加密币", "比特币行情", "BTC价格", "bitcoin",
    ],
    "gold": [
        "黄金", "金价", "gold", "贵金属", "黄金ETF", "国际金价", "伦敦金",
    ],
    "us_stock": [
        "美股", "纳指", "纳斯达克", "标普", "道指", "美联储", "美股行情",
        "华尔街", "NYSE", "NASDAQ", "S&P", "联储",
    ],
    "a_stock": [
        "A股", "沪深", "上证", "深证", "A股行情", "大A", "沪指", "创业板", "科创板",
    ],
    "ai": [
        "AI", "人工智能", "大模型", "ChatGPT", "Claude", "GPT", "Gemini",
        "大语言模型", "LLM", "机器学习", "深度学习", "OpenAI", "Anthropic",
        "通义", "文心", "NVIDIA", "英伟达",
    ],
    "trump": [
        "特朗普", "川普", "Trump", "特朗普政策", "关税", "贸易战", "白宫",
    ],
    "macro": [
        "宏观", "经济", "通胀", "通货膨胀", "利率", "降息", "加息", "美联储",
        "央行", "GDP", "就业", "CPI", "PPI", "PMI", "经济数据",
    ],
    "crypto": [
        "加密货币", "数字货币", "以太坊", "ETH", "币圈", "DeFi", "NFT",
        "Web3", "区块链", "altcoin",
    ],
    "real_estate": [
        "房产", "房市", "楼市", "房价", "买房", "租房", "地产", "REITs",
    ],
    "investment_strategy": [
        "投资", "资产配置", "组合", "仓位", "止损", "定投", "价值投资",
        "成长投资", "策略", "投资逻辑", "择时", "轮动",
    ],
    "tech_stock": [
        "科技股", "FAANG", "苹果", "特斯拉", "微软", "谷歌", "英伟达",
        "NVIDIA", "Meta", "亚马逊", "TSMC", "台积电",
    ],
    "finance": [
        "理财", "基金", "ETF", "债券", "储蓄", "复利", "收益", "年化", "保险",
    ],
    "commodities": [
        "大宗商品", "原油", "石油", "铜", "铁矿石", "农产品", "CRB",
    ],
    "geopolitics": [
        "地缘", "中美", "俄乌", "战争", "制裁", "国际局势", "外交",
    ],
}


def load_topic_keywords_from_file(
    json_path: Optional[str] = None,
) -> dict[str, list[str]]:
    """
    从 topic_keywords.json 加载主题关键词。
    加载失败时使用内联关键词表作为 fallback。

    Args:
        json_path: JSON 文件路径，None 时使用默认路径

    Returns:
        topic_id → 关键词列表的字典
    """
    if json_path is None:
        json_path = str(
            Path(__file__).parent.parent
            / "skills"
            / "juicebro-content-hub"
            / "data"
            / "topic_keywords.json"
        )

    try:
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
        result: dict[str, list[str]] = {}
        for topic_id, topic_data in data.get("topics", {}).items():
            kws = topic_data.get("keywords_zh", []) + topic_data.get("keywords_en", [])
            result[topic_id] = kws
        logger.info(f"从 {json_path} 加载了 {len(result)} 个主题关键词")
        return result
    except Exception as e:
        logger.warning(f"加载 topic_keywords.json 失败，使用内联关键词：{e}")
        return TOPIC_KEYWORDS


# ---------------------------------------------------------------------------
# 分类逻辑
# ---------------------------------------------------------------------------

def classify_topics(
    text: str,
    title: Optional[str] = None,
    keywords_map: Optional[dict[str, list[str]]] = None,
    min_matches: int = 1,
) -> list[str]:
    """
    对内容进行主题分类，返回匹配的 topic_id 列表。

    Args:
        text: 内容文本（summary 或 raw_content）
        title: 内容标题（额外权重来源）
        keywords_map: 自定义关键词表，None 时使用内联表
        min_matches: 最少匹配次数阈值

    Returns:
        匹配到的 topic_id 列表（去重、有序）
    """
    if keywords_map is None:
        keywords_map = TOPIC_KEYWORDS

    combined = (title or "") + " " + text

    matched_topics: list[str] = []

    for topic_id, keywords in keywords_map.items():
        match_count = 0
        for kw in keywords:
            # 大小写不敏感匹配
            if re.search(re.escape(kw), combined, re.IGNORECASE):
                match_count += 1

        if match_count >= min_matches:
            matched_topics.append(topic_id)

    # 按预定义优先级排序（优先级高的在前）
    priority_order = list(TOPIC_KEYWORDS.keys())
    matched_topics.sort(
        key=lambda t: priority_order.index(t) if t in priority_order else 99
    )

    return matched_topics


def classify_post(post: object, keywords_map: Optional[dict] = None) -> list[str]:
    """
    对 NormalizedPost 对象进行主题分类，更新 topic_tags 字段。

    Args:
        post: NormalizedPost 对象（需要有 title、summary、raw_content 属性）
        keywords_map: 自定义关键词表

    Returns:
        更新后的 topic_tags 列表
    """
    text = getattr(post, "summary", "") or ""
    raw = getattr(post, "raw_content", "") or ""
    title = getattr(post, "title", None)

    # 优先使用 raw_content（内容更完整），fallback 到 summary
    content = raw if raw else text

    tags = classify_topics(content, title=title, keywords_map=keywords_map)

    # 更新 post 对象
    if hasattr(post, "topic_tags"):
        post.topic_tags = tags

    return tags


def classify_posts_batch(
    posts: list,
    keywords_map: Optional[dict] = None,
) -> list:
    """
    批量对内容列表进行主题分类。

    Args:
        posts: NormalizedPost 对象列表
        keywords_map: 自定义关键词表

    Returns:
        更新 topic_tags 后的 posts 列表（原地修改）
    """
    if keywords_map is None:
        keywords_map = TOPIC_KEYWORDS

    for post in posts:
        tags = classify_post(post, keywords_map=keywords_map)
        logger.debug(f"[{getattr(post, 'platform', '?')}] 主题标注：{tags}")

    return posts


# ---------------------------------------------------------------------------
# 主题过滤
# ---------------------------------------------------------------------------

def filter_by_topic(
    posts: list,
    topic_id: str,
) -> list:
    """
    过滤出指定主题的内容。

    Args:
        posts: NormalizedPost 对象列表（已完成主题标注）
        topic_id: 目标主题 ID

    Returns:
        匹配的内容列表
    """
    return [
        post for post in posts
        if topic_id in getattr(post, "topic_tags", [])
    ]


# ---------------------------------------------------------------------------
# 主题统计
# ---------------------------------------------------------------------------

def count_by_topic(posts: list) -> dict[str, int]:
    """
    统计各主题的内容条数。

    Args:
        posts: NormalizedPost 对象列表

    Returns:
        topic_id → 条数的字典
    """
    counts: dict[str, int] = {}
    for post in posts:
        for tag in getattr(post, "topic_tags", []):
            counts[tag] = counts.get(tag, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: -x[1]))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("=== topic_classifier.py 测试 ===\n")

    test_texts = [
        ("比特币今天突破 10 万美元，市场情绪高涨", None),
        ("美联储宣布降息 25 个基点，纳指立刻上涨 2%", "美联储降息决议点评"),
        ("分享一个简单的资产配置框架，适合普通人参考", None),
        ("今天天气不错，出去散步了", None),
    ]

    for text, title in test_texts:
        tags = classify_topics(text, title=title)
        print(f"文本：{text[:30]}...")
        print(f"  → 主题标签：{tags}\n")
