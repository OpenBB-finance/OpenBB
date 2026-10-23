"""Nasdaq Crypto Historical Price Model."""

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.crypto_historical import (
    CryptoHistoricalData,
    CryptoHistoricalQueryParams,
)
from pydantic import Field

from openbb_nasdaq.utils.constants import SYMBOL_CHOICES_ENDPOINT


class NasdaqCryptoHistoricalQueryParams(CryptoHistoricalQueryParams):
    """Nasdaq Crypto Historical Price Query.

    Source: https://www.nasdaq.com/market-activity/crypto
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


class NasdaqCryptoHistoricalData(CryptoHistoricalData):
    """Nasdaq Crypto Historical Price Data."""

    symbol: str | None = Field(
        default=None, description="The ticker symbol, when more than one is requested."
    )


class NasdaqCryptoHistoricalFetcher(
    Fetcher[
        NasdaqCryptoHistoricalQueryParams,
        list[NasdaqCryptoHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> NasdaqCryptoHistoricalQueryParams:
        """Transform the query."""
        return NasdaqCryptoHistoricalQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqCryptoHistoricalQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Nasdaq endpoint."""
        from openbb_nasdaq.utils.helpers import gather_historical_prices

        return await gather_historical_prices(
            query.symbol, "crypto", query.start_date, query.end_date
        )

    @staticmethod
    def transform_data(
        query: NasdaqCryptoHistoricalQueryParams, data: list[dict], **kwargs: Any
    ) -> list[NasdaqCryptoHistoricalData]:
        """Transform the data to the standard format."""
        return [NasdaqCryptoHistoricalData.model_validate(d) for d in data]
