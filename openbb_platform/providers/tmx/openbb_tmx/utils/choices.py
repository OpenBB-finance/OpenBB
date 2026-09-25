"""Filter vocabularies for the TMX screeners."""

import json
import re
from pathlib import Path

_ASSETS = Path(__file__).parent.parent / "assets"

_ETF = json.loads((_ASSETS / "etf_choices.json").read_text(encoding="utf-8"))

_SCREENER = json.loads((_ASSETS / "screener_choices.json").read_text(encoding="utf-8"))

ETF_FIELDS = ("asset_class", "region", "fund_family", "investment_style")

SCREENER_FIELDS = {
    "sector": "sectors",
    "industry_group": "industry_groups",
    "industry": "industries",
}


def slugify(name: str) -> str:
    """Reduce a published name to a short snake-case value.

    Parameters
    ----------
    name : str
        The name as published.

    Returns
    -------
    str
        The name as lower snake case, with punctuation dropped.
    """
    cleaned = re.sub(r"[^0-9a-zA-Z]+", "_", name).strip("_").lower()

    return re.sub(r"_+", "_", cleaned)


def _index(names: "list[str]") -> dict:
    """Map each published name to a unique slug."""
    out: dict = {}

    for name in names:
        slug = slugify(name)
        candidate, n = slug, 2

        while candidate in out and out[candidate] != name:
            candidate, n = f"{slug}_{n}", n + 1

        out[candidate] = name

    return out


_ETF_INDEX = {field: _index(_ETF.get(field, [])) for field in ETF_FIELDS}

_SCREENER_INDEX = {
    field: _index(list(_SCREENER.get(group, {})))
    for field, group in SCREENER_FIELDS.items()
}


def etf_value(field: str, slug: str | None) -> str | None:
    """Return the published ETF value a slug selects."""
    return _ETF_INDEX.get(field, {}).get(slug) if slug else None


def screener_code(field: str, slug: str | None) -> str | None:
    """Return the sector code a slug selects."""
    if not slug:
        return None

    name = _SCREENER_INDEX.get(field, {}).get(slug)
    code = _SCREENER.get(SCREENER_FIELDS[field], {}).get(name)

    return str(code) if code is not None else None


def _options(index: dict) -> dict:
    """Build the labelled widget options for one filter."""
    return {
        "x-widget_config": {
            "options": [{"label": name, "value": slug} for slug, name in index.items()]
        }
    }


def etf_widget_config() -> dict:
    """Return the per-field widget configuration for the ETF screener."""
    return {field: _options(_ETF_INDEX[field]) for field in ETF_FIELDS}


def screener_widget_config() -> dict:
    """Return the per-field widget configuration for the equity screener."""
    return {field: _options(_SCREENER_INDEX[field]) for field in SCREENER_FIELDS}


def screener_options(field: str, parent: str | None = None) -> list[dict]:
    """List the labelled options for one screener filter.

    Parameters
    ----------
    field : str
        One of 'sector', 'industry_group', or 'industry'.
    parent : str or None
        Restrict to the children of this parent slug, so an industry group
        narrows to its sector and an industry to its group.

    Returns
    -------
    list[dict]
        The label and value pairs the widget renders.
    """
    index = _SCREENER_INDEX.get(field, {})
    prefix = None

    if parent:
        parent_field = "sector" if field == "industry_group" else "industry_group"
        prefix = screener_code(parent_field, parent)

    options = []

    for slug, name in index.items():
        if prefix and not (screener_code(field, slug) or "").startswith(prefix):
            continue

        options.append({"label": name, "value": slug})

    return options


def api_prefix() -> str:
    """Return the prefix the API is served under.

    Returns
    -------
    str
        The configured prefix, such as '/api/v1'.
    """
    from openbb_core.app.service.system_service import SystemService

    return SystemService().system_settings.api_settings.prefix


LABELS = {
    "ca": "Canada",
    "us": "United States",
    "CA": "Canada",
    "US": "United States",
    "GB": "United Kingdom",
    "CAD": "Canadian Dollar",
    "USD": "US Dollar",
    "tsx": "TSX",
    "tsxv": "TSX Venture",
    "TSX": "Toronto Stock Exchange",
    "TSXV": "TSX Venture Exchange",
    "CSE": "Canadian Securities Exchange",
    "ALPHA": "Alpha Exchange",
    "NEO-L": "NEO Lit",
    "NEO-D": "NEO Dark",
    "NEO-N": "NEO NASDAQ",
    "CMF": "Canadian Mutual Funds",
    "MOE": "Montreal Exchange",
    "ETF": "ETF",
    "asc": "Ascending",
    "desc": "Descending",
    "aum": "AUM",
    "pe_ratio": "P/E Ratio",
    "pb_ratio": "P/B Ratio",
    "return_ytd": "Return YTD",
    "splits_and_dividends": "Splits and Dividends",
    "52w_high": "52-Week High",
    "cdr": "CDR",
    "semi-annually": "Semi-Annually",
    "1m": "1 Minute",
    "2m": "2 Minutes",
    "5m": "5 Minutes",
    "15m": "15 Minutes",
    "30m": "30 Minutes",
    "60m": "60 Minutes",
    "1h": "1 Hour",
    "1d": "1 Day",
    "1W": "1 Week",
    "1M": "1 Month",
}


def literal_choices(values: "tuple[str, ...]", **overrides: str) -> list[dict]:
    """Return the widget choices for a parameter restricted to a set of values.

    Parameters
    ----------
    values : tuple[str, ...]
        The accepted values, in the order they should be offered.
    **overrides : str
        A human-readable label for a value the shared table does not cover.

    Returns
    -------
    list[dict]
        The label and value pairs the Workspace offers.
    """

    def label(value: str) -> str:
        if value in overrides:
            return overrides[value]

        if value in LABELS:
            return LABELS[value]

        return value.replace("_", " ").replace("-", " ").title()

    return [{"label": label(value), "value": value} for value in values]


def cell_group(field: str, description: str) -> dict:
    """Return the widget configuration that groups on a clicked cell.

    Parameters
    ----------
    field : str
        The column, and the shared parameter, a click groups on.
    description : str
        What the parameter carries, for the widget parameter list.

    Returns
    -------
    dict
        The parameter and column definition the click grouping needs.
    """
    return {
        "params": [
            {"paramName": field, "description": description, "show": False},
        ],
        "data": {
            "table": {
                "columnsDefs": [
                    {
                        "field": field,
                        "renderFn": "cellOnClick",
                        "renderFnParams": {
                            "actionType": "groupBy",
                            "groupBy": {"paramName": field},
                        },
                    },
                ]
            }
        },
    }
