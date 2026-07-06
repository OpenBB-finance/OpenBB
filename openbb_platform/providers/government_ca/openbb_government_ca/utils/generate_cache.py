"""Build-time cache generator for ``openbb-government-ca``.

This script is invoked by ``hatch_build.py`` (by path, not by module
name) and is also exposed as the ``generate-government-ca-cache``
console script.

CRITICAL DESIGN CONSTRAINTS
---------------------------
- **Stdlib + ``requests`` only.** ``openbb_core`` is NOT a build-time
  dependency and must not be imported here. The build hook runs in an
  isolated PEP 517 environment that contains only what's listed in
  ``[build-system].requires``.
- **No state outside this file's directory.** The cache is written to
  ``assets/government_ca_cache.json.xz`` relative to the package root.
  All paths are resolved from ``__file__``.
- **Fail soft, log loud.** If an upstream API is unreachable during
  build, the generator writes a *partial* cache with empty data rather
  than aborting the install. The runtime fetcher can then raise a
  clear error. If **both** sections fail, we still write the cache
  and exit 0 — the user gets a working package with empty metadata
  and a clear log trail.

PHASE STATUS
------------
- **Fase 1**: scaffolding (done).
- **Fase 2**: ``_fetch_statscan`` walks ``ind-econ.json`` (done).
- **Fase 3**: ``_fetch_boc`` walks the BoC Valet API (done).
"""

from __future__ import annotations

import json
import lzma
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Add the script's directory to sys.path so we can import _http
# without triggering openbb_government_ca/__init__.py (which
# imports openbb_core — not available in the PEP 517 build env).
_SCRIPT_DIR = str(Path(__file__).resolve().parent)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from _http import NetworkError, http_get_json  # noqa: E402

# Resolve paths relative to this file so the script works regardless
# of the current working directory.
_PKG_ROOT = Path(__file__).resolve().parent.parent  # openbb_government_ca/
_CACHE_DIR = _PKG_ROOT / "assets"
_CACHE_FILE = _CACHE_DIR / "government_ca_cache.json.xz"

# ---------------------------------------------------------------------------
# StatsCan endpoints
# ---------------------------------------------------------------------------
STATSCAN_HOMEPAGE_URL = (
    "https://www150.statcan.gc.ca/n1/dai-quo/ssi/homepage/ind-econ.json"
)
# Per-product observation URL. StatsCan's Web Data Service (WDS) uses
# vector IDs (the ``source`` field in ind-econ.json) to fetch
# observations. We don't fetch observations at build time — we only
# resolve enough structural metadata to let the Fase 4 fetcher
# construct the right URL at runtime.
STATSCAN_WDS_BASE = "https://www150.statcan.gc.ca/t1/wds/rest"

# ---------------------------------------------------------------------------
# BoC endpoints
# ---------------------------------------------------------------------------
BOC_VALET_BASE = "https://www.bankofcanada.ca/valet"
BOC_LIST_SERIES_URL = f"{BOC_VALET_BASE}/lists/series/json"
BOC_LIST_GROUPS_URL = f"{BOC_VALET_BASE}/lists/groups/json"


# ---------------------------------------------------------------------------
# Series & groups of interest (Fase 3 catalog scope)
# ---------------------------------------------------------------------------
# This is the *only* place where the set of cataloged series is
# defined. Adding a series here means the build hook will resolve its
# metadata (label, description, link) and store it in the cache. The
# Fase 5 fetcher reads from this cache to decide which specific series
# to call.
#
# NOTE: The brief mentions ``CBC20210``, ``V39079``, and
# ``BD.CDN.ALL.DQ.YLD``. We catalog ALL of the following so the Fase
# 5 fetcher has the full family to choose from:
#
# - **FX**: the ``FX_RATES_DAILY`` group covers all daily exchange
#   rates. We resolve it as a group so the fetcher can iterate
#   members, AND we also catalog a handful of individual FX series
#   (FXUSDCAD, FXEURCAD, FXGBPCAD, FXJPYCAD, FXMXNCAD, FXCNYCAD,
#   FXINRCAD) so direct lookups by symbol work without expanding the
#   group first.
# - **Policy rate family**: V39076 (low band), V39077 (high band),
#   V39078 (Bank Rate), V39079 (Target for the overnight rate per the
#   official Valet description), and CBC20210 (alias of V39079 per
#   Valet's own label/description).
# - **Benchmark bond yields**: ``BD.CDN.ALL.DQ.YLD`` does NOT exist
#   in the Valet catalog. The real benchmark series are
#   ``BD.CDN.{2YR,3YR,5YR,7YR,10YR,LONG,RRB}.DQ.YLD``. We catalog all
#   of them so the Fase 5 fetcher can map year_2 → BD.CDN.2YR.DQ.YLD,
#   year_3 → BD.CDN.3YR.DQ.YLD, year_5 → BD.CDN.5YR.DQ.YLD,
#   year_7 → BD.CDN.7YR.DQ.YLD, year_10 → BD.CDN.10YR.DQ.YLD,
#   year_30 → BD.CDN.LONG.DQ.YLD. The RRB (Real Return Bonds) is
#   cataloged for completeness but not mapped to a treasury_rates
#   field — it's an inflation-linked bond, not a nominal benchmark.
BOC_INDIVIDUAL_SERIES: tuple[str, ...] = (
    # --- FX (selected majors against CAD) ---
    "FXUSDCAD",
    "FXEURCAD",
    "FXGBPCAD",
    "FXJPYCAD",
    "FXMXNCAD",
    "FXCNYCAD",
    "FXINRCAD",
    # --- Policy overnight rate family (V390*) ---
    # Catalog ALL of them so the Fase 5 fetcher can pick based on the
    # ``description`` field — the descriptions are the source of truth.
    "V39076",  # Operating band - low
    "V39077",  # Operating band - high
    "V39078",  # Bank rate
    "V39079",  # Target for the overnight rate (per Valet description)
    "CBC20210",  # Alias of V39079 (same label & description)
    # --- Benchmark Government of Canada bond yields ---
    "BD.CDN.2YR.DQ.YLD",  # 2-year benchmark
    "BD.CDN.3YR.DQ.YLD",  # 3-year benchmark
    "BD.CDN.5YR.DQ.YLD",  # 5-year benchmark
    "BD.CDN.7YR.DQ.YLD",  # 7-year benchmark
    "BD.CDN.10YR.DQ.YLD",  # 10-year benchmark
    "BD.CDN.LONG.DQ.YLD",  # Long-term benchmark (≈30y)
    "BD.CDN.RRB.DQ.YLD",  # Real Return Bonds (inflation-linked)
)

BOC_GROUPS_OF_INTEREST: tuple[str, ...] = (
    # Daily exchange rates — covers all FX*CAD series. The Fase 5
    # fetcher resolves the symbol parameter against this group's
    # member list to validate the user's input.
    "FX_RATES_DAILY",
)


def _utc_now_iso() -> str:
    """Return the current UTC timestamp in ISO 8601 with ``Z`` suffix."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _write_cache(blob: dict, path: Path | None = None) -> Path:
    """Compress *blob* as LZMA-compressed JSON and write to *path*.

    Returns the path written. Parent directories are created if
    missing. Uses ``preset=9`` for maximum compression (the build
    happens once per release; the cost is paid once at install time
    and pays dividends on every wheel download).

    When *path* is ``None``, the module-level ``_CACHE_FILE`` is
    resolved **at call time** (not at function-definition time) so
    that tests can monkey-patch ``generate_cache._CACHE_FILE`` and
    have the change take effect.
    """
    if path is None:
        # Read at call time so tests that monkey-patch the
        # module-level constant work as expected.
        path = _CACHE_FILE  # type: ignore[assignment]
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(blob, separators=(",", ":")).encode("utf-8")
    with lzma.open(path, "wb", preset=9) as f:
        f.write(raw)
    return path


# ---------------------------------------------------------------------------
# StatsCan fetcher (Fase 2)
# ---------------------------------------------------------------------------
def _parse_homepage_response(payload: Any) -> dict[str, Any]:
    """Parse the ``ind-econ.json`` payload into a structured blob.

    The response shape (per StatsCan's official documentation at
    https://www.statcan.gc.ca/en/developers/ind-econ-json) is::

        {"results": {"geo": [...], "themes_en": [...], "themes_fr": [...],
                      "indicators": [...]}}

    Each indicator carries a ``source`` field (a StatsCan vector ID
    like ``"2280069"``) that the Fase 4 fetcher can use to construct
    observation URLs.

    This parser is defensive: it accepts the documented shape, but
    also tolerates the indicator list being at the top level (some
    StatsCan endpoints return a bare list) or under ``"indicators"``
    without the ``"results"`` wrapper.
    """
    if payload is None:
        return _empty_homepage_blob()

    # Unwrap ``{"results": {...}`` if present.
    if isinstance(payload, dict) and "results" in payload:
        payload = payload["results"]

    if not isinstance(payload, dict):
        return _empty_homepage_blob(warning="unexpected payload type")

    indicators_raw = payload.get("indicators") or []
    geo_raw = payload.get("geo") or []
    themes_en = payload.get("themes_en") or []
    themes_fr = payload.get("themes_fr") or []

    indicators: list[dict[str, Any]] = []
    for raw in indicators_raw:
        if not isinstance(raw, dict):
            continue
        title = raw.get("title") or {}
        value = raw.get("value") or {}
        refper = raw.get("refper") or {}
        growth_rate = raw.get("growth_rate") or {}
        growth = growth_rate.get("growth") or {}
        details = growth_rate.get("details") or {}

        indicators.append(
            {
                "registry_number": str(raw.get("registry_number", "")),
                "indicator_number": str(raw.get("indicator_number", "")),
                "geo_code": str(raw.get("geo_code", "")),
                "title_en": title.get("en", ""),
                "title_fr": title.get("fr", ""),
                "value_en": value.get("en", ""),
                "value_fr": value.get("fr", ""),
                "refper_en": refper.get("en", ""),
                "refper_fr": refper.get("fr", ""),
                "source": str(raw.get("source", "")),  # ← vector ID
                "release_date": str(raw.get("release_date", "")),
                "growth_en": growth.get("en", ""),
                "growth_arrow": str(growth_rate.get("arrow_direction", "")),
                "growth_details_en": details.get("en", ""),
                # Pre-computed URL the Fase 4 fetcher will use to pull
                # observations for this indicator. The WDS endpoint
                # takes a vector ID and a start/end date range.
                "observations_url": (
                    f"{STATSCAN_WDS_BASE}/getDataVector?vectorId="
                    f"{raw.get('source', '')}&startRefPeriod=0&endReferencePeriod=0"
                    if raw.get("source")
                    else ""
                ),
            }
        )

    geo_lookup = {
        str(g.get("geo_code", "")): (g.get("label") or {}).get("en", "")
        for g in geo_raw
        if isinstance(g, dict)
    }
    theme_lookup = {
        str(t.get("theme_id", "")): t.get("label", "")
        for t in themes_en
        if isinstance(t, dict)
    }

    return {
        "homepage_url": STATSCAN_HOMEPAGE_URL,
        "indicators": indicators,
        "geo_lookup": geo_lookup,
        "themes_en": theme_lookup,
        "themes_fr": {
            str(t.get("theme_id", "")): t.get("label", "")
            for t in themes_fr
            if isinstance(t, dict)
        },
        "indicator_count": len(indicators),
    }


def _empty_homepage_blob(warning: str = "") -> dict[str, Any]:
    """Return an empty-but-well-formed homepage blob (no data available)."""
    blob: dict[str, Any] = {
        "homepage_url": STATSCAN_HOMEPAGE_URL,
        "indicators": [],
        "geo_lookup": {},
        "themes_en": {},
        "themes_fr": {},
        "indicator_count": 0,
    }
    if warning:
        blob["warning"] = warning
    return blob


def _fetch_statscan() -> dict:
    """Fetch Statistics Canada metadata.

    Walks the homepage ``ind-econ.json`` endpoint and resolves each
    indicator into a structured cache entry. The Fase 4 fetcher will
    use the ``observations_url`` field on each indicator to pull
    actual time-series observations at runtime.

    Resilience
    ----------
    - Network failures are caught and logged. The build hook does NOT
      abort — instead it ships a partial cache and logs the issue.
    """
    print(
        f"generate-government-ca-cache: fetching StatsCan homepage "
        f"from {STATSCAN_HOMEPAGE_URL}...",
        file=sys.stderr,
    )
    try:
        payload = http_get_json(STATSCAN_HOMEPAGE_URL, timeout=30.0)
    except NetworkError as exc:
        print(
            f"generate-government-ca-cache: WARNING — StatsCan homepage "
            f"unreachable: {exc}. Writing empty statscan section.",
            file=sys.stderr,
        )
        return _empty_homepage_blob(
            warning=f"statscan homepage unreachable at build time: {exc}"
        )

    parsed = _parse_homepage_response(payload)
    print(
        f"generate-government-ca-cache: StatsCan homepage OK — "
        f"{parsed['indicator_count']} indicators resolved.",
        file=sys.stderr,
    )
    return parsed


# ---------------------------------------------------------------------------
# BoC fetcher (Fase 3)
# ---------------------------------------------------------------------------
# Regex that extracts the numeric tenor from a benchmark bond series
# name like ``BD.CDN.10YR.DQ.YLD``. Captures the digit run before
# ``YR``. The Fase 5 yields fetcher uses this to map series to the
# ``treasury_rates`` model fields (year_2, year_3, year_5, year_7,
# year_10, year_30) without hard-coding series names.
import re as _re

_BOND_TENOR_RE = _re.compile(r"^BD\.CDN\.(\d+)YR\.DQ\.YLD$")

# Canonical long-term mapping. The BoC publishes ``BD.CDN.LONG.DQ.YLD``
# as the long-term benchmark (≈30 years). This mapping is documented
# on the BoC's "Canadian Bonds" methodology page and is stable across
# Valet revisions. ``BD.CDN.RRB.DQ.YLD`` is Real Return Bonds
# (inflation-linked) and has no nominal tenor equivalent — it gets
# ``tenor_years=None`` so the Fase 5 yields fetcher skips it when
# filling the ``treasury_rates`` model.
_BOND_LONG_TENOR_YEARS = 30


def _parse_bond_tenor(name: str) -> tuple[str | None, int | None]:
    """Extract ``(tenor_label, tenor_years)`` from a BoC series name.

    Returns ``(None, None)`` for non-bond series. For bond series:

    - ``BD.CDN.2YR.DQ.YLD``   → ``("2Y", 2)``
    - ``BD.CDN.10YR.DQ.YLD``  → ``("10Y", 10)``
    - ``BD.CDN.LONG.DQ.YLD``  → ``("LONG", 30)`` — long-term benchmark
    - ``BD.CDN.RRB.DQ.YLD``   → ``("RRB", None)`` — Real Return Bonds
      (inflation-linked, no nominal tenor equivalent — the Fase 5
      yields fetcher ignores this when filling ``treasury_rates``)

    The mapping is intentionally conservative: only the canonical
    nominal benchmarks get a numeric ``tenor_years``. Anything else
    (RRB, future series we don't recognize) gets ``tenor_years=None``
    so the Fase 5 fetcher can decide what to do.
    """
    upper = name.upper()
    m = _BOND_TENOR_RE.match(upper)
    if m:
        years = int(m.group(1))
        return (f"{years}Y", years)
    if upper == "BD.CDN.LONG.DQ.YLD":
        return ("LONG", _BOND_LONG_TENOR_YEARS)
    if upper == "BD.CDN.RRB.DQ.YLD":
        return ("RRB", None)
    return (None, None)


def _normalize_boc_series_entry(name: str, entry: dict[str, Any]) -> dict[str, Any]:
    """Normalize a single Valet series entry into the cache shape.

    The Valet ``/lists/series/json`` returns entries of the form::

        {"label": "...", "description": "...", "link": "https://..."}

    We add a few derived fields that the Fase 5 fetcher will use:

    - ``observations_url``  — pre-built URL for fetching observations.
    - ``frequency``         — best-effort guess from the series name
                              (``FX*`` → daily, ``BD.CDN.*`` → daily,
                              ``V3907*`` → daily). This is a heuristic
                              because Valet's series list doesn't
                              carry an explicit frequency field.
    - ``tenor``             — for bond series, the tenor label
                              (``"2Y"``, ``"10Y"``, ``"LONG"``,
                              ``"RRB"``). ``None`` for non-bonds.
    - ``tenor_years``       — numeric years (``2``, ``10``, ``30``)
                              for nominal benchmarks; ``None`` for
                              non-bonds or RRB. Lets the Fase 5
                              yields fetcher map directly to
                              ``treasury_rates.year_<N>`` fields
                              without parsing the series name.
    - ``cataloged_at``      — ISO 8601 timestamp for debugging.
    """
    label = str(entry.get("label", "")).strip()
    description = str(entry.get("description", "")).strip()
    link = str(entry.get("link", "")).strip()

    # Best-effort frequency heuristic. The Valet series-list endpoint
    # doesn't expose frequency directly, but the naming conventions
    # are stable enough to guess. The Fase 5 fetcher can override
    # this by passing ``?recent=N`` or ``?start_date=...`` to the
    # observations endpoint.
    upper_name = name.upper()
    if (
        upper_name.startswith("FX")
        or upper_name.startswith("BD.CDN.")
        or upper_name.startswith("V3907")
    ):
        frequency = "daily"
    elif upper_name.startswith("AVG."):
        frequency = "daily"  # CORRA and similar daily averages
    elif upper_name.startswith("A."):
        frequency = "annual"
    elif upper_name.startswith("M."):
        frequency = "monthly"
    else:
        frequency = "unknown"

    tenor, tenor_years = _parse_bond_tenor(name)

    return {
        "name": name,
        "label": label,
        "description": description,
        "link": link,
        "frequency": frequency,
        "tenor": tenor,
        "tenor_years": tenor_years,
        "observations_url": f"{BOC_VALET_BASE}/observations/{name}/json",
        "cataloged_at": _utc_now_iso(),
    }


def _normalize_boc_group_entry(name: str, entry: dict[str, Any]) -> dict[str, Any]:
    """Normalize a single Valet group entry into the cache shape.

    The Valet ``/lists/groups/json`` returns entries of the same
    shape as series (``label``, ``description``, ``link``) but
    without a member list. Resolving members requires a second call
    to ``/groups/<NAME>/json`` — we do that lazily in
    ``_resolve_group_members`` only for groups in
    ``BOC_GROUPS_OF_INTEREST`` to keep build time bounded.
    """
    label = str(entry.get("label", "")).strip()
    description = str(entry.get("description", "")).strip()
    link = str(entry.get("link", "")).strip()

    return {
        "name": name,
        "label": label,
        "description": description,
        "link": link,
        "members_url": f"{BOC_VALET_BASE}/groups/{name}/json",
        "observations_url": (f"{BOC_VALET_BASE}/observations/group/{name}/json"),
        "members": [],  # populated by _resolve_group_members
        "cataloged_at": _utc_now_iso(),
    }


def _resolve_group_members(group_name: str) -> list[str]:
    """Fetch the member list for *group_name* from Valet.

    Returns a sorted list of member series names (e.g.
    ``["FXAUDCAD", "FXEURCAD", ...]``). On failure, returns an empty
    list — the cache entry is still valid, just without member
    resolution. The Fase 5 fetcher can fall back to direct series
    lookups.
    """
    url = f"{BOC_VALET_BASE}/groups/{group_name}/json"
    try:
        payload = http_get_json(url, timeout=30.0)
    except NetworkError as exc:
        print(
            f"generate-government-ca-cache: WARNING — could not resolve "
            f"members of BoC group {group_name!r}: {exc}. Group entry "
            f"will have an empty member list.",
            file=sys.stderr,
        )
        return []

    # The /groups/<NAME>/json endpoint returns the group's details
    # under ``groupDetails.groupSeries``. The keys are the member
    # series names (e.g. ``FXUSDCAD``, ``FXEURCAD``).
    group_details = payload.get("groupDetails", {}) if isinstance(payload, dict) else {}
    group_series = group_details.get("groupSeries", {}) if isinstance(group_details, dict) else {}
    members = sorted(m for m in group_series)
    return members


def _fetch_boc_list(url: str, label: str) -> dict[str, dict[str, Any]]:
    """Fetch a Valet list endpoint (``/lists/series`` or ``/lists/groups``).

    Returns a dict mapping entry name → raw entry dict. On failure,
    raises ``NetworkError`` — the caller handles the
    failure as appropriate.
    """
    print(
        f"generate-government-ca-cache: fetching BoC {label} from {url}...",
        file=sys.stderr,
    )
    payload = http_get_json(url, timeout=60.0)
    # Both list endpoints return ``{"terms": {...}, "series": {...}}``
    # or ``{"terms": {...}, "groups": {...}}``. We extract the
    # relevant map and return it.
    if not isinstance(payload, dict):
        raise NetworkError(url, f"{label} payload is not a dict")
    # The list endpoint uses ``series`` or ``groups`` as the key.
    inner = payload.get("series") or payload.get("groups") or {}
    if not isinstance(inner, dict):
        raise NetworkError(
            url, f"{label} inner payload is not a dict (got {type(inner).__name__})"
        )
    return dict(inner)


def _fetch_boc() -> dict:
    """Fetch Bank of Canada metadata from the Valet API.

    Walks three endpoints:

    1. ``/lists/series/json`` — full catalog of 15,642 series. We
       filter to only those listed in ``BOC_INDIVIDUAL_SERIES`` to
       keep the cache small.
    2. ``/lists/groups/json`` — full catalog of 2,445 groups. We
       filter to only those listed in ``BOC_GROUPS_OF_INTEREST``.
    3. For each group in ``BOC_GROUPS_OF_INTEREST``, an additional
       call to ``/groups/<NAME>/json`` resolves the member list.

    Resilience
    ----------
    - Network failures at the top-level list endpoints produce an
      empty BoC section.
    - Failures resolving group members (3) only blank out that
      group's ``members`` field — the group entry itself is still
      valid.
    """
    # ---- Step 1: fetch the full series list & filter to interest ----
    try:
        all_series_raw = _fetch_boc_list(BOC_LIST_SERIES_URL, "series list")
    except NetworkError as exc:
        print(
            f"generate-government-ca-cache: WARNING — BoC series list "
            f"unreachable: {exc}. Writing empty boc section.",
            file=sys.stderr,
        )
        return _empty_boc_blob(
            warning=f"boc series list unreachable at build time: {exc}"
        )

    print(
        f"generate-government-ca-cache: BoC series list OK — "
        f"{len(all_series_raw)} total series, filtering to "
        f"{len(BOC_INDIVIDUAL_SERIES)} of interest...",
        file=sys.stderr,
    )

    # Build the filtered series cache. If a series-of-interest isn't
    # found in the catalog, we record it under ``missing_series`` so
    # the Fase 5 fetcher can detect the gap and either fall back or
    # raise a clear error.
    series_cache: dict[str, dict[str, Any]] = {}
    missing_series: list[str] = []
    for name in BOC_INDIVIDUAL_SERIES:
        raw_entry = all_series_raw.get(name)
        if raw_entry is None:
            missing_series.append(name)
            continue
        series_cache[name] = _normalize_boc_series_entry(name, raw_entry)

    # ---- Step 2: fetch the full groups list & filter to interest ----
    try:
        all_groups_raw = _fetch_boc_list(BOC_LIST_GROUPS_URL, "groups list")
    except NetworkError as exc:
        print(
            f"generate-government-ca-cache: WARNING — BoC groups list "
            f"unreachable: {exc}. BoC cache will contain series but "
            f"no group member resolution.",
            file=sys.stderr,
        )
        # We still have the series list — partial success. Record the
        # groups failure as a warning rather than aborting the section.
        groups_cache: dict[str, dict[str, Any]] = {}
        groups_warning = f"boc groups list unreachable at build time: {exc}"
    else:
        print(
            f"generate-government-ca-cache: BoC groups list OK — "
            f"{len(all_groups_raw)} total groups, filtering to "
            f"{len(BOC_GROUPS_OF_INTEREST)} of interest...",
            file=sys.stderr,
        )
        groups_cache = {}
        missing_groups: list[str] = []
        for name in BOC_GROUPS_OF_INTEREST:
            raw_entry = all_groups_raw.get(name)
            if raw_entry is None:
                missing_groups.append(name)
                continue
            groups_cache[name] = _normalize_boc_group_entry(name, raw_entry)
        groups_warning = ""

    # ---- Step 3: resolve member lists for each group of interest ----
    if groups_cache:
        for gname, gentry in groups_cache.items():
            members = _resolve_group_members(gname)
            gentry["members"] = members
            print(
                f"generate-government-ca-cache: BoC group {gname!r} "
                f"resolved {len(members)} members.",
                file=sys.stderr,
            )

    # ---- Assemble the final BoC section ----
    blob: dict[str, Any] = {
        "valet_url": BOC_VALET_BASE,
        "series": series_cache,
        "groups": groups_cache,
        "series_count": len(series_cache),
        "groups_count": len(groups_cache),
    }
    if missing_series:
        blob["missing_series"] = missing_series
        print(
            f"generate-government-ca-cache: WARNING — {len(missing_series)} "
            f"series of interest not found in BoC catalog: {missing_series}",
            file=sys.stderr,
        )
    if groups_warning:
        blob["warning"] = groups_warning
    return blob


def _empty_boc_blob(warning: str = "") -> dict[str, Any]:
    """Return an empty-but-well-formed BoC blob."""
    blob: dict[str, Any] = {
        "valet_url": BOC_VALET_BASE,
        "series": {},
        "groups": {},
        "series_count": 0,
        "groups_count": 0,
    }
    if warning:
        blob["warning"] = warning
    return blob


# ---------------------------------------------------------------------------
# Top-level orchestrator
# ---------------------------------------------------------------------------
def build_blob() -> dict:
    """Build the complete cache blob by combining all upstream fetches.

    Each sub-fetcher (``_fetch_boc``, ``_fetch_statscan``) is
    responsible for its own error handling and returns an empty blob
    on failure rather than raising. This means ``build_blob`` itself
    never raises due to network issues — it always produces a
    well-formed blob, possibly with one or both sections empty.

    This is the single entry point used by both ``main()`` (CLI) and
    ``hatch_build.py`` (build hook). Keeping it as a pure function
    makes the cache trivially testable — call ``build_blob()`` with
    the network mocked and assert on the returned dict.
    """
    return {
        "generated_at": _utc_now_iso(),
        "source": "build-hook",
        "boc": _fetch_boc(),
        "statscan": _fetch_statscan(),
    }


def main() -> int:
    """CLI entry point. Returns the process exit code.

    Always returns 0 unless something truly catastrophic happens
    (e.g. the cache file can't be written to disk). Network failures
    are handled inside ``build_blob`` and produce an empty cache,
    not a non-zero exit code.
    """
    print(
        "generate-government-ca-cache: building cache blob...",
        file=sys.stderr,
    )
    blob = build_blob()

    # Light sanity check — fail loudly if the structure is wrong.
    for key in ("generated_at", "source", "boc", "statscan"):
        if key not in blob:
            print(f"ERROR: blob missing required key {key!r}", file=sys.stderr)
            return 2

    print(
        f"generate-government-ca-cache: writing cache to {_CACHE_FILE}...",
        file=sys.stderr,
    )
    written = _write_cache(blob)

    size_kb = written.stat().st_size / 1024
    n_boc_series = blob["boc"].get("series_count", 0)
    n_boc_groups = blob["boc"].get("groups_count", 0)
    n_statscan_indicators = blob["statscan"].get("indicator_count", 0)
    print(
        f"generate-government-ca-cache: done. "
        f"size={size_kb:.1f}KB, "
        f"boc series={n_boc_series} groups={n_boc_groups}, "
        f"statscan indicators={n_statscan_indicators}.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
