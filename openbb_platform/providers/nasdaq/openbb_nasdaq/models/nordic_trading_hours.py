"""Nasdaq Nordic Trading Hours Model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class NasdaqNordicTradingHoursQueryParams(QueryParams):
    """Nasdaq Nordic Trading Hours Query.

    Source: https://www.nasdaq.com/european-market-activity/trading-hours
    """


class NasdaqNordicTradingHoursData(Data):
    """Nasdaq Nordic Trading Hours Data."""

    section: str = Field(description="The market segment the table covers.")
    segment: str = Field(description="The traded instrument segment.")
    market: str = Field(description="The Nasdaq Nordic market.")
    hours: str = Field(description="The session hours, in the market's local time.")


class NasdaqNordicTradingHoursFetcher(
    Fetcher[
        NasdaqNordicTradingHoursQueryParams,
        list[NasdaqNordicTradingHoursData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> NasdaqNordicTradingHoursQueryParams:
        """Transform the query."""
        return NasdaqNordicTradingHoursQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqNordicTradingHoursQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> str:
        """Return the raw markup from the Nasdaq trading-hours page."""
        from openbb_nasdaq.utils.schedule import fetch_trading_hours

        return await fetch_trading_hours()

    @staticmethod
    def transform_data(
        query: NasdaqNordicTradingHoursQueryParams, data: str, **kwargs: Any
    ) -> list[NasdaqNordicTradingHoursData]:
        """Transform the data to the standard format.

        Raises
        ------
        EmptyDataError
            If the page carried no session tables.
        """
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_nasdaq.utils.schedule import parse_trading_hours

        results = parse_trading_hours(data or "")

        if not results:
            raise EmptyDataError("No trading hours were published.")

        return [NasdaqNordicTradingHoursData.model_validate(r) for r in results]
