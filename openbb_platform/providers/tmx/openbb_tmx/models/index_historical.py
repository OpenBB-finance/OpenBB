"""TMX Index Historical Model."""

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.index_historical import (
    IndexHistoricalData,
    IndexHistoricalQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

UNPUBLISHED = ("N/A", "", "-", "null")


class TmxIndexHistoricalQueryParams(IndexHistoricalQueryParams):
    """TMX Index Historical Query Params."""

    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request. The daily levels are"
        + " cached for six hours. To bypass, set to False.",
    )


class TmxIndexHistoricalData(IndexHistoricalData):
    """TMX Index Historical Data."""

    __alias_dict__ = {
        "date": "datetime",
        "open": "openPrice",
        "close": "closePrice",
        "change_percent": "changePercent",
        "trade_value": "tradeValue",
        "transactions": "numberOfTrade",
    }

    change: float | None = Field(
        default=None,
        description="The change in the level from the previous session.",
    )
    change_percent: float | None = Field(
        default=None,
        description="The change in the level from the previous session, as a percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    vwap: float | None = Field(
        default=None,
        description="The volume weighted average price of the session.",
    )
    trade_value: float | None = Field(
        default=None,
        description="The total value traded over the session.",
    )
    transactions: int | None = Field(
        default=None,
        description="The number of transactions over the session.",
    )

    @field_validator("change_percent", mode="before", check_fields=False)
    @classmethod
    def normalize_percent(cls, v):
        """Return percents as normalized percentage points."""
        return float(v) / 100 if v else None


class TmxIndexHistoricalFetcher(
    Fetcher[TmxIndexHistoricalQueryParams, list[TmxIndexHistoricalData]]
):
    """TMX Index Historical Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TmxIndexHistoricalQueryParams:
        """Transform the query."""
        return TmxIndexHistoricalQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxIndexHistoricalQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Read the published levels."""
        from openbb_tmx.utils.helpers import get_daily_price_history

        return await get_daily_price_history(
            query.symbol, query.start_date, query.end_date
        )

    @staticmethod
    def transform_data(
        query: TmxIndexHistoricalQueryParams, data: list[dict], **kwargs: Any
    ) -> list[TmxIndexHistoricalData]:
        """Return the levels oldest first.

        Raises
        ------
        EmptyDataError
            If the index publishes no levels over the window.
        """
        if not data:
            raise EmptyDataError(f"No levels found for index, {query.symbol}")

        return [
            TmxIndexHistoricalData.model_validate(
                {
                    "symbol": query.symbol,
                    **{k: None if v in UNPUBLISHED else v for k, v in row.items()},
                }
            )
            for row in sorted(data, key=lambda row: str(row.get("datetime")))
        ]
