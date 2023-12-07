"""Tiingo Crypto Historical Price Model."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.crypto_historical import (
    CryptoHistoricalData,
    CryptoHistoricalQueryParams,
)
from openbb_core.provider.utils.helpers import get_querystring
from openbb_tiingo.utils.helpers import get_data_one
from pydantic import Field


class TiingoCryptoHistoricalQueryParams(CryptoHistoricalQueryParams):
    """Tiingo Crypto Historical Price Query.

    Source: https://www.tiingo.com/documentation/end-of-day
    """

    __alias_dict__ = {
        "symbol": "tickers",
        "start_date": "startDate",
        "end_date": "endDate",
    }

    interval: Literal[
        "1min", "5min", "15min", "30min", "1hour", "4hour", "1day"
    ] = Field(default="1day", description="Data granularity.", alias="resampleFreq")

    exchanges: Optional[List[str]] = Field(
        default=None,
        description=(
            "To limit the query to a subset of exchanges e.g. ['POLONIEX', 'GDAX']"
        ),
    )
    # pylint: disable=protected-access


class TiingoCryptoHistoricalData(CryptoHistoricalData):
    """Tiingo Crypto Historical Price Data."""

    transactions: Optional[int] = Field(
        default=None, description="Number of trades.", alias="tradesDone"
    )

    volume_notional: Optional[float] = Field(
        default=None,
        description=(
            "The last size done for the asset on the specific date in the "
            "quote currency. The volume of the asset on the specific date in "
            "the quote currency."
        ),
        alias="volumeNotional",
    )


class TiingoCryptoHistoricalFetcher(
    Fetcher[
        TiingoCryptoHistoricalQueryParams,
        List[TiingoCryptoHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the Tiingo endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TiingoCryptoHistoricalQueryParams:
        """Transform the query params."""
        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return TiingoCryptoHistoricalQueryParams(**transformed_params)

    # pylint: disable=protected-access
    @staticmethod
    def extract_data(
        query: TiingoCryptoHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Optional[Any],
    ) -> List[Dict]:
        """Return the raw data from the Tiingo endpoint."""
        api_key = credentials.get("tiingo_token") if credentials else ""

        base_url = "https://api.tiingo.com/tiingo/crypto/prices"
        query_str = get_querystring(query.model_dump(by_alias=True), [])
        url = f"{base_url}?{query_str}&token={api_key}"
        data = get_data_one(url).get("priceData", [])

        return data

    # pylint: disable=unused-argument
    @staticmethod
    def transform_data(
        query: TiingoCryptoHistoricalQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TiingoCryptoHistoricalData]:
        """Return the transformed data."""
        return [TiingoCryptoHistoricalData.model_validate(d) for d in data]
