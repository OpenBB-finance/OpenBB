"""Deribit Futures Historical Model."""

# pylint: disable=unused-argument

from datetime import datetime, timedelta
from typing import Any, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.futures_historical import (
    FuturesHistoricalData,
    FuturesHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_deribit.utils.helpers import DERIBIT_INTERVALS, DeribitIntervals
from pydantic import Field, field_validator, model_validator


class DeribitFuturesHistoricalQueryParams(FuturesHistoricalQueryParams):
    """
    Deribit Futures historical Price Query.

    Source: https://docs.deribit.com/?shell#public-get_tradingview_chart_data
    """

    __json_schema_extra__ = {
        "symbol": {"multiple_items_allowed": True},
        "interval": {
            "multiple_items_allowed": False,
            "choices": DERIBIT_INTERVALS,
        },
    }

    interval: DeribitIntervals = Field(
        default="1d", description=QUERY_DESCRIPTIONS.get("interval", "")
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def _validate_symbol(cls, v):
        """Validate the symbol."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import run_async
        from openbb_deribit.utils.helpers import (
            get_futures_symbols,
            get_perpetual_symbols,
        )

        if not v:
            raise ValueError("Symbol is required.")

        futures_symbols = run_async(get_futures_symbols)
        perpetual_symbols = run_async(get_perpetual_symbols)
        all_symbols = list(perpetual_symbols) + futures_symbols
        symbols = v.upper().split(",")
        new_symbols: list = []

        for symbol in symbols:
            if symbol not in all_symbols:
                raise ValueError(
                    f"Invalid Deribit symbol: {symbol}. Supported symbols are: {', '.join(all_symbols)}"
                )
            if symbol in perpetual_symbols:
                new_symbols.append(perpetual_symbols[symbol])
            else:
                new_symbols.append(symbol)

        return ",".join(new_symbols)

    @model_validator(mode="before")
    @classmethod
    def _validate_model(cls, values):
        """Validate the model."""
        interval = values.get("interval")
        now = datetime.today()

        if not values.get("start_date"):
            if interval == "1m":
                start = now - timedelta(days=30)
            elif interval in ["3m", "5m"]:
                start = now - timedelta(days=60)
            elif interval in ["15m", "30m"]:
                start = now - timedelta(days=90)
            else:
                start = now - timedelta(days=364)

            values["start_date"] = start.strftime("%Y-%m-%d")

        if not values.get("end_date"):
            values["end_date"] = (now + timedelta(days=1)).strftime("%Y-%m-%d")

        return values


class DeribitFuturesHistoricalData(FuturesHistoricalData):
    """Deribit Futures Historical Data."""

    volume_notional: float = Field(description="Trading volume in quote currency.")


class DeribitFuturesHistoricalFetcher(
    Fetcher[DeribitFuturesHistoricalQueryParams, list[DeribitFuturesHistoricalData]]
):
    """Deribit Futures Historical Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> DeribitFuturesHistoricalQueryParams:
        """Transform the query."""
        return DeribitFuturesHistoricalQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeribitFuturesHistoricalQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list:
        """Extract the raw data."""
        # pylint: disable=import-outside-toplevel
        from openbb_deribit.utils.helpers import get_ohlc_data

        symbols = query.symbol.split(",")
        results: list = []

        for symbol in symbols:
            try:
                data = await get_ohlc_data(
                    symbol=symbol,
                    interval=query.interval,
                    start_date=query.start_date,
                    end_date=query.end_date,
                )
                if data:
                    results.extend(data)
            except OpenBBError as e:
                raise e from e

        if not results:
            raise EmptyDataError("No data found.")

        return sorted(results, key=lambda x: x["date"])

    @staticmethod
    def transform_data(
        query: DeribitFuturesHistoricalQueryParams, data: list, **kwargs: Any
    ) -> list[DeribitFuturesHistoricalData]:
        """Transform the data."""
        symbols = query.symbol.split(",")
        if len(symbols) == 1:
            results: list[DeribitFuturesHistoricalData] = []
            for d in data:
                _ = d.pop("symbol", None)
                results.append(DeribitFuturesHistoricalData.model_validate(d))
            return [DeribitFuturesHistoricalData.model_validate(d) for d in data]
        return [DeribitFuturesHistoricalData.model_validate(d) for d in data]
