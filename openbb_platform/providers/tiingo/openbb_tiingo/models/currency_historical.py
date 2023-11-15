"""Tiingo Currency end of day fetcher."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from dateutil.relativedelta import relativedelta
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.currency_historical import (
    CurrencyHistoricalData,
    CurrencyHistoricalQueryParams,
)
from openbb_provider.utils.helpers import make_request
from pydantic import Field


class TiingoCurrencyHistoricalQueryParams(CurrencyHistoricalQueryParams):
    """Tiingo Currency end of day Query.

    Source: https://www.tiingo.com/documentation/end-of-day
    """

    interval: Literal[
        "1min", "5min", "15min", "30min", "1hour", "4hour", "1day"
    ] = Field(default="1day", description="Data granularity.")


class TiingoCurrencyHistoricalData(CurrencyHistoricalData):
    """Tiingo Currency end of day Data."""


class TiingoCurrencyHistoricalFetcher(
    Fetcher[
        TiingoCurrencyHistoricalQueryParams,
        List[TiingoCurrencyHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the Tiingo endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TiingoCurrencyHistoricalQueryParams:
        """Transform the query params."""
        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return TiingoCurrencyHistoricalQueryParams(**transformed_params)

    # pylint: disable=protected-access
    @staticmethod
    def extract_data(
        query: TiingoCurrencyHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Tiingo endpoint."""
        api_key = credentials.get("tiingo_token") if credentials else ""

        base_url = (
            f"https://api.tiingo.com/tiingo/fx/prices?tickers={query.symbol}"
            f"&startDate={query.start_date}"
            f"&endDate={query.end_date}"
            f"&resampleFreq={query.interval}"
            f"&token={api_key}"
        )

        request = make_request(base_url)
        request.raise_for_status()
        return request.json()

    # pylint: disable=unused-argument
    @staticmethod
    def transform_data(
        query: TiingoCurrencyHistoricalQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TiingoCurrencyHistoricalData]:
        """Return the transformed data."""

        return [TiingoCurrencyHistoricalData.model_validate(d) for d in data]
