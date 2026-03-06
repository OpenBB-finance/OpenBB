"""Dashboard-friendly trading response adapters."""

from __future__ import annotations

from typing import Any


def build_trading_status_payload(
    *,
    settings: dict[str, Any],
    account_state: dict[str, Any],
    positions: list[dict[str, Any]],
    latest_signals: list[dict[str, Any]],
    latest_orders: list[dict[str, Any]],
    performance: dict[str, Any],
) -> dict[str, Any]:
    """Build the high-level trading status snapshot used by the UI."""
    runtime_status = str(account_state.get("runtime_status", settings.get("runtime_status", "stopped")) or "stopped")
    return {
        "mode": str(settings.get("execution", {}).get("mode", settings.get("mode", "paper")) or "paper"),
        "runtime_status": runtime_status,
        "last_scan_at": account_state.get("last_scan_at"),
        "last_order_at": account_state.get("last_order_at"),
        "active_strategy_count": sum(
            1 for row in (settings.get("strategies", {}) or {}).values() if isinstance(row, dict) and bool(row.get("enabled", False))
        ),
        "watchlist_size": int(account_state.get("watchlist_size", 0) or 0),
        "open_position_count": len([row for row in positions if float(row.get("quantity", 0.0) or 0.0) > 0.0]),
        "today_signal_count": int(account_state.get("today_signal_count", len(latest_signals)) or 0),
        "today_order_count": int(account_state.get("today_order_count", len(latest_orders)) or 0),
        "today_realized_pnl": float(account_state.get("today_realized_pnl", 0.0) or 0.0),
        "cumulative_pnl": float(performance.get("total_pnl", account_state.get("total_pnl", 0.0)) or 0.0),
        "intraday_drawdown": float(account_state.get("current_drawdown", 0.0) or 0.0),
        "used_capital": float(account_state.get("used_capital", 0.0) or 0.0),
        "available_cash": float(account_state.get("cash", settings.get("account", {}).get("initial_cash", 0.0)) or 0.0),
        "report_urls": list(account_state.get("report_urls", []) or []),
    }
