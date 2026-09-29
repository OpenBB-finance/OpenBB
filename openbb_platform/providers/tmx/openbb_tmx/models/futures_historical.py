"""TMX Futures Historical Model."""

from typing import Any, Literal

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.futures_historical import (
    FuturesHistoricalData,
    FuturesHistoricalQueryParams,
)
from pydantic import Field

from openbb_tmx.utils.choices import literal_choices


class TmxFuturesHistoricalQueryParams(FuturesHistoricalQueryParams):
    """TMX Futures Historical Query."""

    __json_schema_extra__ = {
        "interval": {
            "x-widget_config": {"options": literal_choices(("day", "week", "month"))}
        },
    }

    interval: Literal["day", "week", "month"] = Field(
        default="day",
        description="The interval of the bars.",
    )


class TmxFuturesHistoricalData(FuturesHistoricalData):
    """TMX Futures Historical Data."""


class TmxFuturesHistoricalFetcher(
    Fetcher[TmxFuturesHistoricalQueryParams, list[TmxFuturesHistoricalData]]
):
    """TMX Futures Historical Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TmxFuturesHistoricalQueryParams:
        """Transform the query."""
        return TmxFuturesHistoricalQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxFuturesHistoricalQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the TMX endpoint."""
        import asyncio

        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_tmx.utils.helpers import get_timeseries_history

        results: list[dict] = []

        async def create_task(symbol: str) -> None:
            """Fetch the history for a single future."""
            symbol = symbol.strip().upper()
            symbol = symbol if symbol[:1] in ("/", "^", "$") else f"/{symbol}"
            bars = await get_timeseries_history(
                symbol, query.start_date, query.end_date, query.interval
            )
            results.extend({"symbol": symbol.lstrip("/"), **bar} for bar in bars)

        await asyncio.gather(*(create_task(s) for s in query.symbol.split(",")))

        if not results:
            raise EmptyDataError(f"No history was returned for {query.symbol}.")

        return results

    @staticmethod
    def transform_data(
        query: TmxFuturesHistoricalQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[TmxFuturesHistoricalData]:
        """Transform the data and validate the model."""
        return [
            TmxFuturesHistoricalData.model_validate(
                {
                    "date": d.get("dateTime"),
                    "symbol": d.get("symbol"),
                    "open": d.get("open"),
                    "high": d.get("high"),
                    "low": d.get("low"),
                    "close": d.get("close"),
                    "volume": d.get("volume"),
                }
            )
            for d in sorted(data, key=lambda d: d.get("dateTime") or "")
        ]
