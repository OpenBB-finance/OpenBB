"""FFIEC UBPR Peer Group Average Report Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_federal_reserve.utils.peer_groups import (
    STATIC_PEER_GROUPS,
    peer_group_options,
)

_PEER_GROUP_OPTIONS = peer_group_options()
_PEER_GROUP_NAMES = list(STATIC_PEER_GROUPS)

PGA_SECTIONS = [
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


class FederalReservePeerGroupAverageQueryParams(QueryParams):
    """FFIEC UBPR Peer Group Average Report Query Parameters."""

    __json_schema_extra__ = {
        "peer_group": {
            "x-widget_config": {"options": _PEER_GROUP_OPTIONS},
        },
        "section": {
            "x-widget_config": {
                "options": [{"label": name, "value": name} for name in PGA_SECTIONS]
            }
        },
    }

    peer_group: str = Field(
        default="1",
        description="The UBPR peer-group name; the default groups the largest"
        " insured commercial banks (assets greater than $100 billion).",
        json_schema_extra={"choices": _PEER_GROUP_NAMES},
    )
    section: str = Field(
        default="Summary Ratios",
        description="The Peer Group Average Report section (page) to return.",
        json_schema_extra={"choices": PGA_SECTIONS},
    )
    all_periods: bool = Field(
        default=False,
        description="Return every reported period instead of only the most recent five.",
    )


class FederalReservePeerGroupAverageData(Data):
    """FFIEC UBPR Peer Group Average Report Data.

    One row per report line item; each reporting quarter (the five most recent by
    default, or the full history when ``all_periods`` is set) contributes an
    ISO-date keyed column carrying the peer group average, in the report's own
    section layout.
    """

    label: str = Field(description="The line item, indented by the report hierarchy.")
    is_header: bool = Field(
        default=False, description="Whether the row is a section or sub-section header."
    )
    narrative: str | None = Field(
        default=None,
        description="The MDRM definition of the line item, when available.",
    )


class FederalReservePeerGroupAverageFetcher(
    Fetcher[
        FederalReservePeerGroupAverageQueryParams,
        list[FederalReservePeerGroupAverageData],
    ]
):
    """FFIEC UBPR Peer Group Average Report Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReservePeerGroupAverageQueryParams:
        """Transform the query params."""
        return FederalReservePeerGroupAverageQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReservePeerGroupAverageQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Fetch the requested section from the FFIEC CDR peer group report."""
        from openbb_federal_reserve.utils.peer_group_report import (
            fetch_peer_group_section,
            resolve_peer_group_id,
        )

        try:
            peergroupid = resolve_peer_group_id(query.peer_group)
        except ValueError as error:
            raise OpenBBError(error) from error

        result = fetch_peer_group_section(
            peergroupid, query.section, all_periods=query.all_periods
        )
        if not result["rows"]:
            raise EmptyDataError("The request was returned empty.")
        return result["rows"]

    @staticmethod
    def transform_data(
        query: FederalReservePeerGroupAverageQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReservePeerGroupAverageData]:
        """Validate the parsed section rows."""
        return [FederalReservePeerGroupAverageData.model_validate(row) for row in data]
