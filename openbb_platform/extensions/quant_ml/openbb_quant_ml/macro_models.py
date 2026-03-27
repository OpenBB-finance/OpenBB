"""Pydantic models for Macro tab endpoints."""

from __future__ import annotations

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

MacroStatus = Literal["ok", "insufficient_data", "not_found", "error"]
MacroFreq = Literal["native", "D", "W", "M", "Q"]
MacroFill = Literal["ffill", "interpolate", "none"]
MacroViewMode = Literal["explorer", "compare", "relationship", "release", "report"]
MacroNormalizeMode = Literal["raw", "index100", "zscore", "yoy", "percentile_5y"]


class MacroDataPoint(BaseModel):
    """Timeseries point."""

    date: str
    value: float


class MacroSeriesMeta(BaseModel):
    """Common metadata for macro series responses."""

    key: str
    title: str | None = None
    units: str | None = None
    frequency: str | None = None
    source: str
    transform: str = "level"
    lag_applied: str | None = None
    warning: str | None = None


class MacroSeriesStats(BaseModel):
    """Summary statistics block."""

    last: float | None = None
    change_1m: float | None = None
    change_3m: float | None = None
    z: float | None = None
    percentile_5y: float | None = None


class MacroSeriesResponse(BaseModel):
    """Single series response."""

    meta: MacroSeriesMeta
    data: list[MacroDataPoint] = Field(default_factory=list)
    stats: MacroSeriesStats = Field(default_factory=MacroSeriesStats)
    status: MacroStatus = "ok"
    message: str | None = None


class MacroSeriesMultiResponse(BaseModel):
    """Multi-series response for /series?ids=... queries."""

    status: MacroStatus = "ok"
    message: str | None = None
    series: dict[str, MacroSeriesResponse] = Field(default_factory=dict)


class MacroPresetSeries(BaseModel):
    """Preset series payload for multi-axis chart rendering."""

    id: str
    axis: Literal["left", "right", "bottom"] = "left"
    meta: MacroSeriesMeta
    data: list[MacroDataPoint] = Field(default_factory=list)
    stats: MacroSeriesStats = Field(default_factory=MacroSeriesStats)


class MacroEventItem(BaseModel):
    """Macro preset event row."""

    date: str
    event_type: str
    details: dict[str, float | str] = Field(default_factory=dict)


class MacroPresetResponse(BaseModel):
    """Preset response for paired macro-market workflows."""

    status: MacroStatus = "ok"
    message: str | None = None
    preset_id: str = "copper_gold"
    inputs: dict[str, str | float | bool] = Field(default_factory=dict)
    series: list[MacroPresetSeries] = Field(default_factory=list)
    events: list[MacroEventItem] = Field(default_factory=list)


class MacroCatalogItem(BaseModel):
    """Catalog item."""

    id: str
    source: str
    series_id: str
    title: str | None = None
    frequency: str | None = None
    units: str | None = None
    domain: str | None = None
    default_transform: str = "level"
    publish_lag: int = 1
    notes: str | None = None
    active: bool = True
    tags: list[str] = Field(default_factory=list)
    last_obs: str | None = None
    stale_days: int | None = None
    release_frequency: str | None = None
    default_view: MacroViewMode = "explorer"
    vintage_available: bool = False


class MacroCatalogResponse(BaseModel):
    """Catalog response."""

    status: MacroStatus = "ok"
    message: str | None = None
    items: list[MacroCatalogItem] = Field(default_factory=list)


class MacroCatalogSearchRequest(BaseModel):
    """Catalog search request."""

    q: str = Field(min_length=1, max_length=200)
    domain: str | None = None
    limit: int = Field(default=25, ge=1, le=100)


class MacroCatalogRegisterRequest(BaseModel):
    """Catalog register request."""

    series_id: str = Field(min_length=1, max_length=100)
    domain: str | None = None
    publish_lag: int | None = Field(default=None, ge=0, le=3650)
    default_transform: str | None = None


class MacroSeriesQuery(BaseModel):
    """Series query parameters."""

    key: str = Field(min_length=1, max_length=120)
    start: date | None = None
    end: date | None = None
    transform: str = "level"
    freq: MacroFreq = "native"
    fill: MacroFill = "ffill"

    @field_validator("end")
    @classmethod
    def validate_date_range(cls, end: date | None, info):  # noqa: ANN001
        start = info.data.get("start")
        if start and end and end < start:
            raise ValueError("end must be greater than or equal to start")
        return end


class MacroExpressionRequest(BaseModel):
    """Expression evaluation request."""

    expr: str = Field(min_length=1, max_length=300)
    start: date | None = None
    end: date | None = None
    freq: MacroFreq = "native"
    fill: MacroFill = "ffill"
    transform: str = "level"

    @field_validator("end")
    @classmethod
    def validate_date_range(cls, end: date | None, info):  # noqa: ANN001
        start = info.data.get("start")
        if start and end and end < start:
            raise ValueError("end must be greater than or equal to start")
        return end


class MacroExpressionResponse(MacroSeriesResponse):
    """Expression response."""

    dependencies: list[str] = Field(default_factory=list)


class MacroDerivedSaveRequest(BaseModel):
    """Save derived expression."""

    derived_id: str = Field(min_length=3, max_length=120)
    expression: str = Field(min_length=1, max_length=300)
    default_transform: str = "level"


class MacroDerivedItem(BaseModel):
    """Derived catalog item."""

    derived_id: str
    expression: str
    dependencies: list[str] = Field(default_factory=list)
    default_transform: str = "level"
    created_at: str | None = None
    updated_at: str | None = None
    is_favorite: bool = True


class MacroDerivedResponse(BaseModel):
    """Derived list response."""

    status: MacroStatus = "ok"
    message: str | None = None
    items: list[MacroDerivedItem] = Field(default_factory=list)


class MacroRegimePoint(BaseModel):
    """Regime timepoint."""

    date: str
    risk_on_score: float
    inflation_score: float
    growth_score: float
    liquidity_score: float
    credit_stress_score: float


class MacroRegimeResponse(BaseModel):
    """Regime response."""

    status: MacroStatus = "ok"
    message: str | None = None
    data: list[MacroRegimePoint] = Field(default_factory=list)
    latest: MacroRegimePoint | None = None


class MacroRegimeStateResponse(BaseModel):
    """Compact regime-state response for dashboard signal lights."""

    status: MacroStatus = "ok"
    message: str | None = None
    date: str | None = None
    inflation_up: bool = False
    growth_down: bool = False
    risk_off_proxy: bool = False


class MacroAlertItem(BaseModel):
    """Alert row."""

    rule_id: str
    severity: Literal["info", "warning", "critical"]
    triggered_at: str
    message: str
    value: float
    threshold: float
    context: dict[str, float | str] = Field(default_factory=dict)


class MacroAlertsResponse(BaseModel):
    """Alerts response."""

    status: MacroStatus = "ok"
    message: str | None = None
    current: list[MacroAlertItem] = Field(default_factory=list)
    history: list[MacroAlertItem] = Field(default_factory=list)


class RegimeTransitionItem(BaseModel):
    """One regime transition item."""

    date: str
    axis: str
    from_score: float
    to_score: float
    delta: float
    direction: Literal["rising", "falling"]
    severity: Literal["minor", "major"]


class RegimeLabelPoint(BaseModel):
    """Regime label by date."""

    date: str
    label: str


class RegimeTransitionResponse(BaseModel):
    """Regime transition payload."""

    status: MacroStatus = "ok"
    message: str | None = None
    transitions: list[RegimeTransitionItem] = Field(default_factory=list)
    regime_label_history: list[RegimeLabelPoint] = Field(default_factory=list)


class HmmRegimePoint(BaseModel):
    """HMM state output row."""

    date: str
    state: int
    label: str
    probability: list[float] = Field(default_factory=list)


class HmmRegimePayload(BaseModel):
    """HMM regime payload."""

    status: MacroStatus = "ok"
    message: str | None = None
    states: list[HmmRegimePoint] = Field(default_factory=list)
    state_meta: dict[str, dict[str, float | str]] = Field(default_factory=dict)


class RegimeStreamEvent(BaseModel):
    """SSE regime stream event payload."""

    event_type: Literal["scores_update", "transition", "alert", "error"]
    timestamp: str
    data: dict[str, Any] = Field(default_factory=dict)
    label: str | None = None
    from_label: str | None = None
    to_label: str | None = None


class RegimeSchedulerStatusResponse(BaseModel):
    """Scheduler status payload."""

    running: bool = False
    last_market_refresh: str | None = None
    last_fred_update: str | None = None
    next_market_refresh: str | None = None
    next_fred_update: str | None = None


class MacroHealthObsStats(BaseModel):
    """Observation-layer health summary."""

    total_series_in_catalog: int = 0
    total_series_with_obs: int = 0
    last_obs_date_global: str | None = None
    last_fetched_at_global: str | None = None


class MacroHealthFeatureStats(BaseModel):
    """Feature-layer health summary."""

    total_feature_rows: int = 0
    last_feature_date: str | None = None
    feature_names_present: list[str] = Field(default_factory=list)


class MacroHealthResponse(BaseModel):
    """Macro subsystem health response."""

    status: MacroStatus = "ok"
    message: str | None = None
    fred_api_key_configured: bool = False
    macro_db_path: str = ""
    obs_stats: MacroHealthObsStats = Field(default_factory=MacroHealthObsStats)
    feature_stats: MacroHealthFeatureStats = Field(default_factory=MacroHealthFeatureStats)
    warnings: list[str] = Field(default_factory=list)


class MacroUpdateRequest(BaseModel):
    """Manual update trigger request."""

    series_ids: list[str] | None = None
    start: date | None = None
    end: date | None = None
    all_default: bool = False
    compute_features: bool = True
    features_lookback_days: int | None = Field(default=None, ge=7, le=3650)

    @field_validator("end")
    @classmethod
    def validate_date_range(cls, end: date | None, info):  # noqa: ANN001
        start = info.data.get("start")
        if start and end and end < start:
            raise ValueError("end must be greater than or equal to start")
        return end


class MacroUpdateResponse(BaseModel):
    """Manual update trigger response."""

    status: MacroStatus = "ok"
    message: str | None = None
    updated_series: list[str] = Field(default_factory=list)


class MacroStudySeriesSpec(BaseModel):
    """Study-level series configuration."""

    key: str
    alias: str | None = None
    transform_chain: list[str] = Field(default_factory=list)
    freq: MacroFreq = "native"
    fill: MacroFill = "ffill"
    axis: Literal["left", "right"] = "left"
    normalize_mode: MacroNormalizeMode = "raw"
    lag_mode: str | None = None
    display_style: Literal["line", "area", "bar", "scatter"] = "line"


class MacroViewSpec(BaseModel):
    """Saved view configuration for a study."""

    view_id: str
    mode: MacroViewMode
    title: str | None = None
    layout: dict[str, Any] = Field(default_factory=dict)


class MacroConclusionPayload(BaseModel):
    """Saved conclusion block for a macro study."""

    summary: str = ""
    thesis: str = ""
    risk_cases: list[str] = Field(default_factory=list)
    action_bias: str = "neutral"
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    next_checks: list[str] = Field(default_factory=list)


class StudyReportAttachment(BaseModel):
    """Report attachment linked to a macro study."""

    report_id: int | None = None
    title: str | None = None
    report_path: str
    created_at: str | None = None
    source_run_id: str | None = None
    symbols: list[str] = Field(default_factory=list)


class MacroStudyPayload(BaseModel):
    """Macro study object persisted locally."""

    id: str | None = None
    name: str = Field(min_length=1, max_length=160)
    objective: str = ""
    series_specs: list[MacroStudySeriesSpec] = Field(default_factory=list)
    view_specs: list[MacroViewSpec] = Field(default_factory=list)
    notes: str = ""
    conclusion: MacroConclusionPayload = Field(default_factory=MacroConclusionPayload)
    linked_assets: list[str] = Field(default_factory=list)
    linked_reports: list[StudyReportAttachment] = Field(default_factory=list)
    linked_feature_set_id: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class MacroStudiesResponse(BaseModel):
    """List response for macro studies."""

    status: MacroStatus = "ok"
    message: str | None = None
    items: list[MacroStudyPayload] = Field(default_factory=list)


class MacroCompareResponse(BaseModel):
    """Normalized multi-series comparison payload."""

    status: MacroStatus = "ok"
    message: str | None = None
    normalization: MacroNormalizeMode = "raw"
    series: dict[str, MacroSeriesResponse] = Field(default_factory=dict)


class MacroLeadLagPoint(BaseModel):
    """Lead-lag correlation point."""

    lag: int
    correlation: float


class MacroLeadLagResponse(BaseModel):
    """Lead-lag response payload."""

    status: MacroStatus = "ok"
    message: str | None = None
    lhs: str = ""
    rhs: str = ""
    best_lag: int = 0
    best_correlation: float = 0.0
    table: list[MacroLeadLagPoint] = Field(default_factory=list)
    rolling_corr: list[MacroDataPoint] = Field(default_factory=list)


class MacroScatterPoint(BaseModel):
    """Scatter point with date context."""

    date: str
    x: float
    y: float


class MacroScatterResponse(BaseModel):
    """Scatter response payload."""

    status: MacroStatus = "ok"
    message: str | None = None
    lhs: str = ""
    rhs: str = ""
    correlation: float | None = None
    slope: float | None = None
    intercept: float | None = None
    points: list[MacroScatterPoint] = Field(default_factory=list)


class MacroVintagePoint(BaseModel):
    """Vintage-aware observation row."""

    date: str
    value: float
    realtime_start: str | None = None
    realtime_end: str | None = None
    fetched_at: str | None = None


class MacroVintageResponse(BaseModel):
    """Vintage comparison payload."""

    status: MacroStatus = "ok"
    message: str | None = None
    key: str = ""
    as_of_date: str | None = None
    latest: list[MacroDataPoint] = Field(default_factory=list)
    as_of: list[MacroDataPoint] = Field(default_factory=list)
    revisions: list[MacroVintagePoint] = Field(default_factory=list)
    revision_delta: float | None = None


class MacroReleaseCalendarItem(BaseModel):
    """Release-style metadata row for a series."""

    key: str
    title: str | None = None
    domain: str | None = None
    release_frequency: str | None = None
    last_obs: str | None = None
    stale_days: int | None = None
    estimated_next_release: str | None = None
    vintage_available: bool = False


class MacroReleaseCalendarResponse(BaseModel):
    """Release calendar response."""

    status: MacroStatus = "ok"
    message: str | None = None
    items: list[MacroReleaseCalendarItem] = Field(default_factory=list)


class MacroReportResponse(BaseModel):
    """HTML report export response."""

    status: MacroStatus = "ok"
    message: str | None = None
    study_id: str | None = None
    report_path: str | None = None
    generated_at: str | None = None


class MacroFeatureExportItem(BaseModel):
    """Feature lineage item exported from a study."""

    feature_name: str
    source_study_id: str
    key: str
    transform_chain: list[str] = Field(default_factory=list)
    lag_rule: str | None = None
    as_of_policy: str = "latest"


class MacroFeatureExportResponse(BaseModel):
    """Feature export response."""

    status: MacroStatus = "ok"
    message: str | None = None
    study_id: str | None = None
    artifact_path: str | None = None
    exported_at: str | None = None
    items: list[MacroFeatureExportItem] = Field(default_factory=list)
