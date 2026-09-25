"""Nasdaq Nordic Historical Price Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field

from openbb_nasdaq.utils.constants import NORDIC_SYMBOL_CHOICES_ENDPOINT


class NasdaqNordicHistoricalQueryParams(QueryParams):
    """Nasdaq Nordic Historical Price Query.

    Source: https://www.nasdaq.com/european-market-activity
    """

    __json_schema_extra__ = {
        "symbol": {
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": NORDIC_SYMBOL_CHOICES_ENDPOINT,
                "style": {"popupWidth": 850},
            },
        },
    }

    symbol: str = Field(description="The Nasdaq Nordic instrument symbol.")
    start_date: dateType | None = Field(default=None, description="The start date.")
    end_date: dateType | None = Field(default=None, description="The end date.")


class NasdaqNordicHistoricalData(Data):
    """Nasdaq Nordic Historical Price Data."""

    date: dateType = Field(description="The trading day.")
    symbol: str | None = Field(default=None, description="The instrument symbol.")
    high: float | None = Field(default=None, description="The session high.")
    low: float | None = Field(default=None, description="The session low.")
    close: float | None = Field(default=None, description="The closing price.")
    average_price: float | None = Field(
        default=None, description="The average price across all trades."
    )
    volume: float | None = Field(default=None, description="The total volume.")
    turnover: float | None = Field(
        default=None, description="The turnover, in the trading currency."
    )
    duration: float | None = Field(
        default=None, description="The bond duration, in years."
    )
    yield_to_maturity: float | None = Field(
        default=None,
        description="The bond yield, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    yield_calculation_price: float | None = Field(
        default=None, description="The price the yield was calculated from."
    )
    reference_price: float | None = Field(
        default=None, description="The consolidated reference price."
    )
    consolidated_volume: float | None = Field(
        default=None, description="The consolidated volume."
    )
    consolidated_turnover: float | None = Field(
        default=None, description="The consolidated turnover."
    )


class NasdaqNordicHistoricalFetcher(
    Fetcher[
        NasdaqNordicHistoricalQueryParams,
        list[NasdaqNordicHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> NasdaqNordicHistoricalQueryParams:
        """Transform the query, defaulting to the trailing year."""
        from datetime import timedelta

        today = datetime.now().date()

        if params.get("end_date") is None:
            params["end_date"] = today

        if params.get("start_date") is None:
            params["start_date"] = params["end_date"] - timedelta(days=365)

        return NasdaqNordicHistoricalQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqNordicHistoricalQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Nasdaq endpoint."""
        from openbb_nasdaq.utils.helpers import get_nasdaq_data, rows_from_table
        from openbb_nasdaq.utils.nordic import resolve_nordic_instrument

        instrument = await resolve_nordic_instrument(query.symbol)
        data = await get_nasdaq_data(
            f"nordic/instruments/{instrument['orderbook_id']}/price-history"
            f"?assetClass={instrument['asset_class']}&lang=en"
            f"&fromDate={query.start_date}&toDate={query.end_date}"
        )
        rows = rows_from_table((data or {}).get("priceHistory"))

        return [{**row, "symbol": instrument["orderbook_id"]} for row in rows]

    @staticmethod
    def transform_data(
        query: NasdaqNordicHistoricalQueryParams, data: list[dict], **kwargs: Any
    ) -> list[NasdaqNordicHistoricalData]:
        """Transform the data to the standard format.

        Raises
        ------
        EmptyDataError
            If no session printed in the requested window.
        """
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_nasdaq.utils.helpers import to_date, to_number, to_percent
        from openbb_nasdaq.utils.nordic import NORDIC_PRICE_FIELDS

        if not data:
            raise EmptyDataError(
                f"No prices were reported for {query.symbol} between"
                f" {query.start_date} and {query.end_date}."
            )

        results: list[NasdaqNordicHistoricalData] = []
        symbol = query.symbol.upper()

        for row in data:
            stamped = to_date(row.get("date"))

            if stamped is None:
                continue

            record: dict[str, Any] = {"date": stamped, "symbol": symbol}

            for field, key in NORDIC_PRICE_FIELDS.items():
                record[field] = to_number(row.get(key))

            record["yield_to_maturity"] = to_percent(row.get("yield"))
            results.append(NasdaqNordicHistoricalData.model_validate(record))

        return sorted(results, key=lambda r: r.date)
