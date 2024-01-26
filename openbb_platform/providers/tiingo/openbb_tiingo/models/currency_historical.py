"""Tiingo Currency Historical Price Model."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.currency_historical import (
    CurrencyHistoricalData,
    CurrencyHistoricalQueryParams,
)
from openbb_core.provider.utils.helpers import get_querystring
from openbb_tiingo.utils.helpers import get_data_many
from pydantic import Field


class TiingoCurrencyHistoricalQueryParams(CurrencyHistoricalQueryParams):
    """Tiingo Currency Historical Price Query.

    Source: https://www.tiingo.com/documentation/end-of-day
    """

    __alias_dict__ = {
        "symbol": "tickers",
        "start_date": "startDate",
        "end_date": "endDate",
    }

    interval: Literal["1min", "5min", "15min", "30min", "1hour", "4hour", "1day"] = (
        Field(default="1day", description="Data granularity.", alias="resampleFreq")
    )


class TiingoCurrencyHistoricalData(CurrencyHistoricalData):
    """Tiingo Currency Historical Price Data."""


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

    # pylint: disable=protected-access,unused-argument
    @staticmethod
    def extract_data(
        query: TiingoCurrencyHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Tiingo endpoint."""
        api_key = credentials.get("tiingo_token") if credentials else ""

        base_url = "https://api.tiingo.com/tiingo/fx/prices"
        query_str = get_querystring(query.model_dump(by_alias=True), [])
        url = f"{base_url}?{query_str}&token={api_key}"
        data = get_data_many(url)

        return data

    # pylint: disable=unused-argument
    @staticmethod
    def transform_data(
        query: TiingoCurrencyHistoricalQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TiingoCurrencyHistoricalData]:
        """Return the transformed data."""
        return [TiingoCurrencyHistoricalData.model_validate(d) for d in data]
