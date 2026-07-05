"""Statistics Canada runtime metadata loader.

Reads the StatsCan section of the shipped cache
(``assets/government_ca_cache.json.xz``) without making any network
calls. The cache itself is populated at build time by
``openbb_government_ca.utils.generate_cache``.

The cache carries two complementary views:

- ``indicators`` — the curated "Key Economic Indicators" list from the
  StatsCan homepage (``ind-econ.json``). Each entry has a ``source``
  field with the vector ID used to fetch observations at runtime.
- ``catalog`` — the SDMX-style catalog built from the WDS REST API.
  Contains ``cubes`` (one entry per PID) with dimensions, codelists,
  members, and series (vector IDs). This is **pure metadata**: no
  series values. The runtime fetcher uses it for lookup, listing,
  searching, and parameter Literal types.
"""

from __future__ import annotations

from typing import Any

STATSCAN_PRODUCTS_OF_INTEREST: tuple[str, ...] = ("ind-econ",)


def lookup_product(product_id: str, cache: dict[str, Any]) -> dict[str, Any]:
    """Return the cache section for *product_id*, or raise ``KeyError``.

    Parameters
    ----------
    product_id
        Either a numeric StatsCan vector ID (``"2280069"``) or the
        special token ``"ind-econ"`` for the whole homepage section.
    cache
        The already-loaded StatsCan cache section.
    """
    if product_id == "ind-econ":
        if "indicators" in cache or "homepage_url" in cache:
            return cache
        raise KeyError(
            f"Statistics Canada 'ind-econ' section not found in cache. "
            f"Available keys: {sorted(cache.keys())}"
        )

    indicators = cache.get("indicators", [])
    for ind in indicators:
        if str(ind.get("source", "")) == str(product_id):
            return ind

    sources = [str(i.get("source", "")) for i in indicators if i.get("source")]
    candidates = sorted(s for s in sources if s.startswith(str(product_id)[:3]))
    hint = f" Did you mean one of: {', '.join(candidates[:5])}?" if candidates else ""
    msg = (
        f"Statistics Canada vector/product '{product_id}' not found in cache. "
        f"The cache contains {len(indicators)} indicators."
        f"{hint}"
    )
    raise KeyError(msg)


def list_indicators(cache: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the list of homepage indicators from *cache*."""
    return list(cache.get("indicators", []))


def is_degraded(cache: dict[str, Any]) -> bool:
    """Return ``True`` if the StatsCan cache section was built in degraded mode."""
    return cache.get("status") == "degraded"


def get_catalog(cache: dict[str, Any]) -> dict[str, Any]:
    """Return the SDMX-style catalog section, or an empty dict if absent."""
    catalog = cache.get("catalog") or {}
    return catalog if isinstance(catalog, dict) else {}


def list_cubes(cache: dict[str, Any]) -> list[dict[str, Any]]:
    """Return all cubes in the SDMX catalog as a list."""
    catalog = get_catalog(cache)
    return list(catalog.get("cubes", {}).values())


def lookup_cube(pid: str, cache: dict[str, Any]) -> dict[str, Any]:
    """Return the cube with PID *pid*, or raise ``KeyError``."""
    catalog = get_catalog(cache)
    cubes = catalog.get("cubes", {})
    if pid in cubes:
        return cubes[pid]
    raise KeyError(
        f"StatsCan cube PID {pid!r} not found in catalog. "
        f"The catalog contains {len(cubes)} cubes."
    )


def lookup_series_by_vector(vector_id: str, cache: dict[str, Any]) -> dict[str, Any]:
    """Return the catalog series entry for *vector_id*, or raise ``KeyError``.

    Searches every cube's ``series`` list and returns the first match
    along with the parent cube's PID in the ``cube_pid`` field.
    """
    needle = str(vector_id).lstrip("Vv")
    for cube in list_cubes(cache):
        for s in cube.get("series", []):
            vid = str(s.get("vector_id", "")).lstrip("Vv")
            if vid == needle:
                merged = dict(s)
                merged["cube_pid"] = cube.get("pid", "")
                merged["cube_title_en"] = cube.get("title_en", "")
                return merged
    raise KeyError(
        f"StatsCan vector {vector_id!r} not found in catalog. "
        f"Searched {len(list_cubes(cache))} cubes."
    )


def search_series(query: str, cache: dict[str, Any]) -> list[dict[str, Any]]:
    """Return all catalog series whose label contains *query* (case-insensitive).

    Each result is enriched with ``cube_pid`` and ``cube_title_en``.
    """
    needle = (query or "").lower().strip()
    results: list[dict[str, Any]] = []
    if not needle:
        return results
    for cube in list_cubes(cache):
        for s in cube.get("series", []):
            label = str(s.get("label_en", "")).lower()
            if needle in label:
                merged = dict(s)
                merged["cube_pid"] = cube.get("pid", "")
                merged["cube_title_en"] = cube.get("title_en", "")
                results.append(merged)
    return results


def list_subjects(cache: dict[str, Any]) -> dict[str, str]:
    """Return the ``{subject_code: label}`` mapping from the catalog."""
    catalog = get_catalog(cache)
    return dict(catalog.get("subjects", {}))
