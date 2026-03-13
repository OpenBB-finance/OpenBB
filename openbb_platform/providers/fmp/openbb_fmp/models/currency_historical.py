"""FMP Currency Historical Price Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Literal

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.currency_historical import (
    CurrencyHistoricalData,
    CurrencyHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class FMPCurrencyHistoricalQueryParams(CurrencyHistoricalQueryParams):
    """FMP Currency Historical Price Query.

    Source: https://site.financialmodelingprep.com/developer/docs#forex-historical-price-eod-full
    """

    __alias_dict__ = {"start_date": "from", "end_date": "to"}
    __json_schema_extra__ = {
        "symbol": {"multiple_items_allowed": True},
    }

    interval: Literal["1m", "5m", "1h", "1d"] = Field(
        default="1d", description=QUERY_DESCRIPTIONS.get("interval", "")
    )


class FMPCurrencyHistoricalData(CurrencyHistoricalData):
    """FMP Currency Historical Price Data."""

    change: float | None = Field(
        default=None,
        description="Change in the price from the previous close.",
    )
    change_percent: float | None = Field(
        default=None,
        description="Percent change in the price from the previous close.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )

    @field_validator("change_percent", mode="before", check_fields=False)
    @classmethod
    def _normalize_percent(cls, v):
        """Normalize percent."""
        return v / 100 if v else None


class FMPCurrencyHistoricalFetcher(
    Fetcher[
        FMPCurrencyHistoricalQueryParams,
        list[FMPCurrencyHistoricalData],
    ]
):
    """FMP Currency Historical Price Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPCurrencyHistoricalQueryParams:
        """Transform the query params. Start and end dates are set to a 1 year interval."""
        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return FMPCurrencyHistoricalQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: FMPCurrencyHistoricalQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_fmp.utils.helpers import get_historical_ohlc

        return await get_historical_ohlc(query, credentials, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPCurrencyHistoricalQueryParams, data: list[dict], **kwargs: Any
    ) -> list[FMPCurrencyHistoricalData]:
        """Return the transformed data."""
        return [
            FMPCurrencyHistoricalData.model_validate(d)
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
