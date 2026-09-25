"""Nasdaq Nordic Mortgage Rates Model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class NasdaqNordicMortgageRatesQueryParams(QueryParams):
    """Nasdaq Nordic Mortgage Rates Query.

    Source: https://www.nasdaq.com/european-market-activity/fixed-income/mortgage-rates
    """


class NasdaqNordicMortgageRatesData(Data):
    """Nasdaq Nordic Mortgage Rates Data."""

    lender: str = Field(description="The lending institution.")
    term: str = Field(description="The fixed-rate term.")
    rate: float | None = Field(
        default=None,
        description="The listed mortgage rate, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    url: str | None = Field(default=None, description="The lender's mortgage page.")


class NasdaqNordicMortgageRatesFetcher(
    Fetcher[
        NasdaqNordicMortgageRatesQueryParams,
        list[NasdaqNordicMortgageRatesData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> NasdaqNordicMortgageRatesQueryParams:
        """Transform the query."""
        return NasdaqNordicMortgageRatesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqNordicMortgageRatesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Return the raw data from the Nasdaq endpoint."""
        from openbb_nasdaq.utils.helpers import get_nasdaq_data

        return await get_nasdaq_data("nordic/mortgage-rates?lang=en") or {}

    @staticmethod
    def transform_data(
        query: NasdaqNordicMortgageRatesQueryParams, data: dict, **kwargs: Any
    ) -> list[NasdaqNordicMortgageRatesData]:
        """Transform the data to the standard format.

        Raises
        ------
        EmptyDataError
            If Nasdaq publishes no mortgage rates.
        """
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_nasdaq.utils.helpers import to_percent

        block = (data or {}).get("mortgageRates") or {}
        headers = block.get("headers") or {}
        results: list[NasdaqNordicMortgageRatesData] = []

        for row in block.get("rows") or []:
            for column, label in headers.items():
                if column in ("fullName", "url"):
                    continue

                rate = to_percent(row.get(column))

                if rate is None:
                    continue

                results.append(
                    NasdaqNordicMortgageRatesData.model_validate(
                        {
                            "lender": row.get("fullName"),
                            "term": label,
                            "rate": rate,
                            "url": row.get("url"),
                        }
                    )
                )

        if not results:
            raise EmptyDataError("No mortgage rates were published.")

        return results
