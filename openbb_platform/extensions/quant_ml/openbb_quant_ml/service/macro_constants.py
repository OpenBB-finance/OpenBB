"""Constants and config helpers for Macro services."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from openbb_quant_ml.service.constants import ARTIFACT_ROOT

MACRO_ROOT = ARTIFACT_ROOT / "macro"
MACRO_DB_PATH = MACRO_ROOT / "macro.db"
MACRO_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "macro.yaml"

DEFAULT_FREQ = "native"
DEFAULT_FILL = "ffill"
DEFAULT_TRANSFORM = "level"
DEFAULT_STALE_REFRESH_DAYS = 30
DEFAULT_FRED_BASE_URL = "https://api.stlouisfed.org/fred"
DEFAULT_FRED_MAX_RETRIES = 5
DEFAULT_FRED_TIMEOUT_SEC = 10


@lru_cache(maxsize=1)
def load_macro_config() -> dict[str, Any]:
    """Load macro config YAML from disk."""
    if not MACRO_CONFIG_PATH.exists():
        return {
            "version": "v1",
            "defaults": {
                "stale_refresh_days": DEFAULT_STALE_REFRESH_DAYS,
                "market_fallback_order": ["yfinance", "openbb_http", "cache"],
                "fred": {
                    "base_url": DEFAULT_FRED_BASE_URL,
                    "timeout_sec": DEFAULT_FRED_TIMEOUT_SEC,
                    "max_retries": DEFAULT_FRED_MAX_RETRIES,
                },
            },
            "domains": {},
            "regime_weights": {},
            "alerts": [],
        }
    with MACRO_CONFIG_PATH.open(encoding="utf-8") as file:
        payload = yaml.safe_load(file) or {}
    payload.setdefault("version", "v1")
    payload.setdefault("defaults", {})
    payload.setdefault("domains", {})
    payload.setdefault("regime_weights", {})
    payload.setdefault("alerts", [])
    defaults = payload["defaults"]
    defaults.setdefault("stale_refresh_days", DEFAULT_STALE_REFRESH_DAYS)
    defaults.setdefault("market_fallback_order", ["yfinance", "openbb_http", "cache"])
    defaults.setdefault("fred", {})
    defaults["fred"].setdefault("base_url", DEFAULT_FRED_BASE_URL)
    defaults["fred"].setdefault("timeout_sec", DEFAULT_FRED_TIMEOUT_SEC)
    defaults["fred"].setdefault("max_retries", DEFAULT_FRED_MAX_RETRIES)
    return payload


def invalidate_macro_config_cache() -> None:
    """Clear cached config."""
    load_macro_config.cache_clear()  # type: ignore[attr-defined]
