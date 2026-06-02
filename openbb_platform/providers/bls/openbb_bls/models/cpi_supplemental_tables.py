"""BLS CPI supplemental tables."""

from __future__ import annotations

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_serializer

from openbb_bls.utils.cpi_supplemental_tables import (
    TABLE_REGISTRY,
    discover_latest,
    fetch_xlsx,
    parse_table,
)

CpiSupplementalTableKey = Literal[
    "c-cpi-u",
    "cpi-u-us",
    "cpi-u-regional",
    "cpi-w",
    "historical-cpi-u-index",
    "historical-cpi-u-averages",
]

_HIDE: dict[str, Any] = {"x-widget_config": {"hide": True}}
_TABLE_LABELS: dict[str, str] = {
    key: spec.label for key, spec in TABLE_REGISTRY.items()
}


def _hdr(name: str) -> dict[str, Any]:
    """Override the column header name."""
    return {"x-widget_config": {"headerName": name}}


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


def _num(name: str) -> dict[str, Any]:
    """Numeric (non-percent) column config: headerName + numeric type."""
    return {
        "x-widget_config": {
            "headerName": name,
            "cellDataType": "number",
        }
    }


class BlsCpiSupplementalTablesQueryParams(QueryParams):
    """BLS CPI Supplemental Tables Query Parameters."""

    __json_schema_extra__ = {
        "table": {
            "x-widget_config": {
                "options": [
                    {"label": f"{key} — {label}", "value": key}
                    for key, label in _TABLE_LABELS.items()
                ],
                "style": {"popupWidth": 950},
            }
        },
    }

    table: CpiSupplementalTableKey = Field(
        default="cpi-u-us",
        description="Which CPI supplemental table to load.",
    )
    date: dateType | None = Field(
        default=None,
        description="Snapshot month to fetch; None resolves to the most recent published snapshot.",
    )


class BlsCpiSupplementalTablesData(Data):
    """One (item, reference-date) observation from a CPI supplemental table."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "BLS CPI Supplemental Tables",
                "$.description": "BLS CPI supplemental XLSX tables in long form.",
                "$.gridData": {"w": 30, "h": 27},
                "$.refetchInterval": False,
                "$.source": ["BLS"],
                "$.category": "Economy",
                "$.subCategory": "CPI",
            }
        }
    )

    date: dateType = Field(
        description="Reference date the row's values apply to.",
    )
    label: str = Field(
        description="Row label from the source XLSX.",
        json_schema_extra={
            "x-widget_config": {
                "renderFn": "hoverCard",
                "renderFnParams": {
                    "hoverCard": {
                        "cellField": "value",
                        "markdown": "{footnote}",
                    }
                },
            }
        },
    )

    @field_serializer("label", when_used="json")
    def _serialize_label_with_footnote(self, value: str | None) -> Any:
        """Wrap the label with footnote text for the hover-card renderer."""
        if value and self.footnote:
            return {"value": value, "footnote": self.footnote}
        return value

    indent_level: int | None = Field(
        default=None,
        description="Indent depth in the source XLSX.",
    )
    frequency: str = Field(
        default="monthly",
        description="Reference-date frequency: monthly, semiannual, or annual.",
    )
    index_value: float | None = Field(
        default=None,
        description="Unadjusted (NSA) CPI index level at date.",
        json_schema_extra=_num("Index Value (NSA)"),
    )
    sa_index_value: float | None = Field(
        default=None,
        description="Seasonally-adjusted CPI index level at date.",
        json_schema_extra=_num("Index Value (SA)"),
    )
    pct_change_1m_nsa: float | None = Field(
        default=None,
        description="One-month NSA percent change ending at date.",
        json_schema_extra=_pct("Pct Change 1M NSA"),
    )
    pct_change_1m_sa: float | None = Field(
        default=None,
        description="One-month seasonally-adjusted percent change ending at date.",
        json_schema_extra=_pct("Pct Change 1M SA"),
    )
    pct_change_12m: float | None = Field(
        default=None,
        description="Twelve-month percent change ending at date.",
        json_schema_extra=_pct("Pct Change 12M"),
    )
    pct_change_window: float | None = Field(
        default=None,
        description="Two-month NSA percent change ending at date.",
        json_schema_extra=_pct("Pct Change 2M NSA"),
    )
    pct_change_window_start_date: dateType | None = Field(
        default=None,
        description="Start-of-month for the pct_change_window comparison.",
        json_schema_extra=_HIDE,
    )
    relative_importance: float | None = Field(
        default=None,
        description="Relative-importance weight as a percent of the parent index.",
        json_schema_extra=_pct("Relative Importance"),
    )
    pricing_schedule: str | None = Field(
        default=None,
        description="Pricing-schedule code (M = monthly, S = semiannual, B = bimonthly).",
    )
    half: str | None = Field(
        default=None,
        description="Semiannual half (1st or 2nd) for historical-cpi-u-averages rows.",
        json_schema_extra=_HIDE,
    )
    value_string: str | None = Field(
        default=None,
        description="Raw cell text when the source value is not numeric.",
        json_schema_extra=_HIDE,
    )
    snapshot_date: dateType = Field(
        description="Publication month of the source XLSX snapshot.",
        json_schema_extra=_HIDE,
    )
    table_key: str = Field(
        description="Which CPI table family this row came from.",
        json_schema_extra=_HIDE,
    )
    table_id: str = Field(
        description="Stable identifier for the source (table, snapshot) tuple.",
        json_schema_extra=_HIDE,
    )
    table_name: str = Field(
        description="Human-readable BLS table title for the source snapshot.",
        json_schema_extra=_HIDE,
    )
    sheet: str = Field(
        description="XLSX sheet name the row was read from.",
        json_schema_extra=_HIDE,
    )
    row_index: int = Field(
        description="Sequential ordering index assigned during parsing.",
        json_schema_extra=_HIDE,
    )
    footnote: str | None = Field(
        default=None,
        description="Resolved footnote text for any (N) markers attached to the row's label.",
        json_schema_extra=_HIDE,
    )


class BlsCpiSupplementalTablesFetcher(
    Fetcher[BlsCpiSupplementalTablesQueryParams, list[BlsCpiSupplementalTablesData]]
):
    """BLS CPI Supplemental Tables Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> BlsCpiSupplementalTablesQueryParams:
        """Validate and coerce the query."""
        return BlsCpiSupplementalTablesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: BlsCpiSupplementalTablesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Download the chosen monthly XLSX and parse it long-form."""
        spec = TABLE_REGISTRY[query.table]
        if query.date is None:
            year, month, content = discover_latest(spec.stem)
        else:
            year, month = query.date.year, query.date.month
            content = fetch_xlsx(spec.stem, year, month)
            if content is None:
                raise OpenBBError(
                    f"BLS does not publish the '{query.table}' CPI "
                    f"supplemental XLSX for {year:04d}-{month:02d}."
                )
        return parse_table(content, spec, year, month)

    @staticmethod
    def transform_data(
        query: BlsCpiSupplementalTablesQueryParams,
        data: list[dict[str, Any]],
        **kwargs: Any,
    ) -> list[BlsCpiSupplementalTablesData]:
        """Coerce parsed rows into BlsCpiSupplementalTablesData."""
        if not data:
            raise EmptyDataError(
                f"No rows parsed from BLS CPI supplemental table '{query.table}'."
            )
        return [BlsCpiSupplementalTablesData.model_validate(r) for r in data]
