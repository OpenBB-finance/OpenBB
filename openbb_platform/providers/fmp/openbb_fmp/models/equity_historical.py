"""FMP Equity Historical Price Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Literal

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_historical import (
    EquityHistoricalData,
    EquityHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    QUERY_DESCRIPTIONS,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator, model_validator


class FMPEquityHistoricalQueryParams(EquityHistoricalQueryParams):
    """FMP Equity Historical Price Query.

    Source: https://site.financialmodelingprep.com/developer/docs#historical-price-eod-full
    """

    __alias_dict__ = {"start_date": "from", "end_date": "to"}
    __json_schema_extra__ = {
        "symbol": {"multiple_items_allowed": True},
    }

    interval: Literal["1m", "5m", "15m", "30m", "1h", "4h", "1d"] = Field(
        default="1d", description=QUERY_DESCRIPTIONS.get("interval", "")
    )
    adjustment: Literal["splits_only", "splits_and_dividends", "unadjusted"] = Field(
        default="splits_only",
        description="Type of adjustment for historical prices. Only applies to daily data.",
    )

    @model_validator(mode="before")
    @classmethod
    def _validate_params(cls, values: dict) -> dict:
        """Validate query parameters."""
        interval = values.get("interval", "1d")
        adjustment = values.get("adjustment", "splits_only")

        if adjustment != "splits_only" and interval != "1d":
            raise ValueError("Adjustment can only be applied to daily ('1d') interval.")
        return values


class FMPEquityHistoricalData(EquityHistoricalData):
    """FMP Equity Historical Price Data."""

    __alias_dict__ = {
        "open": "adjOpen",
        "high": "adjHigh",
        "low": "adjLow",
        "close": "adjClose",
    }

    change: float | None = Field(
        default=None,
        description="Change in the price from the previous close.",
    )
    change_percent: float | None = Field(
        default=None,
        description="Change in the price from the previous close, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )

    @field_validator("change_percent", mode="before", check_fields=False)
    @classmethod
    def _normalize_percent(cls, v):
        """Normalize percent."""
        return v / 100 if v else None


class FMPEquityHistoricalFetcher(
    Fetcher[
        FMPEquityHistoricalQueryParams,
        list[FMPEquityHistoricalData],
    ]
):
    """FMP Equity Historical Price Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPEquityHistoricalQueryParams:
        """Transform the query params."""
        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return FMPEquityHistoricalQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: FMPEquityHistoricalQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_fmp.utils.helpers import get_historical_ohlc

        return await get_historical_ohlc(query, credentials, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPEquityHistoricalQueryParams, data: list[dict], **kwargs: Any
    ) -> list[FMPEquityHistoricalData]:
        """Return the transformed data."""
        if not data:
            raise EmptyDataError("No data returned from FMP for the given query.")
        return [
            FMPEquityHistoricalData.model_validate(d)
            for d in sorted(
                data,
                key=lambda x: (
                    (x["date"], x["symbol"])
                    if len(query.symbol.split(",")) > 1
                    else x["date"]
                ),
                reverse=False,
            )
        ]
