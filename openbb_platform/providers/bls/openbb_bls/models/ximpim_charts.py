"""BLS U.S. Import/Export Price Index news-release chart data (per-chart tables)."""

from __future__ import annotations

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, create_model

from openbb_bls.utils.ximpim_charts import (
    CHART_FIELDS,
    CHART_LABELS,
    fetch_and_parse,
)

_HIDE: dict[str, Any] = {"x-widget_config": {"hide": True}}

_DATE_CONFIG: dict[str, Any] = {
    "x-widget_config": {"headerName": "Month", "chartDataType": "time"}
}


def _series(label: str) -> dict[str, Any]:
    """Percent series column: numeric + percent + greenRed + chart series role."""
    return {
        "x-widget_config": {
            "headerName": label,
            "cellDataType": "number",
            "formatterFn": "percent",
            "renderFn": "greenRed",
            "chartDataType": "series",
        }
    }


def _widget(name: str, description: str) -> dict[str, Any]:
    """Table-first widget config that exposes a line-chart toggle over the time axis."""
    return {
        "x-widget_config": {
            "$.name": name,
            "$.description": description,
            "$.gridData": {"w": 40, "h": 20},
            "$.refetchInterval": False,
            "$.source": ["BLS"],
            "$.category": "Economy",
            "$.subCategory": "Import/Export Prices",
            # Table renders first; the chart is an opt-in toggle (one line per
            # series over the monthly time axis).
            "table": {
                "showAll": True,
                "enableCharts": True,
                "chartView": {"enabled": False, "chartType": "line"},
            },
        }
    }


class _XimpimChartQueryParams(QueryParams):
    """Shared query params for the import-export chart tables."""

    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS["start_date"],
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS["end_date"],
    )


class _XimpimChartBaseData(Data):
    """Fields shared by every import-export chart table row."""

    model_config = ConfigDict(extra="ignore")

    date: dateType = Field(
        description="Observation month (first of month).",
        json_schema_extra=_DATE_CONFIG,
    )
    chart: str = Field(
        description="Chart key the row belongs to.",
        json_schema_extra=_HIDE,
    )
    chart_title: str = Field(
        description="Full BLS chart title.",
        json_schema_extra=_HIDE,
    )
    table_id: str = Field(
        description="Source data-table identifier.",
        json_schema_extra=_HIDE,
    )


def _make_data_model(chart_key: str) -> type[Data]:
    """Build a typed Data model declaring one percent column per chart series."""
    field_defs: dict[str, Any] = {}
    for field, label in CHART_FIELDS[chart_key]:
        field_defs[field] = (
            float | None,
            Field(
                default=None,
                description=f"12-month percent change — {label}.",
                json_schema_extra=_series(label),
            ),
        )
    label = CHART_LABELS[chart_key]
    model = create_model(  # type: ignore[call-overload]
        f"BlsXimpimChart_{chart_key.replace('-', '_')}_Data",
        __base__=_XimpimChartBaseData,
        **field_defs,
    )
    model.model_config["json_schema_extra"] = _widget(
        f"BLS {label} (12-Month % Change)",
        f"{label}, 12-month percent change, from the BLS news-release chart package.",
    )
    return model


def _make_fetcher(chart_key: str, data_class: type[Data]) -> type[Fetcher]:
    """Build a Fetcher bound to one import-export chart and its typed Data model."""

    class _Fetcher(Fetcher[_XimpimChartQueryParams, list[Data]]):
        """BLS import-export chart per-table fetcher."""

        require_credentials = False
        data_type = data_class

        @staticmethod
        def transform_query(params: dict[str, Any]) -> _XimpimChartQueryParams:
            """Validate and coerce the query."""
            return _XimpimChartQueryParams(**params)

        @staticmethod
        def extract_data(
            query: _XimpimChartQueryParams,
            credentials: dict[str, str] | None,
            **kwargs: Any,
        ) -> list[dict[str, Any]]:
            """Scrape and parse the bound chart's table, applying date bounds."""
            rows = fetch_and_parse(chart_key)["rows"]
            if query.start_date is not None:
                rows = [r for r in rows if r["date"] >= query.start_date]
            if query.end_date is not None:
                rows = [r for r in rows if r["date"] <= query.end_date]
            return rows

        @staticmethod
        def transform_data(
            query: _XimpimChartQueryParams,
            data: list[dict[str, Any]],
            **kwargs: Any,
        ) -> list[Data]:
            """Coerce parsed rows into the chart-specific Data model."""
            if not data:
                raise EmptyDataError(
                    f"No rows parsed from the BLS import-export chart '{chart_key}'."
                )
            return [data_class.model_validate(r) for r in data]

    _Fetcher.__name__ = f"BlsXimpimChart_{chart_key.replace('-', '_')}_Fetcher"
    _Fetcher.__qualname__ = _Fetcher.__name__
    return _Fetcher


BlsXimpimImportExportData = _make_data_model("import-export")
BlsXimpimImportsByCategoryData = _make_data_model("imports-by-category")
BlsXimpimExportsByCategoryData = _make_data_model("exports-by-category")
BlsXimpimImportsByOriginData = _make_data_model("imports-by-origin")
BlsXimpimExportsByGrainsData = _make_data_model("exports-by-grains")
BlsXimpimAirFaresData = _make_data_model("air-passenger-fares")

BlsXimpimImportExportFetcher = _make_fetcher("import-export", BlsXimpimImportExportData)
BlsXimpimImportsByCategoryFetcher = _make_fetcher(
    "imports-by-category", BlsXimpimImportsByCategoryData
)
BlsXimpimExportsByCategoryFetcher = _make_fetcher(
    "exports-by-category", BlsXimpimExportsByCategoryData
)
BlsXimpimImportsByOriginFetcher = _make_fetcher(
    "imports-by-origin", BlsXimpimImportsByOriginData
)
BlsXimpimExportsByGrainsFetcher = _make_fetcher(
    "exports-by-grains", BlsXimpimExportsByGrainsData
)
BlsXimpimAirFaresFetcher = _make_fetcher("air-passenger-fares", BlsXimpimAirFaresData)
