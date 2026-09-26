"""SEC Litigation RSS Feed Model."""

from datetime import datetime
from typing import Any, cast

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field

from openbb_sec.utils.definitions import HEADERS


class SecRssLitigationQueryParams(QueryParams):
    """SEC Litigation RSS Feed Query.

    Source: https://sec.gov/
    """

    limit: int = Field(
        default=25,
        description="Number of litigation releases to return, newest first.",
    )


class SecRssLitigationData(Data):
    """SEC Litigation RSS Feed Data."""

    title: str = Field(description="The title of the litigation release.")
    date: datetime = Field(description="The date of publication.")
    author: str | None = Field(default=None, description="The author of the release.")
    excerpt: str | None = Field(
        default=None, description="Short summary of the release."
    )
    body: str | None = Field(
        default=None,
        description="Full text of the litigation release, when retrievable.",
    )
    url: str = Field(description="URL to the litigation release.")
    id: str | None = Field(
        default=None, description="The litigation release identifier."
    )


async def _text_callback(response, _session):
    """Return the response body as text."""
    return await response.text()


async def _fetch_body(url: str) -> str | None:
    """Best-effort fetch and clean of a litigation release's full text."""
    try:
        from bs4 import BeautifulSoup

        from openbb_sec.utils.html2markdown import html_to_markdown
        from openbb_sec.utils.ratelimit import sec_amake_request as amake_request

        text = cast(
            "str | None",
            await amake_request(url, headers=HEADERS, response_callback=_text_callback),
        )
        if not text:
            return None
        soup = BeautifulSoup(text, "html.parser")
        for tag in soup(["script", "style", "nav", "header", "footer", "form"]):
            tag.decompose()
        main = (
            soup.find("article")
            or soup.find(id="main-content")
            or soup.find("main")
            or soup.body
        )
        if main is None:
            return None
        body = html_to_markdown(str(main), base_url=url).strip()
        return body or None
    except Exception:  # noqa: BLE001
        return None


class SecRssLitigationFetcher(
    Fetcher[SecRssLitigationQueryParams, list[SecRssLitigationData]]
):
    """SEC RSS Litigation Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> SecRssLitigationQueryParams:
        """Transform the query."""
        return SecRssLitigationQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecRssLitigationQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the litigation releases, attempting to include the full text."""
        import asyncio
        import re
        from email.utils import parsedate_to_datetime

        import xmltodict

        from openbb_sec.utils.ratelimit import sec_amake_request as amake_request

        def _parse_date(value):
            """Parse an RFC822 RSS date string."""
            try:
                return parsedate_to_datetime(value) if value else None
            except (TypeError, ValueError):
                return None

        url = "https://www.sec.gov/enforcement-litigation/litigation-releases/rss"
        content = cast(
            "str | None",
            await amake_request(url, headers=HEADERS, response_callback=_text_callback),
        )
        if not content:
            raise OpenBBError("No data returned from the SEC litigation RSS feed.")

        cleaned = re.sub(r"&(?!amp;|lt;|gt;|quot;|apos;)", "&amp;", content)
        items = xmltodict.parse(cleaned)["rss"]["channel"]["item"]

        if isinstance(items, dict):
            items = [items]

        results: list = []
        for item in items[: query.limit]:
            link = item.get("link", "")
            release_id = None
            if match := re.search(r"(lr-?\d+|\d{5,})", link, re.IGNORECASE):
                release_id = match.group(1).upper()
            results.append(
                {
                    "title": re.sub(r"\s+", " ", (item.get("title") or "")).strip(),
                    "date": _parse_date(item.get("pubDate")),
                    "author": None,
                    "excerpt": re.sub(
                        r"\s+", " ", (item.get("description") or "")
                    ).strip()
                    or None,
                    "url": link,
                    "id": item.get("dc:creator") or release_id,
                }
            )

        bodies = await asyncio.gather(
            *[_fetch_body(r["url"]) for r in results if r["url"]]
        )
        for result, body in zip(results, bodies):
            result["body"] = body or result["excerpt"]

        return results

    @staticmethod
    def transform_data(
        query: SecRssLitigationQueryParams, data: list[dict], **kwargs: Any
    ) -> list[SecRssLitigationData]:
        """Transform the data to the standard format."""
        return [SecRssLitigationData.model_validate(d) for d in data]
