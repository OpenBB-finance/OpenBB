"""BLS Employment Situation news-release chart data (per-chart tables)."""

from __future__ import annotations

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, create_model

from openbb_bls.utils.empsit_charts import CHART_SPECS, fetch_and_parse

_HIDE: dict[str, Any] = {"x-widget_config": {"hide": True}}
_TIME: dict[str, Any] = {
    "x-widget_config": {"headerName": "Month", "chartDataType": "time"}
}
_INDUSTRY: dict[str, Any] = {
    "x-widget_config": {"headerName": "Industry", "chartDataType": "category"}
}


def empsit_model_name(chart_key: str) -> str:
    """Stable widget/model name for one Employment Situation chart key."""
    return "BlsEmpsit" + "".join(p.capitalize() for p in chart_key.split("-"))


def _col(label: str, role: str) -> dict[str, Any]:
    """Build a value column's widget config from its role.

    ``exclude`` keeps the column in the table but drops it from the chart —
    used for grand-total aggregates (e.g. Total nonfarm) that otherwise dwarf
    the individual series on a shared linear axis.
    """
    cfg: dict[str, Any] = {"headerName": label, "cellDataType": "number"}
    if role == "exclude":
        cfg["chartDataType"] = "excluded"
        return {"x-widget_config": cfg}
    cfg["chartDataType"] = "series"
    if role == "change":
        cfg["renderFn"] = "greenRed"
    elif role == "pct":
        cfg["formatterFn"] = "percent"
        cfg["renderFn"] = "greenRed"
    return {"x-widget_config": cfg}


def _widget(label: str, chart_type: str) -> dict[str, Any]:
    """Table-first widget config exposing a chart toggle of the given type."""
    return {
        "x-widget_config": {
            "$.name": f"BLS Employment Situation — {label}",
            "$.description": (
                f"{label}, from the BLS Employment Situation news-release chart package."
            ),
            "$.gridData": {"w": 40, "h": 20},
            "$.refetchInterval": False,
            "$.source": ["BLS"],
            "$.category": "Economy",
            "$.subCategory": "Employment Situation",
            # Table renders first; the chart is an opt-in toggle.
            "table": {
                "showAll": True,
                "enableCharts": True,
                "chartView": {"enabled": False, "chartType": chart_type},
            },
        }
    }


class _EmpsitTsQueryParams(QueryParams):
    """Query params for the monthly time-series charts."""

    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS["start_date"],
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS["end_date"],
    )


class _EmpsitIndustryQueryParams(QueryParams):
    """Query params for the latest-release industry cross-section charts."""


class _EmpsitTsBaseData(Data):
    """Shared fields for a monthly time-series chart row."""

    model_config = ConfigDict(extra="ignore")

    date: dateType = Field(
        description="Observation month (first of month).",
        json_schema_extra=_TIME,
    )
    chart: str = Field(description="Chart key.", json_schema_extra=_HIDE)
    chart_title: str = Field(
        description="Full BLS chart title.", json_schema_extra=_HIDE
    )
    table_id: str = Field(description="Source table id.", json_schema_extra=_HIDE)


class _EmpsitIndustryBaseData(Data):
    """Shared fields for a latest-release industry cross-section row."""

    model_config = ConfigDict(extra="ignore")

    industry: str = Field(
        description="Industry / supersector.",
        json_schema_extra=_INDUSTRY,
    )
    chart: str = Field(description="Chart key.", json_schema_extra=_HIDE)
    chart_title: str = Field(
        description="Full BLS chart title.", json_schema_extra=_HIDE
    )
    table_id: str = Field(description="Source table id.", json_schema_extra=_HIDE)


def _make_data_model(chart_key: str) -> type[Data]:
    """Build a typed Data model declaring one column per chart series."""
    spec = CHART_SPECS[chart_key]
    base = _EmpsitTsBaseData if spec["kind"] == "ts" else _EmpsitIndustryBaseData
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
        f"BlsEmpsit_{chart_key.replace('-', '_')}_Data",
        __base__=base,
        **field_defs,
    )
    model.model_config["json_schema_extra"] = _widget(spec["label"], spec["chart_type"])
    return model


def _make_fetcher(chart_key: str, data_class: type[Data]) -> type[Fetcher]:
    """Build a Fetcher bound to one Employment Situation chart and its Data model."""
    kind = CHART_SPECS[chart_key]["kind"]
    query_model = _EmpsitTsQueryParams if kind == "ts" else _EmpsitIndustryQueryParams

    class _Fetcher(
        Fetcher[_EmpsitTsQueryParams | _EmpsitIndustryQueryParams, list[Data]]
    ):
        """BLS Employment Situation chart per-table fetcher."""

        require_credentials = False
        query_params_type = query_model
        data_type = data_class

        @staticmethod
        def transform_query(
            params: dict[str, Any],
        ) -> _EmpsitTsQueryParams | _EmpsitIndustryQueryParams:
            """Validate and coerce the query."""
            return query_model(**params)

        @staticmethod
        def extract_data(
            query: QueryParams,
            credentials: dict[str, str] | None,
            **kwargs: Any,
        ) -> list[dict[str, Any]]:
            """Scrape and parse the bound chart's table, applying date bounds (ts only)."""
            rows = fetch_and_parse(chart_key)["rows"]
            if kind == "ts":
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
                    f"No rows parsed from the BLS Employment Situation chart "
                    f"'{chart_key}'."
                )
            return [data_class.model_validate(r) for r in data]

    _Fetcher.__name__ = f"BlsEmpsit_{chart_key.replace('-', '_')}_Fetcher"
    _Fetcher.__qualname__ = _Fetcher.__name__
    return _Fetcher


EMPSIT_CHART_FETCHERS: dict[str, type[Fetcher]] = {}
for _key in CHART_SPECS:
    _data_class = _make_data_model(_key)
    EMPSIT_CHART_FETCHERS[empsit_model_name(_key)] = _make_fetcher(_key, _data_class)
