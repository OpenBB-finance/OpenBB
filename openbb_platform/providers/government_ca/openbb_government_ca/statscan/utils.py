"""Statistics Canada runtime metadata loader.

Reads the StatsCan section of the shipped cache
(``assets/government_ca_cache.json.xz``) without making any network
calls. The cache itself is populated at build time by
``openbb_government_ca.utils.generate_cache`` (Fase 2).

StatsCan's developer surface (https://www.statcan.gc.ca/en/developers)
exposes several JSON endpoints. This extension consumes:

- ``https://www150.statcan.gc.ca/n1/dai-quo/ssi/homepage/ind-econ.json``
  The curated list of "key economic indicators" shown on the StatsCan
  homepage. Each entry carries a ``source`` field (a StatsCan vector
  ID like ``"2280069"``) that the Fase 4 fetcher can use to construct
  observation URLs via the Web Data Service (WDS).

The cache we ship (produced by Fase 2) contains:

- ``homepage_url``    — the source URL
- ``indicators``      — list of dicts, one per homepage indicator,
                        each with ``title_en``, ``source`` (vector ID),
                        ``refper_en``, ``growth_en``, ``observations_url``
- ``geo_lookup``      — ``{geo_code: english_label}``
- ``themes_en``       — ``{theme_id: label}``
- ``themes_fr``       — ``{theme_id: label}`` (kept for parity)
- ``indicator_count`` — len(indicators)

This module is a thin lookup layer; the actual API calls happen in
the fetchers themselves.
"""

from __future__ import annotations

from typing import Any

# Special tokens that the Fase 4 fetcher can use to address cache
# sections without hard-coding string literals. Adding a new curated
# view means adding its token here.
STATSCAN_PRODUCTS_OF_INTEREST: tuple[str, ...] = (
    # Key economic indicators — GDP, CPI, unemployment, retail sales,
    # merchandise trade, manufacturing sales, wholesale trade. This
    # is the curated list exposed on the StatsCan homepage.
    "ind-econ",
)


def lookup_product(product_id: str, cache: dict[str, Any]) -> dict[str, Any]:
    """Return the cache section for *product_id*, or raise ``KeyError``.

    Parameters
    ----------
    product_id
        Either a numeric StatsCan vector ID (``"2280069"`` — matches
        the ``source`` field of an indicator in ``ind-econ.json``) or
        the special token ``"ind-econ"`` for the whole homepage
        section.
    cache
        The already-loaded StatsCan cache section (typically
        ``GovernmentCaMetadata().statscan``).

    Returns
    -------
    dict
        For ``"ind-econ"``: the whole StatsCan section (with
        ``indicators``, ``geo_lookup``, etc.).
        For a numeric vector ID: the individual indicator dict.

    Raises
    ------
    KeyError
        If the product/vector is not present in the cache.
    """
    # Special token: return the whole homepage section.
    if product_id == "ind-econ":
        if "indicators" in cache or "homepage_url" in cache:
            return cache
        raise KeyError(
            f"Statistics Canada 'ind-econ' section not found in cache. "
            f"Available keys: {sorted(cache.keys())}"
        )

    # Numeric vector ID: look it up in the indicators list.
    indicators = cache.get("indicators", [])
    for ind in indicators:
        if str(ind.get("source", "")) == str(product_id):
            return ind

    # Helpful "did you mean" hint using a trivial prefix match.
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
    """Return the list of homepage indicators from *cache*.

    Convenience wrapper around ``cache.get("indicators", [])`` so
    callers don't have to know the cache shape.
    """
    return list(cache.get("indicators", []))
