"""BLS CES (Current Employment Statistics) analytical tables."""

from __future__ import annotations

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field

from openbb_bls.utils.ces_analytical_tables import (
    CES_STEMS,
    fetch_table_xlsx,
    parse_ces,
)

_HIDE: dict[str, Any] = {"x-widget_config": {"hide": True}}


def _hdr(name: str) -> dict[str, Any]:
    """Override the column header name."""
    return {"x-widget_config": {"headerName": name}}


def _num(name: str) -> dict[str, Any]:
    """Numeric (level) column config."""
    return {"x-widget_config": {"headerName": name, "cellDataType": "number"}}


def _change(name: str) -> dict[str, Any]:
    """Signed-change column config: numeric + greenRed render."""
    return {
        "x-widget_config": {
            "headerName": name,
            "cellDataType": "number",
            "renderFn": "greenRed",
        }
    }


def _pct(name: str) -> dict[str, Any]:
    """Percent column config: numeric + percent formatter + greenRed render."""
    return {
        "x-widget_config": {
            "headerName": name,
            "cellDataType": "number",
            "formatterFn": "percent",
            "renderFn": "greenRed",
        }
    }


def _grid(name: str, description: str) -> dict[str, Any]:
    """Build the table-level widget config block."""
    return {
        "x-widget_config": {
            "$.name": name,
            "$.description": description,
            "$.gridData": {"w": 40, "h": 27},
            "$.refetchInterval": False,
            "$.source": ["BLS"],
            "$.category": "Economy",
            "$.subCategory": "Employment Situation",
        }
    }


class _CesQueryParams(QueryParams):
    """Shared (empty) query params — the analytical tables track the latest release."""


class _CesBaseData(Data):
    """Fields shared by every CES analytical-table response."""

    model_config = ConfigDict(extra="ignore")

    reference_date: dateType | None = Field(
        default=None,
        description="Reference month the release covers (first of month).",
        json_schema_extra=_hdr("Reference Month"),
    )
    label: str | None = Field(
        default=None,
        description="BLS industry title.",
        json_schema_extra=_hdr("Industry"),
    )
    row_index: int = Field(
        default=0,
        description="Sequential ordering index preserving BLS hierarchy.",
        json_schema_extra=_HIDE,
    )
    table_id: str = Field(
        description="Stable identifier for the source table.",
        json_schema_extra=_HIDE,
    )
    table_title: str = Field(
        description="Full BLS table title.",
        json_schema_extra=_HIDE,
    )


class BlsCesTable1Data(_CesBaseData):
    """CES Table 1 — employment, normal seasonal movement, OTM change, significance."""

    model_config = ConfigDict(
        extra="ignore",
        json_schema_extra=_grid(
            "BLS CES Table 1 — Employment Changes & Significance",
            "Employment: normal seasonal movements, over-the-month changes, and "
            "tests of significance (in thousands).",
        ),
    )

    indent_level: int | None = Field(
        default=None, description="Hierarchy depth.", json_schema_extra=_hdr("Level")
    )
    normal_seasonal_movement: float | None = Field(
        default=None,
        description="Normal (expected) NSA seasonal movement, in thousands.",
        json_schema_extra=_change("Normal Seasonal Movement (NSA)"),
    )
    change_nsa: float | None = Field(
        default=None,
        description="Actual NSA over-the-month change, in thousands.",
        json_schema_extra=_change("OTM Change (NSA)"),
    )
    change_sa: float | None = Field(
        default=None,
        description="Seasonally adjusted over-the-month change, in thousands.",
        json_schema_extra=_change("OTM Change (SA)"),
    )
    change_sa_significant: bool | None = Field(
        default=None,
        description="Whether the SA change passed the test of significance.",
        json_schema_extra=_hdr("SA Change Significant"),
    )
    minimum_significant_change: float | None = Field(
        default=None,
        description="Minimum SA change required for statistical significance.",
        json_schema_extra=_num("Minimum Significant Change"),
    )


class BlsCesTable2Data(_CesBaseData):
    """CES Table 2 — detailed industries ranked by over-the-month change."""

    model_config = ConfigDict(
        extra="ignore",
        json_schema_extra=_grid(
            "BLS CES Table 2 — Ranked Industry OTM Changes",
            "Detailed industry employment ranked by over-the-month changes, tests "
            "of significance, and prior 3-month average, seasonally adjusted.",
        ),
    )

    rank: str | None = Field(
        default=None,
        description="Rank by over-the-month change (ties share a rank).",
        json_schema_extra=_hdr("Rank"),
    )
    naics_code: str | None = Field(
        default=None,
        description="NAICS industry code.",
        json_schema_extra=_hdr("NAICS"),
    )
    change_sa: float | None = Field(
        default=None,
        description="Seasonally adjusted over-the-month change, in thousands.",
        json_schema_extra=_change("OTM Change (SA)"),
    )
    change_sa_significant: bool | None = Field(
        default=None,
        description="Whether the SA change passed the test of significance.",
        json_schema_extra=_hdr("Significant"),
    )
    minimum_significant_change: float | None = Field(
        default=None,
        description="Minimum SA change required for statistical significance.",
        json_schema_extra=_num("Minimum Significant Change"),
    )
    prior_3month_average: float | None = Field(
        default=None,
        description="Prior 3-month average change, in thousands.",
        json_schema_extra=_change("Prior 3-Month Average"),
    )


class BlsCesTable3AData(_CesBaseData):
    """CES Table 3A — SA employment changes over 1/2/3-month and 3/6/12-month spans."""

    model_config = ConfigDict(
        extra="ignore",
        json_schema_extra=_grid(
            "BLS CES Table 3A — Employment Changes & Significance (SA)",
            "Employment changes and tests of significance, seasonally adjusted "
            "(in thousands).",
        ),
    )

    indent_level: int | None = Field(
        default=None, description="Hierarchy depth.", json_schema_extra=_hdr("Level")
    )
    otm_change_latest: float | None = Field(
        default=None,
        description="Over-the-month change for the latest month, in thousands.",
        json_schema_extra=_change("OTM Change (Latest)"),
    )
    otm_change_latest_significant: bool | None = Field(
        default=None,
        description="Whether the latest OTM change is significant.",
        json_schema_extra=_HIDE,
    )
    otm_change_prior_1: float | None = Field(
        default=None,
        description="Over-the-month change one month prior (revised), in thousands.",
        json_schema_extra=_change("OTM Change (1 Mo Prior)"),
    )
    otm_change_prior_1_significant: bool | None = Field(
        default=None,
        description="Whether the prior-month OTM change is significant.",
        json_schema_extra=_HIDE,
    )
    otm_change_prior_2: float | None = Field(
        default=None,
        description="Over-the-month change two months prior (revised), in thousands.",
        json_schema_extra=_change("OTM Change (2 Mo Prior)"),
    )
    otm_change_prior_2_significant: bool | None = Field(
        default=None,
        description="Whether the two-months-prior OTM change is significant.",
        json_schema_extra=_HIDE,
    )
    current_3month_change: float | None = Field(
        default=None,
        description="Current 3-month change, in thousands.",
        json_schema_extra=_change("Current 3-Month Change"),
    )
    current_3month_change_significant: bool | None = Field(
        default=None,
        description="Whether the current 3-month change is significant.",
        json_schema_extra=_HIDE,
    )
    current_6month_change: float | None = Field(
        default=None,
        description="Current 6-month change, in thousands.",
        json_schema_extra=_change("Current 6-Month Change"),
    )
    current_6month_change_significant: bool | None = Field(
        default=None,
        description="Whether the current 6-month change is significant.",
        json_schema_extra=_HIDE,
    )
    current_12month_change: float | None = Field(
        default=None,
        description="Current 12-month change, in thousands.",
        json_schema_extra=_change("Current 12-Month Change"),
    )
    current_12month_change_significant: bool | None = Field(
        default=None,
        description="Whether the current 12-month change is significant.",
        json_schema_extra=_HIDE,
    )


class BlsCesTable3BData(_CesBaseData):
    """CES Table 3B — over-the-month employment changes vs. recent averages (SA)."""

    model_config = ConfigDict(
        extra="ignore",
        json_schema_extra=_grid(
            "BLS CES Table 3B — OTM Changes vs Recent Averages (SA)",
            "Over-the-month employment changes compared with recent averages, "
            "seasonally adjusted (in thousands).",
        ),
    )

    indent_level: int | None = Field(
        default=None, description="Hierarchy depth.", json_schema_extra=_hdr("Level")
    )
    otm_change_latest: float | None = Field(
        default=None,
        description="Over-the-month change for the latest month, in thousands.",
        json_schema_extra=_change("OTM Change (Latest)"),
    )
    otm_change_prior_1: float | None = Field(
        default=None,
        description="Over-the-month change one month prior, in thousands.",
        json_schema_extra=_change("OTM Change (1 Mo Prior)"),
    )
    otm_change_prior_2: float | None = Field(
        default=None,
        description="Over-the-month change two months prior, in thousands.",
        json_schema_extra=_change("OTM Change (2 Mo Prior)"),
    )
    prior_3month_average: float | None = Field(
        default=None,
        description="Prior 3-month average change, in thousands.",
        json_schema_extra=_change("Prior 3-Month Average"),
    )
    prior_6month_average: float | None = Field(
        default=None,
        description="Prior 6-month average change, in thousands.",
        json_schema_extra=_change("Prior 6-Month Average"),
    )
    prior_12month_average: float | None = Field(
        default=None,
        description="Prior 12-month average change, in thousands.",
        json_schema_extra=_change("Prior 12-Month Average"),
    )


class BlsCesTable4Data(_CesBaseData):
    """CES Table 4 — over-the-year employment changes and significance (SA)."""

    model_config = ConfigDict(
        extra="ignore",
        json_schema_extra=_grid(
            "BLS CES Table 4 — Over-the-Year Changes & Significance (SA)",
            "Over-the-year employment changes and tests of significance, "
            "seasonally adjusted (in thousands).",
        ),
    )

    indent_level: int | None = Field(
        default=None, description="Hierarchy depth.", json_schema_extra=_hdr("Level")
    )
    oty_change_number: float | None = Field(
        default=None,
        description="Over-the-year change, in thousands.",
        json_schema_extra=_change("OTY Change (Number)"),
    )
    oty_change_number_significant: bool | None = Field(
        default=None,
        description="Whether the OTY change passed the test of significance.",
        json_schema_extra=_hdr("OTY Change Significant"),
    )
    oty_change_percent: float | None = Field(
        default=None,
        description="Over-the-year percent change.",
        json_schema_extra=_pct("OTY Change (Percent)"),
    )
    minimum_significant_change: float | None = Field(
        default=None,
        description="Minimum change required for statistical significance.",
        json_schema_extra=_num("Minimum Significant Change"),
    )


class BlsCesTable5Data(_CesBaseData):
    """CES Table 5 — average weekly hours and average hourly earnings (NSA + SA)."""

    model_config = ConfigDict(
        extra="ignore",
        json_schema_extra=_grid(
            "BLS CES Table 5 — Hours & Earnings Changes & Significance",
            "Average weekly hours and average hourly earnings of all employees: "
            "normal seasonal movements, over-the-month changes, and tests of "
            "significance.",
        ),
    )

    measure: str | None = Field(
        default=None,
        description="Which series block the row belongs to (hours or earnings).",
        json_schema_extra=_hdr("Measure"),
    )
    normal_seasonal_movement: float | None = Field(
        default=None,
        description="Normal (expected) NSA seasonal movement.",
        json_schema_extra=_change("Normal Seasonal Movement (NSA)"),
    )
    change_nsa: float | None = Field(
        default=None,
        description="Actual NSA over-the-month change.",
        json_schema_extra=_change("OTM Change (NSA)"),
    )
    change_sa: float | None = Field(
        default=None,
        description="Seasonally adjusted over-the-month change.",
        json_schema_extra=_change("OTM Change (SA)"),
    )
    change_sa_significant: bool | None = Field(
        default=None,
        description="Whether the SA change passed the test of significance.",
        json_schema_extra=_hdr("SA Change Significant"),
    )
    minimum_significant_change: float | None = Field(
        default=None,
        description="Minimum SA change required for statistical significance.",
        json_schema_extra=_num("Minimum Significant Change"),
    )


class BlsCesTable6Data(_CesBaseData):
    """CES Table 6 — aggregate weekly hours and payroll changes (SA)."""

    model_config = ConfigDict(
        extra="ignore",
        json_schema_extra=_grid(
            "BLS CES Table 6 — Aggregate Weekly Hours & Payrolls (SA)",
            "Over-the-month and over-the-year changes in aggregate weekly hours and "
            "payrolls of all employees, seasonally adjusted (in thousands).",
        ),
    )

    measure: str | None = Field(
        default=None,
        description="Which series block the row belongs to (hours or payrolls).",
        json_schema_extra=_hdr("Measure"),
    )
    aggregate_value: float | None = Field(
        default=None,
        description="Aggregate level — weekly hours or weekly payrolls per the measure.",
        json_schema_extra=_num("Aggregate"),
    )
    otm_change_number: float | None = Field(
        default=None,
        description="Over-the-month change in aggregate weekly hours, in thousands.",
        json_schema_extra=_change("OTM Change (Number)"),
    )
    otm_change_percent: float | None = Field(
        default=None,
        description="Over-the-month percent change.",
        json_schema_extra=_pct("OTM Change (Percent)"),
    )
    oty_change_number: float | None = Field(
        default=None,
        description="Over-the-year change in aggregate weekly hours, in thousands.",
        json_schema_extra=_change("OTY Change (Number)"),
    )
    oty_change_percent: float | None = Field(
        default=None,
        description="Over-the-year percent change.",
        json_schema_extra=_pct("OTY Change (Percent)"),
    )


class BlsCesTable7Data(_CesBaseData):
    """CES Table 7 — most recent employment peak / trough and changes (SA)."""

    model_config = ConfigDict(
        extra="ignore",
        json_schema_extra=_grid(
            "BLS CES Table 7 — Employment Peak / Trough (SA)",
            "Most recent industry-specific employment peak and trough, and changes "
            "from peak and trough to current employment, seasonally adjusted "
            "(in thousands).",
        ),
    )

    indent_level: int | None = Field(
        default=None, description="Hierarchy depth.", json_schema_extra=_hdr("Level")
    )
    current_employment: float | None = Field(
        default=None,
        description="Current employment at the reference month, in thousands.",
        json_schema_extra=_num("Current Employment"),
    )
    peak_date: dateType | None = Field(
        default=None,
        description="Month of the most recent employment peak.",
        json_schema_extra=_hdr("Peak Month"),
    )
    peak_employment: float | None = Field(
        default=None,
        description="Employment at the most recent peak, in thousands.",
        json_schema_extra=_num("Peak Employment"),
    )
    trough_date: dateType | None = Field(
        default=None,
        description="Month of the most recent employment trough.",
        json_schema_extra=_hdr("Trough Month"),
    )
    trough_employment: float | None = Field(
        default=None,
        description="Employment at the most recent trough, in thousands.",
        json_schema_extra=_num("Trough Employment"),
    )
    change_from_peak: float | None = Field(
        default=None,
        description="Change from peak to current employment, in thousands.",
        json_schema_extra=_change("Change from Peak"),
    )
    change_from_trough: float | None = Field(
        default=None,
        description="Change from trough to current employment, in thousands.",
        json_schema_extra=_change("Change from Trough"),
    )


class BlsCesConfidenceIntervalsQueryParams(QueryParams):
    """Query params for the CES confidence-interval tables (A-C2)."""

    __json_schema_extra__ = {
        "ci_table": {
            "x-widget_config": {
                "options": [
                    {"label": "All tables", "value": None},
                    {"label": "A — Employment", "value": "A"},
                    {"label": "B1 — Hours & Earnings (All employees)", "value": "B1"},
                    {
                        "label": "B2 — Hours & Earnings (Production employees)",
                        "value": "B2",
                    },
                    {"label": "C1 — Overtime (All employees)", "value": "C1"},
                    {"label": "C2 — Overtime (Production employees)", "value": "C2"},
                ]
            }
        },
    }

    ci_table: Literal["A", "B1", "B2", "C1", "C2"] | None = Field(
        default=None,
        description="Restrict results to one confidence-interval table; None returns all.",
    )


class BlsCesConfidenceIntervalsData(_CesBaseData):
    """CES confidence-interval row — 90% CI widths by industry and horizon."""

    model_config = ConfigDict(
        extra="ignore",
        json_schema_extra=_grid(
            "BLS CES Confidence Intervals (Tables A-C2)",
            "90 percent confidence intervals for 1-, 3-, 6-, and 12-month changes "
            "in employment, hours, overtime hours, and earnings.",
        ),
    )

    ci_table: str | None = Field(
        default=None,
        description="Confidence-interval sub-table (A, B1, B2, C1, C2).",
        json_schema_extra=_hdr("CI Table"),
    )
    measure: str | None = Field(
        default=None,
        description="Measure the interval applies to.",
        json_schema_extra=_hdr("Measure"),
    )
    employee_group: str | None = Field(
        default=None,
        description="Employee coverage (all vs. production employees).",
        json_schema_extra=_hdr("Employee Group"),
    )
    indent_level: int | None = Field(
        default=None, description="Hierarchy depth.", json_schema_extra=_hdr("Level")
    )
    ci_1month_first: float | None = Field(
        default=None,
        description="90% CI for the 1-month change, first release.",
        json_schema_extra=_num("1M CI (First Release)"),
    )
    ci_1month_second: float | None = Field(
        default=None,
        description="90% CI for the 1-month change, second release (Table A only).",
        json_schema_extra=_num("1M CI (Second Release)"),
    )
    ci_1month_third: float | None = Field(
        default=None,
        description="90% CI for the 1-month change, third release (Table A only).",
        json_schema_extra=_num("1M CI (Third Release)"),
    )
    ci_3month: float | None = Field(
        default=None,
        description="90% CI for the 3-month change.",
        json_schema_extra=_num("3M CI"),
    )
    ci_6month: float | None = Field(
        default=None,
        description="90% CI for the 6-month change.",
        json_schema_extra=_num("6M CI"),
    )
    ci_12month: float | None = Field(
        default=None,
        description="90% CI for the 12-month change.",
        json_schema_extra=_num("12M CI"),
    )


def _make_fetcher(key: str, data_class: type[Data]) -> type[Fetcher]:
    """Build a Fetcher bound to one CES analytical-table key and Data model."""

    class _Fetcher(Fetcher[_CesQueryParams, list[Data]]):
        """BLS CES analytical-table per-table fetcher."""

        require_credentials = False
        data_type = data_class

        @staticmethod
        def transform_query(params: dict[str, Any]) -> _CesQueryParams:
            """Validate and coerce the query."""
            return _CesQueryParams(**params)

        @staticmethod
        def extract_data(
            query: _CesQueryParams,
            credentials: dict[str, str] | None,
            **kwargs: Any,
        ) -> dict[str, Any]:
            """Download the workbook and parse the bound table."""
            content = fetch_table_xlsx(CES_STEMS[key])
            return parse_ces(content, key)

        @staticmethod
        def transform_data(
            query: _CesQueryParams,
            data: dict[str, Any],
            **kwargs: Any,
        ) -> list[Data]:
            """Coerce parsed rows into the table-specific Data model."""
            rows = data.get("rows", [])
            if not rows:
                raise EmptyDataError(
                    f"No rows parsed from CES analytical table "
                    f"'{data.get('table_id', key)}'."
                )
            return [data_class.model_validate(r) for r in rows]

    _Fetcher.__name__ = f"BlsCes{key.upper()}Fetcher"
    _Fetcher.__qualname__ = _Fetcher.__name__
    return _Fetcher


BlsCesTable1Fetcher = _make_fetcher("t1", BlsCesTable1Data)
BlsCesTable2Fetcher = _make_fetcher("t2", BlsCesTable2Data)
BlsCesTable3AFetcher = _make_fetcher("t3a", BlsCesTable3AData)
BlsCesTable3BFetcher = _make_fetcher("t3b", BlsCesTable3BData)
BlsCesTable4Fetcher = _make_fetcher("t4", BlsCesTable4Data)
BlsCesTable5Fetcher = _make_fetcher("t5", BlsCesTable5Data)
BlsCesTable6Fetcher = _make_fetcher("t6", BlsCesTable6Data)
BlsCesTable7Fetcher = _make_fetcher("t7", BlsCesTable7Data)


class BlsCesConfidenceIntervalsFetcher(
    Fetcher[BlsCesConfidenceIntervalsQueryParams, list[BlsCesConfidenceIntervalsData]]
):
    """BLS CES Confidence Intervals (Tables A-C2) Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> BlsCesConfidenceIntervalsQueryParams:
        """Validate and coerce the query."""
        return BlsCesConfidenceIntervalsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: BlsCesConfidenceIntervalsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Download and parse the confidence-interval workbook, applying any filter."""
        content = fetch_table_xlsx(CES_STEMS["ci"])
        parsed = parse_ces(content, "ci")
        if query.ci_table is not None:
            parsed["rows"] = [
                r for r in parsed["rows"] if r.get("ci_table") == query.ci_table
            ]
        return parsed

    @staticmethod
    def transform_data(
        query: BlsCesConfidenceIntervalsQueryParams,
        data: dict[str, Any],
        **kwargs: Any,
    ) -> list[BlsCesConfidenceIntervalsData]:
        """Coerce parsed rows into the confidence-interval Data model."""
        rows = data.get("rows", [])
        if not rows:
            raise EmptyDataError(
                "No rows parsed from the CES confidence-interval tables "
                f"(ci_table={query.ci_table!r})."
            )
        return [BlsCesConfidenceIntervalsData.model_validate(r) for r in rows]
