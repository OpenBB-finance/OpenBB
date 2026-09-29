"""Cboe Index Snapshots Model."""

from datetime import datetime
from typing import Any, Literal

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.index_snapshots import (
    IndexSnapshotsData,
    IndexSnapshotsQueryParams,
)
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

PERCENT_COLUMNS = [
    "price_change_percent",
    "iv30",
    "iv30_change",
    "iv30_change_percent",
]

DROP_COLUMNS = [
    "exchange_id",
    "seqno",
    "index",
    "security_type",
    "ask_size",
    "bid_size",
]

REGION_URLS = {
    "us": "https://cdn.cboe.com/api/global/delayed_quotes/quotes/all_us_indices.json",
    "eu": "https://cdn.cboe.com/api/global/european_indices/index_quotes/all-indices.json",
    "au": "https://cdn.cboe.com/api/global/au_indices/index_quotes/all-indices.json",
}


class CboeIndexSnapshotsQueryParams(IndexSnapshotsQueryParams):
    """Cboe Index Snapshots Query.

    Source: https://www.cboe.com/
    """

    __json_schema_extra__ = {"region": {"choices": ["us", "eu", "au"]}}

    region: Literal["us", "eu", "au"] = Field(
        default="us",
        description="The region of focus for the data - i.e., us, eu, au."
        + " 'au' covers the Cboe Australia (CXA) indices.",
    )

    @field_validator("region", mode="after", check_fields=False)
    @classmethod
    def validate_region(cls, v):
        """Validate the region."""
        return v if v else "us"


class CboeIndexSnapshotsData(IndexSnapshotsData):
    """Cboe Index Snapshots Data."""

    __alias_dict__ = {
        "prev_close": "prev_day_close",
        "change": "price_change",
        "change_percent": "price_change_percent",
        "price": "current_price",
    }

    bid: float | None = Field(default=None, description="Current bid price.")
    ask: float | None = Field(default=None, description="Current ask price.")
    open: float | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("open", "")
    )
    high: float | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("high", "")
    )
    low: float | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("low", "")
    )
    close: float | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("close", "")
    )
    volume: int | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("volume", "")
    )
    prev_close: float | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("prev_close", "")
    )
    change: float | None = Field(default=None, description="Change in price.")
    change_percent: float | None = Field(
        default=None, description="Change in price as a normalized percentage."
    )
    last_trade_time: datetime | None = Field(
        default=None, description="Last trade timestamp for the symbol."
    )
    status: str | None = Field(
        default=None, description="Status of the market, open or closed."
    )


async def _with_index_names(rows: list[dict]) -> list[dict]:
    """Name each index from the published directory."""
    from openbb_cboe.utils.helpers import get_index_directory

    if not rows:
        return rows

    try:
        directory = await get_index_directory()
    except Exception:  # noqa: BLE001
        return rows

    names = {
        str(symbol): str(name)
        for symbol, name in zip(directory["index_symbol"], directory["name"])
        if isinstance(name, str) and name
    }

    for row in rows:
        symbol = str(row.get("symbol") or "").replace("^", "")
        name = names.get(symbol)
        row["symbol"] = symbol

        if name:
            row["name"] = name

    return rows


class CboeIndexSnapshotsFetcher(
    Fetcher[
        CboeIndexSnapshotsQueryParams,
        list[CboeIndexSnapshotsData],
    ]
):
    """Transform the query, extract and transform the data from the Cboe endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CboeIndexSnapshotsQueryParams:
        """Transform the query."""
        return CboeIndexSnapshotsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CboeIndexSnapshotsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Cboe endpoint."""
        from openbb_core.provider.utils.helpers import amake_request

        data = await amake_request(REGION_URLS[query.region], **kwargs)
        rows = data.get("data", []) if isinstance(data, dict) else data

        return await _with_index_names(rows)

    @staticmethod
    def transform_data(
        query: CboeIndexSnapshotsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[CboeIndexSnapshotsData]:
        """Transform the data to the standard format."""
        from pandas import DataFrame

        if not data:
            raise EmptyDataError()

        df = DataFrame(data)

        for col in PERCENT_COLUMNS:
            if col in df.columns:
                df[col] = df[col] / 100

        df = (
            df.replace(0, None)
            .replace("", None)
            .dropna(how="all", axis=1)
            .fillna("N/A")
            .replace("N/A", None)
        )

        for col in DROP_COLUMNS:
            if col in df.columns:
                df = df.drop(columns=col)

        records = df.to_dict(orient="records")

        for record in records:
            if not isinstance(record.get("name"), str):
                record.pop("name", None)

        return [CboeIndexSnapshotsData.model_validate(d) for d in records]
