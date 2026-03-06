"""Trading runtime storage helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from openbb_quant_ml.service.constants import (
    TRADING_ACCOUNT_STATE_DIR,
    TRADING_ALGORITHM_REGISTRY_DIR,
    TRADING_FILLS_DIR,
    TRADING_LOGS_DIR,
    TRADING_ORDERS_DIR,
    TRADING_PERFORMANCE_DIR,
    TRADING_POSITIONS_DIR,
    TRADING_RISK_DIR,
    TRADING_SETTINGS_DIR,
    TRADING_SIGNALS_DIR,
    TRADING_VALIDATION_REPORTS_DIR,
)
from openbb_quant_ml.service.storage import (
    ensure_storage_dirs,
    load_json,
    save_json,
    save_parquet_atomic,
)


def ensure_trading_dirs() -> None:
    """Ensure all trading directories exist."""
    ensure_storage_dirs()


def latest_scan_meta_path() -> Path:
    return TRADING_SIGNALS_DIR / "latest_meta.json"


def latest_signals_path() -> Path:
    return TRADING_SIGNALS_DIR / "latest.parquet"


def signal_history_path() -> Path:
    return TRADING_SIGNALS_DIR / "history.parquet"


def order_history_path() -> Path:
    return TRADING_ORDERS_DIR / "history.parquet"


def fill_history_path() -> Path:
    return TRADING_FILLS_DIR / "history.parquet"


def open_positions_path() -> Path:
    return TRADING_POSITIONS_DIR / "open_positions.json"


def closed_positions_path() -> Path:
    return TRADING_POSITIONS_DIR / "closed_positions.parquet"


def performance_history_path() -> Path:
    return TRADING_PERFORMANCE_DIR / "daily.parquet"


def latest_performance_path() -> Path:
    return TRADING_PERFORMANCE_DIR / "latest.json"


def event_history_path() -> Path:
    return TRADING_LOGS_DIR / "events.parquet"


def latest_risk_path() -> Path:
    return TRADING_RISK_DIR / "latest.json"


def risk_events_path() -> Path:
    return TRADING_RISK_DIR / "events.parquet"


def algorithm_registry_path() -> Path:
    return TRADING_ALGORITHM_REGISTRY_DIR / "registry.json"


def latest_validation_path() -> Path:
    return TRADING_VALIDATION_REPORTS_DIR / "latest.json"


def account_state_path() -> Path:
    return TRADING_ACCOUNT_STATE_DIR / "current.json"


def settings_runtime_path() -> Path:
    return TRADING_SETTINGS_DIR / "current.json"


def load_frame(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_parquet(path)
    except Exception:
        return pd.DataFrame()


def append_frame(path: Path, frame: pd.DataFrame) -> pd.DataFrame:
    ensure_trading_dirs()
    incoming = frame.copy()
    if path.exists():
        existing = load_frame(path)
        if not existing.empty:
            incoming = pd.concat([existing, incoming], ignore_index=True)
    save_parquet_atomic(path, incoming, index=False)
    return incoming


def save_frame(path: Path, frame: pd.DataFrame) -> None:
    ensure_trading_dirs()
    save_parquet_atomic(path, frame, index=False)


def load_runtime_json(path: Path, default: Any) -> Any:
    ensure_trading_dirs()
    return load_json(path, default=default)


def save_runtime_json(path: Path, payload: Any) -> None:
    ensure_trading_dirs()
    save_json(path, payload)
