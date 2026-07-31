"""Detect which "owning" sibling extensions are installed."""

from __future__ import annotations

from importlib.util import find_spec

ECONOMY_INSTALLED = find_spec("openbb_economy") is not None
CURRENCY_INSTALLED = find_spec("openbb_currency") is not None
FIXEDINCOME_INSTALLED = find_spec("openbb_fixedincome") is not None


def economy_key(standard: str, alias: str) -> str:
    """Return the standard key when economy is installed, else the ECB alias."""
    return standard if ECONOMY_INSTALLED else alias


def currency_key(standard: str, alias: str) -> str:
    """Return the standard key when currency is installed, else the ECB alias."""
    return standard if CURRENCY_INSTALLED else alias


def fixedincome_key(standard: str, alias: str) -> str:
    """Return the standard key when fixedincome is installed, else the ECB alias."""
    return standard if FIXEDINCOME_INSTALLED else alias
