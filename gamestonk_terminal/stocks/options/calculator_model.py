"""Calculator Model"""
___docformat__ = "numpy"

from typing import Dict, Tuple

import numpy as np


def pnl_calculator(
    strike: float, premium: float, put: bool, sell: bool, **kwargs: Dict[str, int]
) -> Tuple[np.array, np.array, float]:
    """Calculate profit/loss for different option variables

    Parameters
    ----------
    strike: float
        Strike price
    premium: float
        Premium
    put: bool
        Is this a put option
    sell: bool
        Are you selling the option
    kwargs

    Returns
    -------
    price_at_expiry : np.array
        Array of prices
    pnl: np.array
        Array of calculated profit/loss
    break_even: float
        Breakeven point
    """

    if "x_min" in kwargs and "x_max" in kwargs:
        price_at_expiry = np.linspace(kwargs["x_min"], kwargs["x_max"], 301)
    else:
        price_at_expiry = np.linspace(strike / 2, 1.5 * strike, 301)

    sell_factor = [1, -1][sell]
    if put:
        break_even = strike - sell_factor * premium
        pnl = strike - premium - price_at_expiry
        pnl = sell_factor * 100 * np.where(price_at_expiry < strike, pnl, -premium)

    else:
        break_even = strike + sell_factor * premium
        pnl = price_at_expiry - strike - premium
        pnl = sell_factor * 100 * np.where(price_at_expiry > strike, pnl, -premium)

    return price_at_expiry, pnl, break_even
