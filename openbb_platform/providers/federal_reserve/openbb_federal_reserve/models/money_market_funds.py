"""Federal Reserve Money Market Funds Investment Holdings Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class FederalReserveMoneyMarketFundsQueryParams(QueryParams):
    """Federal Reserve Money Market Funds Holdings Query Parameters."""

    __json_schema_extra__ = {
        "table": {
            "x-widget_config": {
                "options": [
                    {
                        "label": "Total money market funds investment holdings",
                        "value": "total",
                    },
                    {
                        "label": "Prime money market funds investment holdings",
                        "value": "prime",
                    },
                    {
                        "label": "Government money market funds investment holdings",
                        "value": "government",
                    },
                    {
                        "label": "Tax-exempt money market funds investment holdings",
                        "value": "exempt",
                    },
                    {
                        "label": "Money market funds investment holdings by fund type",
                        "value": "holdings",
                    },
                    {
                        "label": "Money market funds investment holdings country detail",
                        "value": "detail",
                    },
                    {
                        "label": "Money market fund commercial paper holdings",
                        "value": "commercial_paper",
                    },
                    {
                        "label": "Repo money market funds holdings",
                        "value": "repo",
                    },
                ]
            }
        }
    }

    table: Literal[
        "total",
        "prime",
        "government",
        "exempt",
        "holdings",
        "detail",
        "commercial_paper",
        "repo",
    ] = Field(
        default="total",
        description="The Enhanced Financial Accounts table: total/prime/government/"
        "exempt holdings, by-fund-type holdings, country detail, commercial paper,"
        " or repo.",
    )
    country: str | None = Field(
        default=None,
        description="Filter to a single country (the detail tables only).",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveMoneyMarketFundsData(Data):
    """Federal Reserve Money Market Funds Holdings Data."""

    date: dateType = Field(description="The observation date.")


class FederalReserveMoneyMarketFundsFetcher(
    Fetcher[
        FederalReserveMoneyMarketFundsQueryParams,
        list[FederalReserveMoneyMarketFundsData],
    ]
):
    """Federal Reserve Money Market Funds Holdings Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveMoneyMarketFundsQueryParams:
        """Transform the query params."""
        return FederalReserveMoneyMarketFundsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveMoneyMarketFundsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download and melt the requested holdings table, applying filters."""
        from openbb_federal_reserve.utils.mmf import fetch_mmf, parse_mmf

        rows = parse_mmf(fetch_mmf(query.table))
        if query.country:
            wanted = query.country.strip().lower()
            rows = [
                row
                for row in rows
                if row.get("country") and wanted in row["country"].lower()
            ]
        if query.start_date:
            rows = [row for row in rows if row["date"] >= query.start_date]
        if query.end_date:
            rows = [row for row in rows if row["date"] <= query.end_date]
        if not rows:
            raise EmptyDataError("The request was returned empty.")
        return rows

    @staticmethod
    def transform_data(
        query: FederalReserveMoneyMarketFundsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveMoneyMarketFundsData]:
        """Pivot the long rows to wide category columns."""
        from openbb_federal_reserve.utils.workbook import pivot_wide

        index: str | tuple[str, ...] = (
            ("date", "country") if query.table == "detail" else "date"
        )
        records = pivot_wide(
            sorted(data, key=lambda row: (row["date"], str(row.get("country")))),
            index=index,
            column="label",
            value="value",
        )
        return [
            FederalReserveMoneyMarketFundsData.model_validate(record)
            for record in records
        ]
