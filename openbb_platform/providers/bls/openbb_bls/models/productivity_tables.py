"""BLS Productivity supplemental tables."""

from __future__ import annotations

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field

from openbb_bls.utils.productivity_tables import (
    _DATASET_FILE,
    _DATASET_LABELS,
    PRODUCTIVITY_MEASURES,
    PRODUCTIVITY_SECTORS,
    PRODUCTIVITY_UNITS,
    fetch_xlsx,
    parse_dataset,
)

ProductivityDataset = Literal[
    "major-sectors-quarterly",
    "major-sectors-annual",
    "major-sectors-business-cycles",
    "total-economy-hours-employment",
]

_HIDE: dict[str, Any] = {"x-widget_config": {"hide": True}}
# Chart roles for the AgGrid table-to-chart view: a numeric ``value`` series
# plotted over the ``date`` time axis, grouped by the category dimensions the
# user narrows with the dropdowns.
_TIME: dict[str, Any] = {"x-widget_config": {"chartDataType": "time"}}
_CATEGORY: dict[str, Any] = {"x-widget_config": {"chartDataType": "category"}}
_SERIES: dict[str, Any] = {
    "x-widget_config": {"cellDataType": "number", "chartDataType": "series"}
}


class BlsProductivityTablesQueryParams(QueryParams):
    """BLS Productivity Tables Query Parameters."""

    __json_schema_extra__ = {
        "dataset": {
            "x-widget_config": {
                "options": [
                    {"label": f"{key} — {label}", "value": key}
                    for key, label in _DATASET_LABELS.items()
                ],
                "style": {"popupWidth": 950},
            }
        },
        "sector": {
            "x-widget_config": {
                "options": [{"label": v, "value": v} for v in PRODUCTIVITY_SECTORS],
                "style": {"popupWidth": 350},
            }
        },
        "measure": {
            "x-widget_config": {
                "options": [{"label": v, "value": v} for v in PRODUCTIVITY_MEASURES],
                "style": {"popupWidth": 350},
            }
        },
        "units": {
            "x-widget_config": {
                "options": [{"label": v, "value": v} for v in PRODUCTIVITY_UNITS],
                "style": {"popupWidth": 350},
            }
        },
    }

    dataset: ProductivityDataset = Field(
        default="major-sectors-quarterly",
        description="Productivity supplemental dataset to load.",
    )
    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS["start_date"],
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS["end_date"],
    )
    sector: str | None = Field(
        default="Nonfarm business sector",
        description="Sector to restrict the results. Defaults to the headline"
        " Nonfarm business sector; clear it to load every sector.",
    )
    measure: str | None = Field(
        default="Labor productivity",
        description="Measure to restrict the results. Defaults to Labor"
        " productivity; clear it to load every measure.",
    )
    units: str | None = Field(
        default="Index (2017=100)",
        description="Units to restrict the results. Defaults to the 2017=100"
        " index (one row per period); clear it to load every units basis. The"
        " source is long-form, so leaving every dimension open returns one row"
        " per sector / measure / units / period.",
    )


class BlsProductivityTablesData(Data):
    """One observation from a BLS Productivity supplemental dataset."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "BLS Productivity Tables",
                "$.description": (
                    "BLS Productivity prod2 supplemental tables — "
                    "quarterly / annual / business-cycle labor "
                    "productivity for major sectors, plus total-economy "
                    "hours and employment."
                ),
                "$.gridData": {"w": 40, "h": 20},
                "$.refetchInterval": False,
                "$.source": ["BLS"],
                "$.category": "Economy",
                "$.subCategory": "Productivity",
                # Table renders first; the chart is an opt-in toggle that plots
                # the value series over the time axis. Filter with the dropdowns
                # to isolate a single series (or group by a category column).
                "table": {
                    "showAll": True,
                    "enableCharts": True,
                    "chartView": {"enabled": False, "chartType": "line"},
                },
            }
        }
    )

    date: dateType | None = Field(
        default=None,
        description="First-of-period date the observation applies to.",
        json_schema_extra=_TIME,
    )
    period_kind: str = Field(
        description="Period kind for the row (quarter, annual, or business cycle).",
        json_schema_extra=_CATEGORY,
    )
    year: int | None = Field(
        default=None,
        description="Year reported in the source XLSX.",
        json_schema_extra=_HIDE,
    )
    quarter: int | str | None = Field(
        default=None,
        description="Quarter index reported in the source XLSX.",
        json_schema_extra=_HIDE,
    )
    sector: str | None = Field(
        default=None,
        description="BLS sector this row belongs to.",
        json_schema_extra=_CATEGORY,
    )
    basis: str | None = Field(
        default=None,
        description="Worker-counting basis used for the row.",
        json_schema_extra=_CATEGORY,
    )
    component: str | None = Field(
        default=None,
        description="Sub-sector component for the total-economy workbook.",
        json_schema_extra=_CATEGORY,
    )
    measure: str = Field(
        description="Productivity measure being reported.",
        json_schema_extra=_CATEGORY,
    )
    units: str = Field(
        description="Units the value is expressed in.",
        json_schema_extra=_CATEGORY,
    )
    value: float | None = Field(
        default=None,
        description="Numeric observation.",
        json_schema_extra=_SERIES,
    )
    value_string: str | None = Field(
        default=None,
        description="Raw cell text when the value isn't numeric.",
        json_schema_extra=_HIDE,
    )
    cycle_period: str | None = Field(
        default=None,
        description="Business-cycle period label as published by BLS.",
        json_schema_extra=_CATEGORY,
    )
    cycle_start_date: dateType | None = Field(
        default=None,
        description="First-of-quarter start date for the business-cycle period.",
        json_schema_extra=_HIDE,
    )
    cycle_end_date: dateType | None = Field(
        default=None,
        description="First-of-quarter end date for the business-cycle period.",
        json_schema_extra=_HIDE,
    )
    row_index: int = Field(
        description="Sequential parser order preserving the source layout.",
        json_schema_extra=_HIDE,
    )
    table_id: str = Field(
        description="Stable dataset identifier.",
        json_schema_extra=_HIDE,
    )
    table_title: str = Field(
        description="Human-readable dataset title.",
        json_schema_extra=_HIDE,
    )
    source_file: str = Field(
        description="Filename of the source XLSX on bls.gov.",
        json_schema_extra=_HIDE,
    )
    release_date: dateType | None = Field(
        default=None,
        description="Release date stamped in the workbook header.",
    )


class BlsProductivityTablesFetcher(
    Fetcher[BlsProductivityTablesQueryParams, list[BlsProductivityTablesData]]
):
    """BLS Productivity Tables Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> BlsProductivityTablesQueryParams:
        """Validate and coerce the query."""
        return BlsProductivityTablesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: BlsProductivityTablesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Download the chosen prod2 workbook and parse it long-form."""
        filename, _ = _DATASET_FILE[query.dataset]
        content = fetch_xlsx(filename)
        # Drop the "Level - not available" placeholder rows: they carry no value
        # and only inflate the table with apparent duplicates of each period.
        rows = [
            r
            for r in parse_dataset(content, query.dataset)
            if r.get("units") != "Level - not available"
        ]
        sector_filter = query.sector.strip().lower() if query.sector else None
        measure_filter = query.measure.strip().lower() if query.measure else None
        units_filter = query.units.strip().lower() if query.units else None
        start, end = query.start_date, query.end_date
        if (
            sector_filter is None
            and measure_filter is None
            and units_filter is None
            and start is None
            and end is None
        ):
            return rows
        out: list[dict[str, Any]] = []
        for r in rows:
            if (
                sector_filter is not None
                and (r.get("sector") or "").lower() != sector_filter
            ):
                continue
            if (
                measure_filter is not None
                and (r.get("measure") or "").lower() != measure_filter
            ):
                continue
            if (
                units_filter is not None
                and (r.get("units") or "").lower() != units_filter
            ):
                continue
            if start is not None or end is not None:
                row_date = r.get("date")
                if row_date is None:
                    continue
                if start is not None and row_date < start:
                    continue
                if end is not None and row_date > end:
                    continue
            out.append(r)
        return out

    @staticmethod
    def transform_data(
        query: BlsProductivityTablesQueryParams,
        data: list[dict[str, Any]],
        **kwargs: Any,
    ) -> list[BlsProductivityTablesData]:
        """Coerce parsed rows into ``BlsProductivityTablesData``."""
        if not data:
            raise EmptyDataError(
                f"No rows matched the productivity tables query "
                f"(dataset={query.dataset!r})."
            )
        return [BlsProductivityTablesData.model_validate(r) for r in data]
