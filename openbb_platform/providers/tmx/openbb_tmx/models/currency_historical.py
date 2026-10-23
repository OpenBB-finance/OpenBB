"""TMX Currency Historical Model."""

from typing import Any, Literal

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.currency_historical import (
    CurrencyHistoricalData,
    CurrencyHistoricalQueryParams,
)
from pydantic import Field

from openbb_tmx.utils.choices import literal_choices


class TmxCurrencyHistoricalQueryParams(CurrencyHistoricalQueryParams):
    """TMX Currency Historical Query."""

    __json_schema_extra__ = {
        "interval": {
            "x-widget_config": {"options": literal_choices(("day", "week", "month"))}
        },
    }

    interval: Literal["day", "week", "month"] = Field(
        default="day",
        description="The interval of the bars.",
    )


class TmxCurrencyHistoricalData(CurrencyHistoricalData):
    """TMX Currency Historical Data."""


class TmxCurrencyHistoricalFetcher(
    Fetcher[TmxCurrencyHistoricalQueryParams, list[TmxCurrencyHistoricalData]]
):
    """TMX Currency Historical Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TmxCurrencyHistoricalQueryParams:
        """Transform the query."""
        return TmxCurrencyHistoricalQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxCurrencyHistoricalQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the TMX endpoint."""
        import asyncio

        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_tmx.utils.helpers import get_timeseries_history

        results: list[dict] = []

        async def create_task(symbol: str) -> None:
            """Fetch the history for a single pair."""
            symbol = symbol.strip().upper()
            symbol = symbol if symbol.startswith("$") else f"${symbol}"
            bars = await get_timeseries_history(
                symbol, query.start_date, query.end_date, query.interval
            )
            results.extend({"symbol": symbol.lstrip("$"), **bar} for bar in bars)

        await asyncio.gather(*(create_task(s) for s in query.symbol.split(",")))

        if not results:
            raise EmptyDataError(f"No history was returned for {query.symbol}.")

        return results

    @staticmethod
    def transform_data(
        query: TmxCurrencyHistoricalQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[TmxCurrencyHistoricalData]:
        """Transform the data and validate the model."""
        return [
            TmxCurrencyHistoricalData.model_validate(
                {
                    "date": d.get("dateTime"),
                    "symbol": d.get("symbol"),
                    "open": d.get("open"),
                    "high": d.get("high"),
                    "low": d.get("low"),
                    "close": d.get("close"),
                    "volume": d.get("volume") or None,
                }
            )
            for d in sorted(data, key=lambda d: d.get("dateTime") or "")
        ]
