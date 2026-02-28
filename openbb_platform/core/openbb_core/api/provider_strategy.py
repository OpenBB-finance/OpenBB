"""Provider auto-selection strategy for API and MCP usage."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

_PROVIDER_PRIORITY: dict[str, int] = {
    "wind": 100,
    "tushare": 95,
    "polygon": 90,
    "alpha_vantage": 88,
    "yfinance": 85,
    "sec": 84,
    "imf": 83,
    "oecd": 82,
    "ecb": 81,
    "government_us": 80,
    "federal_reserve": 79,
    "finra": 78,
    "finviz": 77,
    "famafrench": 76,
    "multpl": 75,
    "stockgrid": 74,
    "wsj": 73,
    "cboe": 72,
    "deribit": 71,
}

_ROUTE_POLICY_BONUS: dict[str, dict[str, float]] = {
    "/economy/": {
        "imf": 10.0,
        "oecd": 9.0,
        "federal_reserve": 8.0,
        "government_us": 7.0,
        "ecb": 6.0,
    },
    "/equity/": {
        "wind": 6.0,
        "tushare": 5.0,
        "polygon": 4.0,
        "alpha_vantage": 3.0,
        "yfinance": 2.0,
    },
    "/fixedincome/": {
        "federal_reserve": 8.0,
        "government_us": 7.0,
        "ecb": 6.0,
    },
    "/regulators/": {
        "sec": 10.0,
        "finra": 8.0,
    },
}

_CREDENTIAL_READY_BONUS = 1.5
_CREDENTIAL_MISSING_PENALTY = -4.0


def normalize_provider(value: str | None) -> str:
    """Normalize provider string with auto as default."""
    if not value:
        return "auto"
    normalized = str(value).strip().lower()
    return normalized or "auto"


def _credential_value(credentials_obj: Any, key: str) -> str | None:
    """Extract credential value as text from user settings object."""
    try:
        value = getattr(credentials_obj, key, None)
        if value is None:
            return None
        if hasattr(value, "get_secret_value"):
            return value.get_secret_value() or None
        value_str = str(value).strip()
        return value_str or None
    except Exception:
        return None


def has_required_credentials(
    provider: str,
    provider_credentials: dict[str, list[str]],
    credentials_obj: Any,
) -> bool:
    """Check if all provider credential keys are configured in user settings."""
    required = provider_credentials.get(provider, [])
    if not required:
        return True
    return all(_credential_value(credentials_obj, key) for key in required)


def _route_bonus(route: str, provider: str) -> tuple[float, dict[str, float]]:
    policy: dict[str, float] = {}
    best_prefix_len = -1
    for prefix, mapping in _ROUTE_POLICY_BONUS.items():
        if route.startswith(prefix) and len(prefix) > best_prefix_len:
            policy = mapping
            best_prefix_len = len(prefix)
    return policy.get(provider, 0.0), policy


def _normalize_ratio(value: Any) -> float | None:
    """Normalize a ratio value to [0, 1] when possible."""
    if value is None:
        return None
    try:
        f_value = float(value)
    except Exception:
        return None
    if f_value < 0:
        return 0.0
    if f_value > 1:
        if f_value <= 100:
            return round(f_value / 100.0, 6)
        return 1.0
    return round(f_value, 6)


def _health_bonus(provider: str, provider_health: dict[str, Any]) -> float:
    """Compute health bonus/penalty from recent provider metrics."""
    metrics = provider_health.get(provider)
    if not isinstance(metrics, dict):
        return 0.0

    success_rate = _normalize_ratio(
        metrics.get("success_rate", metrics.get("success_ratio"))
    )
    error_rate = _normalize_ratio(
        metrics.get("error_rate_24h", metrics.get("error_rate"))
    )

    latency_raw = metrics.get("latency_ms", metrics.get("avg_latency_ms"))
    try:
        latency_ms = float(latency_raw) if latency_raw is not None else 0.0
    except Exception:
        latency_ms = 0.0
    if latency_ms < 0:
        latency_ms = 0.0

    bonus = 0.0
    if success_rate is not None:
        bonus += success_rate * 18.0
    if error_rate is not None:
        bonus -= error_rate * 20.0
    bonus -= min(latency_ms / 400.0, 6.0)
    return round(max(min(bonus, 20.0), -25.0), 4)


def _default_provider_health_path() -> Path | None:
    home = os.environ.get("HOME") or os.environ.get("USERPROFILE")
    if not home:
        return None
    return Path(home) / ".openbb_platform" / "provider_health.json"


def load_provider_health() -> tuple[dict[str, Any], str]:
    """Load provider health metrics from file if available."""
    configured_path = os.environ.get("OPENBB_PROVIDER_HEALTH_PATH")
    health_path = (
        Path(configured_path).expanduser()
        if configured_path
        else _default_provider_health_path()
    )
    if health_path is None or not health_path.exists():
        return {}, "none"

    try:
        data = json.loads(health_path.read_text(encoding="utf-8"))
    except Exception:
        return {}, str(health_path)

    if not isinstance(data, dict):
        return {}, str(health_path)

    providers = data.get("providers", data)
    if not isinstance(providers, dict):
        return {}, str(health_path)

    normalized: dict[str, Any] = {
        str(name).strip().lower(): metrics
        for name, metrics in providers.items()
        if isinstance(name, str)
    }
    return normalized, str(health_path)


def resolve_provider_strategy(
    route: str,
    requested_provider: str | None,
    command_coverage: dict[str, list[str]],
    provider_credentials: dict[str, list[str]],
    credentials_obj: Any,
    provider_health: dict[str, Any] | None = None,
    health_source: str | None = None,
) -> dict[str, Any]:
    """Resolve provider candidates and strategy reason payload."""
    requested = normalize_provider(requested_provider)
    if provider_health is None:
        provider_health, detected_source = load_provider_health()
    else:
        detected_source = health_source or "inline"

    if requested != "auto":
        base_priority = _PROVIDER_PRIORITY.get(requested, 10)
        route_policy_bonus, route_policy = _route_bonus(route, requested)
        required_creds = provider_credentials.get(requested, [])
        credentials_ready = has_required_credentials(
            requested, provider_credentials, credentials_obj
        )
        if required_creds:
            credential_bonus = (
                _CREDENTIAL_READY_BONUS
                if credentials_ready
                else _CREDENTIAL_MISSING_PENALTY
            )
        else:
            credential_bonus = 0.0
        health = _health_bonus(requested, provider_health)
        total = round(
            base_priority + route_policy_bonus + credential_bonus + health,
            4,
        )
        return {
            "candidates": [requested],
            "selection_reason": {
                "mode": "explicit",
                "route": route,
                "requested_provider": requested,
                "route_policy_applied": bool(route_policy_bonus),
                "route_policy": route_policy,
                "health_source": detected_source,
                "scored_providers": [
                    {
                        "provider": requested,
                        "base_priority": float(base_priority),
                        "route_policy_bonus": route_policy_bonus,
                        "credentials_ready": credentials_ready,
                        "credential_bonus": credential_bonus,
                        "health_bonus": health,
                        "total_score": total,
                    }
                ],
            },
        }

    providers = list(dict.fromkeys(command_coverage.get(route, [])))
    if not providers:
        return {
            "candidates": [],
            "selection_reason": {
                "mode": "auto",
                "route": route,
                "requested_provider": "auto",
                "route_policy_applied": False,
                "route_policy": {},
                "health_source": detected_source,
                "scored_providers": [],
            },
        }

    scored_providers: list[dict[str, Any]] = []
    applied_policy: dict[str, float] = {}
    for provider in providers:
        base_priority = _PROVIDER_PRIORITY.get(provider, 10)
        route_policy_bonus, route_policy = _route_bonus(route, provider)
        if route_policy and not applied_policy:
            applied_policy = route_policy
        required_creds = provider_credentials.get(provider, [])
        credentials_ready = has_required_credentials(
            provider, provider_credentials, credentials_obj
        )
        if required_creds:
            credential_bonus = (
                _CREDENTIAL_READY_BONUS
                if credentials_ready
                else _CREDENTIAL_MISSING_PENALTY
            )
        else:
            credential_bonus = 0.0
        health = _health_bonus(provider, provider_health)
        total = round(
            base_priority + route_policy_bonus + credential_bonus + health,
            4,
        )
        scored_providers.append(
            {
                "provider": provider,
                "base_priority": float(base_priority),
                "route_policy_bonus": route_policy_bonus,
                "credentials_ready": credentials_ready,
                "credential_bonus": credential_bonus,
                "health_bonus": health,
                "total_score": total,
            }
        )

    scored_providers.sort(
        key=lambda item: (item["total_score"], item["base_priority"], item["provider"]),
        reverse=True,
    )
    return {
        "candidates": [item["provider"] for item in scored_providers],
        "selection_reason": {
            "mode": "auto",
            "route": route,
            "requested_provider": "auto",
            "route_policy_applied": bool(applied_policy),
            "route_policy": applied_policy,
            "health_source": detected_source,
            "scored_providers": scored_providers,
        },
    }


def resolve_provider_candidates(
    route: str,
    requested_provider: str | None,
    command_coverage: dict[str, list[str]],
    provider_credentials: dict[str, list[str]],
    credentials_obj: Any,
) -> list[str]:
    """Resolve ordered providers for a command route.

    Rules:
    - explicit provider => single candidate
    - auto/omitted => command coverage providers sorted by quality priority
      and credential readiness.
    """
    strategy = resolve_provider_strategy(
        route=route,
        requested_provider=requested_provider,
        command_coverage=command_coverage,
        provider_credentials=provider_credentials,
        credentials_obj=credentials_obj,
    )
    return strategy["candidates"]


def compute_confidence(provider_used: str | None, fallback_trace: list[dict[str, Any]]) -> float:
    """Compute confidence score based on provider quality and fallback depth."""
    if not provider_used:
        return 0.0
    base = _PROVIDER_PRIORITY.get(provider_used, 50) / 100.0
    failures = sum(1 for item in fallback_trace if item.get("status") == "failed")
    # Penalize each failed attempt and clamp score to [0, 1].
    score = base - failures * 0.12
    if score < 0:
        return 0.0
    if score > 1:
        return 1.0
    return round(score, 4)
