"""Macro alert rule evaluation and persistence."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pandas as pd

from openbb_quant_ml.service.macro_constants import load_macro_config
from openbb_quant_ml.service.macro_db import list_alert_events, save_alert_events
from openbb_quant_ml.service.macro_expression import evaluate_expression


def _to_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _metric_from_name(
    metric_name: str,
    regime_df: pd.DataFrame,
    resolver,
) -> pd.Series:
    if metric_name in regime_df.columns:
        return pd.to_numeric(regime_df[metric_name], errors="coerce")

    # Special form: DGS10-CPIAUCSL_yoy
    if metric_name.endswith("_yoy") and "-" in metric_name:
        left, right_yoy = metric_name.split("-", 1)
        if right_yoy.endswith("_yoy"):
            right = right_yoy[: -len("_yoy")]
            left_series = evaluate_expression(left, resolver=resolver).series
            right_series = evaluate_expression(right, resolver=resolver).series.pct_change(periods=12, fill_method=None)
            aligned_left, aligned_right = left_series.align(right_series, join="outer")
            return aligned_left - aligned_right

    return evaluate_expression(metric_name, resolver=resolver).series


def evaluate_alerts(
    regime_df: pd.DataFrame,
    resolver,
) -> list[dict[str, object]]:
    """Evaluate current alert rules and return triggered items."""
    cfg = load_macro_config()
    rules = cfg.get("alerts", []) or []
    out: list[dict[str, object]] = []
    now = _now_iso()
    for rule in rules:
        rule_id = str(rule.get("rule_id", "")).strip() or uuid4().hex
        metric = str(rule.get("metric", "")).strip()
        op = str(rule.get("op", ">")).strip().lower()
        threshold = _to_float(rule.get("threshold"), 0.0)
        severity = str(rule.get("severity", "warning")).lower()
        lookback_days = int(rule.get("lookback_days", 20))
        if not metric:
            continue

        try:
            series = _metric_from_name(metric, regime_df, resolver).dropna().sort_index()
        except Exception:  # noqa: BLE001
            continue
        if series.empty:
            continue

        latest = float(series.iloc[-1])
        triggered = False
        if op == ">":
            triggered = latest > threshold
        elif op == ">=":
            triggered = latest >= threshold
        elif op == "<":
            triggered = latest < threshold
        elif op == "<=":
            triggered = latest <= threshold
        elif op == "delta_gt":
            past_time = series.index[-1] - pd.Timedelta(days=max(1, lookback_days))
            past_slice = series[series.index <= past_time]
            if past_slice.empty:
                continue
            delta = latest - float(past_slice.iloc[-1])
            latest = delta
            triggered = delta > threshold
        else:
            continue

        if not triggered:
            continue

        message = (
            f"{rule_id}: {metric} {op} {threshold:.4f} "
            f"(value={latest:.4f})"
        )
        out.append(
            {
                "event_id": uuid4().hex,
                "rule_id": rule_id,
                "severity": severity if severity in {"info", "warning", "critical"} else "warning",
                "triggered_at": now,
                "message": message,
                "value": latest,
                "threshold": threshold,
                "context": {"metric": metric, "operator": op},
            }
        )
    return out


def persist_and_get_alerts(current_alerts: list[dict[str, object]], history_limit: int = 200) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Save current alerts and return current/history payloads."""
    if current_alerts:
        save_alert_events(current_alerts)
    history = list_alert_events(limit=history_limit)
    return current_alerts, history
