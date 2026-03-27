"""Persistent watchlist store backed by a JSON file.

The watchlist file lives at ``~/.openbb_platform/watchlist.json`` and supports
multiple named groups, each containing an ordered list of ticker symbols.
All mutations are serialised through an ``RLock``.
"""

from __future__ import annotations

import json
import logging
import threading
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger(__name__)

_WATCHLIST_PATH = Path.home() / ".openbb_platform" / "watchlist.json"
_LOCK = threading.RLock()

_DEFAULT_TICKERS = [
    "NFLX", "AAPL", "GOOGL", "TSLA", "NVDA",
    "IBM", "INTC", "XOM", "AMZN", "AMD", "META",
]


def _read() -> dict[str, Any]:
    with _LOCK:
        if not _WATCHLIST_PATH.exists():
            return _default_watchlist()
        try:
            with _WATCHLIST_PATH.open(encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, dict) and "groups" in data:
                return data
        except (OSError, json.JSONDecodeError) as exc:
            LOGGER.warning("Failed to read watchlist: %s", exc)
        return _default_watchlist()


def _write(data: dict[str, Any]) -> None:
    with _LOCK:
        _WATCHLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
        with _WATCHLIST_PATH.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)


def _default_watchlist() -> dict[str, Any]:
    return {
        "groups": [
            {"name": "Default Watchlist", "tickers": list(_DEFAULT_TICKERS)},
        ],
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_watchlist() -> dict[str, Any]:
    """Return the full watchlist payload."""
    return _read()


def add_group(name: str) -> dict[str, Any]:
    """Add a new empty group. Duplicate names are silently ignored."""
    with _LOCK:
        data = _read()
        existing = {g["name"] for g in data["groups"]}
        if name not in existing:
            data["groups"].append({"name": name, "tickers": []})
            _write(data)
        return data


def remove_group(name: str) -> dict[str, Any]:
    """Remove a group by name."""
    with _LOCK:
        data = _read()
        data["groups"] = [g for g in data["groups"] if g["name"] != name]
        _write(data)
        return data


def add_ticker(group_name: str, symbol: str) -> dict[str, Any]:
    """Add a ticker to a group. Creates the group if it doesn't exist."""
    symbol = symbol.upper().strip()
    with _LOCK:
        data = _read()
        target = None
        for g in data["groups"]:
            if g["name"] == group_name:
                target = g
                break
        if target is None:
            target = {"name": group_name, "tickers": []}
            data["groups"].append(target)
        if symbol not in target["tickers"]:
            target["tickers"].append(symbol)
        _write(data)
        return data


def remove_ticker(group_name: str, symbol: str) -> dict[str, Any]:
    """Remove a ticker from a group."""
    symbol = symbol.upper().strip()
    with _LOCK:
        data = _read()
        for g in data["groups"]:
            if g["name"] == group_name:
                g["tickers"] = [t for t in g["tickers"] if t != symbol]
                break
        _write(data)
        return data


def reorder_tickers(group_name: str, ordered_symbols: list[str]) -> dict[str, Any]:
    """Replace the ticker list of a group with the provided order."""
    with _LOCK:
        data = _read()
        for g in data["groups"]:
            if g["name"] == group_name:
                g["tickers"] = [s.upper().strip() for s in ordered_symbols]
                break
        _write(data)
        return data
