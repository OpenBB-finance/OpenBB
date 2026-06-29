"""Statistics Canada Economic Indicators — key indicators from the homepage.

This fetcher reads from the shipped metadata cache (populated at build
time by Fase 2 of ``generate_cache.py``) and returns the latest
published values of StatsCan's curated "Key Economic Indicators"
homepage list (GDP, CPI, unemployment, retail sales, merchandise
trade, manufacturing sales, wholesale trade, etc.).

It maps to OpenBB's standard ``economy.indicators`` model — the same
model used by ``openbb-oecd`` (PR #7413) — so users get a consistent
interface across Canadian and international economic data.

Design notes
------------
- **No network calls in the happy path.** The cache already contains
  the latest snapshot values from the ``ind-econ.json`` endpoint (the
  ``value_en`` field of each indicator). Fetching historical
  time-series is a separate concern (a future ``observations``
  fetcher that calls the WDS API).
- **Graceful degradation.** If the cache was built in degraded mode
  (StatsCan was unreachable at install time), the fetcher raises a
  clear ``OpenBBError`` instead of returning empty data — this
  matches the user's explicit request from Fase 4.
- **Symbol resolution.** Users can pass either a vector ID
  (``"2280069"`` for Imports), a title substring (``"Imports"``), or
  the special token ``"all"`` to get every homepage indicator.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.economic_indicators import (
    EconomicIndicatorsData,
    EconomicIndicatorsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_government_ca.statscan.utils import is_degraded, list_indicators
from openbb_government_ca.utils.metadata import GovernmentCaMetadata

# Regex used to extract a numeric value from the human-readable
# ``value_en`` string (e.g. ``"$47.6 billion"`` → ``47.6``). The BoC
# and StatsCan both use this style for headline figures. We extract
# the first number-like token and convert to float; if parsing fails
# we leave ``value=None`` and the raw string is preserved in
# ``value_raw`` (an extension field on the Data model).
_NUMERIC_RE = re.compile(r"-?\d+(?:[,\s]\d{3})*(?:\.\d+)?")


def _parse_value(value_str: str) -> float | None:
    """Extract the first numeric value from *value_str*, or ``None``.

    Handles common StatsCan/BoC formatting conventions:
    - ``"$47.6 billion"``     → 47.6
    - ``"18,161,000"``        → 18161000.0
    - ``"-3.9%"``             → -3.9
    - ``"-$1.5 billion"``     → -1.5  (sign before currency symbol)
    - ``"($1.5 billion)"``    → -1.5  (accounting convention for negatives)
    - ``"83,751.6 million"``  → 83751.6
    - ``".."`` / ``""``       → None (StatsCan missing marker)
    """
    if not value_str or not isinstance(value_str, str):
        return None
    s = value_str.strip()
    if s in {"", "..", "...", "NaN", "N/A", "n/a", "NA"}:
        return None
    m = _NUMERIC_RE.search(s)
    if m is None:
        return None
    # Strip thousands separators (comma or space) before float conversion.
    cleaned = m.group(0).replace(",", "").replace(" ", "")
    try:
        value = float(cleaned)
    except ValueError:  # pragma: no cover - regex only matches numeric patterns
        return None
    # Detect a negative sign that's separated from the digits by a
    # currency symbol or other punctuation (e.g. "-$1.5B", "($1.5B)").
    # We look at the substring BEFORE the matched digits; if it contains
    # a "-" or "(" that's not part of another number, we negate.
    prefix = s[: m.start()]
    if "-" in prefix or "(" in prefix:
        value = -abs(value)
    return value


def _parse_refper_to_date(refper: str) -> date | None:
    """Parse a StatsCan ``refper`` string like ``"September 2016"`` to a date.

    Returns the first day of the referenced month (or year, for annual
    indicators). Returns ``None`` if parsing fails — the standard
    model's ``date`` field is optional.
    """
    if not refper or not isinstance(refper, str):
        return None
    s = refper.strip()
    if not s:
        return None

    # Annual: "2016"
    if s.isdigit() and len(s) == 4:
        try:
            return date(int(s), 1, 1)
        except ValueError:
            return None

    # Monthly: "September 2016"
    month_names = [
        "january",
        "february",
        "march",
        "april",
        "may",
        "june",
        "july",
        "august",
        "september",
        "october",
        "november",
        "december",
    ]
    lower = s.lower()
    for i, mname in enumerate(month_names, start=1):
        if lower.startswith(mname):
            # Find the year (4-digit number at the end).
            year_str = s[len(mname) :].strip()
            if year_str.isdigit() and len(year_str) == 4:
                try:
                    return date(int(year_str), i, 1)
                except ValueError:
                    return None
    return None


class StatsCanEconomicIndicatorsQueryParams(EconomicIndicatorsQueryParams):
    """StatsCan Economic Indicators Query.

    Extends the standard model with StatsCan-specific defaults and
    validation. The ``symbol`` field accepts:

    - A numeric vector ID (``"2280069"`` — matches the ``source``
      field of an indicator in ``ind-econ.json``)
    - A title substring (``"Imports"``, ``"Employment"`` —
      case-insensitive match against ``title_en``)
    - The special token ``"all"`` (returns every homepage indicator)
    - A comma-separated list of any of the above
    """

    __json_schema_extra__ = {
        "symbol": {
            "multiple_items_allowed": True,
            "description": (
                "StatsCan vector ID (e.g. '2280069' for Imports), "
                "indicator title substring (e.g. 'Imports'), or 'all' "
                "for every homepage indicator."
            ),
        },
        "country": {
            "description": (
                "StatsCan geo_code. Defaults to '0' (Canada). "
                "Other values: '1'='Newfoundland and Labrador', "
                "'13'='Nunavut', etc."
            ),
        },
    }

    country: str = Field(
        default="0",
        description="StatsCan geo_code (default '0' = Canada).",
    )


class StatsCanEconomicIndicatorsData(EconomicIndicatorsData):
    """StatsCan Economic Indicators Data.

    Extends the standard model with StatsCan-specific fields that
    aren't part of the OpenBB standard but are useful for users who
    want the full context (growth rate, release date, raw value
    string with units).
    """

    value_raw: str | None = Field(
        default=None,
        description="The raw value string from StatsCan (e.g. '$47.6 billion').",
    )
    refper: str | None = Field(
        default=None,
        description="The reference period as published by StatsCan (e.g. 'September 2016').",
    )
    growth_rate: str | None = Field(
        default=None,
        description="The period-over-period growth rate string (e.g. '4.7%').",
    )
    growth_direction: str | None = Field(
        default=None,
        description=(
            "Arrow direction from StatsCan: '1' = up, '2' = down, '3' = flat."
        ),
    )
    growth_details: str | None = Field(
        default=None,
        description=("Context for the growth rate (e.g. '(monthly change)')."),
    )
    release_date: str | None = Field(
        default=None,
        description="ISO date when StatsCan released this indicator.",
    )
    daily_url: str | None = Field(
        default=None,
        description="URL to the StatsCan Daily article for this indicator.",
    )


class StatsCanEconomicIndicatorsFetcher(
    Fetcher[
        StatsCanEconomicIndicatorsQueryParams,
        list[StatsCanEconomicIndicatorsData],
    ]
):
    """StatsCan Economic Indicators Fetcher.

    Reads from the shipped metadata cache (no network in the happy
    path). Returns the latest snapshot values of StatsCan's curated
    homepage economic indicators.
    """

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> StatsCanEconomicIndicatorsQueryParams:
        """Transform the raw params dict into a validated query model."""
        transformed = params.copy()
        # Default to 'all' if no symbol is provided — this matches the
        # OECD fetcher's convention and gives users a useful default.
        if not transformed.get("symbol"):
            transformed["symbol"] = "all"
        # Normalize country: if user passes "canada", convert to geo_code "0".
        country = transformed.get("country")
        if country and isinstance(country, str):
            lower = country.lower().strip()
            if lower in {"canada", "ca", "can"}:
                transformed["country"] = "0"
        return StatsCanEconomicIndicatorsQueryParams(**transformed)

    @staticmethod
    def extract_data(
        query: StatsCanEconomicIndicatorsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw indicator dicts from the cache.

        No network calls — reads exclusively from the shipped metadata
        cache. If the cache is in degraded mode, raises ``OpenBBError``
        with a clear message about reinstalling the package.
        """
        meta = GovernmentCaMetadata()
        statscan_cache = meta.statscan

        if is_degraded(statscan_cache):
            raise OpenBBError(
                "StatsCan metadata cache is in degraded mode — the package "
                "was built when www150.statcan.gc.ca was unreachable. "
                "Reinstall openbb-government-ca with "
                "OPENBB_GOVERNMENT_CA_FORCE_CACHE_REBUILD=1 to retry."
            )

        all_indicators = list_indicators(statscan_cache)
        if not all_indicators:
            raise EmptyDataError(
                "StatsCan cache contains no indicators. The build may have "
                "failed silently — check the build log."
            )

        # Parse the symbol parameter into a list of search terms.
        # The standard model allows comma-separated multi-value.
        symbols = [s.strip() for s in query.symbol.split(",") if s.strip()]
        if not symbols or "all" in [s.lower() for s in symbols]:
            # Filter by geo_code only.
            filtered = [
                ind
                for ind in all_indicators
                if str(ind.get("geo_code", "0")) == str(query.country)
            ]
            if not filtered:
                # If no indicators match the geo_code, return all (the
                # homepage list is mostly Canada-level anyway).
                filtered = list(all_indicators)
            return filtered

        # For each symbol term, match against vector ID (source) or
        # title substring. Deduplicate by source vector ID.
        matched: dict[str, dict] = {}
        for term in symbols:
            term_lower = term.lower()
            for ind in all_indicators:
                source = str(ind.get("source", ""))
                title_en = str(ind.get("title_en", "")).lower()
                # Match by vector ID (exact).
                if source and source == term:
                    matched[source] = ind
                    continue
                # Match by title substring.
                if (
                    term_lower != "all"
                    and term_lower in title_en
                    and source not in matched
                ):
                    matched[source] = ind

        if not matched:
            raise EmptyDataError(
                f"No StatsCan indicators matched symbol={query.symbol!r}. "
                f"Pass 'all' for every homepage indicator, or a vector ID "
                f"(e.g. '2280069' for Imports), or a title substring "
                f"(e.g. 'Imports')."
            )

        return list(matched.values())

    @staticmethod
    def transform_data(
        query: StatsCanEconomicIndicatorsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[StatsCanEconomicIndicatorsData]:
        """Map raw indicator dicts to the standard ``EconomicIndicatorsData`` model.

        Each indicator becomes one row. The ``value`` field is parsed
        from the human-readable ``value_en`` string (e.g. "$47.6
        billion" → 47.6); the raw string is preserved in the
        ``value_raw`` extension field.
        """
        meta = GovernmentCaMetadata()
        geo_lookup = meta.statscan.get("geo_lookup", {})

        output: list[StatsCanEconomicIndicatorsData] = []
        for ind in data:
            source = str(ind.get("source", ""))
            title_en = str(ind.get("title_en", ""))
            value_en = str(ind.get("value_en", ""))
            refper_en = str(ind.get("refper_en", ""))
            geo_code = str(ind.get("geo_code", "0"))

            country_label = geo_lookup.get(geo_code, "Canada")
            obs_date = _parse_refper_to_date(refper_en)
            parsed_value = _parse_value(value_en)

            output.append(
                StatsCanEconomicIndicatorsData(
                    date=obs_date,
                    symbol_root=title_en or source,
                    symbol=source,
                    country=country_label,
                    value=parsed_value,
                    value_raw=value_en or None,
                    refper=refper_en or None,
                    growth_rate=str(ind.get("growth_en", "")) or None,
                    growth_direction=str(ind.get("growth_arrow", "")) or None,
                    growth_details=str(ind.get("growth_details_en", "")) or None,
                    release_date=str(ind.get("release_date", "")) or None,
                    daily_url=None,  # not stored in the cache; could be added later
                )
            )

        # Sort by date descending (most recent first), then by title.
        output.sort(
            key=lambda x: (
                x.date is None,
                -(x.date.toordinal() if x.date else 0),
                x.symbol_root or "",
            )
        )
        return output
