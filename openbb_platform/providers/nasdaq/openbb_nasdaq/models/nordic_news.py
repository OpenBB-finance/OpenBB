"""Nasdaq Nordic News Model."""

from datetime import datetime
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field

from openbb_nasdaq.utils.nordic import (
    NORDIC_NEWS_MARKET_KEYS,
    NORDIC_NEWS_MARKETS,
)


class NasdaqNordicNewsQueryParams(QueryParams):
    """Nasdaq Nordic News Query.

    Source: https://www.nasdaq.com/european-market-activity/news
    """

    __json_schema_extra__ = {"market": {"choices": list(NORDIC_NEWS_MARKET_KEYS)}}

    market: NORDIC_NEWS_MARKETS = Field(
        default="all", description="The Nasdaq Nordic market to list notices for."
    )
    limit: int = Field(default=50, description="The number of notices to return.")


class NasdaqNordicNewsData(Data):
    """Nasdaq Nordic News Data."""

    date: datetime = Field(description="The release time, in CET.")
    title: str = Field(description="The headline of the notice.")
    company: str | None = Field(default=None, description="The issuing company.")
    market: str | None = Field(default=None, description="The listing market.")
    category: str | None = Field(default=None, description="The disclosure category.")
    language: str | None = Field(
        default=None, description="The language of the notice."
    )
    url: str | None = Field(default=None, description="The link to the full notice.")
    attachment_url: str | None = Field(
        default=None, description="The link to the attached document."
    )
    disclosure_id: int | None = Field(
        default=None, description="The Nasdaq disclosure identifier."
    )


class NasdaqNordicNewsFetcher(
    Fetcher[
        NasdaqNordicNewsQueryParams,
        list[NasdaqNordicNewsData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> NasdaqNordicNewsQueryParams:
        """Transform the query."""
        return NasdaqNordicNewsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqNordicNewsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Nasdaq endpoint."""
        from openbb_nasdaq.utils.helpers import _cached_request
        from openbb_nasdaq.utils.nordic import NORDIC_NEWS_URL

        url = (
            f"{NORDIC_NEWS_URL}?countResults=true&globalGroup=exchangeNotice"
            "&displayLanguage=en&timeZone=CET&dateMask=yyyy-MM-dd+HH%3Amm%3Ass"
            f"&limit={query.limit}&start=0&dir=DESC"
            f"&globalName={NORDIC_NEWS_MARKET_KEYS[query.market]}"
        )
        response = await _cached_request(url)
        items = ((response or {}).get("results") or {}).get("item") or []

        return items if isinstance(items, list) else [items]

    @staticmethod
    def transform_data(
        query: NasdaqNordicNewsQueryParams, data: list[dict], **kwargs: Any
    ) -> list[NasdaqNordicNewsData]:
        """Transform the data to the standard format.

        Raises
        ------
        EmptyDataError
            If the market published no notices.
        """
        from openbb_core.provider.utils.errors import EmptyDataError

        if not data:
            raise EmptyDataError(
                f"No exchange notices were returned for '{query.market}'."
            )

        results: list[NasdaqNordicNewsData] = []

        for row in data:
            released = parse_release_time(
                row.get("releaseTime") or row.get("published")
            )

            if released is None:
                continue

            attachments = row.get("attachment") or []
            results.append(
                NasdaqNordicNewsData.model_validate(
                    {
                        "date": released,
                        "title": row.get("headline"),
                        "company": row.get("company"),
                        "market": row.get("market"),
                        "category": row.get("cnsCategory"),
                        "language": row.get("language"),
                        "url": row.get("messageUrl"),
                        "attachment_url": (
                            attachments[0].get("attachmentUrl") if attachments else None
                        ),
                        "disclosure_id": row.get("disclosureId"),
                    }
                )
            )

        return sorted(results, key=lambda r: r.date, reverse=True)


def parse_release_time(value: Any) -> datetime | None:
    """Parse a Nasdaq Nordic release timestamp.

    Parameters
    ----------
    value : Any
        A timestamp such as '2026-07-25 00:43:00'.

    Returns
    -------
    datetime or None
        The naive CET timestamp, or None when unparseable.
    """
    if not isinstance(value, str) or not value.strip():
        return None

    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None
