"""FMP Revenue Geographic Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Literal

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.revenue_geographic import (
    RevenueGeographicData,
    RevenueGeographicQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator


class FMPRevenueGeographicQueryParams(RevenueGeographicQueryParams):
    """FMP Revenue Geographic Query.

    Source: https://site.financialmodelingprep.com/developer/docs#revenue-geographic-segments
    """

    period: Literal["quarter", "annual"] = Field(
        default="annual", description=QUERY_DESCRIPTIONS.get("period", "")
    )


class FMPRevenueGeographicData(RevenueGeographicData):
    """FMP Revenue Geographic Data."""

    @field_validator("period_ending", "filing_date", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):
        """Return the date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d") if v else None


class FMPRevenueGeographicFetcher(
    Fetcher[
        FMPRevenueGeographicQueryParams,
        list[FMPRevenueGeographicData],
    ]
):
    """FMP Revenue Geographic Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPRevenueGeographicQueryParams:
        """Transform the query params."""
        return FMPRevenueGeographicQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPRevenueGeographicQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_fmp.utils.helpers import get_data_many

        api_key = credentials.get("fmp_api_key") if credentials else ""
        base_url = (
            "https://financialmodelingprep.com/stable/revenue-geographic-segmentation?"
        )
        url = f"{base_url}symbol={query.symbol}&period={query.period}&structure=flat&apikey={api_key}"
        return await get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPRevenueGeographicQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FMPRevenueGeographicData]:
        """Return the transformed data."""
        if not data:
            raise EmptyDataError("The request was returned empty.")

        results: list[FMPRevenueGeographicData] = []
        # We need to flatten the data.
        for item in data:
            period_ending = item.get("date")
            fiscal_year = item.get("fiscalYear")
            fiscal_period = item.get("period")
            segment = item.get("data", {})

            for region, revenue_value in segment.items():
                if revenue_value is not None:
                    revenue = int(revenue_value) if revenue_value is not None else None
                    if revenue is not None:
                        results.append(
                            FMPRevenueGeographicData.model_validate(
                                {
                                    "period_ending": period_ending,
                                    "fiscal_year": fiscal_year,
                                    "fiscal_period": fiscal_period,
                                    "region": region.replace("Segment", "").strip(),
                                    "revenue": revenue,
                                }
                            )
                        )

        if not results:
            raise EmptyDataError("Unknown error while transforming the data.")

        return sorted(results, key=lambda x: (x.period_ending or "", x.revenue or 0))
