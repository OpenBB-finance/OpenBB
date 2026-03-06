"""Order intent builder for the trading runtime."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def build_order_intent(
    *,
    signal: dict[str, Any],
    settings: dict[str, Any],
    account_state: dict[str, Any],
    existing_position: dict[str, Any] | None,
    price: float,
) -> dict[str, Any] | None:
    """Build one order intent from a normalized signal."""
    if price <= 0.0:
        return None
    account_cfg = settings.get("account", {})
    risk_cfg = settings.get("risk", {})
    signal_type = str(signal.get("signal_type", signal.get("signal", "entry"))).lower()
    side = str(signal.get("side", "buy")).lower()
    ticker = str(signal.get("ticker", "")).upper()
    strategy_name = str(signal.get("strategy_name", "unknown"))
    if signal_type == "entry" and side == "buy":
        mode = str(account_cfg.get("position_size_mode", "percent") or "percent")
        size_value = float(account_cfg.get("position_size_value", 0.05) or 0.05)
        equity = float(account_state.get("equity", account_cfg.get("initial_cash", 0.0)) or 0.0)
        notional = equity * size_value if mode == "percent" else size_value
        notional = min(
            notional,
            float(account_cfg.get("max_order_notional", notional) or notional),
            float(account_state.get("cash", 0.0) or 0.0),
        )
        if notional <= 0.0:
            return None
        quantity = max(notional / price, 0.0)
    elif signal_type == "exit" and existing_position is not None:
        quantity = float(existing_position.get("quantity", 0.0) or 0.0)
        notional = quantity * price
        side = "sell"
    else:
        return None
    if quantity <= 0.0:
        return None
    stop_loss_pct = float(risk_cfg.get("stop_loss_pct", 0.08) or 0.08)
    take_profit_pct = float(risk_cfg.get("take_profit_pct", 0.15) or 0.15)
    trailing_enabled = bool(risk_cfg.get("trailing_stop_enabled", False))
    trailing_pct = float(risk_cfg.get("trailing_stop_pct", 0.05) or 0.05)
    stop_loss = (
        float(signal.get("stop_loss_hint"))
        if signal.get("stop_loss_hint") not in {None, "", "nan"}
        else price * (1.0 - stop_loss_pct)
    )
    take_profit = (
        float(signal.get("take_profit_hint"))
        if signal.get("take_profit_hint") not in {None, "", "nan"}
        else price * (1.0 + take_profit_pct)
    )
    trailing_stop = price * (1.0 - trailing_pct) if trailing_enabled and side == "buy" else None
    proposed_weight = notional / max(float(account_state.get("equity", 1.0) or 1.0), 1.0)
    return {
        "order_id": f"trd-{uuid4().hex[:12]}",
        "created_at": _now_iso(),
        "ticker": ticker,
        "strategy_name": strategy_name,
        "signal_id": signal.get("signal_id"),
        "status": "pending",
        "side": side,
        "signal_type": signal_type,
        "quantity": float(quantity),
        "requested_price": float(price),
        "filled_price": None,
        "notional": float(notional),
        "stop_loss": float(stop_loss),
        "take_profit": float(take_profit),
        "trailing_stop": float(trailing_stop) if trailing_stop is not None else None,
        "reason": str(signal.get("reason", "") or ""),
        "proposed_weight": float(proposed_weight),
        "metadata": {
            "strength": float(signal.get("strength", 0.0) or 0.0),
            "confidence": float(signal.get("confidence", 0.0) or 0.0),
        },
    }
