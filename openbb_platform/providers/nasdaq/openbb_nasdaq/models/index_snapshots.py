"""Nasdaq Index Snapshots Model."""

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.index_snapshots import (
    IndexSnapshotsData,
    IndexSnapshotsQueryParams,
)
from pydantic import Field

from openbb_nasdaq.utils.constants import CELL_CLICK_SYMBOL

REGION_SCREENERS = {
    "all": "ALL",
    "us": "US",
    "international": "GM",
}

NORDIC_REGION = "nordic"


class NasdaqIndexSnapshotsQueryParams(IndexSnapshotsQueryParams):
    """Nasdaq Index Snapshots Query.

    Source: https://www.nasdaq.com/market-activity/indexes/screener
    """

    __json_schema_extra__ = {
        "region": {
            "choices": [*REGION_SCREENERS, NORDIC_REGION],
            "x-widget_config": {
                "options": [
                    {"label": "All", "value": "all"},
                    {"label": "US", "value": "us"},
                    {"label": "International", "value": "international"},
                    {"label": "Nordic", "value": "nordic"},
                ]
            },
        },
    }

    region: str = Field(
        default="us",
        description="The index universe to return. Nordic indexes are served"
        + " from the Nasdaq Nordic listing.",
    )


class NasdaqIndexSnapshotsData(IndexSnapshotsData):
    """Nasdaq Index Snapshots Data."""

    symbol: str = Field(
        description="The index symbol.",
        json_schema_extra={"x-widget_config": CELL_CLICK_SYMBOL},
    )
    change_percent: float | None = Field(
        default=None,
        description="Change, as a normalized percent, of the index.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    volume: float | None = Field(
        default=None, description="The last session's share volume."
    )


class NasdaqIndexSnapshotsFetcher(
    Fetcher[
        NasdaqIndexSnapshotsQueryParams,
        list[NasdaqIndexSnapshotsData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> NasdaqIndexSnapshotsQueryParams:
        """Transform the query."""
        return NasdaqIndexSnapshotsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqIndexSnapshotsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Nasdaq endpoint.

        Raises
        ------
        OpenBBError
            If the region is not one Nasdaq publishes an index universe for.
        """
        from openbb_core.app.model.abstract.error import OpenBBError

        from openbb_nasdaq.utils.helpers import get_nasdaq_data

        region = query.region.lower()

        if region == NORDIC_REGION:
            data = await get_nasdaq_data(
                "nordic/screener/indexes?tableonly=false&lang=en&size=1000&page=1"
            )

            return (data or {}).get("instrumentListing", {}).get("rows") or []

        if region not in REGION_SCREENERS:
            raise OpenBBError(
                f"'{query.region}' is not a Nasdaq index region."
                f" Choose one of: {', '.join([*REGION_SCREENERS, NORDIC_REGION])}."
            )

        data = await get_nasdaq_data(
            "screener/index?tableonly=true&limit=10000"
            f"&indextype={REGION_SCREENERS[region]}"
        )
        records = ((data or {}).get("records") or {}).get("data") or {}

        return records.get("rows") or []

    @staticmethod
    def transform_data(
        query: NasdaqIndexSnapshotsQueryParams, data: list[dict], **kwargs: Any
    ) -> list[NasdaqIndexSnapshotsData]:
        """Transform the data to the standard format.

        Raises
        ------
        EmptyDataError
            If the region returned no indexes.
        """
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_nasdaq.utils.helpers import clean_value, to_number, to_percent

        if not data:
            raise EmptyDataError(f"No indexes were returned for '{query.region}'.")

        results: list[NasdaqIndexSnapshotsData] = []

        for row in data:
            symbol = row.get("symbol")

            if not symbol:
                continue

            results.append(
                NasdaqIndexSnapshotsData.model_validate(
                    {
                        "symbol": symbol,
                        "name": row.get("companyName") or row.get("fullName"),
                        "currency": clean_value(row.get("currency")),
                        "price": to_number(row.get("lastSalePrice")),
                        "high": to_number(row.get("high")),
                        "low": to_number(row.get("low")),
                        "volume": to_number(row.get("volume")),
                        "change": to_number(row.get("netChange")),
                        "change_percent": to_percent(row.get("percentageChange")),
                    }
                )
            )

        return results
