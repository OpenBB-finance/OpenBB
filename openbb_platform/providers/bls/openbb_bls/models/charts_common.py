"""Shared builder for BLS news-release per-chart typed table widgets."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, create_model

_HIDE: dict[str, Any] = {"x-widget_config": {"hide": True}}

# Friendly column header for each cross-section stub field.
_STUB_HEADER: dict[str, str] = {
    "industry": "Industry",
    "period": "Period",
    "measure": "Measure",
    "commodity": "Commodity",
    "category": "Category",
}


def _col(label: str, role: str) -> dict[str, Any]:
    """Build a value column's widget config from its role."""
    cfg: dict[str, Any] = {
        "headerName": label,
        "cellDataType": "number",
        "chartDataType": "series",
    }
    if role == "pct":
        cfg["formatterFn"] = "percent"
        cfg["renderFn"] = "greenRed"
    return {"x-widget_config": cfg}


def _widget(
    name_prefix: str, label: str, chart_type: str, subcategory: str, pack_label: str
) -> dict[str, Any]:
    """Table-first widget config exposing a chart toggle of the given type."""
    return {
        "x-widget_config": {
            "$.name": f"{name_prefix} — {label}",
            "$.description": (
                f"{label}, from the BLS {pack_label} news-release chart package."
            ),
            "$.gridData": {"w": 40, "h": 20},
            "$.refetchInterval": False,
            "$.source": ["BLS"],
            "$.category": "Economy",
            "$.subCategory": subcategory,
            # Table renders first; the chart is an opt-in toggle.
            "table": {
                "showAll": True,
                "enableCharts": True,
                "chartView": {"enabled": False, "chartType": chart_type},
            },
        }
    }


class _TsQueryParams(QueryParams):
    """Query params for the time-series charts."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS["start_date"]
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS["end_date"]
    )


class _CrossSectionQueryParams(QueryParams):
    """Query params for the latest-release cross-section charts."""


class _ChartData(Data):
    """Base for every chart row: ignore unmodelled columns, keep Data's aliasing."""

    model_config = ConfigDict(extra="ignore")


def _make_base(kind: str, period_header: str) -> type[Data]:
    """Build the shared (stub + bookkeeping) fields for a chart's Data model."""
    if kind == "ts":
        stub_field = "date"
        stub_type: Any = dateType
        stub_cfg = {
            "x-widget_config": {
                "headerName": period_header,
                "chartDataType": "time",
            }
        }
        stub_desc = f"Observation period ({period_header.lower()})."
    else:
        stub_field = kind
        stub_type = str
        stub_cfg = {
            "x-widget_config": {
                "headerName": _STUB_HEADER.get(kind, kind.capitalize()),
                "chartDataType": "category",
            }
        }
        stub_desc = f"{_STUB_HEADER.get(kind, kind.capitalize())} the row applies to."

    fields: dict[str, Any] = {
        stub_field: (
            stub_type,
            Field(description=stub_desc, json_schema_extra=stub_cfg),
        ),
        "chart": (str, Field(description="Chart key.", json_schema_extra=_HIDE)),
        "chart_title": (
            str,
            Field(description="Full BLS chart title.", json_schema_extra=_HIDE),
        ),
        "table_id": (
            str,
            Field(description="Source table id.", json_schema_extra=_HIDE),
        ),
    }
    base = create_model(  # type: ignore[call-overload]
        f"_ChartBase_{kind}_{period_header}",
        __base__=_ChartData,
        **fields,
    )
    return base


def build_chart_pack(
    *,
    specs: dict[str, dict[str, Any]],
    fetch_and_parse: Callable[[str], dict[str, Any]],
    model_name_fn: Callable[[str], str],
    model_id_prefix: str,
    widget_name_prefix: str,
    subcategory: str,
    pack_label: str,
    period_header: str,
) -> dict[str, type[Fetcher]]:
    """Build ``{model_name: Fetcher}`` for every chart in ``specs``."""

    def _make_data_model(chart_key: str) -> type[Data]:
        spec = specs[chart_key]
        base = _make_base(spec["kind"], period_header)
        field_defs: dict[str, Any] = {}
        for field, label, role in spec["fields"]:
            field_defs[field] = (
                float | None,
                Field(
                    default=None,
                    description=f"{label}.",
                    json_schema_extra=_col(label, role),
                ),
            )
        model = create_model(  # type: ignore[call-overload]
            f"{model_id_prefix}_{chart_key.replace('-', '_')}_Data",
            __base__=base,
            **field_defs,
        )
        model.model_config["json_schema_extra"] = _widget(
            widget_name_prefix,
            spec["label"],
            spec["chart_type"],
            subcategory,
            pack_label,
        )
        return model

    def _make_fetcher(chart_key: str, data_class: type[Data]) -> type[Fetcher]:
        is_ts = specs[chart_key]["kind"] == "ts"
        query_model = _TsQueryParams if is_ts else _CrossSectionQueryParams

        class _Fetcher(Fetcher[_TsQueryParams | _CrossSectionQueryParams, list[Data]]):
            """BLS news-release chart per-table fetcher."""

            require_credentials = False
            query_params_type = query_model
            data_type = data_class

            @staticmethod
            def transform_query(
                params: dict[str, Any],
            ) -> _TsQueryParams | _CrossSectionQueryParams:
                """Validate and coerce the query."""
                return query_model(**params)

            @staticmethod
            def extract_data(
                query: QueryParams,
                credentials: dict[str, str] | None,
                **kwargs: Any,
            ) -> list[dict[str, Any]]:
                """Scrape and parse the bound chart's table, applying date bounds (ts)."""
                rows = fetch_and_parse(chart_key)["rows"]
                if is_ts:
                    start = getattr(query, "start_date", None)
                    end = getattr(query, "end_date", None)
                    if start is not None:
                        rows = [r for r in rows if r["date"] >= start]
                    if end is not None:
                        rows = [r for r in rows if r["date"] <= end]
                return rows

            @staticmethod
            def transform_data(
                query: QueryParams,
                data: list[dict[str, Any]],
                **kwargs: Any,
            ) -> list[Data]:
                """Coerce parsed rows into the chart-specific Data model."""
                if not data:
                    raise EmptyDataError(
                        f"No rows parsed from the BLS {pack_label} chart '{chart_key}'."
                    )
                return [data_class.model_validate(r) for r in data]

        _Fetcher.__name__ = f"{model_id_prefix}_{chart_key.replace('-', '_')}_Fetcher"
        _Fetcher.__qualname__ = _Fetcher.__name__
        return _Fetcher

    fetchers: dict[str, type[Fetcher]] = {}
    for key in specs:
        fetchers[model_name_fn(key)] = _make_fetcher(key, _make_data_model(key))
    return fetchers
