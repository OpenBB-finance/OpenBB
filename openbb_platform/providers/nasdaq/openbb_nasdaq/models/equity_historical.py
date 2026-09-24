"""Nasdaq Equity Historical Price Model."""

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_historical import (
    EquityHistoricalData,
    EquityHistoricalQueryParams,
)
from pydantic import Field

from openbb_nasdaq.utils.constants import SYMBOL_CHOICES_ENDPOINT


class NasdaqEquityHistoricalQueryParams(EquityHistoricalQueryParams):
    """Nasdaq Equity Historical Price Query.

    Source: https://www.nasdaq.com/market-activity/stocks
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


class NasdaqEquityHistoricalData(EquityHistoricalData):
    """Nasdaq Equity Historical Price Data."""

    symbol: str | None = Field(
        default=None, description="The ticker symbol, when more than one is requested."
    )


class NasdaqEquityHistoricalFetcher(
    Fetcher[
        NasdaqEquityHistoricalQueryParams,
        list[NasdaqEquityHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> NasdaqEquityHistoricalQueryParams:
        """Transform the query."""
        return NasdaqEquityHistoricalQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqEquityHistoricalQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Nasdaq endpoint."""
        from openbb_nasdaq.utils.helpers import gather_historical_prices

        return await gather_historical_prices(
            query.symbol, "stocks", query.start_date, query.end_date
        )

    @staticmethod
    def transform_data(
        query: NasdaqEquityHistoricalQueryParams, data: list[dict], **kwargs: Any
    ) -> list[NasdaqEquityHistoricalData]:
        """Transform the data to the standard format."""
        return [NasdaqEquityHistoricalData.model_validate(d) for d in data]
