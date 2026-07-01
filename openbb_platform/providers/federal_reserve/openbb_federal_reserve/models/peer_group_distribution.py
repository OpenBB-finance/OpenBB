"""FFIEC UBPR Peer Group Average Distribution Model."""

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

PEER_GROUP_DISTRIBUTION_SECTIONS = [
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


class FederalReservePeerGroupDistributionQueryParams(QueryParams):
    """FFIEC UBPR Peer Group Average Distribution Query Parameters."""

    __json_schema_extra__ = {
        "peer_group": {
            "x-widget_config": {"options": _PEER_GROUP_OPTIONS},
        },
        "section": {
            "x-widget_config": {
                "options": [
                    {"label": name, "value": name}
                    for name in PEER_GROUP_DISTRIBUTION_SECTIONS
                ]
            }
        },
    }

    peer_group: str = Field(
        default="1",
        description="The UBPR peer-group name (e.g. '1', 'NATIONAL', 'ALCOM').",
        json_schema_extra={"choices": _PEER_GROUP_NAMES},
    )
    section: str = Field(
        default="Summary Ratios",
        description="The report page (section) to return.",
        json_schema_extra={"choices": PEER_GROUP_DISTRIBUTION_SECTIONS},
    )
    period: str | None = Field(
        default=None,
        description="The reporting period end date (YYYY-MM-DD); defaults to latest.",
    )


class FederalReservePeerGroupDistributionData(Data):
    """FFIEC UBPR Peer Group Average Distribution Data.

    One row per report line item; the percentile columns (1st .. 99th) and the
    trimmed average describe the ratio's distribution across the peer group for
    the reporting period. The memo footer rows (peer-group aggregate assets, net
    income, and bank count) carry a single peer-group value in a ``PEER GROUP``
    column rather than a percentile.
    """

    label: str = Field(description="The line item, indented by the report hierarchy.")
    is_header: bool = Field(
        default=False, description="Whether the row is a section or sub-section header."
    )
    narrative: str | None = Field(
        default=None,
        description="The Interactive User's Guide definition of the line item's concept, when available.",
    )


class FederalReservePeerGroupDistributionFetcher(
    Fetcher[
        FederalReservePeerGroupDistributionQueryParams,
        list[FederalReservePeerGroupDistributionData],
    ]
):
    """FFIEC UBPR Peer Group Average Distribution Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReservePeerGroupDistributionQueryParams:
        """Transform the query params."""
        query = FederalReservePeerGroupDistributionQueryParams(**params)
        if query.peer_group.strip().upper() not in STATIC_PEER_GROUPS:
            raise OpenBBError(ValueError(f"Unknown peer group '{query.peer_group}'."))
        return query

    @staticmethod
    def extract_data(
        query: FederalReservePeerGroupDistributionQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Fetch the requested distribution page from the FFIEC CDR report."""
        from openbb_federal_reserve.utils.peer_group_distribution import (
            fetch_distribution,
        )
        from openbb_federal_reserve.utils.ubpr_report import report_cycles

        cycle_id: str | None = None
        if query.period:
            month, day, year = (
                query.period.split("-")[1],
                query.period.split("-")[2],
                query.period.split("-")[0],
            )
            target = f"{month}/{day}/{year}"
            cycle_id = next(
                (
                    c["reportingcycleid"]
                    for c in report_cycles()
                    if c["enddateformatted"] == target
                ),
                None,
            )

        result = fetch_distribution(query.peer_group, query.section, cycle_id=cycle_id)
        if not result["rows"]:
            raise EmptyDataError("The request was returned empty.")
        return result["rows"]

    @staticmethod
    def transform_data(
        query: FederalReservePeerGroupDistributionQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReservePeerGroupDistributionData]:
        """Validate the parsed distribution rows."""
        return [
            FederalReservePeerGroupDistributionData.model_validate(row) for row in data
        ]
