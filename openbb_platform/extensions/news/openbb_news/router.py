"""News router."""

from openbb_core.app.router import Router

from openbb_news.news_router import router as _news_router
from openbb_news.rss import router as _rss_router

router = Router(prefix="", description="Financial market news data.")
router.include_router(_news_router)
router.include_router(_rss_router)

__all__ = ["router"]
