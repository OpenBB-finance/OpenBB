"""Performance aggregation for the trading runtime."""

from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime
from typing import Any

import numpy as np
import pandas as pd

from openbb_quant_ml.service.trading.storage import (
    latest_performance_path,
    load_frame,
    performance_history_path,
    save_frame,
    save_runtime_json,
)


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def update_positions_market_values(
    positions: list[dict[str, Any]],
    prices: dict[str, float],
) -> list[dict[str, Any]]:
    """Attach current price, value, pnl, and holding period to open positions."""
    rows: list[dict[str, Any]] = []
    now = datetime.now(UTC)
    for item in positions:
        row = dict(item)
        ticker = str(row.get("ticker", "")).upper()
        price = float(prices.get(ticker, row.get("current_price", row.get("entry_price", 0.0))) or 0.0)
        qty = float(row.get("quantity", 0.0) or 0.0)
        entry = float(row.get("entry_price", 0.0) or 0.0)
        value = qty * price
        unrealized = (price - entry) * qty
        row["current_price"] = price
        row["position_value"] = value
        row["unrealized_pnl"] = unrealized
        row["pnl_pct"] = 0.0 if entry <= 0.0 else (price / entry) - 1.0
        try:
            entry_time = datetime.fromisoformat(str(row.get("entry_time")).replace("Z", "+00:00"))
            row["holding_period_days"] = max((now - entry_time).days, 0)
        except Exception:
            row["holding_period_days"] = 0
        rows.append(row)
    return rows


def build_performance_snapshot(
    *,
    settings: dict[str, Any],
    account_state: dict[str, Any],
    open_positions: list[dict[str, Any]],
    fills: pd.DataFrame,
    closed_positions: pd.DataFrame,
) -> dict[str, Any]:
    """Compute the latest paper-trading performance snapshot."""
    initial_cash = float(account_state.get("initial_cash", settings.get("account", {}).get("initial_cash", 1_000_000.0)) or 1_000_000.0)
    cash = float(account_state.get("cash", initial_cash) or initial_cash)
    used_capital = float(sum(float(item.get("position_value", 0.0) or 0.0) for item in open_positions))
    unrealized = float(sum(float(item.get("unrealized_pnl", 0.0) or 0.0) for item in open_positions))
    realized = float(account_state.get("realized_pnl", 0.0) or 0.0)
    total_pnl = realized + unrealized
    equity = cash + used_capital
    return_pct = 0.0 if initial_cash <= 0.0 else total_pnl / initial_cash
    equity_peak = max(float(account_state.get("equity_peak", initial_cash) or initial_cash), equity)
    drawdown = 0.0 if equity_peak <= 0.0 else (equity / equity_peak) - 1.0
    fill_count = int(len(fills)) if not fills.empty else 0
    closed_count = int(len(closed_positions)) if not closed_positions.empty else 0
    winning = 0
    avg_win = 0.0
    avg_loss = 0.0
    profit_factor = 0.0
    avg_holding_period = 0.0
    if closed_count > 0:
        pnl_series = pd.to_numeric(closed_positions.get("realized_pnl", pd.Series(dtype=float)), errors="coerce").fillna(0.0)
        winning = int((pnl_series > 0.0).sum())
        wins = pnl_series[pnl_series > 0.0]
        losses = pnl_series[pnl_series < 0.0]
        avg_win = float(wins.mean()) if not wins.empty else 0.0
        avg_loss = float(losses.mean()) if not losses.empty else 0.0
        gross_profit = float(wins.sum()) if not wins.empty else 0.0
        gross_loss = abs(float(losses.sum())) if not losses.empty else 0.0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0.0
        avg_holding_period = float(pd.to_numeric(closed_positions.get("holding_period_days", pd.Series(dtype=float)), errors="coerce").fillna(0.0).mean())
    daily_frame = load_frame(performance_history_path())
    if daily_frame.empty:
        returns = pd.Series(dtype=float)
    else:
        returns = pd.to_numeric(daily_frame.get("return_pct", pd.Series(dtype=float)), errors="coerce").fillna(0.0)
    sharpe = 0.0
    sortino = 0.0
    if not returns.empty and returns.std(ddof=0) > 0:
        sharpe = float((returns.mean() / returns.std(ddof=0)) * np.sqrt(252))
        downside = returns[returns < 0.0]
        if not downside.empty and downside.std(ddof=0) > 0:
            sortino = float((returns.mean() / downside.std(ddof=0)) * np.sqrt(252))
    max_drawdown = float(pd.to_numeric(daily_frame.get("drawdown", pd.Series(dtype=float)), errors="coerce").min()) if not daily_frame.empty else float(drawdown)
    turnover = 0.0
    if not fills.empty:
        turnover = float(pd.to_numeric(fills.get("notional", pd.Series(dtype=float)), errors="coerce").fillna(0.0).tail(20).sum() / max(initial_cash, 1.0))
    strategy_contribution: dict[str, float] = defaultdict(float)
    ticker_contribution: dict[str, float] = defaultdict(float)
    if not closed_positions.empty:
        for _, row in closed_positions.iterrows():
            strategy_contribution[str(row.get("strategy", ""))] += float(row.get("realized_pnl", 0.0) or 0.0)
            ticker_contribution[str(row.get("ticker", ""))] += float(row.get("realized_pnl", 0.0) or 0.0)
    return {
        "as_of_date": _now_iso()[:10],
        "generated_at": _now_iso(),
        "equity": equity,
        "cash": cash,
        "used_capital": used_capital,
        "realized_pnl": realized,
        "unrealized_pnl": unrealized,
        "total_pnl": total_pnl,
        "cumulative_return": return_pct,
        "daily_return": float(returns.iloc[-1]) if not returns.empty else return_pct,
        "weekly_return": float(returns.tail(5).sum()) if not returns.empty else return_pct,
        "monthly_return": float(returns.tail(21).sum()) if not returns.empty else return_pct,
        "win_rate": 0.0 if closed_count <= 0 else winning / closed_count,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "profit_factor": profit_factor,
        "sharpe": sharpe,
        "sortino": sortino,
        "max_drawdown": max_drawdown,
        "turnover": turnover,
        "avg_holding_period": avg_holding_period,
        "strategy_contribution": dict(strategy_contribution),
        "ticker_contribution": dict(ticker_contribution),
    }


def persist_performance_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Persist the latest daily performance row and snapshot."""
    frame = load_frame(performance_history_path())
    import pandas as pd  # local import

    incoming = pd.DataFrame(
        [
            {
                "as_of_date": snapshot.get("as_of_date"),
                "equity": snapshot.get("equity", 0.0),
                "cash": snapshot.get("cash", 0.0),
                "used_capital": snapshot.get("used_capital", 0.0),
                "realized_pnl": snapshot.get("realized_pnl", 0.0),
                "unrealized_pnl": snapshot.get("unrealized_pnl", 0.0),
                "total_pnl": snapshot.get("total_pnl", 0.0),
                "return_pct": snapshot.get("daily_return", 0.0),
                "drawdown": snapshot.get("max_drawdown", 0.0),
                "turnover": snapshot.get("turnover", 0.0),
                "created_at": snapshot.get("generated_at", _now_iso()),
            }
        ]
    )
    if frame.empty:
        next_frame = incoming
    else:
        next_frame = pd.concat([frame, incoming], ignore_index=True)
        next_frame = next_frame.drop_duplicates(subset=["as_of_date"], keep="last").sort_values("as_of_date")
    save_frame(performance_history_path(), next_frame)
    save_runtime_json(latest_performance_path(), snapshot)
    return snapshot
