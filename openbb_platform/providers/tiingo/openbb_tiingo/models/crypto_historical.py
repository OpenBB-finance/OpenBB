"""Tiingo Crypto end of day fetcher."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from dateutil.relativedelta import relativedelta
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.crypto_historical import (
    CryptoHistoricalData,
    CryptoHistoricalQueryParams,
)
from openbb_provider.utils.helpers import make_request
from pydantic import Field


class TiingoCryptoHistoricalQueryParams(CryptoHistoricalQueryParams):
    """Tiingo Crypto end of day Query.

    Source: https://www.tiingo.com/documentation/end-of-day
    """

    interval: Literal[
        "1min", "5min", "15min", "30min", "1hour", "4hour", "1day"
    ] = Field(default="1day", description="Data granularity.")

    exchanges: Optional[List[str]] = Field(
        default=None,
        description=(
            "If you would like to limit the query to a subset of exchanes, "
            "pass a comma-separated list of exchanges to select. E.g. 'POLONIEX, GDAX'"
        ),
    )
    # pylint: disable=protected-access


class TiingoCryptoHistoricalData(CryptoHistoricalData):
    """Tiingo Crypto end of day Data."""

    __alias_dict__ = {"transactions": "tradesDone", "volume_notional": "volumeNotional"}

    transactions: Optional[int] = Field(default=None, description="Number of trades.")

    volume_notional: Optional[float] = Field(
        default=None,
        description=(
            "The last size done for the asset on the specific date in the "
            "quote currency. The volume of the asset on the specific date in "
            "the quote currency."
        ),
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
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Tiingo endpoint."""
        api_key = credentials.get("tiingo_token") if credentials else ""

        base_url = (
            f"https://api.tiingo.com/tiingo/crypto/prices?tickers={query.symbol}"
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
        query: TiingoCryptoHistoricalQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TiingoCryptoHistoricalData]:
        """Return the transformed data."""
        price_data = data[0]["priceData"]
        return [TiingoCryptoHistoricalData.model_validate(d) for d in price_data]
