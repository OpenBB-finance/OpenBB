"""Nasdaq ETF Historical Price Model."""

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_historical import (
    EtfHistoricalData,
    EtfHistoricalQueryParams,
)
from pydantic import Field

from openbb_nasdaq.utils.constants import ETF_SYMBOL_CHOICES_ENDPOINT


class NasdaqEtfHistoricalQueryParams(EtfHistoricalQueryParams):
    """Nasdaq ETF Historical Price Query.

    Source: https://www.nasdaq.com/market-activity/etf
    """

    __json_schema_extra__ = {
        "symbol": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": ETF_SYMBOL_CHOICES_ENDPOINT,
                "style": {"popupWidth": 850},
            },
        },
    }


class NasdaqEtfHistoricalData(EtfHistoricalData):
    """Nasdaq ETF Historical Price Data."""

    symbol: str | None = Field(
        default=None, description="The ticker symbol, when more than one is requested."
    )


class NasdaqEtfHistoricalFetcher(
    Fetcher[
        NasdaqEtfHistoricalQueryParams,
        list[NasdaqEtfHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> NasdaqEtfHistoricalQueryParams:
        """Transform the query."""
        return NasdaqEtfHistoricalQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqEtfHistoricalQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Nasdaq endpoint."""
        from openbb_nasdaq.utils.helpers import gather_historical_prices

        return await gather_historical_prices(
            query.symbol, None, query.start_date, query.end_date
        )

    @staticmethod
    def transform_data(
        query: NasdaqEtfHistoricalQueryParams, data: list[dict], **kwargs: Any
    ) -> list[NasdaqEtfHistoricalData]:
        """Transform the data to the standard format."""
        return [NasdaqEtfHistoricalData.model_validate(d) for d in data]
