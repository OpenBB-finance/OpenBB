"""RSS news feed endpoint."""

import asyncio
from datetime import (
    date as dateType,
    datetime,
)
from typing import TYPE_CHECKING, Annotated

from fastapi import Query
from openbb_core.app.model.example import APIEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from pydantic import Field

if TYPE_CHECKING:
    from aiohttp import ClientSession

api_prefix = SystemService().system_settings.api_settings.prefix

router = Router(prefix="", description="RSS news feeds.")


async def _gather_bodies(
    session: "ClientSession", links: list[str | None]
) -> list[str | None]:
    """Fetch article bodies concurrently."""
    from openbb_news.parser import fetch_article_body

    async def one(link: str | None) -> str | None:
        if not link:
            return None
        try:
            return await fetch_article_body(session, link)
        except asyncio.CancelledError:
            raise
        except Exception:  # noqa: BLE001
            return None

    return await asyncio.gather(*(one(link) for link in links))


class NewsItemData(Data):
    """One article in Newsfeed-widget shape."""

    title: str = Field(description="Article headline.")
    date: datetime | dateType | str = Field(description="ISO 8601 publication date.")
    author: str = Field(description="Author (falls back to the feed name).")
    url: str = Field(description="Canonical article URL from the RSS feed.")
    excerpt: str = Field(description="Short plain-text summary.")
    body: str = Field(description="Article body as markdown with inline images.")


@router.command(
    methods=["GET"],
    widget_config={
        "name": "RSS News Feed",
        "description": (
            "Articles from any RSS/Atom feed registered under"
            " [news.rss_feeds] in openbb.toml."
        ),
        "type": "newsfeed",
        "category": "News",
        "subCategory": "RSS",
        "source": ["RSS"],
        "gridData": {"w": 20, "h": 15},
        "refetchInterval": 300000,
        "params": [
            {
                "paramName": "outlet",
                "label": "Provider",
                "value": "benzinga",
                "description": "News outlet grouping the available feeds.",
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/news/rss_providers",
                "style": {"popupWidth": 280},
            },
            {
                "paramName": "source",
                "label": "Feed",
                "value": None,
                "description": "Specific feed within the selected provider.",
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/news/rss_feeds",
                "optionsParams": {"outlet": "$outlet"},
                "style": {"popupWidth": 360},
                "optional": True,
            },
            {
                "paramName": "limit",
                "label": "Limit",
                "value": 20,
                "description": "Maximum number of articles to return.",
                "type": "number",
                "optional": True,
            },
            {
                "paramName": "fetch_body",
                "label": "Fetch full body",
                "value": True,
                "description": "Fetch each article URL for its full body.",
                "type": "boolean",
                "optional": True,
            },
        ],
    },
    examples=[APIEx(parameters={"source": "yahoo_finance"})],
)
async def rss(
    outlet: Annotated[
        str | None,
        Query(title="Provider", description="Outlet id."),
    ] = None,
    source: Annotated[
        str | None,
        Query(title="Source", description="Configured feed key."),
    ] = None,
    limit: Annotated[
        int,
        Query(title="Limit", description="Maximum articles to return.", ge=1),
    ] = 20,
    fetch_body: Annotated[
        bool,
        Query(title="Fetch body", description="Fetch each article URL for its body."),
    ] = True,
) -> OBBject[list[NewsItemData]]:
    """Fetch a registered RSS feed."""
    from openbb_core.provider.utils.helpers import get_async_requests_session

    from openbb_news.parser import (
        fetch_feed,
        html_to_markdown,
        strip_html,
        struct_time_to_iso,
        truncate,
    )
    from openbb_news.registry import default_feed_for, get_feed_url

    if not source:
        source = default_feed_for(outlet)
        if not source:
            return OBBject(results=[])

    url = get_feed_url(source)

    async with await get_async_requests_session() as session:
        parsed = await fetch_feed(session, url)
        feed_title = (parsed.feed.get("title") if parsed.feed else "") or ""
        entries = sorted(
            parsed.entries,
            key=lambda e: (
                e.get("published_parsed") or e.get("updated_parsed") or (0,) * 9
            ),
            reverse=True,
        )[:limit]

        if fetch_body and entries:
            links = [entry.get("link") for entry in entries]
            bodies = await _gather_bodies(session, links)
        else:
            bodies = [None] * len(entries)

    out: list[NewsItemData] = []
    for entry, fetched_body in zip(entries, bodies):
        summary_html = entry.get("summary") or entry.get("description") or ""
        excerpt = truncate(strip_html(summary_html))
        body = fetched_body or html_to_markdown(summary_html) or excerpt
        out.append(
            NewsItemData(
                title=(entry.get("title") or "(untitled)").strip(),
                date=struct_time_to_iso(
                    entry.get("published_parsed") or entry.get("updated_parsed")
                ),
                author=entry.get("author") or feed_title or "Unknown",
                url=(entry.get("link") or "").strip(),
                excerpt=excerpt,
                body=body,
            )
        )

    return OBBject(results=out)


@router.command(methods=["GET"], widget_config={"exclude": True})
async def rss_providers() -> list[dict[str, str]]:
    """Return [{label, value}] for active news providers."""
    from openbb_news.registry import list_providers

    return [
        {"label": label, "value": value} for value, label in list_providers().items()
    ]


@router.command(methods=["GET"], widget_config={"exclude": True})
async def rss_feeds(
    outlet: Annotated[
        str | None,
        Query(title="Outlet", description="Outlet id."),
    ] = None,
) -> list[dict[str, str]]:
    """Return [{label, value}] for feeds under outlet."""
    from openbb_news.registry import list_feed_choices

    return list_feed_choices(outlet)
