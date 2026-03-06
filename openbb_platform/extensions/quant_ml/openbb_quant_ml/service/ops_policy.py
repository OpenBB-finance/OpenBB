"""Operational policy loader for quality, execution, reports, and notifications."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

import yaml

from openbb_quant_ml.service.constants import OPS_POLICY_PATH

DEFAULT_OPS_POLICY: dict[str, Any] = {
    "version": "v1",
    "quality_gate": {
        "enabled": True,
        "block_on_critical": True,
        "thresholds": {
            "market_missing_ratio_warning": 0.05,
            "market_missing_ratio_critical": 0.20,
            "feature_missing_ratio_warning": 0.03,
            "feature_missing_ratio_critical": 0.10,
            "market_outlier_ratio_warning": 0.005,
            "market_outlier_ratio_critical": 0.02,
            "feature_outlier_ratio_warning": 0.01,
            "feature_outlier_ratio_critical": 0.03,
            "symbol_coverage_warning": 0.90,
            "symbol_coverage_critical": 0.75,
            "distribution_shift_warning": 1.5,
            "distribution_shift_critical": 2.5,
            "schema_drift_new_columns_warning": 3,
            "schema_drift_missing_columns_critical": 1,
            "ticker_change_warning": 1,
            "delisting_warning": 1,
            "corporate_action_warning": 1,
        },
    },
    "notifications": {
        "dedupe_window_minutes": 240,
        "max_attempts": 5,
        "retry_backoff_sec": 30,
        "channels": {
            "slack": {"enabled": False},
            "discord": {"enabled": False},
            "webhook": {"enabled": False},
            "telegram": {"enabled": False},
            "email": {"enabled": False},
        },
    },
    "reports": {
        "output_format": "html",
        "latest_per_type_limit": 100,
        "include_raw_payload_excerpt": True,
    },
    "execution": {
        "default_mode": "paper",
        "live_adapter_enabled": False,
        "broker_ready": False,
        "auto_reduce_positions": False,
        "risk_defaults": {
            "max_order_notional": 250_000.0,
            "daily_loss_limit": 50_000.0,
            "max_symbol_exposure": 0.10,
            "execution_cash_buffer": 0.02,
        },
    },
    "scheduler": {"expected_jobs": ["daily", "weekly", "monthly"]},
}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


@lru_cache(maxsize=1)
def _load_ops_policy() -> dict[str, Any]:
    payload: dict[str, Any] = {}
    if OPS_POLICY_PATH.exists():
        try:
            parsed = yaml.safe_load(OPS_POLICY_PATH.read_text(encoding="utf-8")) or {}
            if isinstance(parsed, dict):
                payload = parsed
        except OSError:
            payload = {}
    return _deep_merge(DEFAULT_OPS_POLICY, payload)


def get_ops_policy(*, refresh: bool = False) -> dict[str, Any]:
    """Return merged operational policy payload."""
    if refresh:
        _load_ops_policy.cache_clear()
    return dict(_load_ops_policy())
