"""FFIEC Uniform Bank Performance Report (UBPR) Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

UBPR_SECTIONS = [
    "Summary Ratios",
    "Income Statement $",
    "QTR Income Statement $",
    "Noninterest Income and Expenses",
    "Asset Yields and Funding Costs",
    "Balance Sheet $",
    "Off Balance Sheet Items",
    "Derivative Instruments",
    "Derivative Analysis",
    "Balance Sheet %",
    "Allowance & Loan Mix-a",
    "Allowance & Loan Mix-b",
    "Concentrations of Credit",
    "PD, Nonacc & Rest Loans-a",
    "PD, Nonacc & Rest Loans-b",
    "Interest Rate Risk-a",
    "Interest Rate Risk-b",
    "Liquidity & Funding",
    "Liquidity & Inv Portfolio",
    "Capital Analysis-a",
    "Capital Analysis-b",
    "Capital Analysis-c",
    "Income Statement 1-Qtr-Ann",
    "Securitization & Asset Sale-a",
    "Securitization & Asset Sale-b",
    "Securitization & Asset Sale-c",
    "Fiduciary Services-a",
    "Fiduciary Services-b",
]


class FederalReserveUBPRQueryParams(QueryParams):
    """FFIEC Uniform Bank Performance Report Query Parameters."""

    __json_schema_extra__ = {
        "section": {
            "x-widget_config": {
                "options": [{"label": name, "value": name} for name in UBPR_SECTIONS]
            }
        }
    }

    symbol: str | None = Field(
        default=None,
        description="The bank's stock ticker, resolved to its parent RSSD identifier.",
    )
    rssd_id: str | None = Field(
        default=None,
        description="The bank's RSSD identifier (the UBPR ID RSSD).",
    )
    section: str = Field(
        default="Summary Ratios",
        description="The UBPR report section (page) to return.",
        json_schema_extra={"choices": UBPR_SECTIONS},
    )
    all_periods: bool = Field(
        default=False,
        description="Return every reported period as the bank's own time series;"
        " the peer-group and percentile columns are omitted.",
    )


class FederalReserveUBPRData(Data):
    """FFIEC Uniform Bank Performance Report Data."""

    label: str = Field(description="The line item, indented by the report hierarchy.")
    is_header: bool = Field(
        default=False, description="Whether the row is a section or sub-section header."
    )
    narrative: str | None = Field(
        default=None,
        description="The Interactive User's Guide definition of the line item,"
        " where one is published.",
    )


class FederalReserveUBPRFetcher(
    Fetcher[FederalReserveUBPRQueryParams, list[FederalReserveUBPRData]]
):
    """FFIEC Uniform Bank Performance Report Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FederalReserveUBPRQueryParams:
        """Transform the query params."""
        query = FederalReserveUBPRQueryParams(**params)
        if not query.rssd_id and not query.symbol:
            raise OpenBBError(
                ValueError("Provide a `symbol` or `rssd_id` to identify the bank.")
            )
        return query

    @staticmethod
    def extract_data(
        query: FederalReserveUBPRQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Fetch the requested UBPR section from the FFIEC CDR report router."""
        from openbb_federal_reserve.utils.ticker import (
            resolve_rssd_to_bank,
            resolve_ticker_to_rssd,
        )
        from openbb_federal_reserve.utils.ubpr_report import (
            fetch_ubpr_section,
            no_bank_report_error,
        )

        rssd_id = query.rssd_id
        if not rssd_id and query.symbol:
            rssd_id = resolve_ticker_to_rssd(query.symbol)
            if not rssd_id:
                raise OpenBBError(
                    f"Could not resolve symbol '{query.symbol}' to an RSSD identifier."
                )

        rssd_id, name = resolve_rssd_to_bank(str(rssd_id))
        result = fetch_ubpr_section(
            rssd_id, query.section, all_periods=query.all_periods
        )
        rows = result["rows"]
        if not rows:
            raise EmptyDataError("The request was returned empty.")
        structural = {"label", "is_header", "narrative"}
        if not any(
            value is not None
            for row in rows
            for key, value in row.items()
            if key not in structural
        ):
            raise no_bank_report_error(rssd_id, "UBPR")
        rows[0] = {"_rssd": rssd_id, "_name": name, **rows[0]}
        return rows

    @staticmethod
    def transform_data(
        query: FederalReserveUBPRQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> AnnotatedResult[list[FederalReserveUBPRData]]:
        """Validate the parsed section rows; surface the resolved bank as metadata."""
        head = data[0] if data else {}
        rssd_id = head.pop("_rssd", None)
        name = head.pop("_name", None)
        return AnnotatedResult(
            result=[FederalReserveUBPRData.model_validate(row) for row in data],
            metadata={
                key: value
                for key, value in {
                    "rssd_id": rssd_id,
                    "name": name,
                    "section": query.section,
                }.items()
                if value
            },
        )
