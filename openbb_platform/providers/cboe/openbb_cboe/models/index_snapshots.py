"""CBOE Index Snapshots Model."""

# pylint: disable=unused-argument

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


class CboeIndexSnapshotsQueryParams(IndexSnapshotsQueryParams):
    """CBOE Index Snapshots Query.

    Source: https://www.cboe.com/
    """

    region: Literal["us", "eu"] = Field(
        default="us",
    )

    @field_validator("region", mode="after", check_fields=False)
    @classmethod
    def validate_region(cls, v):
        """Validate region."""
        return v if v else "us"


class CboeIndexSnapshotsData(IndexSnapshotsData):
    """CBOE Index Snapshots Data."""

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


class CboeIndexSnapshotsFetcher(
    Fetcher[
        CboeIndexSnapshotsQueryParams,
        list[CboeIndexSnapshotsData],
    ]
):
    """Transform the query, extract and transform the data from the CBOE endpoints"""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CboeIndexSnapshotsQueryParams:
        """Transform the query."""
        return CboeIndexSnapshotsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CboeIndexSnapshotsQueryParams,
        credentials: dict[str, str] | None,  # pylint: disable=unused-argument
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Cboe endpoint"""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import amake_request

        url: str = ""
        if query.region == "us":
            url = "https://cdn.cboe.com/api/global/delayed_quotes/quotes/all_us_indices.json"
        if query.region == "eu":
            url = "https://cdn.cboe.com/api/global/european_indices/index_quotes/all-indices.json"

        data = await amake_request(url, **kwargs)
        return data.get("data")  # type: ignore

    @staticmethod
    def transform_data(
        query: CboeIndexSnapshotsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[CboeIndexSnapshotsData]:
        """Transform the data to the standard format"""
        # pylint: disable=import-outside-toplevel
        from pandas import DataFrame

        if not data:
            raise EmptyDataError()
        df = DataFrame(data)
        percent_cols = [
            "price_change_percent",
            "iv30",
            "iv30_change",
            "iv30_change_percent",
        ]
        for col in percent_cols:
            if col in df.columns:
                df[col] = round(df[col] / 100, 6)
        df = (
            df.replace(0, None)
            .replace("", None)
            .dropna(how="all", axis=1)
            .fillna("N/A")
            .replace("N/A", None)
        )
        drop_cols = [
            "exchange_id",
            "seqno",
            "index",
            "security_type",
            "ask_size",
            "bid_size",
        ]
        for col in drop_cols:
            if col in df.columns:
                df = df.drop(columns=col)
        return [
            CboeIndexSnapshotsData.model_validate(d)
            for d in df.to_dict(orient="records")
        ]
