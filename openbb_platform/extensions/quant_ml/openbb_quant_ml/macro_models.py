"""Pydantic models for Macro tab endpoints."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator

MacroStatus = Literal["ok", "insufficient_data", "not_found", "error"]
MacroFreq = Literal["native", "D", "W", "M", "Q"]
MacroFill = Literal["ffill", "interpolate", "none"]


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


class MacroUpdateRequest(BaseModel):
    """Manual update trigger request."""

    series_ids: list[str] | None = None
    start: date | None = None
    end: date | None = None
    all_default: bool = False

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
