"""Tiingo Crypto Historical Price Model."""

# pylint: disable=unused-argument

import warnings
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.crypto_historical import (
    CryptoHistoricalData,
    CryptoHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.helpers import (
    ClientResponse,
    amake_requests,
    get_querystring,
)
from pydantic import Field, PrivateAttr, model_validator

_warn = warnings.warn


class TiingoCryptoHistoricalQueryParams(CryptoHistoricalQueryParams):
    """Tiingo Crypto Historical Price Query.

    Source: https://www.tiingo.com/documentation/end-of-day
    """

    __alias_dict__ = {
        "symbol": "tickers",
        "start_date": "startDate",
        "end_date": "endDate",
        "interval": "resampleFreq",
    }
    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}

    interval: Literal["1m", "5m", "15m", "30m", "1h", "4h", "1d"] = Field(
        default="1d", description=QUERY_DESCRIPTIONS.get("interval", "")
    )
    exchanges: Optional[List[str]] = Field(
        default=None,
        description=(
            "To limit the query to a subset of exchanges e.g. ['POLONIEX', 'GDAX']"
        ),
    )
    _frequency: Literal["daily", "weekly", "monthly", "annually"] = PrivateAttr(
        default=None
    )

    # pylint: disable=protected-access
    @model_validator(mode="after")  # type: ignore[arg-type]
    @classmethod
    def set_time_params(cls, values: "TiingoCryptoHistoricalQueryParams"):
        """Set the default start & end date and time params for Tiingo API."""
        frequency_dict = {
            "1d": "1Day",
            "1m": "1Min",
            "5m": "5Min",
            "15m": "15Min",
            "30m": "30Min",
            "1h": "1Hour",
            "4h": "4Hour",
        }
        values._frequency = frequency_dict[values.interval]  # type: ignore[assignment]

        return values


class TiingoCryptoHistoricalData(CryptoHistoricalData):
    """Tiingo Crypto Historical Price Data."""

    transactions: Optional[int] = Field(
        default=None,
        description="Number of transactions for the symbol in the time period.",
        alias="tradesDone",
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
    async def aextract_data(
        query: TiingoCryptoHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Optional[Any],
    ) -> List[Dict]:
        """Return the raw data from the Tiingo endpoint."""
        api_key = credentials.get("tiingo_token") if credentials else ""

        base_url = "https://api.tiingo.com/tiingo/crypto/prices"
        query_str = get_querystring(
            query.model_dump(by_alias=False), ["tickers", "resampleFreq"]
        )
        results = []

        async def callback(response: ClientResponse, _: Any) -> List[Dict]:
            result = await response.json()
            symbol = response.url.query.get("tickers", "")
            if not result:
                _warn(f"No data found the the symbol: {symbol}")
                return results
            data = result[0].get("priceData")
            if "," in query.symbol:
                for d in data:
                    d["symbol"] = symbol.upper() if symbol else None
            if len(data) > 0:
                results.extend(data)
            return results

        urls = [
            f"{base_url}?tickers={symbol}&{query_str}&resampleFreq={query._frequency}&token={api_key}"
            for symbol in query.symbol.split(",")
        ]

        return await amake_requests(urls, callback, **kwargs)

    @staticmethod
    def transform_data(
        query: TiingoCryptoHistoricalQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TiingoCryptoHistoricalData]:
        """Return the transformed data."""
        return [
            TiingoCryptoHistoricalData.model_validate(d)
            for d in sorted(data, key=lambda x: x["date"], reverse=True)
        ]
