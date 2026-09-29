"""Nasdaq Nordic Holidays Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class NasdaqNordicHolidaysQueryParams(QueryParams):
    """Nasdaq Nordic Holidays Query.

    Source: https://www.nasdaq.com/european-market-activity/trading-hours
    """

    year: int | None = Field(
        default=None, description="Restrict the calendar to one year."
    )


class NasdaqNordicHolidaysData(Data):
    """Nasdaq Nordic Holidays Data."""

    date: dateType = Field(description="The date the market is closed.")
    market: str = Field(description="The Nasdaq Nordic market.")
    instrument_group: str = Field(
        description="The instrument group the closure applies to."
    )


class NasdaqNordicHolidaysFetcher(
    Fetcher[
        NasdaqNordicHolidaysQueryParams,
        list[NasdaqNordicHolidaysData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> NasdaqNordicHolidaysQueryParams:
        """Transform the query."""
        return NasdaqNordicHolidaysQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqNordicHolidaysQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> str:
        """Return the raw markup from the Nasdaq trading-hours page."""
        from openbb_nasdaq.utils.schedule import fetch_trading_hours

        return await fetch_trading_hours()

    @staticmethod
    def transform_data(
        query: NasdaqNordicHolidaysQueryParams, data: str, **kwargs: Any
    ) -> list[NasdaqNordicHolidaysData]:
        """Transform the data to the standard format.

        Raises
        ------
        EmptyDataError
            If the page carried no holiday calendar for the requested year.
        """
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_nasdaq.utils.schedule import parse_holidays

        rows = [
            row
            for row in parse_holidays(data or "")
            if query.year is None or row["date"].year == query.year
        ]

        if not rows:
            raise EmptyDataError("No exchange holidays were published.")

        return sorted(
            [NasdaqNordicHolidaysData.model_validate(r) for r in rows],
            key=lambda r: (r.date, r.market, r.instrument_group),
        )
