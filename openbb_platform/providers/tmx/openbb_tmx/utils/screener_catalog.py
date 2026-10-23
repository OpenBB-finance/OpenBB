"""The field, operator, and value catalog the screener builder renders."""

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from openbb_tmx.models.equity_screener import NATIVE_RANGES, RANGED_FIELDS
from openbb_tmx.utils.choices import SCREENER_FIELDS, screener_code, slugify

_ASSETS = Path(__file__).resolve().parent.parent / "assets"

_SOURCE_TO_PARAM = {source: field for field, source in RANGED_FIELDS.items()}

ASSET_TYPES = [
    {"label": "Equity", "value": "Equity"},
    {"label": "ETF", "value": "ETF"},
    {"label": "Mutual Fund", "value": "Mutual Fund"},
    {"label": "Money Market Fund", "value": "Money Market Fund"},
    {"label": "Index", "value": "Index"},
    {"label": "Future", "value": "Future"},
]

OPERATORS = {
    "range": [
        {"label": "is between", "value": "between"},
        {"label": "is at least", "value": "gte"},
        {"label": "is at most", "value": "lte"},
    ],
    "boolean": [{"label": "is", "value": "is"}],
    "select": [{"label": "is", "value": "is"}],
    "tree": [{"label": "is", "value": "is"}],
}

SORT_TYPES = [
    {"label": "Descending", "value": "DESC"},
    {"label": "Ascending", "value": "ASC"},
]

DEFAULT_SORT = "market_cap"

DIRECTORY_FIELDS = ["market_cap", "exchange"]

DIRECTORY_SORT = [
    {"label": "Market Capitalization", "value": "market_cap"},
    {"label": "Symbol", "value": "symbol"},
    {"label": "Name", "value": "name"},
]

QUOTE_SORT = [
    {"label": "Volume", "value": "volume"},
    {"label": "Price", "value": "price"},
    {"label": "% Change", "value": "price_change"},
    {"label": "52-Week High", "value": "high_52w"},
    {"label": "52-Week Low", "value": "low_52w"},
    {"label": "Symbol", "value": "symbol"},
    {"label": "Name", "value": "name"},
]

FUTURE_SORT = [
    {"label": "Open Interest", "value": "open_interest"},
    {"label": "Volume", "value": "volume"},
    {"label": "Last Price", "value": "price"},
    {"label": "Contract Month", "value": "expiration"},
    {"label": "Symbol", "value": "symbol"},
    {"label": "Name", "value": "name"},
]

OPEN_INTEREST_FIELD = {
    "param": "open_interest",
    "label": "Open Interest",
    "description": "The number of contracts outstanding.",
    "category": "trading",
    "category_label": "Trading",
}

ASSET_DEFAULTS: dict[str, dict[str, Any]] = {
    "Equity": {"sort_by": "market_cap", "limit": 100, "fields": None},
    "ETF": {
        "sort_by": "symbol",
        "limit": 100,
        "fields": [*DIRECTORY_FIELDS, "optionable"],
    },
    "Mutual Fund": {"sort_by": "symbol", "limit": 100, "fields": DIRECTORY_FIELDS},
    "Money Market Fund": {
        "sort_by": "symbol",
        "limit": 100,
        "fields": DIRECTORY_FIELDS,
    },
    "Index": {
        "sort_by": "volume",
        "limit": 100,
        "fields": ["exchange", "price", "price_change", "volume"],
        "sort_fields": QUOTE_SORT,
    },
    "Future": {
        "sort_by": "open_interest",
        "limit": 100,
        "fields": ["price", "volume", "open_interest"],
        "sort_fields": FUTURE_SORT,
    },
}

BOOLEAN_FILTERS = {
    "optionable": "optionable",
    "primarysymbol": "primary_symbol",
    "filingcurrent": "filing_current",
    "high52week": "above_52w_high",
    "low52week": "below_52w_low",
}

CRITERIA_TO_SOURCE = {
    "marketcap": "marketCapitalization",
    "close": "stockPrice",
    "divyield": "divYield",
    "div": "divRate",
    "divgrow3": "divGrowthAvg3y",
    "divgrow5": "divGrowthAvg5y",
    "perat": "peRatio",
    "psrat": "psRatio",
    "pbrat": "pbRatio",
    "pcashfrat": "pcfRatio",
    "bvps": "bvps",
    "currat": "currentRatio",
    "quickrat": "quickRatio",
    "totdebteqrat": "debtToEquityRatio",
    "lngtrmdebttototcap": "debtCapitalRatio",
    "latfisceps": "latestFiscalEps",
    "grossmarg": "grossMargin",
    "ebitdamarg": "ebitdaMargin",
    "ebitmarg": "ebitMargin",
    "roa": "roa",
    "roe": "roe",
    "roc": "roc",
    "revps": "revPs",
    "ltmrev": "revenueLtm",
    "totalrevenue": "totalRevenue",
    "freecashflow": "freeCashFlow",
    "employees": "employees",
    "bookvalue": "bookValue",
    "totalequity": "totalEquity",
    "totalassets": "totalAssets",
    "currentliabilities": "currentLiabilities",
    "currentassets": "currentAssets",
    "beta": "beta",
    "alpha": "alpha",
    "r2": "r2",
    "stddev": "stddev",
    "volume": "intradayVolume",
    "yesterdaysvolume": "yesterdaysVolume",
    "averagevolume10": "averageVolume10d",
    "averagevolume30": "averageVolume30d",
    "averagevolume50": "averageVolume50d",
    "averagevolume90": "averageVolume90d",
    "averagetradevalue90": "averageTradeValue90",
    "inspct": "insiderHoldingPct",
    "instpct": "instHoldingPct",
    "pricechange": "priceChange",
    "performance7day": "pricePerfomance7d",
    "performance1month": "pricePerfomance30d",
    "performance3month": "pricePerfomance90d",
    "performanceytd": "pricePerfomanceYtd",
    "performance365": "change52w",
    "revgrow3": "revenueGrowth3yr",
    "revgrow5": "revenueGrowth5yr",
    "incgrow3": "incomeGrowth3yr",
    "incgrow5": "incomeGrowth5yr",
}


def _criteria() -> dict:
    """Read the published criteria catalogue."""
    return json.loads((_ASSETS / "screener_criteria.json").read_text(encoding="utf-8"))


def _sector_tree() -> list[dict]:
    """Build the sector, group, and industry tree the builder cascades through."""
    choices = json.loads(
        (_ASSETS / "screener_choices.json").read_text(encoding="utf-8")
    )
    groups = choices.get("industry_groups", {})
    industries = choices.get("industries", {})
    tree = []

    for name, code in choices.get("sectors", {}).items():
        sector = {"label": name, "value": slugify(name), "children": []}

        for group_name, group_code in groups.items():
            if not str(group_code).startswith(str(code)):
                continue

            sector["children"].append(
                {
                    "label": group_name,
                    "value": slugify(group_name),
                    "children": [
                        {"label": n, "value": slugify(n)}
                        for n, c in industries.items()
                        if str(c).startswith(str(group_code))
                    ],
                }
            )

        tree.append(sector)

    return tree


def _field(
    param: str, label: str, kind: str, category: str, description: str | None, **extra
) -> dict:
    """Describe one filter for the builder."""
    return {
        "param": param,
        "label": label or param,
        "description": description or "",
        "type": kind,
        "category": slugify(category),
        "category_label": category,
        "operators": OPERATORS[kind],
        **extra,
    }


@lru_cache(maxsize=2)
def build_screener_catalog(country: str = "CA") -> dict[str, Any]:
    """Build the catalog of every filter the screener accepts.

    Parameters
    ----------
    country : str
        The screener country, 'CA' or 'US'.

    Returns
    -------
    dict
        The asset types, the fields, the operators, and the sort vocabulary.
    """
    country = country.upper() if country.upper() in ("CA", "US") else "CA"
    fields: list[dict] = []

    seen: set[str] = set()

    def _add(field: dict) -> None:
        """Keep the first declaration of a filter, in catalogue order."""
        if field["param"] not in seen:
            seen.add(field["param"])
            fields.append(field)

    for group in _criteria().get(country, []):
        category = group.get("name") or "Other"

        for entry in group.get("fixed", []):
            param = BOOLEAN_FILTERS.get(entry["id"])

            if param:
                _add(
                    _field(
                        param,
                        entry.get("name"),
                        "boolean",
                        category,
                        entry.get("description"),
                    )
                )
            elif entry["id"] == "sectors":
                _add(
                    _field(
                        "sector",
                        "Sector",
                        "tree",
                        category,
                        entry.get("description"),
                        options=_sector_tree(),
                        levels=["sector", "industry_group", "industry"],
                    )
                )
            elif entry["id"] == "exchangeGroups":
                _add(
                    _field(
                        "exchange",
                        entry.get("name"),
                        "select",
                        category,
                        entry.get("description"),
                        options=[
                            {"label": v, "value": v} for v in entry.get("values") or []
                        ],
                    )
                )

        for entry in group.get("ranged", []):
            source = CRITERIA_TO_SOURCE.get(entry["id"])
            param = _SOURCE_TO_PARAM.get(source) if source else None

            if param:
                _add(
                    _field(
                        param,
                        entry.get("name"),
                        "range",
                        category,
                        entry.get("description"),
                    )
                )

    published = [f["param"] for f in fields]

    _add({**OPEN_INTEREST_FIELD, "operators": OPERATORS["range"], "type": "range"})

    labels = {f["param"]: f["label"] for f in fields}
    sort_fields = [
        {"label": labels.get(param, param), "value": param}
        for param in sorted(RANGED_FIELDS)
    ]

    return {
        "country": country,
        "asset_types": ASSET_TYPES,
        "default_asset": ASSET_TYPES[0]["value"],
        "fields": fields,
        "operators": OPERATORS,
        "sort_types": SORT_TYPES,
        "sort_fields": sort_fields,
        "default_sort": DEFAULT_SORT,
        "asset_defaults": _asset_defaults(sort_fields, published),
    }


def _asset_defaults(sort_fields: list[dict], published: list[str]) -> dict[str, dict]:
    """Describe what each asset type screens on.

    Parameters
    ----------
    sort_fields : list[dict]
        Every sort choice the fundamentals path offers.
    published : list[str]
        Every filter the published criteria catalogue declares.

    Returns
    -------
    dict
        One entry per asset type, naming its fields, sorts, and defaults.
    """
    defaults: dict[str, dict] = {}

    for asset, spec in ASSET_DEFAULTS.items():
        fields = spec["fields"]
        defaults[asset] = {
            "sort_by": spec["sort_by"],
            "limit": spec["limit"],
            "fields": published if fields is None else fields,
            "sort_fields": spec.get("sort_fields")
            or (sort_fields if fields is None else DIRECTORY_SORT),
        }

    return defaults


def query_from_config(config: dict) -> dict:
    """Turn a builder configuration into screener query parameters.

    Parameters
    ----------
    config : dict
        The configuration the builder emits.

    Returns
    -------
    dict
        Parameters accepted by the equity screener model.
    """
    config = config or {}
    params: dict[str, Any] = {}

    for key in ("exchange", "country", "limit", "sort_by", "sort_order"):
        if config.get(key) not in (None, ""):
            params[key] = config[key]

    if config.get("asset_type"):
        params["symbol_type"] = config["asset_type"]

    for condition in config.get("conditions") or []:
        param = condition.get("param")
        operator = condition.get("operator") or "is"
        value = condition.get("value")

        if not param or value in (None, "", [], {}):
            continue

        if param in RANGED_FIELDS or param in NATIVE_RANGES:
            pair = value if isinstance(value, list | tuple) else [value, value]

            if operator in ("between", "gte") and pair[0] not in (None, ""):
                params[f"{param}_min"] = float(pair[0])

            if operator in ("between", "lte") and pair[-1] not in (None, ""):
                params[f"{param}_max"] = float(pair[-1])
        elif param in BOOLEAN_FILTERS.values():
            params[param] = bool(value)
        elif (
            param in SCREENER_FIELDS
            and screener_code(param, str(value))
            or param in ("exchange", "country")
        ):
            params[param] = value

    return params
