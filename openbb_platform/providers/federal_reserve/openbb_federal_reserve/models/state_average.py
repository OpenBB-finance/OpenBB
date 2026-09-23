"""FFIEC UBPR State Average Report Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_federal_reserve.utils.state_average_report import (
    GROUP_TYPES,
    STATE_OPTIONS,
)

STATE_AVERAGE_SECTIONS = [
    "Summary Ratios",
    "Noninterest Income and Expenses",
    "Asset Yields and Funding Costs",
    "Off Balance Sheet Items",
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
    "Income Statement 1-Qtr-Ann",
    "Fiduciary Services-a",
]
STATE_CODES = [option["value"] for option in STATE_OPTIONS]


class FederalReserveStateAverageQueryParams(QueryParams):
    """FFIEC UBPR State Average Report Query Parameters."""

    __json_schema_extra__ = {
        "state": {"x-widget_config": {"options": STATE_OPTIONS}},
        "group_type": {
            "x-widget_config": {
                "options": [
                    {"label": name.title(), "value": name} for name in GROUP_TYPES
                ]
            }
        },
        "section": {
            "x-widget_config": {
                "options": [
                    {"label": name, "value": name} for name in STATE_AVERAGE_SECTIONS
                ]
            }
        },
    }

    state: str = Field(
        default="SD",
        description="The two-letter state (or territory) code to average.",
        json_schema_extra={"choices": STATE_CODES},
    )
    group_type: str = Field(
        default="commercial",
        description="The institution peer group to average across the state.",
        json_schema_extra={"choices": GROUP_TYPES},
    )
    section: str = Field(
        default="Summary Ratios",
        description="The UBPR State Average report section (page) to return.",
        json_schema_extra={"choices": STATE_AVERAGE_SECTIONS},
    )
    all_periods: bool = Field(
        default=False,
        description="Return every reported period instead of only the most recent five.",
    )


class FederalReserveStateAverageData(Data):
    """FFIEC UBPR State Average Report Data."""

    label: str = Field(description="The line item, indented by the report hierarchy.")
    is_header: bool = Field(
        default=False, description="Whether the row is a section or sub-section header."
    )
    narrative: str | None = Field(
        default=None,
        description="The MDRM definition of the line item, when available.",
    )


class FederalReserveStateAverageFetcher(
    Fetcher[
        FederalReserveStateAverageQueryParams,
        list[FederalReserveStateAverageData],
    ]
):
    """FFIEC UBPR State Average Report Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveStateAverageQueryParams:
        """Transform the query params."""
        query = FederalReserveStateAverageQueryParams(**params)
        if query.state.strip().upper() not in STATE_CODES:
            raise OpenBBError(ValueError(f"Unknown state '{query.state}'."))
        if query.group_type not in GROUP_TYPES:
            raise OpenBBError(ValueError(f"`group_type` must be one of {GROUP_TYPES}."))
        return query

    @staticmethod
    def extract_data(
        query: FederalReserveStateAverageQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Fetch the requested State Average section from the FFIEC CDR report."""
        from openbb_federal_reserve.utils.state_average_report import (
            fetch_state_average_section,
        )

        result = fetch_state_average_section(
            query.state,
            query.section,
            group_type=query.group_type,
            all_periods=query.all_periods,
        )
        if not result["rows"]:
            raise EmptyDataError("The request was returned empty.")
        return result["rows"]

    @staticmethod
    def transform_data(
        query: FederalReserveStateAverageQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveStateAverageData]:
        """Validate the parsed section rows."""
        return [FederalReserveStateAverageData.model_validate(row) for row in data]
