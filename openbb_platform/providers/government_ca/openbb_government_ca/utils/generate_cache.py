"""Build-time cache generator for ``openbb-government-ca``.

This script is invoked by ``hatch_build.py`` (by path, not by module
name) and is also exposed as the ``generate-government-ca-cache``
console script.

CRITICAL DESIGN CONSTRAINTS
---------------------------
- Stdlib + ``requests`` only. ``openbb_core`` is NOT a build-time
  dependency and must not be imported here.
- No state outside this file's directory. The cache is written to
  ``assets/government_ca_cache.json.xz`` relative to the package root.
- Fail soft, log loud. If an upstream API is unreachable during
  build, the generator writes a *partial* cache (with the missing
  section marked ``"status": "degraded"`` and a ``"warning"`` field)
  rather than aborting the install.
"""

from __future__ import annotations

import json
import lzma
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _http import NetworkError, http_get_json
else:
    from openbb_government_ca.utils._http import NetworkError, http_get_json

_PKG_ROOT = Path(__file__).resolve().parent.parent
_CACHE_DIR = _PKG_ROOT / "assets"
_CACHE_FILE = _CACHE_DIR / "government_ca_cache.json.xz"

STATSCAN_HOMEPAGE_URL = (
    "https://www150.statcan.gc.ca/n1/dai-quo/ssi/homepage/ind-econ.json"
)
STATSCAN_WDS_BASE = "https://www150.statcan.gc.ca/t1/wds/rest"

BOC_VALET_BASE = "https://www.bankofcanada.ca/valet"
BOC_LIST_SERIES_URL = f"{BOC_VALET_BASE}/lists/series/json"
BOC_LIST_GROUPS_URL = f"{BOC_VALET_BASE}/lists/groups/json"

BOC_INDIVIDUAL_SERIES: tuple[str, ...] = (
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


def _utc_now_iso() -> str:
    """Return the current UTC timestamp in ISO 8601 with ``Z`` suffix."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _write_cache(blob: dict, path: Path | None = None) -> Path:
    """Compress *blob* as LZMA-compressed JSON and write to *path*."""
    if path is None:
        path = _CACHE_FILE  # type: ignore[assignment]
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(blob, separators=(",", ":")).encode("utf-8")
    with lzma.open(path, "wb", preset=9) as f:
        f.write(raw)
    return path


# ---------------------------------------------------------------------------
# StatsCan fetcher
# ---------------------------------------------------------------------------
def _parse_homepage_response(payload: Any) -> dict[str, Any]:
    """Parse the ``ind-econ.json`` payload into a structured blob.

    The response shape is::

        {"results": {"geo": [...], "themes_en": [...], "themes_fr": [...],
                      "indicators": [...]}}

    Each indicator carries a ``source`` field (a StatsCan vector ID
    like ``"2280069"``) used by the runtime fetcher to construct
    observation URLs.
    """
    if payload is None:
        return _empty_homepage_blob()

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
                "source": str(raw.get("source", "")),
                "release_date": str(raw.get("release_date", "")),
                "growth_en": growth.get("en", ""),
                "growth_arrow": str(growth_rate.get("arrow_direction", "")),
                "growth_details_en": details.get("en", ""),
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
    """Return an empty-but-well-formed homepage blob (for degraded mode)."""
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


def _empty_catalog_blob(warning: str = "") -> dict[str, Any]:
    """Return an empty SDMX catalog blob (for degraded mode)."""
    blob: dict[str, Any] = {
        "cubes": {},
        "subjects": {},
        "cube_count": 0,
        "series_count": 0,
    }
    if warning:
        blob["warning"] = warning
    return blob


def _fetch_statscan_catalog() -> dict[str, Any]:
    """Fetch the StatsCan SDMX-style catalog via the WDS REST API.

    Walks two endpoints:

    1. ``getAllCubesListLite`` — lightweight cube list with PID, name,
       frequency, subject, release date. Used to populate the parent
       dimension of the catalog (cubes → series).
    2. ``getCubeMetadata`` — for each cube, fetches dimensions,
       codelists, members, and series info (vector IDs). Used to
       populate the child dimension (series within each cube).

    The catalog is **pure metadata**: descriptions, dimensions,
    codelists, and availability constraints. It carries NO series
    values. The runtime fetcher uses it to resolve user queries
    (lookup, list, search) and to build parameter Literal types.

    Network failures degrade gracefully: a failed cube-list fetch
    returns an empty catalog with ``"status": "degraded"``; a failed
    per-cube metadata fetch skips just that cube.
    """
    cubes_url = f"{STATSCAN_WDS_BASE}/getAllCubesListLite"
    print(
        f"generate-government-ca-cache: fetching StatsCan cube list "
        f"from {cubes_url}...",
        file=sys.stderr,
    )
    try:
        cubes_payload = http_get_json(cubes_url, timeout=60.0)
    except NetworkError as exc:
        print(
            f"generate-government-ca-cache: WARNING — StatsCan cube list "
            f"unreachable: {exc}. Writing degraded SDMX catalog.",
            file=sys.stderr,
        )
        blob = _empty_catalog_blob(
            warning=f"statscan cube list unreachable at build time: {exc}"
        )
        blob["status"] = "degraded"
        return blob

    if not isinstance(cubes_payload, list):
        msg = f"unexpected cubes payload type: {type(cubes_payload).__name__}"
        print(f"generate-government-ca-cache: WARNING — {msg}.", file=sys.stderr)
        blob = _empty_catalog_blob(warning=msg)
        blob["status"] = "degraded"
        return blob

    cubes: dict[str, dict[str, Any]] = {}
    subjects: dict[str, str] = {}
    series_count = 0

    for entry in cubes_payload:
        if not isinstance(entry, dict):
            continue
        pid = str(entry.get("productId", ""))
        if not pid:
            continue
        subject_code = str(entry.get("subjectCode", ""))
        subject_label = str(entry.get("subject", ""))
        if subject_code and subject_label:
            subjects[subject_code] = subject_label

        cubes[pid] = {
            "pid": pid,
            "title_en": str(entry.get("cansimTitleEn", "")),
            "title_fr": str(entry.get("cansimTitleFr", "")),
            "frequency_code": str(entry.get("frequencyCode", "")),
            "subject_code": subject_code,
            "subject_label": subject_label,
            "release_date": str(entry.get("releaseTime", "")),
            "cancelled": bool(entry.get("cancelled", False)),
            "metadata_url": f"{STATSCAN_WDS_BASE}/getCubeMetadata?productId={pid}",
            "series": [],
        }

    print(
        f"generate-government-ca-cache: StatsCan cube list OK — "
        f"{len(cubes)} cubes. Fetching per-cube metadata...",
        file=sys.stderr,
    )

    for pid, cube_entry in cubes.items():
        meta_url = cube_entry["metadata_url"]
        try:
            meta_payload = http_get_json(meta_url, timeout=30.0)
        except NetworkError as exc:
            print(
                f"generate-government-ca-cache: WARNING — metadata for cube "
                f"{pid} unreachable: {exc}. Skipping.",
                file=sys.stderr,
            )
            continue

        if not isinstance(meta_payload, list) or not meta_payload:
            continue
        cube_meta = meta_payload[0]
        if not isinstance(cube_meta, dict):
            continue

        dimensions = []
        for dim in cube_meta.get("dimension", []):
            if not isinstance(dim, dict):
                continue
            members = []
            for m in dim.get("member", []):
                if not isinstance(m, dict):
                    continue
                members.append(
                    {
                        "id": str(m.get("memberId", "")),
                        "code": str(m.get("memberCode", "")),
                        "label_en": str(m.get("memberNameEn", "")),
                        "label_fr": str(m.get("memberNameFr", "")),
                        "parent_id": str(m.get("parentMemberId", "")) or None,
                    }
                )
            dimensions.append(
                {
                    "id": str(dim.get("dimensionId", "")),
                    "code": str(dim.get("dimensionNameEn", "")),
                    "label_en": str(dim.get("dimensionNameEn", "")),
                    "label_fr": str(dim.get("dimensionNameFr", "")),
                    "position": int(dim.get("dimensionPositionId", 0) or 0),
                    "members": members,
                }
            )

        series_list = []
        for s in cube_meta.get("series", []):
            if not isinstance(s, dict):
                continue
            vector_id = str(s.get("vectorId", ""))
            if not vector_id:
                continue
            series_list.append(
                {
                    "vector_id": vector_id,
                    "coordinate": str(s.get("coordinate", "")),
                    "label_en": str(s.get("seriesNameEn", "")),
                    "label_fr": str(s.get("seriesNameFr", "")),
                    "scalar_factor_code": str(s.get("scalerFactorCode", "")),
                    "uom_code": str(s.get("memberUomCode", "")),
                    "frequency_code": str(s.get("frequencyCode", "")),
                    "release_date": str(s.get("releaseTime", "")),
                    "observations_url": (
                        f"{STATSCAN_WDS_BASE}/getDataFromVectorAndLatestNPeriods"
                        f"?vectorIds={vector_id}"
                    ),
                }
            )

        cube_entry["dimensions"] = dimensions
        cube_entry["series"] = series_list
        cube_entry["cansim_id"] = str(cube_meta.get("cansimId", ""))
        cube_entry["survey_code"] = str(cube_meta.get("surveyCode", ""))
        cube_entry["subject_code"] = (
            str(cube_meta.get("subjectCode", "")) or cube_entry["subject_code"]
        )
        cube_entry["title_en"] = (
            str(cube_meta.get("cansimTitleEn", "")) or cube_entry["title_en"]
        )
        cube_entry["title_fr"] = (
            str(cube_meta.get("cansimTitleFr", "")) or cube_entry["title_fr"]
        )
        cube_entry["last_published"] = str(cube_meta.get("lastPublishedCube", ""))
        series_count += len(series_list)

    blob: dict[str, Any] = {
        "wds_url": STATSCAN_WDS_BASE,
        "cubes": cubes,
        "subjects": subjects,
        "cube_count": len(cubes),
        "series_count": series_count,
        "status": "ok",
    }
    print(
        f"generate-government-ca-cache: StatsCan SDMX catalog OK — "
        f"{len(cubes)} cubes, {series_count} series.",
        file=sys.stderr,
    )
    return blob


def _fetch_statscan() -> dict:
    """Fetch Statistics Canada metadata (homepage + SDMX catalog)."""
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
            f"unreachable: {exc}. Writing degraded statscan section.",
            file=sys.stderr,
        )
        blob = _empty_homepage_blob(
            warning=f"statscan homepage unreachable at build time: {exc}"
        )
        blob["status"] = "degraded"
        blob["catalog"] = _empty_catalog_blob(
            warning=f"statscan homepage unreachable at build time: {exc}"
        )
        blob["catalog"]["status"] = "degraded"
        return blob

    parsed = _parse_homepage_response(payload)
    parsed["status"] = "ok"
    print(
        f"generate-government-ca-cache: StatsCan homepage OK — "
        f"{parsed['indicator_count']} indicators resolved.",
        file=sys.stderr,
    )

    parsed["catalog"] = _fetch_statscan_catalog()
    return parsed


# ---------------------------------------------------------------------------
# BoC fetcher
# ---------------------------------------------------------------------------
import re as _re

_BOND_TENOR_RE = _re.compile(r"^BD\.CDN\.(\d+)YR\.DQ\.YLD$")

_BOND_LONG_TENOR_YEARS = 30


def _parse_bond_tenor(name: str) -> tuple[str | None, int | None]:
    """Extract ``(tenor_label, tenor_years)`` from a BoC series name."""
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
    """Normalize a single Valet series entry into the cache shape."""
    label = str(entry.get("label", "")).strip()
    description = str(entry.get("description", "")).strip()
    link = str(entry.get("link", "")).strip()

    upper_name = name.upper()
    if (
        upper_name.startswith("FX")
        or upper_name.startswith("BD.CDN.")
        or upper_name.startswith("V3907")
    ) or upper_name.startswith("AVG."):
        frequency = "daily"
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
    """Normalize a single Valet group entry into the cache shape."""
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
        "members": [],
        "cataloged_at": _utc_now_iso(),
    }


def _resolve_group_members(group_name: str) -> list[str]:
    """Fetch the member list for *group_name* from Valet."""
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

    groups_dict = payload.get("groups", {}) if isinstance(payload, dict) else {}
    members = sorted(m for m in groups_dict if m != group_name)
    return members


def _fetch_boc_list(url: str, label: str) -> dict[str, dict[str, Any]]:
    """Fetch a Valet list endpoint (``/lists/series`` or ``/lists/groups``)."""
    print(
        f"generate-government-ca-cache: fetching BoC {label} from {url}...",
        file=sys.stderr,
    )
    payload = http_get_json(url, timeout=60.0)
    if not isinstance(payload, dict):
        raise NetworkError(url, f"{label} payload is not a dict")
    inner = payload.get("series") or payload.get("groups") or {}
    if not isinstance(inner, dict):
        raise NetworkError(
            url, f"{label} inner payload is not a dict (got {type(inner).__name__})"
        )
    return dict(inner)


def _fetch_boc() -> dict:
    """Fetch Bank of Canada metadata from the Valet API."""
    try:
        all_series_raw = _fetch_boc_list(BOC_LIST_SERIES_URL, "series list")
    except NetworkError as exc:
        print(
            f"generate-government-ca-cache: WARNING — BoC series list "
            f"unreachable: {exc}. Writing degraded boc section.",
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

    series_cache: dict[str, dict[str, Any]] = {}
    missing_series: list[str] = []
    for name in BOC_INDIVIDUAL_SERIES:
        raw_entry = all_series_raw.get(name)
        if raw_entry is None:
            missing_series.append(name)
            continue
        series_cache[name] = _normalize_boc_series_entry(name, raw_entry)

    try:
        all_groups_raw = _fetch_boc_list(BOC_LIST_GROUPS_URL, "groups list")
    except NetworkError as exc:
        print(
            f"generate-government-ca-cache: WARNING — BoC groups list "
            f"unreachable: {exc}. BoC cache will contain series but "
            f"no group member resolution.",
            file=sys.stderr,
        )
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

    if groups_cache:
        for gname, gentry in groups_cache.items():
            members = _resolve_group_members(gname)
            gentry["members"] = members
            print(
                f"generate-government-ca-cache: BoC group {gname!r} "
                f"resolved {len(members)} members.",
                file=sys.stderr,
            )

    blob: dict[str, Any] = {
        "valet_url": BOC_VALET_BASE,
        "series": series_cache,
        "groups": groups_cache,
        "series_count": len(series_cache),
        "groups_count": len(groups_cache),
        "status": "ok",
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
    """Return an empty-but-well-formed BoC blob (for degraded mode)."""
    blob: dict[str, Any] = {
        "valet_url": BOC_VALET_BASE,
        "series": {},
        "groups": {},
        "series_count": 0,
        "groups_count": 0,
        "status": "degraded",
    }
    if warning:
        blob["warning"] = warning
    return blob


# ---------------------------------------------------------------------------
# Top-level orchestrator
# ---------------------------------------------------------------------------
def build_blob() -> dict:
    """Build the complete cache blob by combining all upstream fetches."""
    return {
        "generated_at": _utc_now_iso(),
        "source": "build-hook",
        "boc": _fetch_boc(),
        "statscan": _fetch_statscan(),
    }


def main() -> int:
    """CLI entry point. Returns the process exit code."""
    print(
        "generate-government-ca-cache: building cache blob...",
        file=sys.stderr,
    )
    blob = build_blob()

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
    catalog = blob["statscan"].get("catalog", {})
    n_cubes = catalog.get("cube_count", 0)
    n_catalog_series = catalog.get("series_count", 0)
    boc_status = blob["boc"].get("status", "unknown")
    statscan_status = blob["statscan"].get("status", "unknown")
    print(
        f"generate-government-ca-cache: done. "
        f"size={size_kb:.1f}KB, "
        f"boc[{boc_status}] series={n_boc_series} groups={n_boc_groups}, "
        f"statscan[{statscan_status}] indicators={n_statscan_indicators} "
        f"cubes={n_cubes} catalog_series={n_catalog_series}.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
