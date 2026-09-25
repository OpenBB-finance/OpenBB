"""Debt To The Penny Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field

ENDPOINT = "v2/accounting/od/debt_to_penny"

FIELD_MAP = {
    "record_date": "date",
    "tot_pub_debt_out_amt": "total_public_debt_outstanding",
    "debt_held_public_amt": "debt_held_public",
    "intragov_hold_amt": "intragovernmental_holdings",
}


class DebtToPennyQueryParams(QueryParams):
    """Debt To The Penny Query Parameters.

    Source: https://fiscaldata.treasury.gov/datasets/debt-to-the-penny/debt-to-the-penny
    """

    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", "")
        + " Data begins 1993-04-01. When None, defaults to the trailing 365 days rather than the full history; set it explicitly to reach further back.",
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )


class DebtToPennyData(Data):
    """Debt To The Penny Data.

    Total public debt outstanding, reported for each business day. The split
    between debt held by the public and intragovernmental holdings is
    published daily from 2005-04-04, and only on fiscal-year-end and
    month-end dates before that.
    """

    date: dateType = Field(
        description=DATA_DESCRIPTIONS.get("date", ""),
        json_schema_extra={"x-widget_config": {"pinned": "left"}},
    )
    total_public_debt_outstanding: float = Field(
        description="Total public debt outstanding, in dollars, to the penny.",
    )
    debt_held_public: float | None = Field(
        default=None,
        description="Debt held by the public, in dollars."
        + " Excludes Federal Financing Bank securities.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Debt Held by the Public"}
        },
    )
    intragovernmental_holdings: float | None = Field(
        default=None,
        description="Intragovernmental holdings, in dollars."
        + " Includes Federal Financing Bank securities.",
    )


class DebtToPennyFetcher(
    Fetcher[
        DebtToPennyQueryParams,
        list[DebtToPennyData],
    ]
):
    """Fetch the total public debt outstanding from the FiscalData API."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> DebtToPennyQueryParams:
        """Transform the query params."""
        return DebtToPennyQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DebtToPennyQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the data from the FiscalData API."""
        from openbb_government_us.treasury.utils.fiscal_data import (
            build_filters,
            default_start_date,
            get_fiscal_data,
        )

        start_date = default_start_date(query.start_date, query.end_date, 365)
        filters = build_filters(
            [
                ("record_date", "gte", start_date),
                ("record_date", "lte", query.end_date),
            ]
        )

        return await get_fiscal_data(ENDPOINT, filters=filters, sort="record_date")

    @staticmethod
    def transform_data(
        query: DebtToPennyQueryParams, data: list[dict], **kwargs: Any
    ) -> list[DebtToPennyData]:
        """Transform the data, newest business day first."""
        return sorted(
            (
                DebtToPennyData.model_validate(
                    {
                        target: row[source]
                        for source, target in FIELD_MAP.items()
                        if source in row
                    }
                )
                for row in data
            ),
            key=lambda row: row.date,
            reverse=True,
        )
