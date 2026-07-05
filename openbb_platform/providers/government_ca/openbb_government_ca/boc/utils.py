"""Bank of Canada runtime metadata loader.

The BoC Valet API (https://www.bankofcanada.ca/valet/) exposes three
relevant resource families:

- ``/lists/series/json``           — every series name + label + description
- ``/lists/groups/json``           — curated groups (e.g. ``FX_RATES_DAILY``)
- ``/observations/{series}/json``  — actual time-series observations
"""

from __future__ import annotations

from typing import Any

BOC_SERIES_OF_INTEREST: tuple[str, ...] = (
    "FXUSDCAD",
    "FXEURCAD",
    "FXGBPCAD",
    "FXJPYCAD",
    "FXMXNCAD",
    "FXCNYCAD",
    "FXINRCAD",
    "V39076",
    "V39077",
    "V39078",
    "V39079",
    "CBC20210",
    "BD.CDN.2YR.DQ.YLD",
    "BD.CDN.3YR.DQ.YLD",
    "BD.CDN.5YR.DQ.YLD",
    "BD.CDN.7YR.DQ.YLD",
    "BD.CDN.10YR.DQ.YLD",
    "BD.CDN.LONG.DQ.YLD",
    "BD.CDN.RRB.DQ.YLD",
)

BOC_GROUPS_OF_INTEREST: tuple[str, ...] = ("FX_RATES_DAILY",)


def lookup_series(series_name: str, cache: dict[str, Any]) -> dict[str, Any]:
    """Return the cache entry for *series_name*, or raise ``KeyError``.

    Parameters
    ----------
    series_name
        Either a top-level series (``FXUSDCAD``, ``V39079``,
        ``BD.CDN.10YR.DQ.YLD``...) or a group name (``FX_RATES_DAILY``).
        Group entries carry a ``"kind": "group"`` marker.
    cache
        The already-loaded BoC cache section (typically
        ``GovernmentCaMetadata().boc``).
    """
    series = cache.get("series", {})
    groups = cache.get("groups", {})

    if series_name in series:
        return series[series_name]
    if series_name in groups:
        entry = dict(groups[series_name])
        entry.setdefault("kind", "group")
        return entry

    candidates = sorted(
        s
        for s in (*series.keys(), *groups.keys())
        if s.upper().startswith(series_name.upper()[:3])
    )
    hint = f" Did you mean one of: {', '.join(candidates[:5])}?" if candidates else ""
    msg = (
        f"Bank of Canada series '{series_name}' not found in cache. "
        f"The cache contains {len(series)} series and {len(groups)} groups."
        f"{hint}"
    )
    raise KeyError(msg)


def lookup_series_by_description(
    description_substring: str, cache: dict[str, Any]
) -> list[dict[str, Any]]:
    """Return all cache entries whose ``description`` contains the substring."""
    needle = description_substring.lower()
    matches: list[dict[str, Any]] = []
    for entry in cache.get("series", {}).values():
        if not isinstance(entry, dict):
            continue
        desc = str(entry.get("description", "")).lower()
        if needle in desc:
            matches.append(entry)
    return matches


def list_series(cache: dict[str, Any]) -> list[dict[str, Any]]:
    """Return all cataloged series as a list (safe accessor)."""
    return list(cache.get("series", {}).values())


def list_groups(cache: dict[str, Any]) -> list[dict[str, Any]]:
    """Return all cataloged groups as a list (safe accessor)."""
    return list(cache.get("groups", {}).values())


def is_degraded(cache: dict[str, Any]) -> bool:
    """Return ``True`` if the BoC cache section was built in degraded mode."""
    return cache.get("status") == "degraded"


def missing_series(cache: dict[str, Any]) -> list[str]:
    """Return the list of series-of-interest that weren't in the Valet catalog."""
    return list(cache.get("missing_series", []))
