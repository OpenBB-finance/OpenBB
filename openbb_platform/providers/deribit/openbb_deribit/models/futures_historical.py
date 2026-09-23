"""Deribit Futures Historical Model."""

from datetime import (
    date as dateType,
    datetime,
    timedelta,
)
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.futures_historical import (
    FuturesHistoricalData,
    FuturesHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, model_validator

from openbb_deribit.utils.constants import (
    INSTRUMENT_CHOICES_ENDPOINT,
    INTERVALS,
    SYMBOL_STYLE,
    Intervals,
)

INTERVAL_LOOKBACK = {
    "1m": 30,
    "3m": 60,
    "5m": 60,
    "10m": 90,
    "15m": 90,
    "30m": 90,
}
DEFAULT_LOOKBACK = 364


class DeribitFuturesHistoricalQueryParams(FuturesHistoricalQueryParams):
    """Deribit Futures Historical Query.

    Source: https://docs.deribit.com/api-reference/market-data/public-get_tradingview_chart_data
    """

    __json_schema_extra__ = {
        "symbol": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": INSTRUMENT_CHOICES_ENDPOINT,
                "style": SYMBOL_STYLE,
            },
        },
        "interval": {
            "multiple_items_allowed": False,
            "choices": list(INTERVALS),
        },
        "expiration": {"x-widget_config": {"exclude": True}},
    }

    symbol: str = Field(
        description=QUERY_DESCRIPTIONS.get("symbol", "")
        + " Any listed instrument works, not only futures. A perpetual can also"
        + " be given by its shortened root, such as 'SOLUSDC'."
    )
    interval: Intervals = Field(
        default="1d", description=QUERY_DESCRIPTIONS.get("interval", "")
    )

    @model_validator(mode="before")
    @classmethod
    def validate_model(cls, values):
        """Fill in a span the interval can be served over."""
        if not isinstance(values, dict):
            return values

        now = datetime.today()

        if not values.get("start_date"):
            lookback = INTERVAL_LOOKBACK.get(
                str(values.get("interval") or "1d"), DEFAULT_LOOKBACK
            )
            values["start_date"] = (now - timedelta(days=lookback)).strftime("%Y-%m-%d")

        if not values.get("end_date"):
            values["end_date"] = (now + timedelta(days=1)).strftime("%Y-%m-%d")

        return values


class DeribitFuturesHistoricalData(FuturesHistoricalData):
    """Deribit Futures Historical Data."""

    date: datetime | dateType = Field(
        description=DATA_DESCRIPTIONS.get("date", ""),
        json_schema_extra={"x-widget_config": {"chartDataType": "category"}},
    )
    open: float | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("open", ""),
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    high: float | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("high", ""),
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    low: float | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("low", ""),
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    close: float = Field(
        description=DATA_DESCRIPTIONS.get("close", ""),
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "series"},
        },
    )
    volume: float | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("volume", ""),
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    symbol: str | None = Field(
        default=None,
        description="The name of the instrument.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    volume_notional: float | None = Field(
        default=None,
        description="The volume of the candle, in quote currency.",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )


class DeribitFuturesHistoricalFetcher(
    Fetcher[DeribitFuturesHistoricalQueryParams, list[DeribitFuturesHistoricalData]]
):
    """Transform the query, extract and transform the data from the Deribit endpoint."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> DeribitFuturesHistoricalQueryParams:
        """Transform the query."""
        return DeribitFuturesHistoricalQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeribitFuturesHistoricalQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Deribit endpoint.

        Raises
        ------
        EmptyDataError
            If none of the instruments published candles over the span.
        """
        from openbb_deribit.utils.helpers import get_ohlc_data, get_perpetual_symbols

        symbols = [s.strip().upper() for s in query.symbol.split(",") if s.strip()]
        perpetuals = await get_perpetual_symbols()
        results: list[dict] = []

        for symbol in symbols:
            results.extend(
                await get_ohlc_data(
                    perpetuals.get(symbol, symbol),
                    query.start_date,
                    query.end_date,
                    query.interval,
                )
            )

        if not results:
            raise EmptyDataError(
                f"Deribit published no candles over the span for {', '.join(symbols)}."
            )

        return results

    @staticmethod
    def transform_data(
        query: DeribitFuturesHistoricalQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[DeribitFuturesHistoricalData]:
        """Transform the data to the model."""
        single = len([s for s in query.symbol.split(",") if s.strip()]) == 1

        return [
            DeribitFuturesHistoricalData.model_validate(
                {key: value for key, value in record.items() if key != "symbol"}
                if single
                else record
            )
            for record in sorted(data, key=lambda d: (d["date"], d["symbol"]))
        ]
