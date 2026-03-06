"""Risk checks for the trading runtime."""

from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime
from typing import Any

import pandas as pd


def _now() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def evaluate_signal_risk(
    *,
    signal: dict[str, Any],
    settings: dict[str, Any],
    account_state: dict[str, Any],
    positions: list[dict[str, Any]],
    existing_orders: list[dict[str, Any]],
    symbol_frame: pd.DataFrame,
    symbol_meta: dict[str, Any],
    strategy_enabled: bool,
    algorithm_status: str | None = None,
    allow_auto_order: bool = True,
) -> dict[str, Any]:
    """Evaluate one normalized signal against runtime risk rules."""
    checks: list[dict[str, Any]] = []
    risk_cfg = settings.get("risk", {})
    account_cfg = settings.get("account", {})
    execution_cfg = settings.get("execution", {})

    def fail(rule_id: str, message: str, severity: str = "critical", value: Any = None, limit: Any = None) -> None:
        checks.append(
            {
                "rule_id": rule_id,
                "passed": False,
                "severity": severity,
                "message": message,
                "value": value,
                "limit": limit,
            }
        )

    def passed(rule_id: str, value: Any = None, limit: Any = None) -> None:
        checks.append(
            {
                "rule_id": rule_id,
                "passed": True,
                "severity": "info",
                "message": "passed",
                "value": value,
                "limit": limit,
            }
        )

    if not strategy_enabled:
        fail("strategy_disabled", "strategy disabled", value=0, limit=1)
    else:
        passed("strategy_enabled")

    if algorithm_status and algorithm_status in {"draft", "dev", "paused", "deprecated"}:
        fail("algorithm_status", f"algorithm status blocks execution: {algorithm_status}", value=algorithm_status, limit="sandbox|validated|active")
    else:
        passed("algorithm_status", value=algorithm_status or "builtin")

    if not bool(execution_cfg.get("signal_generation", True)):
        fail("signal_generation_disabled", "signal generation is disabled", value=0, limit=1)
    else:
        passed("signal_generation_enabled")

    if symbol_frame.empty:
        fail("stale_data", "no market data available", value=0, limit=1)
    else:
        latest_date = pd.to_datetime(symbol_frame["date"]).max()
        age_days = max(0, int((_now().date() - latest_date.date()).days))
        max_delay = int(settings.get("scan", {}).get("max_data_delay_days", 5) or 5)
        if age_days > max_delay:
            fail("stale_data", "stale data", value=age_days, limit=max_delay)
        else:
            passed("stale_data", value=age_days, limit=max_delay)

    latest = symbol_frame.iloc[-1] if not symbol_frame.empty else pd.Series(dtype=float)
    avg_dollar_volume = float(latest.get("avg_dollar_volume", 0.0) or 0.0)
    if avg_dollar_volume <= 0.0 and not symbol_frame.empty:
        prices = pd.to_numeric(symbol_frame.get("close", pd.Series(dtype=float)), errors="coerce").fillna(0.0)
        volumes = pd.to_numeric(symbol_frame.get("volume", pd.Series(dtype=float)), errors="coerce").fillna(0.0)
        avg_dollar_volume = float((prices * volumes).tail(20).mean() or 0.0)
    min_adv = float(risk_cfg.get("min_avg_dollar_volume", 0.0) or 0.0)
    if avg_dollar_volume < min_adv:
        fail("insufficient_liquidity", "insufficient liquidity", value=avg_dollar_volume, limit=min_adv)
    else:
        passed("liquidity", value=avg_dollar_volume, limit=min_adv)

    atr_pct = float(latest.get("atr_pct", 0.0) or 0.0)
    if atr_pct <= 0.0 and not symbol_frame.empty:
        highs = pd.to_numeric(symbol_frame.get("high", pd.Series(dtype=float)), errors="coerce").fillna(0.0)
        lows = pd.to_numeric(symbol_frame.get("low", pd.Series(dtype=float)), errors="coerce").fillna(0.0)
        closes = pd.to_numeric(symbol_frame.get("close", pd.Series(dtype=float)), errors="coerce").fillna(0.0)
        prev_close = closes.shift(1)
        tr = pd.concat(
            [
                (highs - lows).abs(),
                (highs - prev_close).abs(),
                (lows - prev_close).abs(),
            ],
            axis=1,
        ).max(axis=1)
        close_now = float(closes.iloc[-1] or 0.0) if not closes.empty else 0.0
        atr_pct = 0.0 if close_now <= 0.0 else float(tr.tail(14).mean() or 0.0) / close_now
    max_atr_pct = float(risk_cfg.get("max_atr_pct", 1.0) or 1.0)
    if atr_pct > max_atr_pct:
        fail("volatility_filter_failed", "volatility filter failed", severity="warning", value=atr_pct, limit=max_atr_pct)
    else:
        passed("volatility", value=atr_pct, limit=max_atr_pct)

    available_cash = float(account_state.get("cash", account_cfg.get("initial_cash", 0.0)) or 0.0)
    capital_cap = float(risk_cfg.get("capital_cap", account_cfg.get("initial_cash", 0.0)) or 0.0)
    used_capital = float(account_state.get("used_capital", 0.0) or 0.0)
    if capital_cap > 0.0 and used_capital >= capital_cap:
        fail("capital_exceeded", "capital exceeded", value=used_capital, limit=capital_cap)
    else:
        passed("capital_cap", value=used_capital, limit=capital_cap)

    daily_realized = float(account_state.get("today_realized_pnl", 0.0) or 0.0)
    daily_loss_limit = float(risk_cfg.get("daily_loss_limit", 0.0) or 0.0)
    if daily_loss_limit > 0.0 and daily_realized <= -daily_loss_limit:
        fail("daily_loss_limit", "daily loss limit exceeded", value=daily_realized, limit=-daily_loss_limit)
    else:
        passed("daily_loss_limit", value=daily_realized, limit=-daily_loss_limit)

    drawdown = float(account_state.get("current_drawdown", 0.0) or 0.0)
    dd_limit = float(risk_cfg.get("portfolio_drawdown_limit", 1.0) or 1.0)
    if drawdown <= -abs(dd_limit):
        fail("drawdown_limit", "portfolio drawdown limit exceeded", value=drawdown, limit=-abs(dd_limit))
    else:
        passed("drawdown_limit", value=drawdown, limit=-abs(dd_limit))

    open_positions = [row for row in positions if float(row.get("quantity", 0.0) or 0.0) > 0.0]
    max_positions = int(account_cfg.get("max_concurrent_positions", 10) or 10)
    ticker = str(signal.get("ticker", "") or "")
    side = str(signal.get("side", "buy") or "buy").lower()
    has_position = any(str(row.get("ticker", "")) == ticker for row in open_positions)
    if side == "buy" and not has_position and len(open_positions) >= max_positions:
        fail("max_positions_reached", "max positions reached", value=len(open_positions), limit=max_positions)
    else:
        passed("max_positions", value=len(open_positions), limit=max_positions)

    if not bool(risk_cfg.get("allow_duplicate_exposure", False)):
        duplicate_order = any(
            str(row.get("ticker", "")) == ticker and str(row.get("status", "")).lower() in {"pending", "submitted"}
            for row in existing_orders
        )
        if (has_position and side == "buy") or duplicate_order:
            fail("duplicate_exposure_blocked", "duplicate exposure blocked", severity="warning", value=1, limit=0)
        else:
            passed("duplicate_exposure")
    else:
        passed("duplicate_exposure_allowed")

    sector = str(symbol_meta.get("sector_l1", symbol_meta.get("category", "other")) or "other")
    sector_weights: dict[str, float] = defaultdict(float)
    equity = float(account_state.get("equity", account_cfg.get("initial_cash", 0.0)) or 0.0)
    for row in open_positions:
        row_sector = str(row.get("sector", "other") or "other")
        value = float(row.get("position_value", 0.0) or 0.0)
        if equity > 0:
            sector_weights[row_sector] += value / equity
    sector_limit = float(risk_cfg.get("max_sector_weight", 1.0) or 1.0)
    pending_weight = float(signal.get("proposed_weight", 0.0) or 0.0)
    if side == "buy" and equity > 0 and sector_weights[sector] + pending_weight > sector_limit:
        fail("sector_concentration", "sector concentration limit exceeded", severity="warning", value=sector_weights[sector] + pending_weight, limit=sector_limit)
    else:
        passed("sector_concentration", value=sector_weights.get(sector, 0.0), limit=sector_limit)

    daily_orders = int(account_state.get("today_order_count", 0) or 0)
    max_daily_orders = int(account_cfg.get("max_daily_orders", 20) or 20)
    if daily_orders >= max_daily_orders:
        fail("daily_orders_cap", "max daily orders reached", value=daily_orders, limit=max_daily_orders)
    else:
        passed("daily_orders_cap", value=daily_orders, limit=max_daily_orders)

    approved = all(bool(item.get("passed", False)) for item in checks if item["severity"] in {"critical", "warning"})
    if not allow_auto_order and side == "buy":
        approved = False
        fail("auto_order_disabled", "automatic order creation is disabled", severity="info", value=0, limit=1)
    return {
        "passed": approved,
        "checks": checks,
        "status": "passed" if approved else "blocked",
        "reason_codes": [item["rule_id"] for item in checks if not item["passed"]],
    }
