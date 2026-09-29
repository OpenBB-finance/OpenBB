"""BLS JOLTS change-analysis supplemental tables."""

from __future__ import annotations

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field

from openbb_bls.utils.jolts_tables import (
    _NATIONAL_TABLE_MEASURES,
    _STATE_TABLE_MEASURES,
    fetch_change_analysis_txt,
    parse_change_analysis,
)

JoltsScope = Literal["national", "state"]

_HIDE: dict[str, Any] = {"x-widget_config": {"hide": True}}


def _build_table_options() -> list[dict[str, Any]]:
    """Return a `(scope, table_number) → human label` dropdown list."""
    options: list[dict[str, Any]] = []
    for n, (measure, period) in _NATIONAL_TABLE_MEASURES.items():
        suffix = " (SA)" if period == "over-the-month" else " (NSA)"
        options.append(
            {
                "label": f"National Table {n} — {measure} {period}{suffix}",
                "value": n,
            }
        )
    for n, (measure, period) in _STATE_TABLE_MEASURES.items():
        suffix = " (SA)" if period == "over-the-month" else " (NSA)"
        options.append(
            {
                "label": f"State Table {n} — {measure} {period}{suffix}",
                "value": n + 100,
            }
        )
    return options


class BlsJoltsChangeAnalysisQueryParams(QueryParams):
    """BLS JOLTS Change-Analysis Tables Query Parameters."""

    __json_schema_extra__ = {
        "table_number": {
            "x-widget_config": {
                "style": {"popupWidth": 950},
                "options": _build_table_options(),
            }
        },
    }

    scope: JoltsScope = Field(
        default="national",
        description="JOLTS change-analysis family to load.",
    )
    table_number: int = Field(
        default=1,
        ge=1,
        le=12,
        description="Numbered change-analysis table to load.",
    )


class BlsJoltsChangeAnalysisData(Data):
    """One row from a BLS JOLTS change-analysis table."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "BLS JOLTS Change-Analysis Tables",
                "$.description": (
                    "Job Openings and Labor Turnover Survey "
                    "change-analysis tables (jlt_tableN / jltst_tableN) "
                    "— estimated rate and level changes plus significance "
                    "test results, by industry/region or by state."
                ),
                "$.gridData": {"w": 30, "h": 27},
                "$.refetchInterval": False,
                "$.source": ["BLS"],
                "$.category": "Economy",
                "$.subCategory": "JOLTS",
            }
        }
    )

    table_id: str = Field(
        description="Stable identifier for the source table.",
        json_schema_extra=_HIDE,
    )
    table_title: str = Field(
        description="Full BLS table title.",
        json_schema_extra=_HIDE,
    )
    scope: str = Field(
        description="National or state scope of the table.",
        json_schema_extra=_HIDE,
    )
    table_number: int = Field(
        description="Source table number within the scope.",
        json_schema_extra=_HIDE,
    )
    measure: str = Field(
        description="JOLTS measure published in this table.",
    )
    period: str = Field(
        description="Comparison window for the table.",
    )
    seasonally_adjusted: bool | None = Field(
        default=None,
        description="Whether the table is seasonally adjusted.",
    )
    period_start: dateType | None = Field(
        default=None,
        description="First-of-month start date of the comparison window.",
    )
    period_end: dateType | None = Field(
        default=None,
        description="First-of-month end date of the comparison window.",
    )
    source_date: dateType | None = Field(
        default=None,
        description="Release date stamped in the TXT footer.",
        json_schema_extra=_HIDE,
    )
    row_index: int = Field(
        description="Sequential ordering index preserving the source row order.",
        json_schema_extra=_HIDE,
    )
    section: str | None = Field(
        default=None,
        description="Section header the row appears under in the source TXT.",
    )
    indent_spaces: int = Field(
        description="Leading-space count from the source TXT encoding hierarchy depth.",
        json_schema_extra=_HIDE,
    )
    label: str = Field(
        description="Row label — industry, region, or state name.",
    )
    rate_change: float | None = Field(
        default=None,
        description="Estimated rate change in percentage points over the comparison window.",
    )
    rate_min_significant: float | None = Field(
        default=None,
        description="Minimum rate change in percentage points needed to reach 90-percent significance.",
    )
    rate_passes_significance: bool = Field(
        default=False,
        description="Whether the rate change is statistically significant at 90 percent.",
    )
    level_change_thousands: float | None = Field(
        default=None,
        description="Estimated level change in thousands over the comparison window.",
    )
    level_min_significant_thousands: float | None = Field(
        default=None,
        description="Minimum level change in thousands needed to reach 90-percent significance.",
    )
    level_passes_significance: bool = Field(
        default=False,
        description="Whether the level change is statistically significant at 90 percent.",
    )


class BlsJoltsChangeAnalysisFetcher(
    Fetcher[BlsJoltsChangeAnalysisQueryParams, list[BlsJoltsChangeAnalysisData]]
):
    """BLS JOLTS Change-Analysis Tables Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> BlsJoltsChangeAnalysisQueryParams:
        """Validate and coerce the query."""
        return BlsJoltsChangeAnalysisQueryParams(**params)

    @staticmethod
    def extract_data(
        query: BlsJoltsChangeAnalysisQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Download and parse one change-analysis TXT table."""
        scope_map = (
            _NATIONAL_TABLE_MEASURES
            if query.scope == "national"
            else _STATE_TABLE_MEASURES
        )
        if query.table_number not in scope_map:
            raise OpenBBError(
                f"JOLTS {query.scope} table {query.table_number} does not "
                f"exist (valid range: {min(scope_map)}-{max(scope_map)})."
            )
        content = fetch_change_analysis_txt(query.scope, query.table_number)
        return parse_change_analysis(content, query.scope, query.table_number)

    @staticmethod
    def transform_data(
        query: BlsJoltsChangeAnalysisQueryParams,
        data: dict[str, Any],
        **kwargs: Any,
    ) -> list[BlsJoltsChangeAnalysisData]:
        """Coerce parsed rows into ``BlsJoltsChangeAnalysisData``."""
        rows = data.get("rows", [])
        if not rows:
            raise EmptyDataError(
                f"No rows parsed from BLS JOLTS {query.scope} table "
                f"{query.table_number}."
            )
        return [BlsJoltsChangeAnalysisData.model_validate(r) for r in rows]
