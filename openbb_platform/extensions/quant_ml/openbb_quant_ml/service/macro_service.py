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
    MacroRegimePoint,
    MacroRegimeResponse,
    MacroSeriesMeta,
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
from openbb_quant_ml.service.macro_db import (
    list_alert_events,
    list_derived_expressions,
    load_observations,
    save_derived_expression,
)
from openbb_quant_ml.service.macro_expression import MacroExpressionError, evaluate_expression
from openbb_quant_ml.service.macro_market import get_market_series
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
    updated = update_series_ids([series_id], start=start, end=end)
    if not updated:
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


def trigger_update_response(request: MacroUpdateRequest) -> MacroUpdateResponse:
    """Trigger on-demand refresh."""
    try:
        if request.all_default:
            updated = update_all_defaults(start=request.start, end=request.end)
        else:
            updated = update_series_ids(request.series_ids or [], start=request.start, end=request.end)
    except Exception as exc:  # noqa: BLE001
        return MacroUpdateResponse(status="error", message=str(exc), updated_series=[])
    if not updated:
        return MacroUpdateResponse(
            status="insufficient_data",
            message="No series updated. Check FRED_API_KEY or requested series IDs.",
            updated_series=[],
        )
    return MacroUpdateResponse(status="ok", updated_series=updated)
