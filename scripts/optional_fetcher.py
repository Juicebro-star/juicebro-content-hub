"""
optional_fetcher.py
-------------------
可选数据获取接口（骨架实现）。

本脚本定义了各平台内容获取的标准接口，当前为骨架型实现，返回空列表或
演示数据。V2 阶段可在各平台的 fetch_* 方法中接入 RSS 订阅或公开 API。

安全原则：
- 仅通过公开渠道获取内容（RSS / 公开 API）
- 不存储登录凭证
- 不绕过平台反爬机制
- 不模拟登录行为
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

# 北京时间偏移
CST = timezone(timedelta(hours=8))


@dataclass
class RawPost:
    """平台原始内容单元，尚未规范化。"""
    platform_id: str
    account_name: str
    raw_text: str
    raw_time_str: Optional[str]
    title: Optional[str]
    source_url: Optional[str]
    extra: dict = field(default_factory=dict)


@dataclass
class FetchResult:
    """单次平台查询结果。"""
    platform_id: str
    status: str  # accessible | login_required | paid_only | unreachable | skipped
    posts: list[RawPost]
    error_message: Optional[str] = None
    fetched_at: Optional[datetime] = None


class PlatformFetcher:
    """
    各平台内容获取器的基类。

    子类实现 fetch() 方法，返回 FetchResult。
    当前均为骨架实现，V2 阶段在子类中填充真实获取逻辑。
    """

    def __init__(self, platform_id: str, account_name: str):
        self.platform_id = platform_id
        self.account_name = account_name

    def fetch(self, days: int = 7) -> FetchResult:
        """
        获取最近 days 天的内容。

        Args:
            days: 时间范围（天数），默认 7 天

        Returns:
            FetchResult 对象
        """
        raise NotImplementedError("子类必须实现 fetch() 方法")

    def _make_result(
        self,
        status: str,
        posts: list[RawPost] | None = None,
        error_message: str | None = None,
    ) -> FetchResult:
        return FetchResult(
            platform_id=self.platform_id,
            status=status,
            posts=posts or [],
            error_message=error_message,
            fetched_at=datetime.now(tz=CST),
        )


# ---------------------------------------------------------------------------
# 平台具体实现（均为骨架，V2 阶段填充）
# ---------------------------------------------------------------------------


class WeiboFetcher(PlatformFetcher):
    """微博内容获取器（骨架）。"""

    def __init__(self) -> None:
        super().__init__("weibo", "果汁哥6688")

    def fetch(self, days: int = 7) -> FetchResult:
        # EXTEND: V2 阶段在此实现微博用户时间线抓取
        # 建议方案：通过 Weibo Web API（需登录 Cookie）或第三方 RSS
        # 示例 API：https://weibo.com/ajax/statuses/mymblog?uid={uid}&page=1&feature=0
        # 注意：需要 Cookie，属于需用户授权的操作
        logger.info("[weibo] 骨架模式：返回空结果")
        return self._make_result(
            status="accessible",
            posts=[],  # EXTEND: 替换为真实抓取结果
        )


class BilibiliFetcher(PlatformFetcher):
    """bilibili 内容获取器（骨架，有公开 API 可用）。"""

    def __init__(self, uid: Optional[str] = None) -> None:
        super().__init__("bilibili", "果汁哥juicebro")
        self.uid = uid  # 需要先确认 UID

    def fetch(self, days: int = 7) -> FetchResult:
        if not self.uid:
            logger.warning("[bilibili] UID 未配置，跳过查询")
            return self._make_result(
                status="unreachable",
                error_message="bilibili UID 未配置，请先确认账号 UID",
            )

        # EXTEND: V2 阶段在此调用 B 站公开 API
        # 视频列表 API（无需认证）：
        #   GET https://api.bilibili.com/x/space/arc/search?mid={uid}&ps=30&pn=1&order=pubdate
        # 专栏文章 API（无需认证）：
        #   GET https://api.bilibili.com/x/space/article?mid={uid}&pn=1&ps=10&sort=publish_time
        #
        # 注意：B 站 API 有 rate limit，建议每分钟不超过 30 次请求
        # 响应示例（视频）：
        # {
        #   "code": 0,
        #   "data": {
        #     "list": {
        #       "vlist": [
        #         {"bvid": "BV1xxx", "title": "...", "pubdate": 1705276800, "length": "35:20", ...}
        #       ]
        #     }
        #   }
        # }

        logger.info(f"[bilibili] 骨架模式：UID={self.uid}，返回空结果")
        return self._make_result(
            status="accessible",
            posts=[],  # EXTEND: 替换为 API 调用结果
        )


class XueqiuFetcher(PlatformFetcher):
    """雪球内容获取器（骨架）。"""

    def __init__(self) -> None:
        super().__init__("xueqiu", "juicebro")

    def fetch(self, days: int = 7) -> FetchResult:
        # EXTEND: V2 阶段在此实现雪球用户时间线获取
        # 建议方案：访问 https://xueqiu.com/u/juicebro 解析公开时间线
        # 注意：雪球有防爬机制，直接 Web 访问需要 Cookie
        logger.info("[xueqiu] 骨架模式：返回空结果")
        return self._make_result(
            status="accessible",
            posts=[],  # EXTEND: 替换为真实结果
        )


class XiaoyuzhouFetcher(PlatformFetcher):
    """小宇宙播客获取器（骨架，RSS 支持最好）。"""

    def __init__(self, podcast_id: Optional[str] = None) -> None:
        super().__init__("xiaoyuzhou", "果汁哥")
        self.podcast_id = podcast_id

    def fetch(self, days: int = 30) -> FetchResult:
        if not self.podcast_id:
            logger.warning("[xiaoyuzhou] podcast_id 未配置，跳过查询")
            return self._make_result(
                status="unreachable",
                error_message="小宇宙 podcast_id 未配置，请先确认播客 ID",
            )

        # EXTEND: V2 阶段在此实现 RSS 订阅解析
        # RSS URL 格式：https://feed.xiaoyuzhoufm.com/podcasts/{podcast_id}.xml
        # 使用 feedparser 库解析 RSS：
        #
        # import feedparser
        # rss_url = f"https://feed.xiaoyuzhoufm.com/podcasts/{self.podcast_id}.xml"
        # feed = feedparser.parse(rss_url)
        # for entry in feed.entries:
        #     raw_post = RawPost(
        #         platform_id="xiaoyuzhou",
        #         account_name="果汁哥",
        #         raw_text=entry.get("summary", ""),
        #         raw_time_str=entry.get("published", None),
        #         title=entry.get("title", None),
        #         source_url=entry.get("link", None),
        #         extra={"duration": entry.get("itunes_duration", None)},
        #     )

        logger.info(f"[xiaoyuzhou] 骨架模式：podcast_id={self.podcast_id}，返回空结果")
        return self._make_result(
            status="accessible",
            posts=[],  # EXTEND: 替换为 RSS 解析结果
        )


class XimalayaFetcher(PlatformFetcher):
    """喜马拉雅播客获取器（骨架）。"""

    def __init__(self) -> None:
        super().__init__("ximalaya", "果汁哥juicebro")

    def fetch(self, days: int = 30) -> FetchResult:
        # EXTEND: V2 阶段在此实现喜马拉雅主播页面解析
        # 参考接口：https://www.ximalaya.com/revision/anchor/getByUid?uid={uid}
        logger.info("[ximalaya] 骨架模式：返回空结果")
        return self._make_result(
            status="accessible",
            posts=[],  # EXTEND: 替换为真实结果
        )


class ZhishixingqiuFetcher(PlatformFetcher):
    """知识星球（付费，直接返回受限状态）。"""

    def __init__(self) -> None:
        super().__init__("zhishixingqiu", "果汁哥私享圈")

    def fetch(self, days: int = 7) -> FetchResult:
        # 知识星球为付费内容，不尝试访问，直接返回 paid_only
        return self._make_result(
            status="paid_only",
            error_message="知识星球'果汁哥私享圈'为付费社区，内容不可公开查询",
        )


class WechatPrivateFetcher(PlatformFetcher):
    """个人微信（私域，直接返回不适用状态）。"""

    def __init__(self) -> None:
        super().__init__("wechat_private", "guozhige2024")

    def fetch(self, days: int = 7) -> FetchResult:
        return self._make_result(
            status="not_applicable",
            error_message="个人微信属于私域，不可公开查询",
        )


# ---------------------------------------------------------------------------
# 聚合查询入口
# ---------------------------------------------------------------------------

# 平台 ID → Fetcher 类映射
FETCHER_REGISTRY: dict[str, type[PlatformFetcher]] = {
    "weibo": WeiboFetcher,
    "bilibili": BilibiliFetcher,
    "xueqiu": XueqiuFetcher,
    "xiaoyuzhou": XiaoyuzhouFetcher,
    "ximalaya": XimalayaFetcher,
    "zhishixingqiu": ZhishixingqiuFetcher,
    "wechat_private": WechatPrivateFetcher,
    # EXTEND: 添加更多平台的 Fetcher
    # "xiaohongshu": XiaohongshuFetcher,
    # "douyin": DouyinFetcher,
    # "kuaishou": KuaishouFetcher,
    # "toutiao": ToutiaoFetcher,
    # "wechat_oa": WechatOAFetcher,
    # "yuanbao": YuanbaoFetcher,
}


def fetch_all_platforms(
    platform_ids: list[str] | None = None,
    days: int = 7,
) -> dict[str, FetchResult]:
    """
    批量查询多个平台。

    Args:
        platform_ids: 要查询的平台 ID 列表，None 表示查询所有已注册平台
        days: 查询时间范围（天数）

    Returns:
        platform_id → FetchResult 的字典
    """
    if platform_ids is None:
        platform_ids = list(FETCHER_REGISTRY.keys())

    results: dict[str, FetchResult] = {}

    for pid in platform_ids:
        fetcher_cls = FETCHER_REGISTRY.get(pid)
        if fetcher_cls is None:
            logger.warning(f"平台 '{pid}' 没有对应的 Fetcher，跳过")
            results[pid] = FetchResult(
                platform_id=pid,
                status="skipped",
                posts=[],
                error_message=f"平台 '{pid}' 暂无 Fetcher 实现",
            )
            continue

        try:
            fetcher = fetcher_cls()
            results[pid] = fetcher.fetch(days=days)
            logger.info(
                f"[{pid}] 查询完成：status={results[pid].status}, posts={len(results[pid].posts)}"
            )
        except Exception as e:
            logger.error(f"[{pid}] 查询异常：{e}")
            results[pid] = FetchResult(
                platform_id=pid,
                status="unreachable",
                posts=[],
                error_message=str(e),
            )

    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("=== juicebro-content-hub 数据获取骨架测试 ===\n")
    results = fetch_all_platforms(days=7)
    for pid, result in results.items():
        print(f"[{pid}] status={result.status}, posts={len(result.posts)}")
        if result.error_message:
            print(f"       error: {result.error_message}")
