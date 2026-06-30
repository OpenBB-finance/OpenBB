"""Detect which "owning" sibling extensions are installed.

ECB models map onto standard models owned by the economy, currency, and
fixedincome extensions. When an owner is installed, the ECB fetcher registers
under the *standard* model name (so e.g. ``obb.economy.balance_of_payments(
provider='ecb')`` works) and the ECB router does not re-register that command.
When the owner is absent, the fetcher registers under an ECB *alias* and the
router exposes the command in the ``obb.ecb.*`` namespace.
"""

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
