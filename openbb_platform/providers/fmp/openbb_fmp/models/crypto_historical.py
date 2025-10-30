"""FMP Cryptos Historical Price Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Literal

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.crypto_historical import (
    CryptoHistoricalData,
    CryptoHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class FMPCryptoHistoricalQueryParams(CryptoHistoricalQueryParams):
    """
    FMP Crypto Historical Price Query.

    Source:
    https://site.financialmodelingprep.com/developer/docs#cryptocurrency-historical-price-eod-full
    """

    __alias_dict__ = {"start_date": "from", "end_date": "to"}
    __json_schema_extra__ = {
        "symbol": {"multiple_items_allowed": True},
    }

    interval: Literal["1m", "5m", "1h", "1d"] = Field(
        default="1d", description=QUERY_DESCRIPTIONS.get("interval", "")
    )


class FMPCryptoHistoricalData(CryptoHistoricalData):
    """FMP Crypto Historical Price Data."""

    __alias_dict__ = {
        "change_percent": "changeOverTime",
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


class FMPCryptoHistoricalFetcher(
    Fetcher[
        FMPCryptoHistoricalQueryParams,
        list[FMPCryptoHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPCryptoHistoricalQueryParams:
        """Transform the query params. Start and end dates are set to 1 year interval."""
        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return FMPCryptoHistoricalQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: FMPCryptoHistoricalQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_fmp.utils.helpers import get_historical_ohlc

        return await get_historical_ohlc(query, credentials, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPCryptoHistoricalQueryParams, data: list[dict], **kwargs: Any
    ) -> list[FMPCryptoHistoricalData]:
        """Return the transformed data."""
        return [
            FMPCryptoHistoricalData.model_validate(d)
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
