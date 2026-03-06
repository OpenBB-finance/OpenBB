"""Portfolio and account state persistence for the trading runtime."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from openbb_quant_ml.service.trading.storage import (
    account_state_path,
    closed_positions_path,
    load_frame,
    load_runtime_json,
    open_positions_path,
    save_frame,
    save_runtime_json,
)


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def load_account_state(initial_cash: float) -> dict[str, Any]:
    """Load or initialize runtime account state."""
    payload = load_runtime_json(account_state_path(), default={})
    if not isinstance(payload, dict) or not payload:
        payload = {
            "mode": "paper",
            "runtime_status": "stopped",
            "initial_cash": float(initial_cash),
            "cash": float(initial_cash),
            "equity": float(initial_cash),
            "used_capital": 0.0,
            "realized_pnl": 0.0,
            "unrealized_pnl": 0.0,
            "total_pnl": 0.0,
            "today_realized_pnl": 0.0,
            "today_signal_count": 0,
            "today_order_count": 0,
            "today_fill_count": 0,
            "equity_peak": float(initial_cash),
            "current_drawdown": 0.0,
            "last_scan_at": None,
            "last_order_at": None,
            "last_fill_at": None,
            "last_cycle_id": None,
            "error_count": 0,
            "recent_exits": {},
        }
    return payload


def save_account_state(payload: dict[str, Any]) -> dict[str, Any]:
    payload = dict(payload)
    save_runtime_json(account_state_path(), payload)
    return payload


def load_open_positions() -> list[dict[str, Any]]:
    payload = load_runtime_json(open_positions_path(), default={"items": []})
    if not isinstance(payload, dict):
        return []
    items = payload.get("items", [])
    return [item for item in items if isinstance(item, dict)]


def save_open_positions(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    clean = [dict(item) for item in items if float(item.get("quantity", 0.0) or 0.0) > 0.0]
    save_runtime_json(open_positions_path(), {"items": clean})
    return clean


def append_closed_position(item: dict[str, Any]) -> None:
    frame = load_frame(closed_positions_path())
    next_frame = frame
    import pandas as pd  # local import to avoid import cycles

    incoming = pd.DataFrame([item])
    if frame.empty:
        next_frame = incoming
    else:
        next_frame = pd.concat([frame, incoming], ignore_index=True)
    save_frame(closed_positions_path(), next_frame)


def apply_fill_to_portfolio(
    *,
    fill: dict[str, Any],
    account_state: dict[str, Any],
    positions: list[dict[str, Any]],
    symbol_meta: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any] | None]:
    """Apply one filled order to the account state and open positions."""
    next_account = dict(account_state)
    next_positions = [dict(item) for item in positions]
    ticker = str(fill.get("ticker", "")).upper()
    side = str(fill.get("side", "buy")).lower()
    price = float(fill.get("price", 0.0) or 0.0)
    qty = float(fill.get("quantity", 0.0) or 0.0)
    fee = float(fill.get("fee", 0.0) or 0.0)
    filled_at = str(fill.get("filled_at") or _now_iso())
    realized_close: dict[str, Any] | None = None

    match_index = next((idx for idx, row in enumerate(next_positions) if str(row.get("ticker", "")).upper() == ticker), None)
    if side == "buy":
        if match_index is None:
            next_positions.append(
                {
                    "ticker": ticker,
                    "strategy": str(fill.get("strategy_name", "") or ""),
                    "entry_time": filled_at,
                    "entry_price": price,
                    "current_price": price,
                    "quantity": qty,
                    "position_value": qty * price,
                    "unrealized_pnl": 0.0,
                    "realized_pnl": 0.0,
                    "pnl_pct": 0.0,
                    "holding_period_days": 0,
                    "stop_loss_level": None,
                    "take_profit_level": None,
                    "trailing_stop_level": None,
                    "exit_signal_status": "hold",
                    "sector": str(symbol_meta.get("sector_l1", symbol_meta.get("category", "other")) or "other"),
                    "name": str(symbol_meta.get("name", ticker) or ticker),
                }
            )
        else:
            row = dict(next_positions[match_index])
            old_qty = float(row.get("quantity", 0.0) or 0.0)
            old_price = float(row.get("entry_price", 0.0) or 0.0)
            new_qty = old_qty + qty
            row["entry_price"] = ((old_qty * old_price) + (qty * price)) / max(new_qty, 1e-12)
            row["quantity"] = new_qty
            row["current_price"] = price
            row["position_value"] = new_qty * price
            next_positions[match_index] = row
        next_account["cash"] = float(next_account.get("cash", 0.0) or 0.0) - (qty * price) - fee
        next_account["last_fill_at"] = filled_at
    else:
        if match_index is None:
            return next_account, next_positions, None
        row = dict(next_positions[match_index])
        old_qty = float(row.get("quantity", 0.0) or 0.0)
        entry_price = float(row.get("entry_price", 0.0) or 0.0)
        sell_qty = min(old_qty, qty)
        realized = (price - entry_price) * sell_qty - fee
        row["quantity"] = old_qty - sell_qty
        row["current_price"] = price
        row["position_value"] = max(row["quantity"], 0.0) * price
        row["realized_pnl"] = float(row.get("realized_pnl", 0.0) or 0.0) + realized
        if row["quantity"] <= 1e-12:
            realized_close = {
                **row,
                "exit_time": filled_at,
                "exit_price": price,
                "closed_quantity": sell_qty,
                "realized_pnl": row["realized_pnl"],
            }
            del next_positions[match_index]
        else:
            next_positions[match_index] = row
        next_account["cash"] = float(next_account.get("cash", 0.0) or 0.0) + (sell_qty * price) - fee
        next_account["realized_pnl"] = float(next_account.get("realized_pnl", 0.0) or 0.0) + realized
        next_account["today_realized_pnl"] = float(next_account.get("today_realized_pnl", 0.0) or 0.0) + realized
        next_account["last_fill_at"] = filled_at
        if realized_close is not None:
            recent_exits = dict(next_account.get("recent_exits", {}) or {})
            recent_exits[ticker] = filled_at
            next_account["recent_exits"] = recent_exits

    return next_account, next_positions, realized_close
