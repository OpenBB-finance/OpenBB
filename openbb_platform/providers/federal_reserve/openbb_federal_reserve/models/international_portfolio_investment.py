"""Federal Reserve International Portfolio Investment Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_federal_reserve.utils.ipi import TABLES


class FederalReserveInternationalPortfolioInvestmentQueryParams(QueryParams):
    """Federal Reserve International Portfolio Investment Query Parameters."""

    __json_schema_extra__ = {
        "table": {
            "x-widget_config": {
                "options": [
                    {"label": label, "value": code}
                    for code, (_, label) in TABLES.items()
                ]
            }
        }
    }

    table: Literal[
        "table1",
        "table1a",
        "table1b",
        "table1c",
        "table1d",
        "table1e",
        "table2",
        "table2a",
        "table2b",
    ] = Field(
        default="table1",
        description="The holdings table: foreign residents' holdings of U.S."
        " securities - total (table1), Treasury (1a), agency (1b), corporate"
        " bonds (1c), stocks (1d), short-term Treasury memo (1e); or U.S."
        " residents' holdings of foreign securities - total (table2), bonds (2a),"
        " stocks (2b).",
    )
    country: str | None = Field(
        default=None,
        description="Filter to a single country or region (matched in the path).",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveInternationalPortfolioInvestmentData(Data):
    """Federal Reserve International Portfolio Investment Data."""

    date: dateType = Field(description="The observation date.")
    country: str = Field(description="The country or region.")


class FederalReserveInternationalPortfolioInvestmentFetcher(
    Fetcher[
        FederalReserveInternationalPortfolioInvestmentQueryParams,
        list[FederalReserveInternationalPortfolioInvestmentData],
    ]
):
    """Federal Reserve International Portfolio Investment Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveInternationalPortfolioInvestmentQueryParams:
        """Transform the query params."""
        return FederalReserveInternationalPortfolioInvestmentQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveInternationalPortfolioInvestmentQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download and melt the requested holdings table, applying filters."""
        from openbb_federal_reserve.utils.ipi import TABLES, fetch_ipi, parse_ipi

        rows = parse_ipi(fetch_ipi(query.table), TABLES[query.table][1])
        if query.country:
            wanted = query.country.strip().lower()
            rows = [row for row in rows if wanted in row["country"].lower()]
        if query.start_date:
            rows = [row for row in rows if row["date"] >= query.start_date]
        if query.end_date:
            rows = [row for row in rows if row["date"] <= query.end_date]
        if not rows:
            raise EmptyDataError("The request was returned empty.")
        return rows

    @staticmethod
    def transform_data(
        query: FederalReserveInternationalPortfolioInvestmentQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveInternationalPortfolioInvestmentData]:
        """Pivot the long rows to wide ``(date, country)`` + measure column."""
        from openbb_federal_reserve.utils.workbook import pivot_wide

        records = pivot_wide(
            sorted(data, key=lambda row: (row["date"], row["country"])),
            index=("date", "country"),
            column="label",
            value="value",
        )
        return [
            FederalReserveInternationalPortfolioInvestmentData.model_validate(record)
            for record in records
        ]
