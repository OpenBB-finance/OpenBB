"""BLS JOLTS revision tables (SA / NSA XLSX)."""

from __future__ import annotations

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field

from openbb_bls.utils.jolts_tables import fetch_revision_xlsx, parse_revision_xlsx

_HIDE: dict[str, Any] = {"x-widget_config": {"hide": True}}


def _num(name: str) -> dict[str, Any]:
    """Numeric (non-percent) column config: headerName + numeric type."""
    return {
        "x-widget_config": {
            "headerName": name,
            "cellDataType": "number",
        }
    }


def _pct(name: str) -> dict[str, Any]:
    """Percent-column config: headerName + numeric type + percent formatter + greenRed render."""
    return {
        "x-widget_config": {
            "headerName": name,
            "cellDataType": "number",
            "formatterFn": "percent",
            "renderFn": "greenRed",
        }
    }


class BlsJoltsRevisionsQueryParams(QueryParams):
    """BLS JOLTS Revisions Query Parameters."""

    seasonally_adjusted: bool = Field(
        default=True,
        description="Whether to return the seasonally-adjusted revision workbook.",
    )
    industry_code: str | None = Field(
        default=None,
        description="Optional industry or region sheet code to restrict the results.",
    )
    measure: str | None = Field(
        default=None,
        description="Optional measure name to restrict the results.",
    )


class BlsJoltsRevisionsData(Data):
    """One (industry, month, measure) JOLTS revision row with all three vintages + deltas."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "BLS JOLTS Revision Tables",
                "$.description": (
                    "JOLTS first-published vs second-revision vs benchmark "
                    "levels and the implied revision deltas."
                ),
                "$.gridData": {"w": 30, "h": 27},
                "$.refetchInterval": False,
                "$.source": ["BLS"],
                "$.category": "Economy",
                "$.subCategory": "JOLTS",
            }
        }
    )

    date: dateType = Field(
        description="First-of-month reference date the revision values describe.",
    )
    industry_code: str = Field(
        description="BLS industry or region sheet code.",
    )
    industry_name: str = Field(
        description="Human-readable industry or region name.",
    )
    seasonally_adjusted: bool = Field(
        description="Whether the row comes from the seasonally-adjusted workbook.",
        json_schema_extra=_HIDE,
    )
    measure: str = Field(
        description="JOLTS measure for the row.",
    )
    level_1st: float | None = Field(
        default=None,
        description="First-published level (thousands).",
        json_schema_extra=_num("1st (level)"),
    )
    level_2nd: float | None = Field(
        default=None,
        description="Second-revision level (thousands).",
        json_schema_extra=_num("2nd (level)"),
    )
    level_benchmark: float | None = Field(
        default=None,
        description="Benchmarked level (thousands).",
        json_schema_extra=_num("Benchmark (level)"),
    )
    revision_1st_to_2nd_level: float | None = Field(
        default=None,
        description="Level change from first-published to second-revision (thousands).",
        json_schema_extra=_num("Revision 1st→2nd (level)"),
    )
    revision_1st_to_2nd_pct: float | None = Field(
        default=None,
        description="Percent change from first-published to second-revision.",
        json_schema_extra=_pct("Revision 1st→2nd (%)"),
    )
    revision_2nd_to_benchmark_level: float | None = Field(
        default=None,
        description="Level change from second-revision to benchmark (thousands).",
        json_schema_extra=_num("Revision 2nd→Benchmark (level)"),
    )
    revision_2nd_to_benchmark_pct: float | None = Field(
        default=None,
        description="Percent change from second-revision to benchmark.",
        json_schema_extra=_pct("Revision 2nd→Benchmark (%)"),
    )
    row_index: int = Field(
        description="Sequential parser order.",
        json_schema_extra=_HIDE,
    )
    table_id: str = Field(
        description="Stable identifier for the workbook.",
        json_schema_extra=_HIDE,
    )
    table_title: str = Field(
        description="Human-readable workbook title.",
        json_schema_extra=_HIDE,
    )


class BlsJoltsRevisionsFetcher(
    Fetcher[BlsJoltsRevisionsQueryParams, list[BlsJoltsRevisionsData]]
):
    """BLS JOLTS Revisions Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> BlsJoltsRevisionsQueryParams:
        """Validate and coerce the query."""
        return BlsJoltsRevisionsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: BlsJoltsRevisionsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Download the SA or NSA revision XLSX and parse it long-form."""
        content = fetch_revision_xlsx(query.seasonally_adjusted)
        rows = parse_revision_xlsx(content, query.seasonally_adjusted)
        industry_filter = (
            query.industry_code.strip().upper() if query.industry_code else None
        )
        measure_filter = query.measure.strip().lower() if query.measure else None
        if industry_filter is None and measure_filter is None:
            return rows
        out: list[dict[str, Any]] = []
        for r in rows:
            if (
                industry_filter is not None
                and r["industry_code"].upper() != industry_filter
            ):
                continue
            if measure_filter is not None and r["measure"].lower() != measure_filter:
                continue
            out.append(r)
        return out

    @staticmethod
    def transform_data(
        query: BlsJoltsRevisionsQueryParams,
        data: list[dict[str, Any]],
        **kwargs: Any,
    ) -> list[BlsJoltsRevisionsData]:
        """Coerce parsed rows into ``BlsJoltsRevisionsData``."""
        if not data:
            raise EmptyDataError("No rows matched the JOLTS revisions query.")
        return [BlsJoltsRevisionsData.model_validate(r) for r in data]
