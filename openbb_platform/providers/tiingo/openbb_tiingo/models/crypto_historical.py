"""Tiingo Crypto Historical Price Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Literal, Optional, Union
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.crypto_historical import (
    CryptoHistoricalData,
    CryptoHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError, UnauthorizedError
from pydantic import Field


class TiingoCryptoHistoricalQueryParams(CryptoHistoricalQueryParams):
    """Tiingo Crypto Historical Price Query.

    Source: https://www.tiingo.com/documentation/crypto
    """

    __alias_dict__ = {
        "start_date": "startDate",
        "end_date": "endDate",
        "symbol": "tickers",
    }
    __json_schema_extra__ = {
        "symbol": {"multiple_items_allowed": True},
        "exchanges": {"multiple_items_allowed": True},
        "interval": {
            "choices": [
                "1m",
                "5m",
                "15m",
                "30m",
                "90m",
                "1h",
                "2h",
                "4h",
                "1d",
                "7d",
                "30d",
            ]
        },
    }

    interval: Union[
        Literal[
            "1m",
            "5m",
            "15m",
            "30m",
            "90m",
            "1h",
            "2h",
            "4h",
            "1d",
            "7d",
            "30d",
        ],
        str,
    ] = Field(default="1d", description=QUERY_DESCRIPTIONS.get("interval", ""))

    exchanges: Optional[Union[list[str], str]] = Field(
        default=None,
        description=(
            "To limit the query to a subset of exchanges e.g. ['POLONIEX', 'GDAX']"
        ),
    )


class TiingoCryptoHistoricalData(CryptoHistoricalData):
    """Tiingo Crypto Historical Price Data."""

    __alias_dict__ = {
        "transactions": "tradesDone",
        "volume_notional": "volumeNotional",
    }

    transactions: Optional[int] = Field(
        default=None,
        description="Number of transactions for the symbol in the time period.",
    )

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
        list[TiingoCryptoHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the Tiingo endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TiingoCryptoHistoricalQueryParams:
        """Transform the query params."""
        # pylint: disable=import-outside-toplevel
        from dateutil.relativedelta import relativedelta

        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return TiingoCryptoHistoricalQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: TiingoCryptoHistoricalQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Optional[Any],
    ) -> list[dict]:
        """Return the raw data from the Tiingo endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import get_querystring
        from openbb_tiingo.utils.helpers import get_data

        api_key = credentials.get("tiingo_token") if credentials else ""

        base_url = "https://api.tiingo.com/tiingo/crypto/prices"
        query_str = get_querystring(query.model_dump(by_alias=True), ["interval"])

        if query.interval.endswith("m"):
            frequency = f"{query.interval[:-1]}min"
        elif query.interval.endswith("h"):
            frequency = f"{query.interval[:-1]}hour"
        elif query.interval.endswith("d"):
            frequency = f"{query.interval[:-1]}day"
        else:
            frequency = "1day"

        results: list = []
        url = f"{base_url}?{query_str}&resampleFreq={frequency}&token={api_key}"

        try:
            results = await get_data(url)
        except (EmptyDataError, OpenBBError, UnauthorizedError) as e:
            raise e from e

        return results

    @staticmethod
    def transform_data(
        query: TiingoCryptoHistoricalQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[TiingoCryptoHistoricalData]:
        """Return the transformed data."""
        # pylint: disable=import-outside-toplevel
        from pandas import to_datetime

        results: list[TiingoCryptoHistoricalData] = []
        symbols = query.symbol.split(",")
        returned_symbols = [item.get("ticker", "").upper() for item in data]

        for symbol in symbols:
            if symbol not in returned_symbols:
                warn(f"No data found for {symbol}")

        for item in data:
            symbol = item.get("ticker", "").upper()
            price_data = item.get("priceData", [])

            if not price_data:
                warn(f"No data found for {symbol}")
                continue

            for row in price_data:
                if len(returned_symbols) > 1:
                    row["symbol"] = symbol
                if query.interval.endswith("d"):
                    row["date"] = to_datetime(row["date"]).date()
                else:
                    row["date"] = to_datetime(row["date"], utc=True)

                results.append(TiingoCryptoHistoricalData.model_validate(row))

        return sorted(results, key=lambda x: x.date)
