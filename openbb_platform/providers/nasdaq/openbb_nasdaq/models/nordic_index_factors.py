"""Nasdaq Nordic Index Factors Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class NasdaqNordicIndexFactorsQueryParams(QueryParams):
    """Nasdaq Nordic Index Factors Query.

    Source: https://www.nasdaq.com/european-market-activity/fixed-income/index-factors
    """


class NasdaqNordicIndexFactorsData(Data):
    """Nasdaq Nordic Index Factors Data.

    The inflation index factors applied to Danish index-linked mortgage bonds,
    published as a grid of measures against effective dates.
    """

    date: dateType = Field(description="The date the factor takes effect.")
    attribute: str = Field(description="The reported factor.")
    value: float | None = Field(default=None, description="The factor value.")


class NasdaqNordicIndexFactorsFetcher(
    Fetcher[
        NasdaqNordicIndexFactorsQueryParams,
        list[NasdaqNordicIndexFactorsData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> NasdaqNordicIndexFactorsQueryParams:
        """Transform the query."""
        return NasdaqNordicIndexFactorsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqNordicIndexFactorsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Return the raw data from the Nasdaq endpoint."""
        from openbb_nasdaq.utils.helpers import get_nasdaq_data

        return await get_nasdaq_data("nordic/index-factors?lang=en") or {}

    @staticmethod
    def transform_data(
        query: NasdaqNordicIndexFactorsQueryParams, data: dict, **kwargs: Any
    ) -> list[NasdaqNordicIndexFactorsData]:
        """Transform the data to the standard format.

        Raises
        ------
        EmptyDataError
            If Nasdaq publishes no index factors.
        """
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_nasdaq.utils.helpers import to_date, to_number
        from openbb_nasdaq.utils.translations import translate

        results: list[NasdaqNordicIndexFactorsData] = []

        for block in ((data or {}).get("indexFactors") or {}).values():
            if not isinstance(block, dict):
                continue

            for row in block.get("rows") or []:
                for column, value in row.items():
                    effective = to_date(column)

                    if column == "attribute" or effective is None:
                        continue

                    number = to_number(value)

                    if number is None:
                        continue

                    results.append(
                        NasdaqNordicIndexFactorsData.model_validate(
                            {
                                "date": effective,
                                "attribute": translate(row.get("attribute")),
                                "value": number,
                            }
                        )
                    )

        if not results:
            raise EmptyDataError("No index factors were published.")

        return sorted(results, key=lambda r: (r.date, r.attribute))
