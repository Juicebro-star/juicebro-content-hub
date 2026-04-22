"""
dedupe_posts.py
---------------
跨平台内容去重处理器（骨架实现）。

去重策略：
1. 精确去重：相同 dedupe_hash → 完全相同内容
2. 模糊去重：标题前20字相同 + 发布时间在24小时内 → 可能为同源内容
3. 音频去重：标题相同 + 时长相差 ±30秒 → 视为同一节目
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

logger = logging.getLogger(__name__)

CST = timezone(timedelta(hours=8))


@dataclass
class DedupeResult:
    """去重处理结果。"""
    unique_posts: list  # NormalizedPost 列表（已去重）
    removed_count: int  # 被移除的重复条目数
    merge_log: list[str]  # 合并操作日志


# ---------------------------------------------------------------------------
# 去重核心逻辑
# ---------------------------------------------------------------------------

def _extract_datetime(publish_time_str: Optional[str]) -> Optional[datetime]:
    """将 ISO8601 字符串解析为 datetime 对象。"""
    if not publish_time_str:
        return None
    try:
        dt = datetime.fromisoformat(publish_time_str)
        return dt.astimezone(CST)
    except ValueError:
        return None


def _title_key(title: Optional[str], n: int = 20) -> str:
    """提取标题前 n 字作为去重键（清理空白）。"""
    if not title:
        return ""
    return title.strip()[:n]


def _are_within_hours(
    t1: Optional[datetime],
    t2: Optional[datetime],
    hours: float = 24,
) -> bool:
    """判断两个时间点是否在指定小时数范围内。"""
    if t1 is None or t2 is None:
        return False
    return abs((t1 - t2).total_seconds()) <= hours * 3600


def _duration_similar(
    d1: Optional[int],  # 秒数
    d2: Optional[int],
    tolerance_seconds: int = 30,
) -> bool:
    """判断两个时长是否相似（用于音频去重）。"""
    if d1 is None or d2 is None:
        return False
    return abs(d1 - d2) <= tolerance_seconds


# ---------------------------------------------------------------------------
# 平台优先级（去重时保留优先级更高的平台版本）
# ---------------------------------------------------------------------------

PLATFORM_PRIORITY = {
    "bilibili": 1,       # 通常为完整版，优先级最高
    "xiaoyuzhou": 2,     # 播客原生平台
    "xueqiu": 3,
    "wechat_oa": 4,
    "toutiao": 5,
    "weibo": 6,
    "xiaohongshu": 7,
    "douyin": 8,
    "kuaishou": 9,       # 与抖音高度重叠，优先级低于抖音
    "ximalaya": 10,      # 播客同步平台，优先级低于小宇宙
    "yuanbao": 11,
    "wechat_private": 99,
    "zhishixingqiu": 99,
}


def get_priority(platform_id: str) -> int:
    return PLATFORM_PRIORITY.get(platform_id, 50)


# ---------------------------------------------------------------------------
# 主去重函数
# ---------------------------------------------------------------------------

def dedupe_posts(posts: list) -> DedupeResult:
    """
    对规范化内容列表进行去重处理。

    Args:
        posts: NormalizedPost 对象列表（已规范化）

    Returns:
        DedupeResult 对象
    """
    if not posts:
        return DedupeResult(unique_posts=[], removed_count=0, merge_log=[])

    merge_log: list[str] = []
    removed_indices: set[int] = set()

    # 按平台优先级排序（优先级高的排前面，去重时保留）
    indexed_posts = sorted(
        enumerate(posts),
        key=lambda x: get_priority(x[1].platform),
    )

    # 精确去重：相同 dedupe_hash
    seen_hashes: dict[str, int] = {}  # hash → 保留的 post 原始索引
    for orig_idx, post in indexed_posts:
        if post.dedupe_hash and post.dedupe_hash in seen_hashes:
            keeper_idx = seen_hashes[post.dedupe_hash]
            keeper = posts[keeper_idx]
            # 记录 also_posted_on
            if post.platform not in keeper.also_posted_on:
                keeper.also_posted_on.append(post.platform)
            removed_indices.add(orig_idx)
            merge_log.append(
                f"[精确去重] {post.platform}/{post.dedupe_hash[:8]}... "
                f"→ 合并到 {keeper.platform}"
            )
        elif post.dedupe_hash:
            seen_hashes[post.dedupe_hash] = orig_idx

    # 模糊去重：标题相似 + 时间相近（跳过已标记为重复的）
    active_indices = [i for i, _ in indexed_posts if i not in removed_indices]

    for i, idx_i in enumerate(active_indices):
        post_i = posts[idx_i]
        for idx_j in active_indices[i + 1 :]:
            if idx_j in removed_indices:
                continue
            post_j = posts[idx_j]

            # 音频去重：标题 + 时长
            if post_i.content_type == "audio" and post_j.content_type == "audio":
                title_match = (
                    _title_key(post_i.title, 15) == _title_key(post_j.title, 15)
                    and _title_key(post_i.title, 15) != ""
                )
                dur_i = post_i.media.get("duration_seconds") if post_i.media else None
                dur_j = post_j.media.get("duration_seconds") if post_j.media else None
                if title_match and _duration_similar(dur_i, dur_j):
                    # 保留优先级高的
                    if get_priority(post_i.platform) <= get_priority(post_j.platform):
                        keeper, dup = post_i, post_j
                        dup_idx = idx_j
                    else:
                        keeper, dup = post_j, post_i
                        dup_idx = idx_i
                    if dup.platform not in keeper.also_posted_on:
                        keeper.also_posted_on.append(dup.platform)
                    removed_indices.add(dup_idx)
                    merge_log.append(
                        f"[音频去重] {dup.platform}/{_title_key(dup.title)} "
                        f"→ 合并到 {keeper.platform}"
                    )
                    continue

            # 视频去重：标题前20字 + 时间24小时内
            if post_i.content_type == "video" and post_j.content_type == "video":
                title_match = (
                    _title_key(post_i.title) == _title_key(post_j.title)
                    and _title_key(post_i.title) != ""
                )
                time_match = _are_within_hours(
                    _extract_datetime(post_i.publish_time),
                    _extract_datetime(post_j.publish_time),
                    hours=48,
                )
                if title_match and time_match:
                    if get_priority(post_i.platform) <= get_priority(post_j.platform):
                        keeper, dup = post_i, post_j
                        dup_idx = idx_j
                    else:
                        keeper, dup = post_j, post_i
                        dup_idx = idx_i
                    if dup.platform not in keeper.also_posted_on:
                        keeper.also_posted_on.append(dup.platform)
                    removed_indices.add(dup_idx)
                    merge_log.append(
                        f"[视频去重] {dup.platform}/{_title_key(dup.title)} "
                        f"→ 合并到 {keeper.platform}"
                    )

    # 构建去重后的列表（按原始顺序，跳过被标记的）
    unique_posts = [post for i, post in enumerate(posts) if i not in removed_indices]
    removed_count = len(removed_indices)

    logger.info(
        f"去重完成：原始 {len(posts)} 条 → 去重后 {len(unique_posts)} 条，"
        f"移除 {removed_count} 条"
    )

    return DedupeResult(
        unique_posts=unique_posts,
        removed_count=removed_count,
        merge_log=merge_log,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("=== dedupe_posts.py 骨架测试 ===")
    print("（当前为骨架实现，需传入真实 NormalizedPost 列表进行测试）")
