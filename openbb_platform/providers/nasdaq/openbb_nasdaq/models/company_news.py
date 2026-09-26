"""Nasdaq Company News Model."""

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.company_news import (
    CompanyNewsData,
    CompanyNewsQueryParams,
)
from pydantic import Field

from openbb_nasdaq.utils.constants import SYMBOL_CHOICES_ENDPOINT


class NasdaqCompanyNewsQueryParams(CompanyNewsQueryParams):
    """Nasdaq Company News Query.

    Source: https://www.nasdaq.com/market-activity/stocks
    """

    __json_schema_extra__ = {
        "symbol": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": SYMBOL_CHOICES_ENDPOINT,
                "style": {"popupWidth": 850},
            },
        },
    }


class NasdaqCompanyNewsData(CompanyNewsData):
    """Nasdaq Company News Data."""

    publisher: str | None = Field(
        default=None, description="The publisher of the article."
    )
    topic: str | None = Field(default=None, description="The Nasdaq topic tag.")


class NasdaqCompanyNewsFetcher(
    Fetcher[
        NasdaqCompanyNewsQueryParams,
        list[NasdaqCompanyNewsData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> NasdaqCompanyNewsQueryParams:
        """Transform the query."""
        return NasdaqCompanyNewsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqCompanyNewsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Nasdaq endpoint."""
        import asyncio
        from warnings import warn

        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_nasdaq.utils.helpers import get_nasdaq_data, resolve_asset_class

        symbols = [
            s.strip().upper() for s in (query.symbol or "").split(",") if s.strip()
        ]
        results: list[dict] = []

        async def get_one(symbol: str) -> None:
            """Collect the article list for one symbol."""
            asset_class = await resolve_asset_class(symbol)

            try:
                data = await get_nasdaq_data(
                    f"news/topic/articlebysymbol?q={symbol}%7C{asset_class}"
                    f"&offset=0&limit={query.limit}&fallback=true"
                )
            except Exception as exc:  # noqa: BLE001
                warn(f"No news was returned for {symbol}. {exc}")
                return

            for row in (data or {}).get("rows") or []:
                results.append({**row, "requested_symbol": symbol})

        await asyncio.gather(*[get_one(symbol) for symbol in symbols])

        if not results:
            raise EmptyDataError("No news articles were returned for any symbol.")

        return results

    @staticmethod
    def transform_data(
        query: NasdaqCompanyNewsQueryParams, data: list[dict], **kwargs: Any
    ) -> list[NasdaqCompanyNewsData]:
        """Transform the data to the standard format."""
        from openbb_nasdaq.utils.helpers import to_date

        results: list[NasdaqCompanyNewsData] = []
        seen: set = set()

        for row in data:
            url = row.get("url") or ""
            published = to_date(row.get("created"))

            if url in seen or published is None:
                continue

            seen.add(url)

            if query.start_date and published < query.start_date:
                continue

            if query.end_date and published > query.end_date:
                continue

            symbols = [
                s.split("|", 1)[0].upper() for s in (row.get("related_symbols") or [])
            ] or [row["requested_symbol"]]
            results.append(
                NasdaqCompanyNewsData.model_validate(
                    {
                        "date": published,
                        "title": row.get("title"),
                        "excerpt": row.get("description"),
                        "url": (
                            url
                            if url.startswith("http")
                            else f"https://www.nasdaq.com{url}"
                        ),
                        "symbols": ",".join(symbols),
                        "publisher": row.get("publisher"),
                        "topic": (row.get("primarytopic") or "").split("|", 1)[0]
                        or None,
                        "images": (
                            [{"url": row["image"]}] if row.get("image") else None
                        ),
                    }
                )
            )

        return sorted(results, key=lambda r: r.date, reverse=True)[: query.limit]
