"""Provider auto-selection strategy for API and MCP usage."""

from __future__ import annotations

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
    requested = normalize_provider(requested_provider)
    if requested != "auto":
        return [requested]

    providers = list(command_coverage.get(route, []))
    if not providers:
        return []

    def score(name: str) -> tuple[int, int, str]:
        priority = _PROVIDER_PRIORITY.get(name, 10)
        creds = 1 if has_required_credentials(name, provider_credentials, credentials_obj) else 0
        return (priority, creds, name)

    providers = sorted(providers, key=score, reverse=True)
    return providers


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
