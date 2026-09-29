"""Nasdaq Nordic Average Bond Yield Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field

BASIS = {"before_tax": "beforeTax", "after_tax": "afterTax"}


class NasdaqNordicBondYieldsQueryParams(QueryParams):
    """Nasdaq Nordic Average Bond Yield Query.

    Source: https://www.nasdaq.com/european-market-activity/fixed-income/average-bond-yield
    """

    __json_schema_extra__ = {"basis": {"choices": list(BASIS)}}

    basis: Literal["before_tax", "after_tax"] = Field(
        default="before_tax",
        description="Whether the yields are reported before or after tax.",
    )


class NasdaqNordicBondYieldsData(Data):
    """Nasdaq Nordic Average Bond Yield Data.

    Nasdaq reports the Danish average bond yield as a grid of issuer segments
    against residual maturity buckets, so the record is one row per segment,
    attribute, and bucket.
    """

    date: dateType | None = Field(default=None, description="The reporting date.")
    segment: str = Field(description="The issuer segment.")
    attribute: str = Field(description="The reported measure.")
    maturity: str = Field(description="The residual maturity bucket, in years.")
    value: float | None = Field(default=None, description="The reported value.")


class NasdaqNordicBondYieldsFetcher(
    Fetcher[
        NasdaqNordicBondYieldsQueryParams,
        list[NasdaqNordicBondYieldsData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> NasdaqNordicBondYieldsQueryParams:
        """Transform the query."""
        return NasdaqNordicBondYieldsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqNordicBondYieldsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Return the raw data from the Nasdaq endpoint."""
        from openbb_nasdaq.utils.helpers import get_nasdaq_data

        return await get_nasdaq_data("nordic/average-yield?lang=en") or {}

    @staticmethod
    def transform_data(
        query: NasdaqNordicBondYieldsQueryParams, data: dict, **kwargs: Any
    ) -> list[NasdaqNordicBondYieldsData]:
        """Transform the data to the standard format.

        Raises
        ------
        EmptyDataError
            If Nasdaq publishes no yields on the requested basis.
        """
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_nasdaq.utils.helpers import to_date, to_number
        from openbb_nasdaq.utils.translations import translate

        block = (data or {}).get(BASIS[query.basis]) or {}
        headers = block.get("headers") or {}
        reported = to_date((data or {}).get("date"))
        results: list[NasdaqNordicBondYieldsData] = []

        for section in block.get("sections") or []:
            segment = translate(section.get("name"))

            for row in section.get("rows") or []:
                for column, label in headers.items():
                    if column == "attribute":
                        continue

                    results.append(
                        NasdaqNordicBondYieldsData.model_validate(
                            {
                                "date": reported,
                                "segment": segment,
                                "attribute": translate(row.get("attribute")),
                                "maturity": label,
                                "value": to_number(row.get(column)),
                            }
                        )
                    )

        if not results:
            raise EmptyDataError(f"No '{query.basis}' bond yields were published.")

        return results
