"""Eligibility rule predicates used by staged universe filters."""

from __future__ import annotations

from typing import Any


def is_trade_halted_too_long(halt_days: Any, max_halt_days: int) -> bool:
    """Return True when halt duration breaches policy threshold."""
    try:
        value = int(float(halt_days))
    except (TypeError, ValueError):
        value = 0
    return value >= int(max_halt_days) + 1


def is_excluded_status(
    *,
    management_flag: bool,
    delisting_pending_flag: bool,
    special_status_flag: bool,
    hard_to_borrow_flag: bool,
    portfolio_mode: str,
    exclude_htb_for_long_short: bool,
) -> bool:
    """Return True when any status flag requires exclusion."""
    if management_flag or delisting_pending_flag or special_status_flag:
        return True
    if (
        exclude_htb_for_long_short
        and str(portfolio_mode).strip().lower() == "long_short"
        and hard_to_borrow_flag
    ):
        return True
    return False

