"""Universe policy loader for staged universe construction."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

DEFAULT_UNIVERSE_POLICY: dict[str, Any] = {
    "version": "v1",
    "mode": "global_unified",
    "missing_data_policy": "strict_exclude",
    "legacy_universe_policy": {
        "mode": "deprecate_one_release",
        "sunset_date": "2026-06-30",
        "replacement_id": "global_core_equity",
    },
    "u0_filters": {
        "allowed_security_types": ["common_stock"],
        "excluded_security_types": [
            "etf",
            "etn",
            "mutual_fund",
            "closed_end_fund",
            "adr",
            "dr",
            "spac",
            "lp",
            "mlp",
            "bdc",
            "preferred",
            "rights",
            "warrant",
            "convertible",
            "tracking_stock",
        ],
        "major_exchanges": ["NYSE", "NASDAQ", "KOSPI", "KOSDAQ"],
        "excluded_exchange_types": ["OTC", "PINK", "BULLETIN"],
        "min_price_20d_avg": 5.0,
        "min_free_float_ratio": 0.10,
        "min_float_mcap_usd": 500_000_000.0,
        "min_ipo_trading_days": 60,
    },
    "u1_filters": {
        "min_median_dollar_volume_63d": 5_000_000.0,
        "min_trading_frequency_63d": 0.90,
        "min_annual_turnover_ratio_252d": 0.75,
    },
    "u2_filters": {
        "max_trading_halt_days": 29,
        "exclude_management_flag": True,
        "exclude_delisting_pending_flag": True,
        "exclude_special_status_flag": True,
        "exclude_hard_to_borrow_for_long_short": True,
    },
    "asof_policy": {
        "market_data_cutoff": "T-1_close",
        "shares_float_cutoff": "T-1",
        "fundamentals_lag_days": 60,
        "prohibit_future_data": True,
    },
    "rebalance_policy": {
        "frequency": "monthly",
        "decision_time": "month_end",
        "cutoff": "T-1",
        "execution": "T+1_open",
    },
    "portfolio_constraints": {
        "target_count": 150,
        "min_count": 100,
        "max_count": 200,
        "max_weight_per_stock": 0.04,
        "sector_cap": 0.25,
        "country_cap": 0.35,
    },
    "liquidity_constraints": {
        "adv_lookback_days": 20,
        "max_adv_participation": 0.05,
    },
    "risk_constraints": {
        "max_risk_contribution_per_stock": 0.05,
        "covariance_lookback_days": 126,
        "epsilon": 1.0e-9,
    },
    "institutional_mode": {
        "delisting_require_event": False,
    },
}

UNIVERSE_POLICY_PATH = (
    Path(__file__).resolve().parent.parent / "config" / "universe_policy.yaml"
)

LEGACY_UNIVERSE_IDS: tuple[str, ...] = (
    "sp500",
    "nasdaq100",
    "dow30",
    "sox",
    "kospi200",
    "kosdaq100",
    "russell1000",
    "all_in_one",
)


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


@lru_cache(maxsize=1)
def load_universe_policy() -> dict[str, Any]:
    """Load staged universe policy with defaults."""
    if not UNIVERSE_POLICY_PATH.exists():
        return dict(DEFAULT_UNIVERSE_POLICY)
    try:
        with UNIVERSE_POLICY_PATH.open(encoding="utf-8") as file:
            parsed = yaml.safe_load(file) or {}
    except OSError:
        parsed = {}
    if not isinstance(parsed, dict):
        parsed = {}
    return _deep_merge(DEFAULT_UNIVERSE_POLICY, parsed)


def get_universe_policy(*, refresh: bool = False) -> dict[str, Any]:
    """Return normalized universe policy payload."""
    if refresh:
        load_universe_policy.cache_clear()
    return dict(load_universe_policy())


def get_legacy_universe_meta(universe_id: str | None) -> dict[str, Any]:
    """Return deprecation metadata for legacy universe identifiers."""
    key = str(universe_id or "").strip().lower()
    if key not in LEGACY_UNIVERSE_IDS:
        return {
            "deprecated": False,
            "replacement_id": None,
            "sunset_date": None,
        }
    policy = get_universe_policy()
    legacy_meta = policy.get("legacy_universe_policy", {})
    if not isinstance(legacy_meta, dict):
        legacy_meta = {}
    return {
        "deprecated": True,
        "replacement_id": str(legacy_meta.get("replacement_id", "global_core_equity")),
        "sunset_date": str(legacy_meta.get("sunset_date", "2026-06-30")),
    }
