"""Trading runtime configuration helpers."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from openbb_quant_ml.service.constants import (
    TRADING_CONFIG_PATH,
    TRADING_SETTINGS_DIR,
)
from openbb_quant_ml.service.storage import load_json, save_json
from openbb_quant_ml.service.universe import list_universe_ids

SETTINGS_OVERRIDE_PATH = TRADING_SETTINGS_DIR / "current.json"

DEFAULT_TRADING_CONFIG: dict[str, Any] = {
    "version": "v1",
    "tab_name": "Trading",
    "mode": "paper",
    "runtime_status": "stopped",
    "universe_id": "default",
    "schedule": {
        "mode": "eod",
        "scan_interval_minutes": 1440,
        "timeframe": "1d",
        "last_run_timezone": "UTC",
    },
    "scan": {
        "lookback_days": 320,
        "provider": "yfinance",
        "max_workers": 8,
        "max_data_delay_days": 5,
    },
    "execution": {
        "mode": "paper",
        "auto_order": False,
        "manual_approval": False,
        "signal_generation": True,
        "fill_policy": "close",
        "slippage_bps": 2.0,
        "commission_bps": 1.0,
        "allow_partial_fill": False,
    },
    "account": {
        "initial_cash": 1_000_000.0,
        "position_size_mode": "percent",
        "position_size_value": 0.05,
        "max_concurrent_positions": 12,
        "max_daily_new_entries": 5,
        "max_daily_gross_entry": 250_000.0,
        "max_order_notional": 150_000.0,
        "reentry_cooldown_days": 5,
        "max_daily_orders": 20,
        "trading_window": "regular",
    },
    "risk": {
        "max_position_weight": 0.10,
        "max_sector_weight": 0.35,
        "min_avg_dollar_volume": 2_500_000.0,
        "max_atr_pct": 0.12,
        "stop_loss_pct": 0.08,
        "take_profit_pct": 0.15,
        "trailing_stop_enabled": False,
        "trailing_stop_pct": 0.05,
        "daily_loss_limit": 35_000.0,
        "portfolio_drawdown_limit": 0.15,
        "capital_cap": 750_000.0,
        "allow_duplicate_exposure": False,
    },
    "strategies": {
        "ema_cross": {
            "enabled": True,
            "params": {
                "fast_span": 12,
                "slow_span": 26,
                "rsi_ceiling": 72.0,
            },
        },
        "rsi_reversal": {
            "enabled": True,
            "params": {
                "oversold": 30.0,
                "rebound_level": 35.0,
                "overbought_exit": 70.0,
            },
        },
        "breakout_volume": {
            "enabled": True,
            "params": {
                "lookback": 20,
                "volume_multiple": 1.8,
                "min_atr_pct": 0.01,
                "max_atr_pct": 0.10,
            },
        },
    },
    "custom_algorithms": {
        "path": "openbb_quant_ml/algorithms",
        "auto_pause_failure_threshold": 3,
        "allowed_auto_order_statuses": ["active"],
        "default_status": "sandbox",
        "signal_only_dev": True,
        "dry_run_default": True,
    },
    "ui": {
        "polling_ms": 5000,
        "history_limit": 250,
    },
}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _normalize_config(payload: dict[str, Any]) -> dict[str, Any]:
    config = _deep_merge(DEFAULT_TRADING_CONFIG, payload)
    universe_id = str(config.get("universe_id", "default") or "default").strip()
    available = set(list_universe_ids())
    config["universe_id"] = universe_id if universe_id in available else "default"
    execution = config.get("execution", {})
    if not isinstance(execution, dict):
        execution = {}
    mode = str(execution.get("mode", "paper") or "paper").strip().lower()
    execution["mode"] = mode if mode in {"paper", "shadow_live", "live_adapter"} else "paper"
    config["execution"] = execution
    runtime_status = str(config.get("runtime_status", "stopped") or "stopped").strip().lower()
    if runtime_status not in {"running", "paused", "stopped"}:
        runtime_status = "stopped"
    config["runtime_status"] = runtime_status
    return config


@lru_cache(maxsize=1)
def _load_file_defaults() -> dict[str, Any]:
    if not Path(TRADING_CONFIG_PATH).exists():
        return {}
    try:
        parsed = yaml.safe_load(Path(TRADING_CONFIG_PATH).read_text(encoding="utf-8")) or {}
    except OSError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def get_trading_config(*, refresh: bool = False) -> dict[str, Any]:
    """Return merged trading runtime config with persisted overrides."""
    if refresh:
        _load_file_defaults.cache_clear()
    file_defaults = _load_file_defaults()
    overrides = load_json(SETTINGS_OVERRIDE_PATH, default={})
    if not isinstance(overrides, dict):
        overrides = {}
    return _normalize_config(_deep_merge(file_defaults, overrides))


def save_trading_settings(update: dict[str, Any]) -> dict[str, Any]:
    """Merge and persist one trading settings update."""
    current = get_trading_config(refresh=True)
    merged = _normalize_config(_deep_merge(current, update))
    save_json(SETTINGS_OVERRIDE_PATH, merged)
    _load_file_defaults.cache_clear()
    return get_trading_config(refresh=True)
