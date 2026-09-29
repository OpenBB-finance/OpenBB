"""Federal Reserve Bank of Boston New England Economic Indicators helpers."""

from __future__ import annotations

import base64
import json
import re
from typing import Any

BASE_URL = "https://www.bostonfed.org"
NEEI_URL = f"{BASE_URL}/data/data-tools/new-england-economic-indicators"

_SERIES_DATA = re.compile(
    r'<div class="hidden series-data">\s*([^<]+?)\s*</div>', re.DOTALL
)
_ANCHOR = re.compile(r"<a[^>]*>([^<]+)</a>")

INDICATORS: dict[str, str] = {
    "payroll_employment": "Payroll Employment",
    "employment_by_supersector": "Employment by Supersector",
    "labor_force_participation_rate": "Labor Force Participation Rate",
    "job_openings_rate_jolts": "Job Openings Rate (JOLTS)",
    "number_unemployed": "Number Unemployed",
    "initial_claims": "Initial Claims",
    "unemployment_rates": "Unemployment Rates",
    "u_6_rate": "U-6 Rate",
    "average_hourly_earnings": "Average Hourly Earnings",
    "personal_income": "Personal Income",
    "wages_and_salaries": "Wages and Salaries",
    "employment_cost_index": "Employment Cost Index",
    "consumer_price_index": "Consumer Price Index",
    "home_price_index": "Home Price Index",
    "housing_permits": "Housing Permits",
    "construction_contracts_dodge": "Construction Contracts (Dodge)",
    "zillow_observed_rent_index": "Zillow Observed Rent Index",
    "total_exports": "Total Exports",
    "total_exports_by_industries": "Total Exports by Industries",
    "total_exports_by_destination": "Total Exports by Destination",
    "economic_activity_index": "Economic Activity Index",
}

GEOGRAPHIES: dict[str, str] = {
    "us": "United States",
    "new_england": "New England",
    "ct": "Connecticut",
    "me": "Maine",
    "ma": "Massachusetts",
    "nh": "New Hampshire",
    "ri": "Rhode Island",
    "vt": "Vermont",
}

_GEOGRAPHY_BY_CODE: dict[str, str] = {
    "111": "us",
    "111100": "new_england",
    "111110": "new_england",
    "09": "ct",
    "23": "me",
    "25": "ma",
    "33": "nh",
    "44": "ri",
    "50": "vt",
    "14460": "ma",
    "25540": "ct",
    "38860": "me",
    "31700": "nh",
    "39300": "ri",
    "15540": "vt",
}

_GEOGRAPHY_BY_NAME: dict[str, str] = {
    "us": "us",
    "ne": "new_england",
    "ct": "ct",
    "me": "me",
    "ma": "ma",
    "nh": "nh",
    "ri": "ri",
    "vt": "vt",
}

_TRANSFORMS: dict[str | None, str] = {
    "YRYR%": "year_over_year_percent",
    "index": "index",
}

_TRANSFORM_SUFFIX: dict[str, str] = {
    "year_over_year_percent": "(Y/Y %)",
    "index": "(Index)",
}

_UNIT_PARENTHETICAL = re.compile(r"\s*\([^()]*\)\s*\$?\s*$")
_TRAILING_PARENTHETICAL = re.compile(r"(\([^()]*\))\s*\$?\s*$")
_LEADING_UNITS = re.compile(r"^Units\s+")
_BOILERPLATE_PREFIX = re.compile(r"^(?:All Empl\w*|Exp\w* Value):\s*")


def fetch_page() -> str:
    """Return the raw NEEI dashboard HTML.

    Returns
    -------
    str
        The landing page HTML.
    """
    from openbb_core.provider.utils.helpers import make_request

    response = make_request(NEEI_URL)
    response.raise_for_status()
    return response.text


def _label_for(html: str, position: int) -> str:
    """Return the nearest preceding chart-tab label for a series-data block."""
    preceding = html[max(0, position - 500) : position]
    anchors = _ANCHOR.findall(preceding)
    return anchors[-1].strip() if anchors else ""


def parse_islands(html: str) -> dict[str, list[dict[str, Any]]]:
    """Decode every base64 ``series-data`` block, keyed by its chart label.

    Parameters
    ----------
    html : str
        The NEEI dashboard HTML.

    Returns
    -------
    dict[str, list[dict]]
        A mapping of chart label to its decoded list of geography series.
    """
    islands: dict[str, list[dict[str, Any]]] = {}
    for match in _SERIES_DATA.finditer(html):
        label = _label_for(html, match.start())
        if not label:
            continue
        try:
            decoded = json.loads(base64.b64decode(match.group(1)))
        except (ValueError, json.JSONDecodeError):
            continue
        if isinstance(decoded, list):
            islands[label] = decoded
    return islands


def _resolve_geography(series: dict[str, Any]) -> str | None:
    """Resolve a series to one of :data:`GEOGRAPHIES`, or ``None`` if unknown."""
    code = series.get("geography")
    if code in _GEOGRAPHY_BY_CODE:
        return _GEOGRAPHY_BY_CODE[code]

    description = (series.get("description") or "").lower()
    if description:
        if "united states" in description or "total u.s." in description:
            return "us"
        for key, name in GEOGRAPHIES.items():
            if key == "us":
                continue
            if name.lower() in description:
                return key

    name = (series.get("name") or "").strip().lower()
    if name in _GEOGRAPHY_BY_NAME:
        return _GEOGRAPHY_BY_NAME[name]

    return None


def _unit_for(series: dict[str, Any]) -> str | None:
    """Return the unit of a series' published values."""
    func = series.get("func")
    if func == "YRYR%":
        return "percent"
    if func == "index":
        return "index"
    data_type = series.get("dataType")
    units = {
        "%": "percent",
        "US$": "dollars",
        "INDEX": "index",
        "Units": "units",
    }
    return units.get(data_type) if data_type else None


def _transform_for(series: dict[str, Any]) -> str:
    """Return the transform applied to a series' published values."""
    return _TRANSFORMS.get(series.get("func"), "level")


def _clean_description(description: str | None) -> str:
    """Return a description with stray leading boilerplate removed."""
    base = _LEADING_UNITS.sub("", (description or "").strip()).strip()
    return _BOILERPLATE_PREFIX.sub("", base).strip()


def _column_label(description: str | None, name: str | None, transform: str) -> str:
    """Return a clean, unambiguous column label for a pivoted series."""
    base = _clean_description(description)
    if not base:
        return (name or "").strip()
    suffix = _TRANSFORM_SUFFIX.get(transform)
    if suffix:
        base = _UNIT_PARENTHETICAL.sub("", base).strip()
        return f"{base} {suffix}"
    return base


def _geography_label(
    geography: str | None, description: str | None, name: str | None, transform: str
) -> str:
    """Return a geography-first column label for a one-series-per-geography chart."""
    if geography is None or geography not in GEOGRAPHIES:
        return _column_label(description, name, transform)
    base = GEOGRAPHIES[geography]
    suffix = _TRANSFORM_SUFFIX.get(transform)
    if suffix:
        return f"{base} {suffix}"
    match = _TRAILING_PARENTHETICAL.search(_clean_description(description))
    return f"{base} {match.group(1)}" if match else base


def _is_geography_mode(series_list: list[dict[str, Any]]) -> bool:
    """Return whether a chart carries at most one series per resolved geography."""
    seen: set[str] = set()
    for series in series_list:
        geography = _resolve_geography(series)
        if geography is None:
            continue
        if geography in seen:
            return False
        seen.add(geography)
    return True


def _frequency_for(series: dict[str, Any]) -> str | None:
    """Return the native frequency label for a series."""
    code = series.get("originalFrequency") or series.get("frequency")
    if code == 40:
        return "monthly"
    if code == 30:
        return "quarterly"
    return None


def _series_records(
    indicator: str, series: dict[str, Any], geography_mode: bool
) -> list[dict[str, Any]]:
    """Flatten one decoded series into one long-format record per observation."""
    geography = _resolve_geography(series)
    raw_description = series.get("description") or None
    description = _clean_description(raw_description) or None
    name = series.get("name") or None
    unit = _unit_for(series)
    transform = _transform_for(series)
    label = (
        _geography_label(geography, raw_description, name, transform)
        if geography_mode
        else _column_label(raw_description, name, transform)
    )
    frequency = _frequency_for(series)
    source = series.get("sourceName")
    records: list[dict[str, Any]] = []
    for point in series.get("dataPoints", []):
        records.append(
            {
                "date": point["date"],
                "indicator": indicator,
                "name": name,
                "description": description,
                "label": label,
                "geography": geography,
                "value": point.get("nSeriesData"),
                "unit": unit,
                "transform": transform,
                "frequency": frequency,
                "source": source,
            }
        )
    return records


def _strip_shared_label_prefix(records: list[dict[str, Any]]) -> None:
    """Drop a redundant ``Category:`` prefix shared by every column label, in place."""
    from os.path import commonprefix

    labels = {record["label"] for record in records}
    if len(labels) < 2:
        return
    common = commonprefix(sorted(labels))
    cut = common.rfind(": ")
    if cut == -1:
        return
    prefix = common[: cut + 2]
    for record in records:
        label = record["label"]
        if len(label) > len(prefix) and label.startswith(prefix):
            record["label"] = label[len(prefix) :]


def fetch_indicator(
    indicator: str, geography: str | None = None
) -> list[dict[str, Any]]:
    """Return every series for a NEEI chart, in long format.

    Parameters
    ----------
    indicator : str
        One of the keys of :data:`INDICATORS`.
    geography : str | None
        One of the keys of :data:`GEOGRAPHIES`. When provided, only series that
        resolve to that geography are returned; when ``None`` every series in the
        chart is returned.

    Returns
    -------
    list[dict]
        One record per observation, carrying the series ``name``,
        ``description``, resolved ``geography``, ``value``, and source metadata.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    if indicator not in INDICATORS:
        raise OpenBBError(
            f"No Boston Fed indicator '{indicator}'. Choose from {sorted(INDICATORS)}."
        )
    if geography is not None and geography not in GEOGRAPHIES:
        raise OpenBBError(
            f"No geography '{geography}'. Choose from {sorted(GEOGRAPHIES)}."
        )

    html = cached(
        "boston_neei_page",
        lambda: seconds_until_next_release("monthly"),
        fetch_page,
    )
    islands = parse_islands(html)
    series_list = islands.get(INDICATORS[indicator])
    if not series_list:
        return []
    geography_mode = _is_geography_mode(series_list)
    records: list[dict[str, Any]] = []
    for series in series_list:
        records.extend(_series_records(indicator, series, geography_mode))
    _strip_shared_label_prefix(records)
    if geography is not None:
        records = [record for record in records if record["geography"] == geography]
    return records
