"""Nasdaq Index Search Model."""

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.index_search import (
    IndexSearchData,
    IndexSearchQueryParams,
)
from pydantic import Field

from openbb_nasdaq.utils.screener_filters import (
    INDEX_TYPE,
    INDEX_TYPE_CHOICES,
    INDEX_TYPE_MAP,
)


class NasdaqIndexSearchQueryParams(IndexSearchQueryParams):
    """Nasdaq Index Search Query.

    Source: https://www.nasdaq.com/market-activity/indexes/screener
    """

    __json_schema_extra__ = {
        "index_type": {"x-widget_config": {"options": INDEX_TYPE_CHOICES}},
    }

    index_type: INDEX_TYPE = Field(
        default="all_indexes", description="Filter by the index domicile."
    )


class NasdaqIndexSearchData(IndexSearchData):
    """Nasdaq Index Search Data."""

    last_price: float | None = Field(default=None, description="The last index level.")
    change: float | None = Field(
        default=None, description="The change from the previous close."
    )
    change_percent: float | None = Field(
        default=None,
        description="The change from the previous close, as a normalized percentage.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )


class NasdaqIndexSearchFetcher(
    Fetcher[
        NasdaqIndexSearchQueryParams,
        list[NasdaqIndexSearchData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> NasdaqIndexSearchQueryParams:
        """Transform the query."""
        return NasdaqIndexSearchQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqIndexSearchQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Nasdaq endpoint."""
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_nasdaq.utils.helpers import get_nasdaq_data

        index_type = INDEX_TYPE_MAP[query.index_type]
        data = await get_nasdaq_data(
            f"screener/index?tableonly=true&limit=10000&indextype={index_type}"
        )
        rows = ((data or {}).get("records") or {}).get("data") or {}
        rows = rows.get("rows") or []

        if not rows:
            raise EmptyDataError("No indexes matched the requested filters.")

        return rows

    @staticmethod
    def transform_data(
        query: NasdaqIndexSearchQueryParams, data: list[dict], **kwargs: Any
    ) -> list[NasdaqIndexSearchData]:
        """Transform the data to the standard format."""
        from openbb_nasdaq.utils.helpers import to_number, to_percent

        results = [
            NasdaqIndexSearchData.model_validate(
                {
                    "symbol": row.get("symbol"),
                    "name": row.get("companyName"),
                    "last_price": to_number(row.get("lastSalePrice")),
                    "change": to_number(row.get("netChange")),
                    "change_percent": to_percent(row.get("percentageChange")),
                }
            )
            for row in data
            if row.get("symbol")
        ]

        if query.query:
            needle = query.query.lower()
            field = "symbol" if query.is_symbol else None
            results = [
                r
                for r in results
                if (
                    needle in (r.symbol or "").lower()
                    if field
                    else needle in (r.symbol or "").lower()
                    or needle in (r.name or "").lower()
                )
            ]

        return results
