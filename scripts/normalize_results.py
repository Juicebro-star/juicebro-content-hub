"""
normalize_results.py
--------------------
将平台原始内容（RawPost）规范化为标准 NormalizedPost 格式。

核心逻辑：
1. 解析发布时间（相对时间 → 绝对时间）
2. 判断内容类型
3. 提取摘要
4. 计算 dedupe_hash
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

CST = timezone(timedelta(hours=8))


@dataclass
class NormalizedPost:
    """规范化内容单元，对应 schemas/normalized_post.schema.json。"""
    platform: str
    account: str
    publish_time: Optional[str]       # ISO8601 或 None
    title: Optional[str]
    summary: str
    content_type: str                 # video | article | audio | short_post | image_post
    topic_tags: list[str]
    source_locator: Optional[str]
    raw_content: Optional[str] = None
    dedupe_hash: Optional[str] = None
    also_posted_on: list[str] = field(default_factory=list)
    media: Optional[dict] = None
    engagement: Optional[dict] = None
    extraction_notes: str = ""


# ---------------------------------------------------------------------------
# 时间解析
# ---------------------------------------------------------------------------

def parse_publish_time(
    raw_time_str: Optional[str],
    reference_time: Optional[datetime] = None,
) -> Optional[str]:
    """
    将原始时间字符串解析为 ISO8601 格式（北京时间）。

    Args:
        raw_time_str: 原始时间字符串，支持多种格式
        reference_time: 相对时间计算的基准时间，None 时使用当前时间

    Returns:
        ISO8601 字符串，或 None（无法解析时）
    """
    if not raw_time_str:
        return None

    now = reference_time or datetime.now(tz=CST)

    # 相对时间：X分钟前
    match = re.match(r"(\d+)\s*分钟前", raw_time_str)
    if match:
        dt = now - timedelta(minutes=int(match.group(1)))
        return dt.isoformat()

    # 相对时间：X小时前
    match = re.match(r"(\d+)\s*小时前", raw_time_str)
    if match:
        dt = now - timedelta(hours=int(match.group(1)))
        return dt.isoformat()

    # 相对时间：X天前
    match = re.match(r"(\d+)\s*天前", raw_time_str)
    if match:
        dt = now - timedelta(days=int(match.group(1)))
        return dt.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()

    # 昨天 HH:mm
    match = re.match(r"昨天\s*(\d{2}):(\d{2})", raw_time_str)
    if match:
        yesterday = now - timedelta(days=1)
        dt = yesterday.replace(
            hour=int(match.group(1)),
            minute=int(match.group(2)),
            second=0,
            microsecond=0,
        )
        return dt.isoformat()

    # MM-DD HH:mm（当年）
    match = re.match(r"(\d{1,2})-(\d{1,2})\s+(\d{2}):(\d{2})", raw_time_str)
    if match:
        try:
            dt = now.replace(
                month=int(match.group(1)),
                day=int(match.group(2)),
                hour=int(match.group(3)),
                minute=int(match.group(4)),
                second=0,
                microsecond=0,
            )
            return dt.isoformat()
        except ValueError:
            pass

    # YYYY-MM-DD HH:mm:ss（绝对时间）
    patterns = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%Y/%m/%d %H:%M",
        "%Y/%m/%d",
    ]
    for pat in patterns:
        try:
            dt = datetime.strptime(raw_time_str, pat).replace(tzinfo=CST)
            return dt.isoformat()
        except ValueError:
            continue

    # RFC822（RSS 格式）：Wed, 15 Jan 2024 18:00:00 +0800
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(raw_time_str)
        dt = dt.astimezone(CST)
        return dt.isoformat()
    except Exception:
        pass

    logger.warning(f"无法解析时间字符串：{raw_time_str!r}")
    return None


# ---------------------------------------------------------------------------
# 内容类型判断
# ---------------------------------------------------------------------------

def infer_content_type(
    platform_id: str,
    raw_text: str,
    title: Optional[str],
    extra: dict,
) -> str:
    """
    根据平台特征和内容特征推断 content_type。

    Args:
        platform_id: 平台 ID
        raw_text: 原始文本内容
        title: 标题（若有）
        extra: 平台附加字段（如 duration、has_video、has_image 等）

    Returns:
        content_type 枚举值
    """
    # 播客平台固定为 audio
    if platform_id in ("ximalaya", "xiaoyuzhou"):
        return "audio"

    # 有时长字段通常为视频
    if extra.get("duration") and platform_id not in ("ximalaya", "xiaoyuzhou"):
        return "video"

    # 有视频标志
    if extra.get("has_video") or extra.get("video_url"):
        return "video"

    # 小红书以图文为主
    if platform_id == "xiaohongshu":
        if extra.get("image_count", 0) > 0:
            return "image_post"
        return "short_post"

    # 图片内容
    if extra.get("has_image") or extra.get("image_count", 0) > 0:
        return "image_post"

    # 长文章（有标题且文字较长）
    if title and len(raw_text) > 500:
        return "article"

    # 默认短帖
    return "short_post"


# ---------------------------------------------------------------------------
# 摘要提取
# ---------------------------------------------------------------------------

def extract_summary(text: str, max_length: int = 150) -> str:
    """
    从原始文本中提取摘要。

    Args:
        text: 原始文本
        max_length: 最大字符数

    Returns:
        摘要字符串
    """
    if not text:
        return ""

    # 清理 HTML 标签（简单处理）
    text = re.sub(r"<[^>]+>", "", text)

    # 清理多余空白
    text = re.sub(r"\s+", " ", text).strip()

    if len(text) <= max_length:
        return text

    # 截断在句子边界
    truncated = text[:max_length]
    last_sentence_end = max(
        truncated.rfind("。"),
        truncated.rfind("！"),
        truncated.rfind("？"),
        truncated.rfind("…"),
    )
    if last_sentence_end > max_length // 2:
        return truncated[: last_sentence_end + 1]

    return truncated + "..."


# ---------------------------------------------------------------------------
# dedupe hash 计算
# ---------------------------------------------------------------------------

def compute_dedupe_hash(title: Optional[str], summary: str) -> str:
    """
    计算去重指纹：MD5(title + "_" + summary[:200])，取前16位。

    Args:
        title: 标题
        summary: 摘要

    Returns:
        16位十六进制字符串
    """
    base = (title or "") + "_" + summary[:200]
    return hashlib.md5(base.encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# 主规范化函数
# ---------------------------------------------------------------------------

def normalize_raw_post(
    platform_id: str,
    account_name: str,
    raw_text: str,
    raw_time_str: Optional[str],
    title: Optional[str] = None,
    source_url: Optional[str] = None,
    extra: Optional[dict] = None,
    reference_time: Optional[datetime] = None,
) -> NormalizedPost:
    """
    将单条原始内容规范化为 NormalizedPost。

    Args:
        platform_id: 平台 ID
        account_name: 账号名
        raw_text: 原始文本内容
        raw_time_str: 原始时间字符串
        title: 标题（可选）
        source_url: 内容链接（可选）
        extra: 平台附加字段（可选）
        reference_time: 时间解析基准（可选）

    Returns:
        NormalizedPost 对象
    """
    extra = extra or {}
    notes = []

    # 解析时间
    publish_time = parse_publish_time(raw_time_str, reference_time=reference_time)
    if raw_time_str and not publish_time:
        notes.append(f"时间解析失败，原始值：{raw_time_str!r}")

    # 提取摘要
    summary = extract_summary(raw_text)
    if not summary:
        summary = title or "(内容为空)"
        notes.append("原始内容为空，摘要使用标题代替")

    # 判断内容类型
    content_type = infer_content_type(platform_id, raw_text, title, extra)

    # 计算 dedupe_hash
    dedupe_hash = compute_dedupe_hash(title, summary)

    # 构建 media 字段
    media: Optional[dict] = None
    if content_type in ("video", "audio", "image_post"):
        media = {
            "duration_seconds": extra.get("duration_seconds"),
            "duration_display": extra.get("duration"),
            "thumbnail_url": extra.get("thumbnail_url"),
            "episode_number": extra.get("episode_number"),
            "image_count": extra.get("image_count"),
        }

    # 构建 engagement 字段
    engagement: Optional[dict] = None
    engagement_keys = ("view_count", "like_count", "comment_count", "collect_count", "repost_count")
    if any(k in extra for k in engagement_keys):
        engagement = {k: extra.get(k) for k in engagement_keys}

    return NormalizedPost(
        platform=platform_id,
        account=account_name,
        publish_time=publish_time,
        title=title,
        summary=summary,
        content_type=content_type,
        topic_tags=[],  # topic_tags 由 topic_classifier.py 填充
        source_locator=source_url,
        raw_content=raw_text[:2000] if raw_text else None,
        dedupe_hash=dedupe_hash,
        also_posted_on=[],
        media=media,
        engagement=engagement,
        extraction_notes="; ".join(notes),
    )


def normalize_batch(raw_posts: list[dict]) -> list[NormalizedPost]:
    """
    批量规范化原始内容列表。

    Args:
        raw_posts: 原始内容字典列表（包含 normalize_raw_post 所需的所有字段）

    Returns:
        NormalizedPost 列表
    """
    results = []
    for item in raw_posts:
        try:
            post = normalize_raw_post(**item)
            results.append(post)
        except Exception as e:
            logger.error(f"规范化失败：{e}，原始数据：{item}")
    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("=== normalize_results.py 骨架测试 ===\n")

    test_cases = [
        {
            "platform_id": "weibo",
            "account_name": "果汁哥6688",
            "raw_text": "今天比特币突破 10 万美元，市场情绪高涨，但我觉得需要冷静看待。历史上每次情绪顶点后都有回调...",
            "raw_time_str": "2小时前",
            "title": None,
            "source_url": "https://weibo.com/xxx",
        },
        {
            "platform_id": "bilibili",
            "account_name": "果汁哥juicebro",
            "raw_text": "本期视频深度分析2024年降息路径预测...",
            "raw_time_str": "2024-01-14 20:00",
            "title": "【深度分析】美联储2024年降息路径预测",
            "source_url": "https://www.bilibili.com/video/BV1xx",
            "extra": {"duration": "39:00", "duration_seconds": 2340, "view_count": 45678},
        },
    ]

    for case in test_cases:
        extra = case.pop("extra", {})
        post = normalize_raw_post(**case, extra=extra)
        print(json.dumps(asdict(post), ensure_ascii=False, indent=2))
        print()
