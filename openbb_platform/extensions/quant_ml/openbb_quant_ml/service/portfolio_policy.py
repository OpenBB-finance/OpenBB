"""Portfolio policy loader and normalization helpers."""

from __future__ import annotations

import math
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from openbb_quant_ml.models import PortfolioPolicyResponse

POLICY_PATH = (
    Path(__file__).resolve().parent.parent / "config" / "portfolio_policy.yaml"
)

DEFAULT_PORTFOLIO_POLICY: dict[str, Any] = {
    "template": "diversified_long_only",
    "single_name_max_abs_weight": 0.10,
    "small_universe_policy": "cash_buffer",
    "sector_concentration_max": 0.35,
    "turnover_max": 0.8,
    "gross_exposure_max": 1.0,
    "net_exposure_abs_max": 1.0,
    "cash_symbol": "CASH",
    "cash_category": "cash_proxy",
}


def _safe_float(value: Any, default: float) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    if math.isnan(out) or math.isinf(out):
        return default
    return out


def _safe_str(value: Any, default: str) -> str:
    text = str(value or "").strip()
    return text or default


@lru_cache(maxsize=1)
def _load_policy() -> dict[str, Any]:
    payload: dict[str, Any] = {}
    if POLICY_PATH.exists():
        try:
            with POLICY_PATH.open(encoding="utf-8") as file:
                parsed = yaml.safe_load(file) or {}
            if isinstance(parsed, dict):
                payload = parsed
        except OSError:
            payload = {}

    defaults = DEFAULT_PORTFOLIO_POLICY
    policy = {
        "template": _safe_str(payload.get("template"), defaults["template"]),
        "single_name_max_abs_weight": max(
            0.0,
            min(
                1.0,
                _safe_float(
                    payload.get("single_name_max_abs_weight"),
                    defaults["single_name_max_abs_weight"],
                ),
            ),
        ),
        "small_universe_policy": _safe_str(
            payload.get("small_universe_policy"), defaults["small_universe_policy"]
        ),
        "sector_concentration_max": max(
            0.0,
            min(
                1.0,
                _safe_float(
                    payload.get("sector_concentration_max"),
                    defaults["sector_concentration_max"],
                ),
            ),
        ),
        "turnover_max": max(
            0.0, _safe_float(payload.get("turnover_max"), defaults["turnover_max"])
        ),
        "gross_exposure_max": max(
            0.0,
            _safe_float(
                payload.get("gross_exposure_max"), defaults["gross_exposure_max"]
            ),
        ),
        "net_exposure_abs_max": max(
            0.0,
            _safe_float(
                payload.get("net_exposure_abs_max"), defaults["net_exposure_abs_max"]
            ),
        ),
        "cash_symbol": _safe_str(
            payload.get("cash_symbol"), defaults["cash_symbol"]
        ).upper(),
        "cash_category": _safe_str(
            payload.get("cash_category"), defaults["cash_category"]
        ),
    }
    return policy


def get_portfolio_policy(*, refresh: bool = False) -> dict[str, Any]:
    """Return normalized portfolio policy."""
    if refresh:
        _load_policy.cache_clear()
    return dict(_load_policy())


def get_policy_max_weight_cap() -> float:
    """Return absolute single-name cap from policy."""
    policy = get_portfolio_policy()
    return float(policy["single_name_max_abs_weight"])


def apply_effective_max_weight(requested_max_weight: float | int | None) -> float:
    """Apply hard max-weight policy to a requested max weight value."""
    requested = _safe_float(requested_max_weight, 0.0)
    if requested <= 0:
        requested = 1.0
    return min(requested, get_policy_max_weight_cap())


def get_portfolio_policy_response() -> PortfolioPolicyResponse:
    """Return typed policy payload for API response."""
    return PortfolioPolicyResponse(**get_portfolio_policy())
