"""Federal Reserve Bank of Boston New England Economic Indicators Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_federal_reserve.utils.boston import INDICATORS

_INDICATORS = tuple(INDICATORS)


class FederalReserveBostonEconomicIndicatorsQueryParams(QueryParams):
    """Boston Fed New England Economic Indicators Query Parameters."""

    indicator: Literal[_INDICATORS] = Field(  # ty: ignore[invalid-type-form]
        default="payroll_employment",
        description="The New England Economic Indicators chart to retrieve. Each chart"
        + " returns every constituent series, across all geographies and categories,"
        + " as its own column.",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveBostonEconomicIndicatorsData(Data):
    """Boston Fed New England Economic Indicators Data.

    One row per observation date, with one clean column label per series carrying
    that series' value. Every constituent series of the selected chart - across all
    geographies and categories - is pivoted to wide, so the columns vary with the
    requested indicator. Charts with a single series per geography are labelled by
    geography (for example ``United States`` or ``Massachusetts``); multi-category
    charts keep the descriptive measure label so geography and category stay
    distinct. Index and year-over-year charts carry an explicit ``(Index)`` or
    ``(YoY %)`` marker so the displayed number is never mistaken for a raw level.
    """

    date: dateType = Field(description="The observation date.")


class FederalReserveBostonEconomicIndicatorsFetcher(
    Fetcher[
        FederalReserveBostonEconomicIndicatorsQueryParams,
        list[FederalReserveBostonEconomicIndicatorsData],
    ]
):
    """Boston Fed New England Economic Indicators Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveBostonEconomicIndicatorsQueryParams:
        """Transform the query params."""
        return FederalReserveBostonEconomicIndicatorsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveBostonEconomicIndicatorsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Decode the requested chart from the NEEI dashboard page."""
        from openbb_federal_reserve.utils.boston import fetch_indicator

        records = fetch_indicator(query.indicator, None)
        if not records:
            raise EmptyDataError("The request was returned empty.")
        return records

    @staticmethod
    def transform_data(
        query: FederalReserveBostonEconomicIndicatorsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveBostonEconomicIndicatorsData]:
        """Filter by date, then pivot the series to wide ``date`` + column rows."""
        from openbb_federal_reserve.utils.workbook import pivot_wide

        records = data
        if query.start_date:
            records = [
                record
                for record in records
                if dateType.fromisoformat(record["date"]) >= query.start_date
            ]
        if query.end_date:
            records = [
                record
                for record in records
                if dateType.fromisoformat(record["date"]) <= query.end_date
            ]
        ordered = sorted(
            records,
            key=lambda record: (
                record["date"],
                record.get("label") or "",
                record.get("name") or "",
            ),
        )
        for record in ordered:
            record["column"] = (
                record.get("label")
                or record.get("description")
                or record.get("name")
                or ""
            )
        rows = pivot_wide(ordered, index="date", column="column", value="value")
        return [
            FederalReserveBostonEconomicIndicatorsData.model_validate(record)
            for record in rows
        ]
