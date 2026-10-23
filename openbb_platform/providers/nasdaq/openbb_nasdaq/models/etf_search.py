"""Nasdaq ETF Search Model."""

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_search import (
    EtfSearchData,
    EtfSearchQueryParams,
)
from pydantic import Field

from openbb_nasdaq.utils.constants import CELL_CLICK_SYMBOL
from openbb_nasdaq.utils.screener_filters import (
    ETF_ASSET_CLASS,
    ETF_ASSET_CLASS_CHOICES,
    ETF_ASSET_CLASS_MAP,
    ETF_FUND_FAMILY,
    ETF_FUND_FAMILY_CHOICES,
    ETF_FUND_FAMILY_MAP,
    ETF_PERFORMANCE,
    ETF_PERFORMANCE_CHOICES,
    ETF_PERFORMANCE_MAP,
    ETF_REGION,
    ETF_REGION_CHOICES,
    ETF_REGION_MAP,
    ETF_SECTOR,
    ETF_SECTOR_CHOICES,
    ETF_SECTOR_MAP,
)

_MAX_CONCURRENCY = 16
_MAX_ATTEMPTS = 3
_RETRY_BACKOFF = 0.5


class NasdaqEtfSearchQueryParams(EtfSearchQueryParams):
    """Nasdaq ETF Search Query.

    Source: https://www.nasdaq.com/market-activity/etf/screener
    """

    __json_schema_extra__ = {
        "fund_family": {"x-widget_config": {"options": ETF_FUND_FAMILY_CHOICES}},
        "sector": {"x-widget_config": {"options": ETF_SECTOR_CHOICES}},
        "asset_class": {"x-widget_config": {"options": ETF_ASSET_CLASS_CHOICES}},
        "region": {"x-widget_config": {"options": ETF_REGION_CHOICES}},
        "performance": {"x-widget_config": {"options": ETF_PERFORMANCE_CHOICES}},
    }

    fund_family: ETF_FUND_FAMILY = Field(
        default="all_funds", description="Filter by the fund family."
    )
    sector: ETF_SECTOR = Field(
        default="all_sectors", description="Filter by the fund's sector."
    )
    asset_class: ETF_ASSET_CLASS = Field(
        default="all_asset_classes", description="Filter by the fund's asset class."
    )
    region: ETF_REGION = Field(
        default="all_region", description="Filter by the fund's geography."
    )
    performance: ETF_PERFORMANCE = Field(
        default="all_performance", description="Filter by trailing annual performance."
    )


class NasdaqEtfSearchData(EtfSearchData):
    """Nasdaq ETF Search Data."""

    symbol: str = Field(
        description="The fund symbol.",
        json_schema_extra={"x-widget_config": CELL_CLICK_SYMBOL},
    )
    last_price: float | None = Field(default=None, description="The last price.")
    change_percent: float | None = Field(
        default=None,
        description="The change from the previous close, as a normalized percentage.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    one_year_percent: float | None = Field(
        default=None,
        description="The trailing one-year return, as a normalized percentage.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )


class NasdaqEtfSearchFetcher(
    Fetcher[
        NasdaqEtfSearchQueryParams,
        list[NasdaqEtfSearchData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> NasdaqEtfSearchQueryParams:
        """Transform the query."""
        return NasdaqEtfSearchQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqEtfSearchQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Nasdaq endpoint."""
        import asyncio

        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_nasdaq.utils.helpers import get_nasdaq_data

        params = {
            "fundfamily": ETF_FUND_FAMILY_MAP[query.fund_family],
            "sector": ETF_SECTOR_MAP[query.sector],
            "assetclass": ETF_ASSET_CLASS_MAP[query.asset_class],
            "region": ETF_REGION_MAP[query.region],
            "performance": ETF_PERFORMANCE_MAP[query.performance],
        }
        querystring = "&".join(f"{k}={v}" for k, v in params.items() if v != "all")
        suffix = f"&{querystring}" if querystring else ""
        base = f"screener/etf?tableonly=true&limit=10000{suffix}"

        def _page_rows(payload: dict | None) -> list[dict]:
            records = (payload or {}).get("records") or {}
            return ((records.get("data") or {}).get("rows")) or []

        first = await get_nasdaq_data(f"{base}&offset=0") or {}
        rows = _page_rows(first)
        records = first.get("records") or {}
        total = int(records.get("totalrecords") or len(rows))
        page_size = int(records.get("limit") or len(rows) or 1)

        if page_size and total > len(rows):
            semaphore = asyncio.Semaphore(_MAX_CONCURRENCY)

            async def get_page(offset: int) -> list[dict]:
                """Fetch one page of the listing, retrying on a refused request."""
                async with semaphore:
                    for attempt in range(_MAX_ATTEMPTS):
                        try:
                            return _page_rows(
                                await get_nasdaq_data(f"{base}&offset={offset}")
                            )
                        except Exception:  # noqa: BLE001
                            await asyncio.sleep(_RETRY_BACKOFF * (attempt + 1))

                    return []

            pages = await asyncio.gather(
                *[get_page(offset) for offset in range(page_size, total, page_size)]
            )

            for page_rows in pages:
                rows.extend(page_rows)

        if not rows:
            raise EmptyDataError("No ETFs matched the requested filters.")

        return rows

    @staticmethod
    def transform_data(
        query: NasdaqEtfSearchQueryParams, data: list[dict], **kwargs: Any
    ) -> list[NasdaqEtfSearchData]:
        """Transform the data to the standard format."""
        from openbb_nasdaq.utils.helpers import to_number, to_percent

        results = [
            NasdaqEtfSearchData.model_validate(
                {
                    "symbol": row.get("symbol"),
                    "name": row.get("companyName"),
                    "last_price": to_number(row.get("lastSalePrice")),
                    "change_percent": to_percent(row.get("percentageChange")),
                    "one_year_percent": to_percent(
                        row.get("oneYearPercentage")
                        or row.get("oneYearPercentagechange")
                    ),
                }
            )
            for row in data
            if row.get("symbol")
        ]

        if query.query:
            needle = query.query.lower()
            results = [
                r
                for r in results
                if needle in (r.symbol or "").lower()
                or needle in (r.name or "").lower()
            ]

        return results
