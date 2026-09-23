"""Nasdaq Nordic Historical Trades Model."""

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

HISTORY_MONTHS = 3


class NasdaqNordicHistoricalTradesQueryParams(QueryParams):
    """Nasdaq Nordic Historical Trades Query.

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
    start_date: dateType | None = Field(
        default=None,
        description="The start date. Nasdaq publishes three months of trades.",
    )
    end_date: dateType | None = Field(default=None, description="The end date.")


class NasdaqNordicHistoricalTradesData(Data):
    """Nasdaq Nordic Historical Trades Data."""

    date: datetime = Field(description="The time of the trade, in CET.")
    symbol: str | None = Field(default=None, description="The instrument symbol.")
    price: float | None = Field(default=None, description="The trade price.")
    volume: float | None = Field(default=None, description="The trade volume.")
    buyer: str | None = Field(default=None, description="The buying member.")
    seller: str | None = Field(default=None, description="The selling member.")
    trade_type: str | None = Field(default=None, description="The type of trade.")
    market: str | None = Field(default=None, description="The reporting market.")
    mmt_flag: str | None = Field(
        default=None, description="The MiFID market model typology flags."
    )
    orderbook: str | None = Field(
        default=None, description="Whether the trade was on or off the orderbook."
    )
    cancelled: str | None = Field(
        default=None, description="Whether the trade was cancelled."
    )
    agreement_time: str | None = Field(
        default=None, description="The time the trade was agreed."
    )


class NasdaqNordicHistoricalTradesFetcher(
    Fetcher[
        NasdaqNordicHistoricalTradesQueryParams,
        list[NasdaqNordicHistoricalTradesData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> NasdaqNordicHistoricalTradesQueryParams:
        """Transform the query, defaulting to the published three-month window."""
        from datetime import timedelta

        today = datetime.now().date()

        if params.get("end_date") is None:
            params["end_date"] = today

        if params.get("start_date") is None:
            params["start_date"] = params["end_date"] - timedelta(
                days=HISTORY_MONTHS * 30
            )

        return NasdaqNordicHistoricalTradesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqNordicHistoricalTradesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Nasdaq endpoint."""
        from openbb_nasdaq.utils.helpers import get_nasdaq_data, rows_from_table
        from openbb_nasdaq.utils.nordic import resolve_nordic_instrument

        instrument = await resolve_nordic_instrument(query.symbol)
        data = await get_nasdaq_data(
            f"nordic/instruments/{instrument['orderbook_id']}/trade-history"
            f"?assetClass={instrument['asset_class']}&type=TABLE_VIEW&lang=en"
            f"&fromDate={query.start_date}&toDate={query.end_date}"
        )

        return rows_from_table((data or {}).get("trades"))

    @staticmethod
    def transform_data(
        query: NasdaqNordicHistoricalTradesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[NasdaqNordicHistoricalTradesData]:
        """Transform the data to the standard format.

        Raises
        ------
        EmptyDataError
            If no trade printed in the requested window.
        """
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_nasdaq.utils.helpers import clean_value, to_number
        from openbb_nasdaq.utils.nordic import NORDIC_TRADE_FIELDS

        if not data:
            raise EmptyDataError(
                f"No trades were reported for {query.symbol} between"
                f" {query.start_date} and {query.end_date}."
            )

        results: list[NasdaqNordicHistoricalTradesData] = []

        for row in data:
            stamped = parse_trade_time(row.get("time"))

            if stamped is None:
                continue

            record: dict[str, Any] = {
                "date": stamped,
                "symbol": row.get("name") or query.symbol.upper(),
            }

            for field, key in NORDIC_TRADE_FIELDS.items():
                record[field] = (
                    to_number(row.get(key))
                    if field in ("price", "volume")
                    else clean_value(row.get(key))
                )

            results.append(NasdaqNordicHistoricalTradesData.model_validate(record))

        return sorted(results, key=lambda r: r.date)


def parse_trade_time(value: Any) -> datetime | None:
    """Parse a Nasdaq Nordic trade timestamp.

    Parameters
    ----------
    value : Any
        A timestamp such as '2026-07-23 10:12:54'.

    Returns
    -------
    datetime or None
        The naive CET timestamp, or None when unparseable.
    """
    if not isinstance(value, str) or not value.strip():
        return None

    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None
