"""Saved screener configurations, kept beside the OpenBB user settings."""

import json
import re
from pathlib import Path

_STORE = Path.home() / ".openbb_platform" / "tmx_screener_presets.json"

_NAME = re.compile(r"^[\w \-]{1,64}$")

DEFAULTS: dict[str, dict] = {
    "Large Cap Dividend": {
        "asset_type": "Equity",
        "sort_by": "dividend_yield",
        "limit": 100,
        "conditions": [
            {"param": "market_cap", "operator": "gte", "value": [5e9, None]},
            {"param": "dividend_yield", "operator": "gte", "value": [3, None]},
        ],
    },
    "Value": {
        "asset_type": "Equity",
        "sort_by": "market_cap",
        "limit": 100,
        "conditions": [
            {"param": "pe_ratio", "operator": "lte", "value": [None, 15]},
            {"param": "pb_ratio", "operator": "lte", "value": [None, 2]},
            {"param": "return_on_equity", "operator": "gte", "value": [10, None]},
        ],
    },
    "Growth": {
        "asset_type": "Equity",
        "sort_by": "revenue_growth_3y",
        "limit": 100,
        "conditions": [
            {"param": "revenue_growth_3y", "operator": "gte", "value": [15, None]},
            {"param": "market_cap", "operator": "gte", "value": [1e9, None]},
        ],
    },
    "Momentum": {
        "asset_type": "Equity",
        "sort_by": "performance_90d",
        "limit": 100,
        "conditions": [
            {"param": "performance_90d", "operator": "gte", "value": [0.1, None]},
            {"param": "volume_avg_30d", "operator": "gte", "value": [100000, None]},
        ],
    },
    "Low Volatility": {
        "asset_type": "Equity",
        "sort_by": "market_cap",
        "limit": 100,
        "conditions": [
            {"param": "beta", "operator": "lte", "value": [None, 1]},
            {"param": "market_cap", "operator": "gte", "value": [2e9, None]},
        ],
    },
    "Optionable Liquid": {
        "asset_type": "Equity",
        "sort_by": "volume_avg_30d",
        "limit": 100,
        "conditions": [
            {"param": "optionable", "operator": "is", "value": True},
            {"param": "volume_avg_30d", "operator": "gte", "value": [500000, None]},
        ],
    },
    "All ETFs": {
        "asset_type": "ETF",
        "sort_by": "symbol",
        "sort_order": "ASC",
        "limit": 100,
        "conditions": [],
    },
    "TSX-Listed ETFs": {
        "asset_type": "ETF",
        "sort_by": "symbol",
        "sort_order": "ASC",
        "limit": 100,
        "conditions": [{"param": "exchange", "operator": "is", "value": "TSX"}],
    },
    "Optionable ETFs": {
        "asset_type": "ETF",
        "sort_by": "symbol",
        "sort_order": "ASC",
        "limit": 100,
        "conditions": [{"param": "optionable", "operator": "is", "value": True}],
    },
    "All Mutual Funds": {
        "asset_type": "Mutual Fund",
        "sort_by": "symbol",
        "sort_order": "ASC",
        "limit": 100,
        "conditions": [],
    },
    "Money Market Funds": {
        "asset_type": "Money Market Fund",
        "sort_by": "symbol",
        "sort_order": "ASC",
        "limit": 100,
        "conditions": [],
    },
    "All Indices": {
        "asset_type": "Index",
        "sort_by": "symbol",
        "sort_order": "ASC",
        "limit": 100,
        "conditions": [],
    },
    "All Futures": {
        "asset_type": "Future",
        "sort_by": "symbol",
        "sort_order": "ASC",
        "limit": 100,
        "conditions": [],
    },
}


def _read() -> dict:
    """Read the preset store, treating an unreadable store as empty."""
    try:
        return json.loads(_STORE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _write(presets: dict) -> None:
    """Write the preset store, creating its directory when absent."""
    _STORE.parent.mkdir(parents=True, exist_ok=True)
    _STORE.write_text(json.dumps(presets, indent=2), encoding="utf-8")


def list_presets() -> list[dict]:
    """List the shipped configurations and every saved one.

    Returns
    -------
    list[dict]
        One entry per configuration, carrying its name and its label.
    """
    saved = sorted(_read())

    return [{"name": n, "label": n} for n in DEFAULTS] + [
        {"name": n, "label": n} for n in saved if n not in DEFAULTS
    ]


def load_preset(name: str) -> dict:
    """Load one saved configuration.

    Parameters
    ----------
    name : str
        The configuration name.

    Returns
    -------
    dict
        The stored configuration.

    Raises
    ------
    FileNotFoundError
        If no configuration carries that name.
    """
    presets = _read()

    if name in presets:
        return presets[name]

    if name in DEFAULTS:
        return dict(DEFAULTS[name])

    raise FileNotFoundError(name)


def save_preset(name: str, config: dict) -> list[dict]:
    """Save a configuration under a name.

    Parameters
    ----------
    name : str
        The configuration name, letters, digits, spaces, and dashes only.
    config : dict
        The configuration to store.

    Returns
    -------
    list[dict]
        The refreshed list of configurations.

    Raises
    ------
    ValueError
        If the name is not usable.
    """
    if not _NAME.match(name or ""):
        raise ValueError("A preset name may carry letters, digits, spaces, and dashes.")

    presets = _read()
    presets[name] = config
    _write(presets)

    return list_presets()


def delete_preset(name: str) -> list[dict]:
    """Delete one saved configuration.

    Parameters
    ----------
    name : str
        The configuration name.

    Returns
    -------
    list[dict]
        The refreshed list of configurations.
    """
    presets = _read()
    presets.pop(name, None)
    _write(presets)

    return list_presets()
