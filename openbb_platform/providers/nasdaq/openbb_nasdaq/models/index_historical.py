"""Nasdaq Index Historical Price Model."""

from datetime import datetime
from typing import Any, Literal

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.index_historical import (
    IndexHistoricalData,
    IndexHistoricalQueryParams,
)
from pydantic import Field

from openbb_nasdaq.utils.constants import INDEX_SYMBOL_CHOICES_ENDPOINT


class NasdaqIndexHistoricalQueryParams(IndexHistoricalQueryParams):
    """Nasdaq Index Historical Price Query.

    Source: https://www.nasdaq.com/market-activity/indexes
    """

    __json_schema_extra__ = {
        "symbol": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": INDEX_SYMBOL_CHOICES_ENDPOINT,
                "style": {"popupWidth": 850},
            },
        },
        "interval": {"choices": ["1m", "1d"]},
    }

    interval: Literal["1m", "1d"] = Field(
        default="1d",
        description="The data interval. One-minute data covers the current"
        + " session only and ignores the date range.",
    )


class NasdaqIndexHistoricalData(IndexHistoricalData):
    """Nasdaq Index Historical Price Data."""

    symbol: str | None = Field(
        default=None, description="The ticker symbol, when more than one is requested."
    )


class NasdaqIndexHistoricalFetcher(
    Fetcher[
        NasdaqIndexHistoricalQueryParams,
        list[NasdaqIndexHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> NasdaqIndexHistoricalQueryParams:
        """Transform the query."""
        return NasdaqIndexHistoricalQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqIndexHistoricalQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Nasdaq endpoint."""
        from openbb_nasdaq.utils.helpers import (
            gather_historical_prices,
            get_nasdaq_data,
        )

        if query.interval == "1d":
            return await gather_historical_prices(
                query.symbol, "index", query.start_date, query.end_date
            )

        symbols = [s.strip().upper() for s in query.symbol.split(",") if s.strip()]
        params = "&".join(f"symbol={symbol}&chartFor={symbol}" for symbol in symbols)
        data = await get_nasdaq_data(f"quote/indices?{params}")

        return data if isinstance(data, list) else []

    @staticmethod
    def transform_data(
        query: NasdaqIndexHistoricalQueryParams, data: list[dict], **kwargs: Any
    ) -> list[NasdaqIndexHistoricalData]:
        """Transform the data to the standard format.

        Raises
        ------
        EmptyDataError
            If no index returned a session series.
        """
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_nasdaq.utils.helpers import to_number

        if query.interval == "1d":
            return [NasdaqIndexHistoricalData.model_validate(d) for d in data]

        results: list[NasdaqIndexHistoricalData] = []

        for row in data:
            symbol = row.get("symbol")

            for point in row.get("indexCharts") or []:
                stamped = parse_chart_time((point.get("z") or {}).get("dateTime"))

                if stamped is None:
                    continue

                results.append(
                    NasdaqIndexHistoricalData.model_validate(
                        {
                            "date": stamped,
                            "symbol": symbol,
                            "close": to_number(point.get("y")),
                        }
                    )
                )

        if not results:
            raise EmptyDataError(f"No intraday series was returned for {query.symbol}.")

        return sorted(results, key=lambda r: (r.date, r.symbol or ""))


def parse_chart_time(value: Any) -> datetime | None:
    """Parse a Nasdaq index chart timestamp.

    Parameters
    ----------
    value : Any
        A timestamp such as '7/24/2026 9:30:58 AM', in US/Eastern time.

    Returns
    -------
    datetime or None
        The naive US/Eastern timestamp, or None when unparseable.
    """
    if not isinstance(value, str) or not value.strip():
        return None

    try:
        return datetime.strptime(value.strip(), "%m/%d/%Y %I:%M:%S %p")
    except ValueError:
        return None
