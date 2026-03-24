"""Trading runtime service tests."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
from openbb_quant_ml.service import reporting
from openbb_quant_ml.service.trading import (
    custom_algorithm_registry as algo_registry,
    performance_tracker,
    portfolio_state_manager,
    registry as trading_registry,
    runtime,
)


def _make_trend_frame(symbol: str, cross_up: bool = True) -> pd.DataFrame:
    dates = pd.date_range(end=pd.Timestamp.utcnow().normalize(), periods=120, freq="B")
    if cross_up:
        closes = [100.0] * 110 + [95.0, 94.0, 93.0, 92.0, 91.0, 90.0, 89.0, 88.0, 87.0, 140.0]
    else:
        closes = [100.0] * len(dates)
    rows = []
    for date_value, close in zip(dates, closes, strict=True):
        rows.append(
            {
                "date": date_value,
                "open": close * 0.995,
                "high": close * 1.01,
                "low": close * 0.99,
                "close": close,
                "volume": 500_000.0,
                "symbol": symbol,
            }
        )
    return pd.DataFrame(rows)


def _patch_trading_paths(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    reports_dir = tmp_path / "reports"
    db_path = tmp_path / "run_registry.sqlite3"

    monkeypatch.setattr(reporting, "REPORTS_DIR", reports_dir)
    monkeypatch.setattr(trading_registry, "RUN_REGISTRY_DB_PATH", db_path)

    monkeypatch.setattr(runtime, "latest_scan_meta_path", lambda: tmp_path / "signals" / "latest_meta.json")
    monkeypatch.setattr(runtime, "latest_signals_path", lambda: tmp_path / "signals" / "latest.parquet")
    monkeypatch.setattr(runtime, "signal_history_path", lambda: tmp_path / "signals" / "history.parquet")
    monkeypatch.setattr(runtime, "order_history_path", lambda: tmp_path / "orders" / "history.parquet")
    monkeypatch.setattr(runtime, "fill_history_path", lambda: tmp_path / "fills" / "history.parquet")
    monkeypatch.setattr(runtime, "risk_events_path", lambda: tmp_path / "risk" / "events.parquet")
    monkeypatch.setattr(runtime, "latest_risk_path", lambda: tmp_path / "risk" / "latest.json")
    monkeypatch.setattr(runtime, "latest_performance_path", lambda: tmp_path / "performance" / "latest.json")
    monkeypatch.setattr(runtime, "closed_positions_path", lambda: tmp_path / "positions" / "closed.parquet")

    monkeypatch.setattr(performance_tracker, "performance_history_path", lambda: tmp_path / "performance" / "daily.parquet")
    monkeypatch.setattr(performance_tracker, "latest_performance_path", lambda: tmp_path / "performance" / "latest.json")

    monkeypatch.setattr(portfolio_state_manager, "account_state_path", lambda: tmp_path / "account" / "current.json")
    monkeypatch.setattr(portfolio_state_manager, "open_positions_path", lambda: tmp_path / "positions" / "open.json")
    monkeypatch.setattr(portfolio_state_manager, "closed_positions_path", lambda: tmp_path / "positions" / "closed.parquet")

    monkeypatch.setattr(algo_registry, "algorithm_registry_path", lambda: tmp_path / "algorithms" / "registry.json")


def _trading_settings(auto_order: bool = False) -> dict[str, object]:
    return {
        "version": "v1",
        "mode": "paper",
        "runtime_status": "running",
        "universe_id": "default",
        "scan": {"lookback_days": 320, "provider": "yfinance", "max_workers": 1, "max_data_delay_days": 5},
        "execution": {
            "mode": "paper",
            "auto_order": auto_order,
            "manual_approval": False,
            "signal_generation": True,
            "fill_policy": "close",
            "slippage_bps": 2.0,
            "commission_bps": 1.0,
        },
        "account": {
            "initial_cash": 100_000.0,
            "position_size_mode": "percent",
            "position_size_value": 0.10,
            "max_concurrent_positions": 5,
            "max_daily_orders": 10,
            "max_order_notional": 25_000.0,
        },
        "risk": {
            "min_avg_dollar_volume": 1_000_000.0,
            "max_atr_pct": 0.30,
            "capital_cap": 100_000.0,
            "daily_loss_limit": 10_000.0,
            "portfolio_drawdown_limit": 0.30,
            "allow_duplicate_exposure": False,
            "max_sector_weight": 0.60,
            "stop_loss_pct": 0.08,
            "take_profit_pct": 0.15,
            "trailing_stop_enabled": False,
        },
        "strategies": {
            "ema_cross": {"enabled": True, "params": {"fast_span": 12, "slow_span": 26, "rsi_ceiling": 99.0}},
            "rsi_reversal": {"enabled": False, "params": {}},
            "breakout_volume": {"enabled": False, "params": {}},
        },
        "custom_algorithms": {
            "default_status": "sandbox",
            "signal_only_dev": True,
        },
        "ui": {"history_limit": 250},
    }


def test_trading_cycle_creates_pending_order_and_manual_approval_flow(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _patch_trading_paths(monkeypatch, tmp_path)
    monkeypatch.setattr(runtime, "get_trading_config", lambda refresh=False: _trading_settings(auto_order=False))
    monkeypatch.setattr(runtime, "load_trading_universe", lambda universe_id: ["AAA", "BBB"])
    monkeypatch.setattr(
        runtime,
        "load_symbol_metadata",
        lambda: {
            "AAA": {"symbol": "AAA", "name": "Alpha", "sector_l1": "Tech", "category": "equity"},
            "BBB": {"symbol": "BBB", "name": "Beta", "sector_l1": "Health", "category": "equity"},
        },
    )
    monkeypatch.setattr(
        runtime,
        "load_trading_market_data",
        lambda **kwargs: ({"AAA": _make_trend_frame("AAA", cross_up=True), "BBB": _make_trend_frame("BBB", cross_up=False)}, []),
    )
    monkeypatch.setattr(runtime, "sync_custom_algorithm_registry", lambda: [])
    monkeypatch.setattr(runtime, "discover_custom_algorithms", lambda: [])

    result = runtime.run_trading_cycle()
    assert result["status"] == "completed"
    assert result["signal_count"] >= 1
    assert result["order_count"] >= 1
    orders = runtime.get_trading_orders_payload(limit=20)["items"]
    assert orders[0]["status"] == "pending"

    approved = runtime.approve_trading_order_payload(str(orders[0]["order_id"]))
    assert approved["status"] == "filled"

    positions = runtime.get_trading_positions_payload()["items"]
    assert len(positions) == 1
    assert positions[0]["ticker"] == "AAA"

    performance = runtime.get_trading_performance_payload()
    assert "equity_curve" in performance


def test_custom_algorithm_registry_toggle_and_validation(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _patch_trading_paths(monkeypatch, tmp_path)
    monkeypatch.setattr(runtime, "get_trading_config", lambda refresh=False: _trading_settings(auto_order=False))
    monkeypatch.setattr(runtime, "load_trading_universe", lambda universe_id: ["AAA"])
    monkeypatch.setattr(
        runtime,
        "load_trading_market_data",
        lambda **kwargs: ({"AAA": _make_trend_frame("AAA", cross_up=True)}, []),
    )

    rows = algo_registry.sync_custom_algorithm_registry()
    assert any(row["name"] == "sample_momentum" for row in rows)

    toggled = runtime.toggle_trading_algorithm_payload(
        name="sample_momentum",
        active=True,
        status="active",
        sandbox_mode=False,
        signal_only=False,
    )
    selected = next(row for row in toggled["items"] if row["name"] == "sample_momentum")
    assert selected["active"] is True
    assert selected["status"] == "active"

    report = runtime.validate_trading_algorithm_payload("sample_momentum")
    assert report["name"] == "sample_momentum"
    assert report["report_path"] is not None


def test_get_trading_orders_payload_sanitizes_nan_values(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _patch_trading_paths(monkeypatch, tmp_path)
    runtime.save_frame(
        runtime.order_history_path(),
        pd.DataFrame(
            [
                {
                    "order_id": "ord-nan",
                    "created_at": pd.Timestamp("2026-03-20T12:00:00Z"),
                    "ticker": "AAA",
                    "strategy_name": "ema_cross",
                    "status": "pending",
                    "side": "buy",
                    "quantity": 10.0,
                    "requested_price": float("nan"),
                    "notional": float("inf"),
                    "stop_loss": float("nan"),
                    "take_profit": float("-inf"),
                }
            ]
        ),
    )

    payload = runtime.get_trading_orders_payload(limit=10)

    assert payload["items"][0]["requested_price"] == 0.0
    assert payload["items"][0]["notional"] == 0.0
    assert payload["items"][0]["stop_loss"] == 0.0
    assert payload["items"][0]["take_profit"] == 0.0
