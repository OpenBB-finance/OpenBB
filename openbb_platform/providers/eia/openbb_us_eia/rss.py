"""EIA RSS feed HTML widget."""

from fastapi import Depends
from fastapi.responses import HTMLResponse
from openbb_core.app.router import Router

from openbb_us_eia.browsers import request_info
from openbb_us_eia.utils.rss import (
    EIA_RSS_FEEDS,
    build_feed,
    feed_choices,
    render_rss_html,
)

router = Router(prefix="", description="EIA RSS feeds.")


async def rss_feed(
    feed: str = "today_in_energy",
    theme: str = "dark",
    info: dict = Depends(request_info),
) -> HTMLResponse:
    """Articles, releases, testimony, and fuel-price updates from EIA's RSS feeds."""
    from openbb_core.provider.utils.helpers import get_async_requests_session

    from openbb_us_eia.utils.rss import fetch_feed

    if feed not in EIA_RSS_FEEDS:
        feed = "today_in_energy"

    proxy_base = info["url"].rsplit("/rss_feed", 1)[0] + "/eia_proxy"
    async with await get_async_requests_session() as session:
        parsed = await fetch_feed(session, EIA_RSS_FEEDS[feed]["url"])

    data = build_feed(feed, parsed, 50, proxy_base)
    return HTMLResponse(content=render_rss_html(data, theme))


router._api_router.add_api_route(
    path="/rss_feed",
    endpoint=rss_feed,
    methods=["GET"],
    response_class=HTMLResponse,
    openapi_extra={
        "widget_config": {
            "name": "EIA RSS Feeds",
            "description": "Articles, releases, testimony, and fuel-price updates"
            " from the U.S. Energy Information Administration RSS feeds.",
            "category": "EIA",
            "subCategory": "News & Feeds",
            "source": ["EIA"],
            "type": "html",
            "widgetId": "eia_rss_feeds_us_eia_obb",
            "gridData": {"w": 40, "h": 20},
            "params": [
                {
                    "paramName": "feed",
                    "label": "Feed",
                    "type": "tabs",
                    "value": "today_in_energy",
                    "description": "The EIA RSS feed to display.",
                    "show": True,
                    "options": feed_choices(),
                },
                {"paramName": "theme", "show": False},
            ],
            "refetchInterval": 900000,
        }
    },
)
