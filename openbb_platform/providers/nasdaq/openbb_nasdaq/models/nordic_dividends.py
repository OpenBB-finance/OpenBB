"""Nasdaq Nordic Dividends Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.historical_dividends import (
    HistoricalDividendsData,
    HistoricalDividendsQueryParams,
)
from pydantic import Field

from openbb_nasdaq.utils.constants import NORDIC_SYMBOL_CHOICES_ENDPOINT


class NasdaqNordicDividendsQueryParams(HistoricalDividendsQueryParams):
    """Nasdaq Nordic Dividends Query.

    Source: https://www.nasdaq.com/european-market-activity/shares
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


class NasdaqNordicDividendsData(HistoricalDividendsData):
    """Nasdaq Nordic Dividends Data."""

    payment_date: dateType | None = Field(
        default=None, description="The date the distribution was paid."
    )
    dividend_type: str | None = Field(
        default=None, description="The kind of distribution - i.e., 'Cash'."
    )
    currency: str | None = Field(
        default=None, description="The currency the amount is declared in."
    )


class NasdaqNordicDividendsFetcher(
    Fetcher[
        NasdaqNordicDividendsQueryParams,
        list[NasdaqNordicDividendsData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> NasdaqNordicDividendsQueryParams:
        """Transform the query."""
        return NasdaqNordicDividendsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqNordicDividendsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Morningstar fact sheet."""
        from openbb_nasdaq.utils.factsheet import get_instrument_factsheet

        sheet = await get_instrument_factsheet(query.symbol)

        return sheet.get("dividends") or []

    @staticmethod
    def transform_data(
        query: NasdaqNordicDividendsQueryParams, data: list[dict], **kwargs: Any
    ) -> list[NasdaqNordicDividendsData]:
        """Transform the data to the standard format.

        Raises
        ------
        EmptyDataError
            If the listing has declared no distributions.
        """
        from datetime import datetime

        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_nasdaq.utils.helpers import to_number

        def parse(value: Any) -> dateType | None:
            """Parse a day-first fact sheet date."""
            try:
                return datetime.strptime(str(value), "%d/%m/%Y").date()
            except (TypeError, ValueError):
                return None

        results: list[NasdaqNordicDividendsData] = []

        for row in data:
            ex_date = parse(row.get("ex_date"))

            if ex_date is None:
                continue

            if query.start_date and ex_date < query.start_date:
                continue

            if query.end_date and ex_date > query.end_date:
                continue

            results.append(
                NasdaqNordicDividendsData.model_validate(
                    {
                        "ex_dividend_date": ex_date,
                        "amount": to_number(row.get("amount")),
                        "payment_date": parse(row.get("payment_date")),
                        "dividend_type": row.get("type"),
                        "currency": row.get("currency"),
                    }
                )
            )

        if not results:
            raise EmptyDataError(f"No distributions were declared for {query.symbol}.")

        return sorted(results, key=lambda r: r.ex_dividend_date, reverse=True)
