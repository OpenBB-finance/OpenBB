"""Macro endpoint service orchestration."""

from __future__ import annotations

from datetime import date
from typing import Any, cast

import pandas as pd

from openbb_quant_ml.macro_models import (
    MacroAlertItem,
    MacroAlertsResponse,
    MacroCatalogItem,
    MacroCatalogResponse,
    MacroDataPoint,
    MacroDerivedItem,
    MacroDerivedResponse,
    MacroExpressionRequest,
    MacroExpressionResponse,
    MacroHealthFeatureStats,
    MacroHealthObsStats,
    MacroHealthResponse,
    MacroPresetResponse,
    MacroRegimePoint,
    MacroRegimeResponse,
    MacroRegimeStateResponse,
    MacroSeriesMeta,
    MacroSeriesMultiResponse,
    MacroSeriesQuery,
    MacroSeriesResponse,
    MacroSeriesStats,
    MacroUpdateRequest,
    MacroUpdateResponse,
)
from openbb_quant_ml.service.macro_alerts import evaluate_alerts, persist_and_get_alerts
from openbb_quant_ml.service.macro_catalog import (
    bootstrap_default_catalog,
    list_catalog_items,
    register_series,
    resolve_catalog_item,
    search_catalog,
)
from openbb_quant_ml.service.macro_constants import MACRO_DB_PATH, load_macro_config
from openbb_quant_ml.service.macro_db import (
    get_macro_feature_health_stats,
    get_macro_obs_health_stats,
    list_alert_events,
    list_derived_expressions,
    load_observations,
    save_derived_expression,
)
from openbb_quant_ml.service.macro_expression import MacroExpressionError, evaluate_expression
from openbb_quant_ml.service.macro_fred_client import FredClient
from openbb_quant_ml.service.macro_market import get_market_series
from openbb_quant_ml.service.macro_presets import get_copper_gold_preset_response as build_copper_gold_preset_response
from openbb_quant_ml.service.macro_regime import compute_regime_scores
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
    has_fred_api_key = FredClient().has_api_key
    updated = update_series_ids([series_id], start=start, end=end)
    if not updated and not has_fred_api_key:
        warning = "missing_api_key_cache_fallback"
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


def _resolver_factory(start: date | None, end: date | None, freq: str, fill: str):
    cache: dict[str, pd.Series] = {}

    def resolver(symbol_key: str) -> pd.Series:
        key = symbol_key.strip()
        if key in cache:
            return cache[key]
        series, _, _ = _get_series(key, start=start, end=end)
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
    items = [MacroCatalogItem(**row) for row in list_catalog_items(domain=domain)]
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


def get_health_response() -> MacroHealthResponse:
    """Return macro storage/update health summary for UI diagnostics."""
    warnings: list[str] = []
    fred_api_key_configured = FredClient().has_api_key
    if not fred_api_key_configured:
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
