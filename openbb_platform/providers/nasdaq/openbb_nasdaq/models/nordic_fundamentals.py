"""Nasdaq Nordic Fundamentals Model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field

from openbb_nasdaq.utils.constants import NORDIC_SYMBOL_CHOICES_ENDPOINT


class NasdaqNordicFundamentalsQueryParams(QueryParams):
    """Nasdaq Nordic Fundamentals Query.

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

    symbol: str = Field(description="The Nasdaq Nordic instrument symbol.")


class NasdaqNordicFundamentalsData(Data):
    """Nasdaq Nordic Fundamentals Data.

    The statements, ratios, and growth rates Morningstar compiles for a Nordic
    listing. Sections differ by company, so the record is one row per label,
    section, and period.
    """

    section: str | None = Field(
        default=None, description="The fact sheet section the row belongs to."
    )
    label: str = Field(description="The line item, as Morningstar publishes it.")
    period: str = Field(
        description="The fiscal year, quarter, or horizon the value covers."
    )
    value: float | None = Field(default=None, description="The reported value.")


class NasdaqNordicFundamentalsFetcher(
    Fetcher[
        NasdaqNordicFundamentalsQueryParams,
        list[NasdaqNordicFundamentalsData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> NasdaqNordicFundamentalsQueryParams:
        """Transform the query."""
        return NasdaqNordicFundamentalsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqNordicFundamentalsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Return the raw data from the Morningstar fact sheet."""
        from openbb_nasdaq.utils.factsheet import get_instrument_factsheet

        return await get_instrument_factsheet(query.symbol)

    @staticmethod
    def transform_data(
        query: NasdaqNordicFundamentalsQueryParams, data: dict, **kwargs: Any
    ) -> list[NasdaqNordicFundamentalsData]:
        """Transform the data to the standard format.

        Raises
        ------
        EmptyDataError
            If the fact sheet carries no populated tables.
        """
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_nasdaq.utils.helpers import to_number

        results = [
            NasdaqNordicFundamentalsData.model_validate(
                {
                    "section": row["section"],
                    "label": row["label"],
                    "period": row["period"],
                    "value": to_number(row["value"]),
                }
            )
            for row in data.get("series") or []
            if to_number(row["value"]) is not None
        ]

        if not results:
            raise EmptyDataError(
                f"The fact sheet for {query.symbol} carries no reported figures."
            )

        return results
