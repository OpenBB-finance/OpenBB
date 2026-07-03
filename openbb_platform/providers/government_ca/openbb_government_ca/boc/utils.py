"""Bank of Canada runtime metadata loader.

Reads the BoC section of the shipped cache
(``assets/government_ca_cache.json.xz``) without making any network
calls. The cache itself is populated at build time by
``openbb_government_ca.utils.generate_cache`` (Phase 3).

The BoC Valet API (https://www.bankofcanada.ca/valet/) exposes three
relevant resource families:

- ``/lists/series/json``           — every series name + label + description
- ``/lists/groups/json``           — curated groups (e.g. ``FX_RATES_DAILY``)
- ``/observations/{series}/json``  — actual time-series observations

The cache we ship contains, per series of interest:

- ``name``           — e.g. ``FXUSDCAD``, ``V39079``, ``BD.CDN.10YR.DQ.YLD``
- ``label``          — the BoC's official label (may differ from ``name``)
- ``description``    — long-form text from Valet (this is the source of
                       truth for picking the right series — e.g.
                       "Target for the overnight rate" identifies V39079)
- ``frequency``      — best-effort heuristic from the series name
                       (``daily`` for FX*, BD.CDN.*, V3907*; ``annual``
                       for A.*; ``monthly`` for M.*; ``unknown`` otherwise)
- ``observations_url`` — pre-built Valet URL the fetcher will call
- ``cataloged_at``   — ISO 8601 timestamp when the cache was built

Per group of interest:

- ``name``           — e.g. ``FX_RATES_DAILY``
- ``label``, ``description`` — from Valet
- ``members``        — sorted list of member series names (resolved at
                       build time via a second call to
                       ``/groups/<NAME>/json``)
- ``members_url``, ``observations_url`` — pre-built URLs

Plus top-level:

- ``valet_url``      — base URL of the Valet API
- ``series_count``, ``groups_count`` — number of cataloged entries
- ``status``         — ``"ok"`` or ``"degraded"``
- ``missing_series`` — list of series we asked for but the Valet
                       catalog didn't have (useful for debugging)
- ``warning``        — present only in degraded mode

This module is a thin lookup layer; the actual API calls happen in
the fetchers themselves.
"""

from __future__ import annotations

from typing import Any

# Series & groups explicitly required by the task brief. These tuples
# are the **single source of truth** for what the build hook
# catalogs. They're re-exported here so the Phase 5 fetchers can
# iterate them without hard-coding string literals.
#
# NOTE on V39079 vs CBC20210: both have the same official Valet
# description ("Target for the overnight rate"). The Phase 5 fetcher
# for ``obb.boc.rates`` should pick one based on the ``description``
# field of the cache entry — that's the source of truth, not the
# series name. See the Phase 3 worklog entry for the full discussion.
BOC_SERIES_OF_INTEREST: tuple[str, ...] = (
    # FX (majors against CAD)
    "FXUSDCAD",
    "FXEURCAD",
    "FXGBPCAD",
    "FXJPYCAD",
    "FXMXNCAD",
    "FXCNYCAD",
    "FXINRCAD",
    # Policy overnight rate family (full V390* family + CBC20210 alias)
    "V39076",
    "V39077",
    "V39078",
    "V39079",
    "CBC20210",
    # Benchmark Government of Canada bond yields
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
        The generator stores groups with a ``"kind": "group"`` marker
        so callers can distinguish them from individual series.
    cache
        The already-loaded BoC cache section (typically
        ``GovernmentCaMetadata().boc``).

    Returns
    -------
    dict
        At minimum ``{"name", "label", "description", "frequency",
        "observations_url"}``; group entries additionally carry
        ``{"kind": "group", "members": list[str]}``.

    Raises
    ------
    KeyError
        If the series is not present in the cache. The fetcher is
        expected to translate this into an ``OpenBBError`` with a
        helpful message (e.g. "Did you mean FXUSDCAD?").
    """
    series = cache.get("series", {})
    groups = cache.get("groups", {})

    if series_name in series:
        return series[series_name]
    if series_name in groups:
        entry = dict(groups[series_name])
        entry.setdefault("kind", "group")
        return entry

    # Helpful "did you mean" hint using a trivial prefix match.
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
    """Return all cache entries whose ``description`` contains the substring.

    This is the recommended way to find a series when you know its
    semantic role but not its name. For example, to find the "Target
    for the overnight rate" series::

        matches = lookup_series_by_description("Target for the overnight", boc_cache)
        # Returns [V39079 entry, CBC20210 entry] — both have that description.

    The Phase 5 ``obb.boc.rates`` fetcher uses this to pick the right
    series without hard-coding a name that might change.
    """
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
    """Return ``True`` if the BoC cache section was built in degraded mode.

    Degraded mode means the build hook couldn't reach the BoC Valet
    API when the package was installed. The cache is still valid
    (just empty), and the Phase 5 fetcher can either fall back to
    direct API calls or raise a clear error.
    """
    return cache.get("status") == "degraded"


def missing_series(cache: dict[str, Any]) -> list[str]:
    """Return the list of series-of-interest that weren't in the Valet catalog.

    A non-empty list means we asked for series the BoC no longer
    publishes (or never did). The Phase 5 fetcher should treat these as
    permanently unavailable and raise a clear error if asked for one.
    """
    return list(cache.get("missing_series", []))
