"""Federal Reserve BHCPR peer-group report viewer model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_validator

_PEER_GROUP_LABELS = {
    "1": "Peer 1 — $10B and over",
    "2": "Peer 2 — $3B to $10B",
    "3": "Peer 3 — $1B to $3B",
    "4": "Peer 4 — $500M to $1B",
    "5": "Peer 5 — under $500M",
    "6": "Peer 6 — under $300M (legacy)",
    "9": "Peer 9 — 2nd tier and atypical BHCs",
}
_peer_group_choices = [
    {"label": label, "value": value} for value, label in _PEER_GROUP_LABELS.items()
]
_year_choices = [
    {"label": str(year), "value": year}
    for year in sorted(range(2002, datetime.now().year + 1), reverse=True)
]


class FederalReserveBhcprReportQueryParams(QueryParams):
    """Federal Reserve BHCPR Peer-Group Report Query."""

    __json_schema_extra__ = {
        "peer_group": {
            "x-widget_config": {
                "value": "1",
                "options": _peer_group_choices,
            }
        },
        "year": {
            "x-widget_config": {
                "type": "number",
                "value": None,
                "options": [{"label": "All Years", "value": None}, *_year_choices],
            }
        },
    }

    peer_group: str = Field(
        default="1",
        description="The BHCPR peer group, ranked by total consolidated assets.",
    )
    year: int | None = Field(
        default=None,
        description="The report year. If None, all years are returned.",
    )

    @field_validator("peer_group", mode="before", check_fields=False)
    @classmethod
    def _validate_peer_group(cls, v):
        """Validate the peer group against the known set."""
        if v is None:
            return "1"
        value = str(v).strip()
        if value not in _PEER_GROUP_LABELS:
            raise ValueError(
                f"Invalid peer group. Must be one of: {', '.join(_PEER_GROUP_LABELS)}"
            )
        return value


class FederalReserveBhcprReportData(Data):
    """Federal Reserve BHCPR Peer-Group Report Data."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.type": "multi_file_viewer",
                "$.name": "BHCPR Peer-Group Reports",
                "$.category": "Federal Reserve",
                "$.subCategory": "FRB",
                "$.description": "Bank Holding Company Performance Report (BHCPR)"
                " peer-group average PDFs. Choose a peer group and year, then select"
                " one or more quarterly reports to view.",
                "$.gridData": {"w": 30, "h": 27},
                "$.refetchInterval": False,
                "$.endpoint": "bhcpr_report_download",
                "$.params": [
                    {
                        "type": "endpoint",
                        "paramName": "url",
                        "optionsEndpoint": "bhcpr_report_choices",
                        "optionsParams": {
                            "peer_group": "$peer_group",
                            "year": "$year",
                        },
                        "show": False,
                        "multiSelect": True,
                        "roles": ["fileSelector"],
                    },
                ],
                "$.data": {},
            }
        }
    )

    peer_group: int = Field(description="The BHCPR peer group number.")
    year: int = Field(description="The report year.")
    quarter: int = Field(description="The report quarter, from 1 to 4.")
    period_end: dateType = Field(description="The report period-end date.")
    name: str = Field(description="The report PDF filename.")
    url: str = Field(description="The report PDF URL.")


class FederalReserveBhcprReportFetcher(
    Fetcher[
        FederalReserveBhcprReportQueryParams,
        list[FederalReserveBhcprReportData],
    ]
):
    """Federal Reserve BHCPR Peer-Group Report Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FederalReserveBhcprReportQueryParams:
        """Transform the query parameters."""
        return FederalReserveBhcprReportQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveBhcprReportQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Filter the BHCPR report index to the requested peer group and year."""
        from openbb_federal_reserve.utils.ffiec import list_bhcpr_reports

        rows = [
            report
            for report in list_bhcpr_reports()
            if str(report["peer_group"]) == query.peer_group
            and (query.year is None or report["year"] == query.year)
        ]
        if not rows:
            raise EmptyDataError("No BHCPR reports matched the query.")
        return rows

    @staticmethod
    def transform_data(
        query: FederalReserveBhcprReportQueryParams,
        data: list[dict[str, Any]],
        **kwargs: Any,
    ) -> list[FederalReserveBhcprReportData]:
        """Sort newest-first and validate to the data model."""
        ordered = sorted(
            data, key=lambda row: (row["year"], row["quarter"]), reverse=True
        )
        return [FederalReserveBhcprReportData.model_validate(row) for row in ordered]
