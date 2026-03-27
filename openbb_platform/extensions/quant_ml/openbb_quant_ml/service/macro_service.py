"""Macro endpoint service orchestration."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Any, cast

import numpy as np
import pandas as pd

from openbb_quant_ml.macro_models import (
    HmmRegimePayload,
    HmmRegimePoint,
    MacroAlertItem,
    MacroAlertsResponse,
    MacroCatalogItem,
    MacroCatalogResponse,
    MacroCompareResponse,
    MacroConclusionPayload,
    MacroDataPoint,
    MacroDerivedItem,
    MacroDerivedResponse,
    MacroExpressionRequest,
    MacroExpressionResponse,
    MacroFeatureExportItem,
    MacroFeatureExportResponse,
    MacroHealthFeatureStats,
    MacroHealthObsStats,
    MacroHealthResponse,
    MacroLeadLagPoint,
    MacroLeadLagResponse,
    MacroPresetResponse,
    MacroRegimePoint,
    MacroRegimeResponse,
    MacroRegimeStateResponse,
    MacroReleaseCalendarItem,
    MacroReleaseCalendarResponse,
    MacroReportResponse,
    MacroSeriesMeta,
    MacroSeriesMultiResponse,
    MacroSeriesQuery,
    MacroSeriesResponse,
    MacroSeriesStats,
    MacroScatterPoint,
    MacroScatterResponse,
    MacroStudyPayload,
    MacroStudiesResponse,
    MacroStudySeriesSpec,
    MacroUpdateRequest,
    MacroUpdateResponse,
    MacroViewSpec,
    MacroVintagePoint,
    MacroVintageResponse,
    RegimeLabelPoint,
    RegimeSchedulerStatusResponse,
    RegimeTransitionItem,
    RegimeTransitionResponse,
)
from openbb_quant_ml.service.macro_alerts import evaluate_alerts, persist_and_get_alerts
from openbb_quant_ml.service.macro_catalog import (
    bootstrap_default_catalog,
    list_catalog_items,
    register_series,
    resolve_catalog_item,
    search_catalog,
)
from openbb_quant_ml.service.macro_constants import MACRO_DB_PATH, MACRO_ROOT, load_macro_config
from openbb_quant_ml.service.macro_db import (
    attach_report_to_macro_study,
    get_macro_feature_health_stats,
    get_macro_obs_health_stats,
    get_obs_summaries,
    get_macro_study,
    list_alert_events,
    list_macro_studies,
    list_derived_expressions,
    load_observation_vintages,
    load_observations_asof,
    load_observations,
    save_macro_study,
    save_derived_expression,
)
from openbb_quant_ml.service.reporting import get_reports_history_response
from openbb_quant_ml.service.macro_expression import MacroExpressionError, evaluate_expression
from openbb_quant_ml.service.macro_fred_client import FredClient
from openbb_quant_ml.service.macro_market import get_market_series
from openbb_quant_ml.service.macro_presets import get_copper_gold_preset_response as build_copper_gold_preset_response
from openbb_quant_ml.service.macro_regime import (
    classify_regime_label,
    compute_regime_scores,
    detect_regime_transitions,
)
from openbb_quant_ml.service.macro_regime_hmm import fit_hmm_regime
from openbb_quant_ml.service.macro_transforms import (
    apply_publish_lag,
    apply_transform,
    compute_stats,
    default_publish_lag_days,
    infer_frequency_label,
    lag_period_text,
    normalize_series,
    resample_series,
)
from openbb_quant_ml.service.macro_update import update_all_defaults, update_series_ids
from openbb_quant_ml.service.regime_scheduler import (
    ensure_scheduler_started,
    get_scheduler_status,
    trigger_regime_refresh,
)
from openbb_quant_ml.service.storage import save_json, utc_now_iso

_DERIVED_BOOTSTRAPPED = False


def _series_to_points(series: pd.Series) -> list[MacroDataPoint]:
    clean = series.dropna().sort_index()
    return [
        MacroDataPoint(date=idx.date().isoformat(), value=float(value))
        for idx, value in clean.items()
    ]


def _stats_to_model(stats: dict[str, float | None]) -> MacroSeriesStats:
    return MacroSeriesStats(
        last=stats.get("last"),
        change_1m=stats.get("change_1m"),
        change_3m=stats.get("change_3m"),
        z=stats.get("z"),
        percentile_5y=stats.get("percentile_5y"),
    )


def _step_delta_for_frequency(frequency_label: str | None) -> timedelta:
    freq = str(frequency_label or "").lower()
    if "day" in freq or freq == "d":
        return timedelta(days=1)
    if "week" in freq or freq == "w":
        return timedelta(days=7)
    if "quarter" in freq or freq == "q":
        return timedelta(days=90)
    return timedelta(days=30)


def _estimate_next_release(last_obs: str | None, frequency_label: str | None, publish_lag: int | None) -> str | None:
    if not last_obs:
        return None
    try:
        base = pd.Timestamp(last_obs)
    except Exception:  # noqa: BLE001
        return None
    next_ts = base + _step_delta_for_frequency(frequency_label) + timedelta(days=max(0, int(publish_lag or 0)))
    return next_ts.date().isoformat()


def _compute_stale_days(last_obs: str | None) -> int | None:
    if not last_obs:
        return None
    try:
        return max(
            0,
            int((pd.Timestamp.utcnow().normalize() - pd.Timestamp(last_obs)).days),
        )
    except Exception:  # noqa: BLE001
        return None


def _get_catalog_obs_summaries(
    rows: list[dict[str, Any]],
) -> dict[tuple[str, str], dict[str, Any]]:
    pairs = [
        (str(row.get("source", "FRED")), str(row.get("series_id", "")))
        for row in rows
    ]
    return get_obs_summaries(pairs)


def _normalize_mode_for_series(series: pd.Series, normalize_mode: str) -> pd.Series:
    mode = str(normalize_mode or "raw").lower()
    if mode == "raw":
        return series
    if mode == "index100":
        clean = series.dropna()
        if clean.empty:
            return series
        base = float(clean.iloc[0])
        if abs(base) <= 1e-12:
            return pd.Series(np.nan, index=series.index, dtype=float)
        return (series / base) * 100.0
    if mode == "zscore":
        return apply_transform(series, cast(Any, "zscore"))
    if mode == "yoy":
        return apply_transform(series, cast(Any, "yoy"))
    if mode == "percentile_5y":
        return apply_transform(series, cast(Any, "percentile_5y"))
    return series


def _apply_transform_chain(series: pd.Series, transform_chain: list[str]) -> pd.Series:
    out = series.copy()
    for raw_step in transform_chain:
        step = str(raw_step or "").strip()
        if not step:
            continue
        if ":" not in step:
            out = apply_transform(out, cast(Any, step))
            continue
        name, raw_arg = step.split(":", 1)
        name = name.strip().lower()
        arg = raw_arg.strip()
        if name == "lag":
            out = out.shift(max(1, int(float(arg or "1"))))
        elif name == "lead":
            out = out.shift(-max(1, int(float(arg or "1"))))
        elif name == "rolling_min":
            win = max(2, int(float(arg or "5")))
            out = out.rolling(win, min_periods=max(2, win // 4)).min()
        elif name == "rolling_max":
            win = max(2, int(float(arg or "5")))
            out = out.rolling(win, min_periods=max(2, win // 4)).max()
        elif name == "ema":
            span = max(1, int(float(arg or "12")))
            out = out.ewm(span=span, adjust=False, min_periods=1).mean()
        else:
            out = apply_transform(out, cast(Any, name))
    return out


def _series_response_from_series(
    key: str,
    series: pd.Series,
    meta_raw: dict[str, Any],
    *,
    transform: str,
    warning: str | None = None,
) -> MacroSeriesResponse:
    return MacroSeriesResponse(
        meta=MacroSeriesMeta(
            key=str(meta_raw.get("key", key)),
            title=cast(str | None, meta_raw.get("title")),
            units=cast(str | None, meta_raw.get("units")),
            frequency=cast(str | None, meta_raw.get("frequency")),
            source=str(meta_raw.get("source", "unknown")),
            transform=transform,
            lag_applied=cast(str | None, meta_raw.get("lag_applied")),
            warning=warning,
        ),
        data=_series_to_points(series),
        stats=_stats_to_model(compute_stats(series)),
        status="ok",
    )


def _seed_macro_studies_if_needed() -> None:
    if list_macro_studies():
        return
    save_macro_study(
        {
            "name": "Labor and Inflation Monitor",
            "objective": "Track labor slack, inflation pressure, and policy stance before exporting features.",
            "series_specs": [
                {
                    "key": "FRED:UNRATE",
                    "alias": "Unemployment",
                    "transform_chain": [],
                    "freq": "M",
                    "fill": "ffill",
                    "axis": "left",
                    "normalize_mode": "raw",
                    "display_style": "line",
                },
                {
                    "key": "FRED:CPIAUCSL",
                    "alias": "CPI",
                    "transform_chain": ["yoy"],
                    "freq": "M",
                    "fill": "ffill",
                    "axis": "right",
                    "normalize_mode": "yoy",
                    "display_style": "line",
                },
                {
                    "key": "FRED:FEDFUNDS",
                    "alias": "Fed Funds",
                    "transform_chain": [],
                    "freq": "M",
                    "fill": "ffill",
                    "axis": "right",
                    "normalize_mode": "raw",
                    "display_style": "line",
                },
            ],
            "view_specs": [
                {"view_id": "explorer", "mode": "explorer", "title": "Explorer", "layout": {}},
                {"view_id": "compare", "mode": "compare", "title": "Compare", "layout": {}},
                {"view_id": "relationship", "mode": "relationship", "title": "Relationship", "layout": {}},
                {"view_id": "release", "mode": "release", "title": "Release", "layout": {}},
                {"view_id": "report", "mode": "report", "title": "Report", "layout": {}},
            ],
            "notes": "Initial seed study for macro monitoring.",
            "conclusion": {
                "summary": "",
                "thesis": "",
                "risk_cases": [],
                "action_bias": "neutral",
                "confidence": None,
                "next_checks": [],
            },
            "linked_assets": ["SPY", "TLT", "GLD"],
        }
    )


def _normalize_key(key: str) -> tuple[str, str]:
    text = str(key or "").strip()
    if not text:
        raise ValueError("key is required")
    if text.upper().startswith("FRED:"):
        return "FRED", text.split(":", 1)[1].strip().upper()
    catalog_item = resolve_catalog_item(text, create_if_missing=False)
    if catalog_item and str(catalog_item.get("source", "")).upper() == "FRED":
        return "FRED", str(catalog_item.get("series_id", text)).upper()
    return "MARKET", text.upper()


def _load_fred_series(
    series_id: str,
    start: date | None,
    end: date | None,
) -> tuple[pd.Series, dict[str, Any], str | None]:
    item = resolve_catalog_item(f"FRED:{series_id}", create_if_missing=True) or {}
    warning: str | None = None
    updated = update_series_ids([series_id], start=start, end=end)
    if not updated:
        warning = "fred_cache_fallback"
    rows = load_observations("FRED", series_id, start.isoformat() if start else None, end.isoformat() if end else None)
    series = normalize_series(rows)
    if series.empty:
        raise ValueError(f"No observations found for FRED:{series_id}")

    frequency = str(item.get("frequency") or infer_frequency_label(series))
    lag_days = int(item.get("publish_lag") or default_publish_lag_days(frequency))
    series_lagged = apply_publish_lag(series, lag_days=lag_days)
    meta = {
        "key": f"FRED:{series_id}",
        "title": item.get("title") or series_id,
        "units": item.get("units"),
        "frequency": frequency,
        "source": "FRED",
        "lag_applied": lag_period_text(lag_days, frequency),
    }
    return series_lagged, meta, warning


def _load_market_symbol(
    symbol: str,
    start: date | None,
    end: date | None,
) -> tuple[pd.Series, dict[str, Any], str | None]:
    series, source, warning = get_market_series(symbol, start=start, end=end)
    if series.empty:
        raise ValueError(f"No market observations found for symbol: {symbol}")
    meta = {
        "key": symbol,
        "title": symbol,
        "units": "price",
        "frequency": infer_frequency_label(series),
        "source": f"MARKET:{source}",
        "lag_applied": lag_period_text(0, None),
    }
    return series, meta, warning


def _get_series(
    key: str,
    start: date | None,
    end: date | None,
) -> tuple[pd.Series, dict[str, Any], str | None]:
    source, series_id = _normalize_key(key)
    if source == "FRED":
        return _load_fred_series(series_id, start=start, end=end)
    return _load_market_symbol(series_id, start=start, end=end)


def _get_series_asof(
    key: str,
    start: date | None,
    end: date | None,
    as_of_date: date | None = None,
) -> tuple[pd.Series, dict[str, Any], str | None]:
    if as_of_date is None:
        return _get_series(key, start=start, end=end)
    source, series_id = _normalize_key(key)
    if source != "FRED":
        return _get_series(key, start=start, end=end)

    item = resolve_catalog_item(f"FRED:{series_id}", create_if_missing=True) or {}
    rows = load_observations_asof(
        "FRED",
        series_id,
        as_of_date=as_of_date.isoformat(),
        start=start.isoformat() if start else None,
        end=end.isoformat() if end else None,
    )
    series = normalize_series(rows)
    if series.empty:
        raise ValueError(f"No observations found for FRED:{series_id} as of {as_of_date.isoformat()}")
    frequency = str(item.get("frequency") or infer_frequency_label(series))
    lag_days = int(item.get("publish_lag") or default_publish_lag_days(frequency))
    series_lagged = apply_publish_lag(series, lag_days=lag_days)
    meta = {
        "key": f"FRED:{series_id}",
        "title": item.get("title") or series_id,
        "units": item.get("units"),
        "frequency": frequency,
        "source": "FRED",
        "lag_applied": lag_period_text(lag_days, frequency),
    }
    return series_lagged, meta, f"as_of:{as_of_date.isoformat()}"


def _resolver_factory(start: date | None, end: date | None, freq: str, fill: str, as_of_date: date | None = None):
    cache: dict[str, pd.Series] = {}

    def resolver(symbol_key: str) -> pd.Series:
        key = symbol_key.strip()
        if key in cache:
            return cache[key]
        series, _, _ = _get_series_asof(key, start=start, end=end, as_of_date=as_of_date)
        transformed = resample_series(
            series,
            freq=cast(Any, freq),
            fill=cast(Any, fill),
            start=start,
            end=end,
        )
        cache[key] = transformed
        return transformed

    return resolver


def get_catalog_response(domain: str | None = None) -> MacroCatalogResponse:
    """Return registered macro catalog items."""
    bootstrap_default_catalog()
    bootstrap_default_derived_expressions()
    _seed_macro_studies_if_needed()
    rows = list(list_catalog_items(domain=domain))
    obs_summary_by_series = _get_catalog_obs_summaries(rows)
    items: list[MacroCatalogItem] = []
    for row in rows:
        obs_summary = obs_summary_by_series.get(
            (str(row.get("source", "FRED")), str(row.get("series_id", ""))),
            {},
        )
        last_obs = cast(str | None, obs_summary.get("last_obs"))
        items.append(
            MacroCatalogItem(
                **row,
                tags=[str(row.get("domain") or "macro").lower(), str(row.get("source") or "fred").lower()],
                last_obs=last_obs,
                stale_days=_compute_stale_days(last_obs),
                release_frequency=str(row.get("frequency") or "").lower() or None,
                default_view="explorer",
                vintage_available=bool(obs_summary.get("vintage_available")),
            )
        )
    return MacroCatalogResponse(status="ok", items=items)


def search_catalog_response(query: str, domain: str | None = None, limit: int = 25) -> MacroCatalogResponse:
    """Search FRED catalog and return candidate list."""
    try:
        rows = search_catalog(query=query, domain=domain, limit=limit)
    except Exception as exc:  # noqa: BLE001
        return MacroCatalogResponse(status="insufficient_data", message=str(exc), items=[])
    items = [MacroCatalogItem(**row) for row in rows]
    return MacroCatalogResponse(status="ok", items=items)


def register_catalog_response(
    series_id: str,
    domain: str | None = None,
    publish_lag: int | None = None,
    default_transform: str | None = None,
) -> MacroCatalogResponse:
    """Register one series and return upserted row."""
    try:
        row = register_series(
            series_id=series_id,
            domain=domain,
            publish_lag=publish_lag,
            default_transform=default_transform,
        )
    except Exception as exc:  # noqa: BLE001
        return MacroCatalogResponse(status="insufficient_data", message=str(exc), items=[])
    return MacroCatalogResponse(status="ok", items=[MacroCatalogItem(**row)])


def get_series_response(query: MacroSeriesQuery) -> MacroSeriesResponse:
    """Load series + transform + stats."""
    try:
        series, meta_raw, warning = _get_series(query.key, start=query.start, end=query.end)
    except Exception as exc:  # noqa: BLE001
        return MacroSeriesResponse(
            meta=MacroSeriesMeta(
                key=query.key,
                source="unknown",
                transform=query.transform,
            ),
            data=[],
            stats=MacroSeriesStats(),
            status="insufficient_data",
            message=str(exc),
        )

    transformed = apply_transform(series, cast(Any, query.transform))
    transformed = resample_series(
        transformed,
        freq=cast(Any, query.freq),
        fill=cast(Any, query.fill),
        start=query.start,
        end=query.end,
    )
    stats = compute_stats(transformed)
    meta = MacroSeriesMeta(
        key=str(meta_raw.get("key", query.key)),
        title=cast(str | None, meta_raw.get("title")),
        units=cast(str | None, meta_raw.get("units")),
        frequency=cast(str | None, meta_raw.get("frequency")),
        source=str(meta_raw.get("source", "unknown")),
        transform=query.transform,
        lag_applied=cast(str | None, meta_raw.get("lag_applied")),
        warning=warning,
    )
    return MacroSeriesResponse(
        meta=meta,
        data=_series_to_points(transformed),
        stats=_stats_to_model(stats),
        status="ok",
    )


def get_series_multi_response(
    ids: list[str],
    start: date | None = None,
    end: date | None = None,
    transform: str = "level",
    freq: str = "native",
    fill: str = "ffill",
) -> MacroSeriesMultiResponse:
    """Return multiple macro/market series keyed by id."""
    items: dict[str, MacroSeriesResponse] = {}
    errors: list[str] = []
    for key in ids:
        key_norm = str(key or "").strip()
        if not key_norm:
            continue
        payload = get_series_response(
            MacroSeriesQuery(
                key=key_norm,
                start=start,
                end=end,
                transform=transform,
                freq=cast(Any, freq),
                fill=cast(Any, fill),
            )
        )
        items[key_norm] = payload
        if payload.status != "ok" and payload.message:
            errors.append(f"{key_norm}: {payload.message}")
    if not items:
        return MacroSeriesMultiResponse(status="insufficient_data", message="No valid ids provided.", series={})
    status = "ok" if not errors else "insufficient_data"
    message = " | ".join(errors[:5]) if errors else None
    return MacroSeriesMultiResponse(status=cast(Any, status), message=message, series=items)


def evaluate_expression_response(request: MacroExpressionRequest) -> MacroExpressionResponse:
    """Evaluate user expression with safe parser."""
    resolver = _resolver_factory(request.start, request.end, request.freq, request.fill)
    try:
        evaluated = evaluate_expression(request.expr, resolver=resolver)
        transformed = apply_transform(evaluated.series, cast(Any, request.transform))
        transformed = resample_series(
            transformed,
            freq=cast(Any, request.freq),
            fill=cast(Any, request.fill),
            start=request.start,
            end=request.end,
        )
        stats = compute_stats(transformed)
        return MacroExpressionResponse(
            meta=MacroSeriesMeta(
                key=request.expr,
                title=request.expr,
                units=None,
                frequency=infer_frequency_label(transformed) if not transformed.empty else None,
                source="expression",
                transform=request.transform,
                lag_applied=None,
            ),
            data=_series_to_points(transformed),
            stats=_stats_to_model(stats),
            status="ok",
            dependencies=evaluated.dependencies,
        )
    except MacroExpressionError as exc:
        return MacroExpressionResponse(
            meta=MacroSeriesMeta(
                key=request.expr,
                source="expression",
                transform=request.transform,
            ),
            data=[],
            stats=MacroSeriesStats(),
            status="error",
            message=str(exc),
            dependencies=[],
        )
    except Exception as exc:  # noqa: BLE001
        return MacroExpressionResponse(
            meta=MacroSeriesMeta(
                key=request.expr,
                source="expression",
                transform=request.transform,
            ),
            data=[],
            stats=MacroSeriesStats(),
            status="insufficient_data",
            message=str(exc),
            dependencies=[],
        )


def save_derived_response(derived_id: str, expression: str, default_transform: str = "level") -> MacroDerivedResponse:
    """Persist expression as derived favorite."""
    try:
        deps = evaluate_expression(expression, resolver=_resolver_factory(None, None, "native", "ffill")).dependencies
    except Exception:
        deps = []
    save_derived_expression(
        derived_id=derived_id,
        expression=expression,
        dependencies=deps,
        default_transform=default_transform,
        is_favorite=True,
    )
    return list_derived_response()


def list_derived_response() -> MacroDerivedResponse:
    """List derived expressions."""
    bootstrap_default_derived_expressions()
    rows = list_derived_expressions()
    items = [
        MacroDerivedItem(
            derived_id=str(row.get("derived_id", "")),
            expression=str(row.get("expression", "")),
            dependencies=cast(list[str], row.get("dependencies", [])),
            default_transform=str(row.get("default_transform", "level")),
            created_at=cast(str | None, row.get("created_at")),
            updated_at=cast(str | None, row.get("updated_at")),
            is_favorite=bool(row.get("is_favorite", True)),
        )
        for row in rows
    ]
    return MacroDerivedResponse(status="ok", items=items)


def get_regime_response(
    start: date | None = None,
    end: date | None = None,
    freq: str = "W",
    fill: str = "ffill",
) -> MacroRegimeResponse:
    """Compute 5-axis macro regime scores."""
    resolver = _resolver_factory(start, end, freq, fill)
    try:
        frame = compute_regime_scores(resolver=resolver, start=start, end=end, freq=freq, fill=fill)
        frame = frame.ffill().fillna(50.0)
    except Exception as exc:  # noqa: BLE001
        return MacroRegimeResponse(status="insufficient_data", message=str(exc), data=[], latest=None)

    if frame.empty:
        return MacroRegimeResponse(status="insufficient_data", message="No regime data available.", data=[], latest=None)

    points = [
        MacroRegimePoint(
            date=idx.date().isoformat(),
            risk_on_score=float(row.get("risk_on_score", 0.0)),
            inflation_score=float(row.get("inflation_score", 0.0)),
            growth_score=float(row.get("growth_score", 0.0)),
            liquidity_score=float(row.get("liquidity_score", 0.0)),
            credit_stress_score=float(row.get("credit_stress_score", 0.0)),
        )
        for idx, row in frame.iterrows()
    ]
    latest = points[-1] if points else None
    return MacroRegimeResponse(status="ok", data=points, latest=latest)


def get_regime_state_response(target_date: date | None = None) -> MacroRegimeStateResponse:
    """Return compact macro regime flags for dashboard signal lights."""
    regime = get_regime_response(start=None, end=target_date, freq="W", fill="ffill")
    if regime.status != "ok" or not regime.latest:
        return MacroRegimeStateResponse(status="insufficient_data", message=regime.message)
    latest = regime.latest
    return MacroRegimeStateResponse(
        status="ok",
        date=latest.date,
        inflation_up=bool(float(latest.inflation_score) >= 50.0),
        growth_down=bool(float(latest.growth_score) < 50.0),
        risk_off_proxy=bool(float(latest.risk_on_score) < 50.0 or float(latest.credit_stress_score) > 50.0),
    )


def get_alerts_response(
    start: date | None = None,
    end: date | None = None,
    history_limit: int = 200,
) -> MacroAlertsResponse:
    """Evaluate and return macro alerts."""
    regime = get_regime_response(start=start, end=end, freq="W", fill="ffill")
    resolver = _resolver_factory(start, end, "W", "ffill")
    if regime.status != "ok" or not regime.data:
        history = list_alert_events(limit=history_limit)
        return MacroAlertsResponse(
            status="insufficient_data",
            message=regime.message or "No regime data available for alerts.",
            current=[],
            history=[MacroAlertItem(**item) for item in history],
        )

    frame = pd.DataFrame([item.model_dump() for item in regime.data]).set_index("date")
    frame.index = pd.to_datetime(frame.index)
    current_raw = evaluate_alerts(frame, resolver=resolver)
    current_raw, history_raw = persist_and_get_alerts(current_raw, history_limit=history_limit)
    return MacroAlertsResponse(
        status="ok",
        current=[MacroAlertItem(**item) for item in current_raw],
        history=[MacroAlertItem(**item) for item in history_raw],
    )


def get_regime_transitions_response(
    start: date | None = None,
    end: date | None = None,
    threshold: float = 10.0,
    freq: str = "W",
    fill: str = "ffill",
) -> RegimeTransitionResponse:
    """Return axis-level regime transitions plus label history."""
    regime = get_regime_response(start=start, end=end, freq=freq, fill=fill)
    if regime.status != "ok" or not regime.data:
        return RegimeTransitionResponse(
            status="insufficient_data",
            message=regime.message or "No regime data available.",
            transitions=[],
            regime_label_history=[],
        )

    frame = pd.DataFrame([item.model_dump() for item in regime.data]).set_index("date")
    frame.index = pd.to_datetime(frame.index)
    transitions_df = detect_regime_transitions(frame, threshold=threshold)
    transitions = [
        RegimeTransitionItem(
            date=str(row["date"]),
            axis=str(row["axis"]),
            from_score=float(row["from_score"]),
            to_score=float(row["to_score"]),
            delta=float(row["delta"]),
            direction=cast(Any, str(row["direction"])),
            severity=cast(Any, str(row["severity"])),
        )
        for _, row in transitions_df.iterrows()
    ]
    labels = [
        RegimeLabelPoint(
            date=item.date,
            label=classify_regime_label(item.model_dump()),
        )
        for item in regime.data
    ]
    return RegimeTransitionResponse(
        status="ok",
        transitions=transitions,
        regime_label_history=labels,
    )


def get_hmm_regime_response(
    start: date | None = None,
    end: date | None = None,
    n_states: int = 4,
    freq: str = "W",
    fill: str = "ffill",
) -> HmmRegimePayload:
    """Return HMM-based regime state sequence."""
    regime = get_regime_response(start=start, end=end, freq=freq, fill=fill)
    if regime.status != "ok" or not regime.data:
        return HmmRegimePayload(
            status="insufficient_data",
            message=regime.message or "No regime data available.",
            states=[],
            state_meta={},
        )
    score_frame = pd.DataFrame([item.model_dump() for item in regime.data]).set_index("date")
    score_frame.index = pd.to_datetime(score_frame.index)
    score_frame = score_frame.sort_index()
    hmm = fit_hmm_regime(score_frame, n_states=n_states)
    if hmm is None:
        return HmmRegimePayload(
            status="insufficient_data",
            message="HMM dependency unavailable or insufficient data.",
            states=[],
            state_meta={},
        )

    index = list(hmm.get("index", []))
    state_seq = list(hmm.get("states", []))
    proba_seq = list(hmm.get("probabilities", []))
    state_meta_raw = cast(dict[int, dict[str, Any]], hmm.get("state_meta", {}))

    states: list[HmmRegimePoint] = []
    for idx, state in enumerate(state_seq):
        date_value = pd.Timestamp(index[idx]).date().isoformat()
        proba = proba_seq[idx] if idx < len(proba_seq) else []
        label = str(state_meta_raw.get(int(state), {}).get("label", "Transitional"))
        states.append(
            HmmRegimePoint(
                date=date_value,
                state=int(state),
                label=label,
                probability=[float(value) for value in list(proba)],
            )
        )

    state_meta: dict[str, dict[str, float | str]] = {}
    for state_idx, payload in state_meta_raw.items():
        means = cast(dict[str, float], payload.get("means", {}))
        state_meta[str(state_idx)] = {
            "label": str(payload.get("label", "Transitional")),
            **{key: float(value) for key, value in means.items()},
        }
    return HmmRegimePayload(status="ok", states=states, state_meta=state_meta)


def get_regime_scheduler_status_response() -> RegimeSchedulerStatusResponse:
    """Return scheduler running status and recent timestamps."""
    ensure_scheduler_started()
    payload = get_scheduler_status()
    return RegimeSchedulerStatusResponse(
        running=bool(payload.get("running", False)),
        last_market_refresh=cast(str | None, payload.get("last_market_refresh")),
        last_fred_update=cast(str | None, payload.get("last_fred_update")),
        next_market_refresh=cast(str | None, payload.get("next_market_refresh")),
        next_fred_update=cast(str | None, payload.get("next_fred_update")),
    )


def trigger_regime_refresh_response() -> dict[str, str]:
    """Trigger immediate macro regime refresh."""
    ensure_scheduler_started()
    payload = trigger_regime_refresh()
    status = str(payload.get("status", "ok"))
    return {"status": status}


def get_health_response() -> MacroHealthResponse:
    """Return macro storage/update health summary for UI diagnostics."""
    warnings: list[str] = []
    fred_api_key_configured = FredClient().has_api_key
    openbb_core_available = True
    try:
        from openbb import obb as _obb  # type: ignore[import-not-found]
        _ = _obb
    except Exception:
        openbb_core_available = False
    if not fred_api_key_configured and not openbb_core_available:
        warnings.append("missing_api_key_cache_fallback")

    obs_stats_raw = get_macro_obs_health_stats()
    feat_stats_raw = get_macro_feature_health_stats(top_n=12)

    status: str = "ok"
    message: str | None = None
    if int(obs_stats_raw.get("total_series_with_obs", 0)) <= 0:
        status = "insufficient_data"
        warnings.append("macro_observations_empty")
        message = "No macro observations are stored. Run macro update first."
    if int(feat_stats_raw.get("total_feature_rows", 0)) <= 0:
        status = "insufficient_data"
        warnings.append("macro_features_empty")
        if not message:
            message = "Macro features are missing. Re-run update with compute_features enabled."

    last_obs = obs_stats_raw.get("last_obs_date_global")
    last_feat = feat_stats_raw.get("last_feature_date")
    if last_obs and last_feat:
        try:
            stale_days = int((pd.Timestamp(last_obs) - pd.Timestamp(last_feat)).days)
            if stale_days > 7:
                warnings.append("macro_features_stale_vs_observations")
        except Exception:  # noqa: BLE001
            pass

    return MacroHealthResponse(
        status=cast(Any, status),
        message=message,
        fred_api_key_configured=fred_api_key_configured,
        macro_db_path=str(MACRO_DB_PATH),
        obs_stats=MacroHealthObsStats(**obs_stats_raw),
        feature_stats=MacroHealthFeatureStats(**feat_stats_raw),
        warnings=warnings,
    )


def trigger_update_response(request: MacroUpdateRequest) -> MacroUpdateResponse:
    """Trigger on-demand refresh."""
    try:
        if request.all_default:
            updated = update_all_defaults(
                start=request.start,
                end=request.end,
                compute_features=request.compute_features,
                features_lookback_days=request.features_lookback_days,
            )
        else:
            updated = update_series_ids(
                request.series_ids or [],
                start=request.start,
                end=request.end,
                compute_features=request.compute_features,
                features_lookback_days=request.features_lookback_days,
            )
    except Exception as exc:  # noqa: BLE001
        return MacroUpdateResponse(status="error", message=str(exc), updated_series=[])
    if not updated:
        return MacroUpdateResponse(
            status="insufficient_data",
            message="No series updated. Check FRED_API_KEY or requested series IDs.",
            updated_series=[],
        )
    return MacroUpdateResponse(status="ok", updated_series=updated)


def get_market_ratio_response(
    lhs: str,
    rhs: str,
    start: date | None = None,
    end: date | None = None,
    freq: str = "D",
    fill: str = "ffill",
) -> MacroSeriesResponse:
    """Return ratio series x / y on aligned calendar."""
    request = MacroExpressionRequest(
        expr=f"{lhs}/{rhs}",
        start=start,
        end=end,
        freq=cast(Any, freq),
        fill=cast(Any, fill),
        transform="level",
    )
    result = evaluate_expression_response(request)
    result.meta.title = f"{lhs}/{rhs}"
    return result


def get_market_rolling_corr_response(
    x: str,
    y: str,
    window: int = 60,
    start: date | None = None,
    end: date | None = None,
    freq: str = "D",
    fill: str = "ffill",
) -> MacroSeriesResponse:
    """Return rolling correlation series for two assets."""
    window_safe = max(2, min(int(window), 504))
    request = MacroExpressionRequest(
        expr=f"rolling_corr({x},{y},{window_safe})",
        start=start,
        end=end,
        freq=cast(Any, freq),
        fill=cast(Any, fill),
        transform="level",
    )
    result = evaluate_expression_response(request)
    result.meta.title = f"rolling_corr({x},{y},{window_safe})"
    return result


def list_studies_response() -> MacroStudiesResponse:
    """List persisted macro studies."""
    _seed_macro_studies_if_needed()
    rows = list_macro_studies()
    return MacroStudiesResponse(
        status="ok",
        items=[MacroStudyPayload(**row) for row in rows],
    )


def get_study_response(study_id: str) -> MacroStudiesResponse:
    """Return one study wrapped in list response shape."""
    _seed_macro_studies_if_needed()
    row = get_macro_study(study_id)
    if row is None:
        return MacroStudiesResponse(status="not_found", message=f"Unknown study: {study_id}", items=[])
    return MacroStudiesResponse(status="ok", items=[MacroStudyPayload(**row)])


def save_study_response(payload: MacroStudyPayload) -> MacroStudiesResponse:
    """Persist a study and return the saved payload."""
    saved = save_macro_study(payload.model_dump())
    return MacroStudiesResponse(status="ok", items=[MacroStudyPayload(**saved)])


def _load_series_for_spec(
    spec: MacroStudySeriesSpec,
    *,
    start: date | None = None,
    end: date | None = None,
    as_of_date: date | None = None,
) -> tuple[pd.Series, dict[str, Any], str | None]:
    series, meta_raw, warning = _get_series_asof(spec.key, start=start, end=end, as_of_date=as_of_date)
    series = _apply_transform_chain(series, spec.transform_chain)
    series = resample_series(
        series,
        freq=cast(Any, spec.freq),
        fill=cast(Any, spec.fill),
        start=start,
        end=end,
    )
    meta = {**meta_raw}
    if spec.alias:
        meta["title"] = spec.alias
    return series, meta, warning


def get_compare_response(
    study_id: str,
    *,
    normalization: str = "raw",
    start: date | None = None,
    end: date | None = None,
    as_of_date: date | None = None,
) -> MacroCompareResponse:
    """Build normalized multi-series comparison payload for a study."""
    row = get_macro_study(study_id)
    if row is None:
        return MacroCompareResponse(status="not_found", message=f"Unknown study: {study_id}")
    study = MacroStudyPayload(**row)
    series_map: dict[str, MacroSeriesResponse] = {}
    errors: list[str] = []
    for spec in study.series_specs:
        try:
            series, meta_raw, warning = _load_series_for_spec(spec, start=start, end=end, as_of_date=as_of_date)
            normalized = _normalize_mode_for_series(series, normalization if normalization != "raw" else spec.normalize_mode)
            series_map[spec.key] = _series_response_from_series(
                spec.key,
                normalized,
                meta_raw,
                transform=normalization if normalization != "raw" else spec.normalize_mode,
                warning=warning,
            )
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{spec.key}: {exc}")
    status = "ok" if series_map and not errors else "insufficient_data"
    return MacroCompareResponse(
        status=cast(Any, status),
        message=" | ".join(errors[:5]) if errors else None,
        normalization=cast(Any, normalization),
        series=series_map,
    )


def get_leadlag_response(
    lhs: str,
    rhs: str,
    *,
    start: date | None = None,
    end: date | None = None,
    freq: str = "W",
    fill: str = "ffill",
    max_lag: int = 12,
) -> MacroLeadLagResponse:
    """Compute lead-lag correlation table for two series."""
    try:
        left, _, _ = _get_series(lhs, start=start, end=end)
        right, _, _ = _get_series(rhs, start=start, end=end)
    except Exception as exc:  # noqa: BLE001
        return MacroLeadLagResponse(status="insufficient_data", message=str(exc), lhs=lhs, rhs=rhs)

    left = resample_series(left, freq=cast(Any, freq), fill=cast(Any, fill), start=start, end=end)
    right = resample_series(right, freq=cast(Any, freq), fill=cast(Any, fill), start=start, end=end)
    left, right = left.align(right, join="inner")
    if left.dropna().empty or right.dropna().empty:
        return MacroLeadLagResponse(status="insufficient_data", message="No overlapping observations.", lhs=lhs, rhs=rhs)

    table: list[MacroLeadLagPoint] = []
    best_lag = 0
    best_corr = 0.0
    has_best = False
    max_lag_safe = max(1, min(int(max_lag), 24))
    for lag in range(-max_lag_safe, max_lag_safe + 1):
        shifted = right.shift(lag)
        corr = float(left.corr(shifted))
        if np.isnan(corr):
            corr = 0.0
        table.append(MacroLeadLagPoint(lag=lag, correlation=corr))
        if (not has_best) or abs(corr) > abs(best_corr):
            best_corr = corr
            best_lag = lag
            has_best = True

    rolling = left.rolling(window=max(3, min(26, max_lag_safe * 2)), min_periods=3).corr(right)
    return MacroLeadLagResponse(
        status="ok",
        lhs=lhs,
        rhs=rhs,
        best_lag=best_lag,
        best_correlation=best_corr,
        table=table,
        rolling_corr=_series_to_points(rolling),
    )


def get_scatter_response(
    lhs: str,
    rhs: str,
    *,
    start: date | None = None,
    end: date | None = None,
    freq: str = "W",
    fill: str = "ffill",
) -> MacroScatterResponse:
    """Build scatter payload with regression metadata."""
    try:
        left, _, _ = _get_series(lhs, start=start, end=end)
        right, _, _ = _get_series(rhs, start=start, end=end)
    except Exception as exc:  # noqa: BLE001
        return MacroScatterResponse(status="insufficient_data", message=str(exc), lhs=lhs, rhs=rhs)
    left = resample_series(left, freq=cast(Any, freq), fill=cast(Any, fill), start=start, end=end)
    right = resample_series(right, freq=cast(Any, freq), fill=cast(Any, fill), start=start, end=end)
    left, right = left.align(right, join="inner")
    frame = pd.DataFrame({"x": left, "y": right}).dropna()
    if frame.empty:
        return MacroScatterResponse(status="insufficient_data", message="No overlapping observations.", lhs=lhs, rhs=rhs)

    corr = float(frame["x"].corr(frame["y"]))
    slope: float | None = None
    intercept: float | None = None
    if len(frame) >= 2:
        slope, intercept = [float(value) for value in np.polyfit(frame["x"], frame["y"], 1)]

    points = [
        MacroScatterPoint(date=index.date().isoformat(), x=float(row["x"]), y=float(row["y"]))
        for index, row in frame.tail(250).iterrows()
    ]
    return MacroScatterResponse(
        status="ok",
        lhs=lhs,
        rhs=rhs,
        correlation=corr,
        slope=slope,
        intercept=intercept,
        points=points,
    )


def get_vintage_response(
    key: str,
    *,
    as_of_date: date,
    start: date | None = None,
    end: date | None = None,
) -> MacroVintageResponse:
    """Compare latest series against as-of vintage for one FRED key."""
    try:
        source, series_id = _normalize_key(key)
    except Exception as exc:  # noqa: BLE001
        return MacroVintageResponse(status="error", message=str(exc), key=key, as_of_date=as_of_date.isoformat())
    if source != "FRED":
        return MacroVintageResponse(
            status="insufficient_data",
            message="Vintage history is only available for FRED series.",
            key=key,
            as_of_date=as_of_date.isoformat(),
        )
    latest_rows = load_observations("FRED", series_id, start.isoformat() if start else None, end.isoformat() if end else None)
    asof_rows = load_observations_asof(
        "FRED",
        series_id,
        as_of_date=as_of_date.isoformat(),
        start=start.isoformat() if start else None,
        end=end.isoformat() if end else None,
    )
    latest = normalize_series(latest_rows)
    asof = normalize_series(asof_rows)
    latest_overlap, asof_overlap = latest.align(asof, join="inner")
    revision_delta: float | None = None
    if not latest_overlap.dropna().empty and not asof_overlap.dropna().empty:
        revision_delta = float((latest_overlap - asof_overlap).dropna().iloc[-1])
    latest_obs_date = end.isoformat() if end else (latest_rows[-1]["date"] if latest_rows else None)
    revisions = []
    if latest_obs_date:
        revisions = [MacroVintagePoint(**row) for row in load_observation_vintages("FRED", series_id, str(latest_obs_date))]
    return MacroVintageResponse(
        status="ok",
        key=key,
        as_of_date=as_of_date.isoformat(),
        latest=_series_to_points(latest),
        as_of=_series_to_points(asof),
        revisions=revisions,
        revision_delta=revision_delta,
    )


def get_release_calendar_response(domain: str | None = None) -> MacroReleaseCalendarResponse:
    """Return release-oriented metadata for catalog series."""
    bootstrap_default_catalog()
    rows = list(list_catalog_items(domain=domain))
    obs_summary_by_series = _get_catalog_obs_summaries(rows)
    items: list[MacroReleaseCalendarItem] = []
    for row in rows:
        obs_summary = obs_summary_by_series.get(
            (str(row.get("source", "FRED")), str(row.get("series_id", ""))),
            {},
        )
        last_obs = cast(str | None, obs_summary.get("last_obs"))
        items.append(
            MacroReleaseCalendarItem(
                key=str(row.get("id")),
                title=cast(str | None, row.get("title")),
                domain=cast(str | None, row.get("domain")),
                release_frequency=cast(str | None, row.get("frequency")),
                last_obs=last_obs,
                stale_days=_compute_stale_days(last_obs),
                estimated_next_release=_estimate_next_release(last_obs, cast(str | None, row.get("frequency")), cast(int | None, row.get("publish_lag"))),
                vintage_available=bool(obs_summary.get("vintage_available")),
            )
        )
    return MacroReleaseCalendarResponse(status="ok", items=items)


def create_report_response(study_id: str) -> MacroReportResponse:
    """Export one study to HTML."""
    row = get_macro_study(study_id)
    if row is None:
        return MacroReportResponse(status="not_found", message=f"Unknown study: {study_id}", study_id=study_id)
    study = MacroStudyPayload(**row)
    report_dir = MACRO_ROOT / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"{study_id}.html"
    conclusion = study.conclusion
    series_rows = "".join(
        f"<li><strong>{spec.alias or spec.key}</strong> ({spec.key}) - chain: {', '.join(spec.transform_chain) or 'level'}</li>"
        for spec in study.series_specs
    )
    linked_assets = ", ".join(study.linked_assets) or "None"
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>{study.name}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; color: #111827; }}
    h1, h2 {{ margin-bottom: 8px; }}
    .muted {{ color: #6b7280; }}
    .card {{ border: 1px solid #d1d5db; border-radius: 10px; padding: 16px; margin-top: 16px; }}
  </style>
</head>
<body>
  <h1>{study.name}</h1>
  <p class="muted">{study.objective}</p>
  <div class="card">
    <h2>Series Basket</h2>
    <ul>{series_rows}</ul>
  </div>
  <div class="card">
    <h2>Conclusion</h2>
    <p><strong>Summary:</strong> {conclusion.summary}</p>
    <p><strong>Thesis:</strong> {conclusion.thesis}</p>
    <p><strong>Action Bias:</strong> {conclusion.action_bias}</p>
    <p><strong>Confidence:</strong> {conclusion.confidence if conclusion.confidence is not None else 'n/a'}</p>
    <p><strong>Risk Cases:</strong> {', '.join(conclusion.risk_cases) or 'None'}</p>
    <p><strong>Next Checks:</strong> {', '.join(conclusion.next_checks) or 'None'}</p>
  </div>
  <div class="card">
    <h2>Notes</h2>
    <pre style="white-space: pre-wrap">{study.notes}</pre>
  </div>
  <div class="card">
    <h2>Linked Assets</h2>
    <p>{linked_assets}</p>
  </div>
</body>
</html>"""
    report_path.write_text(html, encoding="utf-8")
    attach_report_to_macro_study(
        study_id,
        report_id=None,
        title=f"Macro Study Report: {study.name}",
        report_path=str(report_path),
        created_at=utc_now_iso(),
        source_run_id=None,
        symbols=[str(item).upper() for item in study.linked_assets],
    )
    return MacroReportResponse(
        status="ok",
        study_id=study_id,
        report_path=str(report_path),
        generated_at=utc_now_iso(),
    )


def attach_report_response(
    study_id: str,
    *,
    report_id: int | None = None,
    report_path: str | None = None,
) -> MacroStudiesResponse:
    """Attach an existing report artifact to a macro study."""
    if not study_id:
        return MacroStudiesResponse(status="not_found", message="study_id is required")
    selected_report = None
    if report_id is not None:
        for item in get_reports_history_response(limit=500).items:
            if item.id == report_id:
                selected_report = item
                break
    elif report_path:
        for item in get_reports_history_response(limit=500).items:
            if str(item.report_path).strip() == str(report_path).strip():
                selected_report = item
                break
    if selected_report is None and report_path:
        saved = attach_report_to_macro_study(
            study_id,
            report_id=None,
            title=Path(report_path).stem,
            report_path=str(report_path),
            created_at=utc_now_iso(),
            symbols=[],
        )
        if saved is None:
            return MacroStudiesResponse(status="not_found", message=f"Unknown study: {study_id}")
        return MacroStudiesResponse(status="ok", items=[MacroStudyPayload(**saved)])
    if selected_report is None:
        return MacroStudiesResponse(status="not_found", message="Unknown report attachment target")
    saved = attach_report_to_macro_study(
        study_id,
        report_id=selected_report.id,
        title=selected_report.title,
        report_path=selected_report.report_path,
        created_at=selected_report.created_at,
        source_run_id=selected_report.run_id,
        symbols=selected_report.symbols,
    )
    if saved is None:
        return MacroStudiesResponse(status="not_found", message=f"Unknown study: {study_id}")
    return MacroStudiesResponse(status="ok", items=[MacroStudyPayload(**saved)])


def export_features_response(study_id: str, *, as_of_policy: str = "latest") -> MacroFeatureExportResponse:
    """Export feature lineage metadata derived from a study."""
    row = get_macro_study(study_id)
    if row is None:
        return MacroFeatureExportResponse(status="not_found", message=f"Unknown study: {study_id}", study_id=study_id)
    study = MacroStudyPayload(**row)
    items = [
        MacroFeatureExportItem(
            feature_name=f"{(spec.alias or spec.key).lower().replace(':', '_').replace(' ', '_')}_{'_'.join(spec.transform_chain or ['level'])}",
            source_study_id=study_id,
            key=spec.key,
            transform_chain=spec.transform_chain,
            lag_rule=spec.lag_mode,
            as_of_policy=as_of_policy,
        )
        for spec in study.series_specs
    ]
    export_dir = MACRO_ROOT / "feature_exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = export_dir / f"{study_id}.json"
    save_json(
        artifact_path,
        {
            "study_id": study_id,
            "exported_at": utc_now_iso(),
            "items": [item.model_dump() for item in items],
        },
    )
    return MacroFeatureExportResponse(
        status="ok",
        study_id=study_id,
        artifact_path=str(artifact_path),
        exported_at=utc_now_iso(),
        items=items,
    )


def bootstrap_default_derived_expressions() -> None:
    """Bootstrap default derived expressions from macro config once per process."""
    global _DERIVED_BOOTSTRAPPED
    if _DERIVED_BOOTSTRAPPED:
        return

    cfg = load_macro_config()
    defaults = cfg.get("derived_defaults", [])
    if not isinstance(defaults, list) or not defaults:
        _DERIVED_BOOTSTRAPPED = True
        return

    resolver = _resolver_factory(None, None, "native", "ffill")
    for item in defaults:
        if not isinstance(item, dict):
            continue
        derived_id = str(item.get("derived_id", "")).strip()
        expression = str(item.get("expression", "")).strip()
        default_transform = str(item.get("default_transform", "level")).strip() or "level"
        if not derived_id or not expression:
            continue
        try:
            deps = evaluate_expression(expression, resolver=resolver).dependencies
        except Exception:
            deps = []
        save_derived_expression(
            derived_id=derived_id,
            expression=expression,
            dependencies=deps,
            default_transform=default_transform,
            is_favorite=True,
        )
    _DERIVED_BOOTSTRAPPED = True


def get_copper_gold_preset_response(
    *,
    start: date | None = None,
    end: date | None = None,
    freq: str = "W",
    fill: str = "ffill",
    scale: float = 1000.0,
    adjust_units: bool = True,
    yield_key: str = "FRED:DGS10",
    corr_window: int = 52,
    slope_window: int = 13,
    divergence_min_weeks: int = 4,
    include_corr: bool = True,
) -> MacroPresetResponse:
    """Return copper/gold preset payload with DGS10 and divergence events."""
    resolver = _resolver_factory(start=start, end=end, freq=freq, fill=fill)
    return build_copper_gold_preset_response(
        resolver=resolver,
        start=start,
        end=end,
        freq=freq,
        fill=fill,
        scale=scale,
        adjust_units=adjust_units,
        yield_key=yield_key,
        corr_window=corr_window,
        slope_window=slope_window,
        divergence_min_weeks=divergence_min_weeks,
        include_corr=include_corr,
    )
