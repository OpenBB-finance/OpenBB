"""ECB Releases & Documents Model (RSS feeds, Newsfeed widget).

ECB press releases, publications, and blog posts from the official RSS feeds.
The RSS items carry only a title/link/date, so each article's page is fetched
and rendered to markdown (with inline images) for the Newsfeed widget's ``body``
— the full content is available up front, no separate viewer needed.
"""

# pylint: disable=unused-argument

from typing import Any, Literal

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.world_news import (
    WorldNewsData,
    WorldNewsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_ecb.utils.non_sdmx import RSS_FEEDS


class ECBReleasesQueryParams(WorldNewsQueryParams):
    """ECB Releases & Documents Query."""

    category: Literal["all", "press_releases", "publications", "blog"] = Field(
        default="all",
        description="Which ECB feed(s) to fetch.",
    )
    limit: int = Field(
        default=20,
        description="Maximum number of releases to return (each article's body is"
        " fetched, so a modest page size keeps it responsive).",
    )


class ECBReleasesData(WorldNewsData):
    """ECB Releases & Documents Data (Newsfeed shape)."""

    author: str = Field(
        default="European Central Bank", description="Publisher of the release."
    )
    excerpt: str | None = Field(
        default=None, description="Short plain-text preview of the article."
    )
    body: str | None = Field(
        default=None, description="Full article content as markdown with inline images."
    )


class ECBReleasesFetcher(Fetcher[ECBReleasesQueryParams, list[ECBReleasesData]]):
    """Fetch ECB releases and documents from the official RSS feeds."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> ECBReleasesQueryParams:
        """Transform query."""
        return ECBReleasesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: ECBReleasesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Fetch the RSS items, then each article's body (markdown), concurrently."""
        # pylint: disable=import-outside-toplevel
        import asyncio

        from openbb_ecb.utils.data_cache import cached_records, make_key
        from openbb_ecb.utils.non_sdmx import fetch_release_body, fetch_rss_items

        feeds = list(RSS_FEEDS) if query.category == "all" else [query.category]

        async def get_feed(feed: str) -> list[dict]:
            async def loader() -> list[dict]:
                return await fetch_rss_items(feed)

            return await cached_records(
                "releases", make_key("releases", feed=feed), loader
            )

        gathered = await asyncio.gather(*[get_feed(f) for f in feeds])
        items = [item for batch in gathered for item in batch]
        # Newest first, then cap before fetching bodies (the expensive step).
        items.sort(key=lambda i: i.get("date") or "", reverse=True)
        items = items[: query.limit]

        async def attach_body(item: dict) -> dict:
            url = item.get("url") or ""

            async def loader() -> list[dict]:
                body = await fetch_release_body(url)
                return [{"body": body}] if body else []

            cached = await cached_records(
                "release_body", make_key("release_body", url=url), loader
            )
            return {**item, "body": cached[0]["body"] if cached else ""}

        return list(await asyncio.gather(*[attach_body(i) for i in items]))

    @staticmethod
    def transform_data(
        query: ECBReleasesQueryParams, data: list[dict], **kwargs: Any
    ) -> list[ECBReleasesData]:
        """Filter by date range, sort, derive an excerpt, and validate."""
        from openbb_ecb.utils.non_sdmx import release_excerpt

        start = query.start_date.isoformat() if query.start_date else None
        end = query.end_date.isoformat() if query.end_date else None
        filtered = [
            item
            for item in data
            if item.get("date")
            and (not start or item["date"][:10] >= start)
            and (not end or item["date"][:10] <= end)
        ]
        if not filtered:
            raise EmptyDataError("No ECB releases found for the query.")
        filtered.sort(key=lambda i: i.get("date") or "", reverse=True)
        return [
            ECBReleasesData.model_validate(
                {
                    **item,
                    "author": "European Central Bank",
                    "excerpt": release_excerpt(item.get("body") or ""),
                }
            )
            for item in filtered
        ]
