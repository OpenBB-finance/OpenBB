"""Valuing Deribit option positions.

The chain quotes every contract in its quote currency per unit of the
underlying, so a position is valued the same way whichever settlement style a
contract has. What differs is where the profit lands: an inverse contract pays
in the coin, so its result is also reported there, which is the number the
account actually moves by.
"""

MIN_VOL = 0.0001
MAX_VOL = 5.0
VOL_STEPS = 100


def intrinsic(price: float, strike: float, option_type: str) -> float:
    """Return the exercise value of one unit of the underlying."""
    return (
        max(0.0, price - strike)
        if option_type.startswith("c")
        else max(0.0, strike - price)
    )


def option_value(
    forward: float,
    strike: float,
    years: float,
    sigma: float,
    discount: float,
    option_type: str,
) -> float:
    """Value one unit of the underlying off its forward price.

    Parameters
    ----------
    forward : float
        The forward price of the underlying at expiration.
    strike : float
        The strike of the contract.
    years : float
        The time to expiration, in years.
    sigma : float
        The implied volatility, as a decimal.
    discount : float
        The discount factor to expiration.
    option_type : str
        Either 'call' or 'put'.

    Returns
    -------
    float
        The value of one unit, in the quote currency.
    """
    from math import log, sqrt
    from statistics import NormalDist

    if years <= 0 or sigma <= 0 or forward <= 0 or strike <= 0:
        return discount * intrinsic(forward, strike, option_type)

    normal = NormalDist()
    deviation = sigma * sqrt(years)
    d1 = (log(forward / strike) + 0.5 * sigma**2 * years) / deviation
    d2 = d1 - deviation

    if option_type.startswith("c"):
        return discount * (forward * normal.cdf(d1) - strike * normal.cdf(d2))

    return discount * (strike * normal.cdf(-d2) - forward * normal.cdf(-d1))


def implied_vol(
    price: float,
    forward: float,
    strike: float,
    years: float,
    discount: float,
    option_type: str,
) -> "float | None":
    """Return the volatility one quoted price implies.

    A chain publishes a volatility alongside a price, and the two do not always
    agree. Valuing a position at a volatility its own quote does not imply
    prices the exit off a different market than the entry, which shows a
    position as losing before it has moved.

    Parameters
    ----------
    price : float
        The quoted price of one unit.
    forward : float
        The forward price of the underlying at expiration.
    strike : float
        The strike of the contract.
    years : float
        The time to expiration, in years.
    discount : float
        The discount factor to expiration.
    option_type : str
        Either 'call' or 'put'.

    Returns
    -------
    float or None
        The volatility the price implies, or None when no volatility does.
    """
    if price <= 0 or years <= 0 or forward <= 0 or strike <= 0:
        return None

    if price <= discount * intrinsic(forward, strike, option_type):
        return None

    low, high = MIN_VOL, MAX_VOL

    if option_value(forward, strike, years, high, discount, option_type) < price:
        return None

    for _ in range(VOL_STEPS):
        middle = (low + high) / 2

        if option_value(forward, strike, years, middle, discount, option_type) < price:
            low = middle
        else:
            high = middle

    return (low + high) / 2


def leg_value(leg: dict, price: float, elapsed: int) -> float:
    """Return what one unit of a leg is worth at a price.

    Parameters
    ----------
    leg : dict
        The contract, its volatility, and its days to expiration.
    price : float
        The price of the underlying at the valuation date.
    elapsed : int
        Days from now to the valuation date.

    Returns
    -------
    float
        The exercise value of a leg that has expired by the valuation date,
        otherwise its modelled value, in the quote currency per unit.
    """
    remaining = int(leg.get("dte") or 0) - elapsed

    if remaining <= 0 or not leg.get("implied_volatility"):
        return intrinsic(price, float(leg["strike"]), str(leg["option_type"]))

    return option_value(
        price,
        float(leg["strike"]),
        remaining / 365,
        float(leg["implied_volatility"]),
        1.0,
        str(leg["option_type"]),
    )


def net_cost(legs: "list[dict]") -> float:
    """Return what a position costs to open, in the quote currency.

    A negative result is a credit.
    """
    return sum(
        float(leg["quantity"]) * float(leg["size"]) * float(leg["price"])
        for leg in legs
    )


def position_value(legs: "list[dict]", price: float, elapsed: int) -> float:
    """Return what a position is worth at a price, in the quote currency."""
    return sum(
        float(leg["quantity"]) * float(leg["size"]) * leg_value(leg, price, elapsed)
        for leg in legs
    )


def payoff(
    legs: "list[dict]",
    prices: "list[float]",
    elapsed: int = 0,
    inverse: bool = False,
    entry_price: "float | None" = None,
) -> "list[float]":
    """Return the profit and loss of a position across a price range, in the quote currency.

    An inverse contract is paid for in the coin, so the premium is coin the
    account no longer holds, and what that costs is whatever the coin is worth
    at the price being valued. The payout is already quoted, so only the
    premium is carried. A linear contract is paid for in the quote currency and
    its premium is simply that.

    This is why an inverse position's loss is not flat: holding it through a
    rise that leaves it worthless still costs more, because the coin paid for
    it became worth more.

    Parameters
    ----------
    legs : list[dict]
        Each leg's strike, type, quantity, contract size, price, days to
        expiration, and implied volatility.
    prices : list[float]
        The underlying prices to evaluate.
    elapsed : int
        Days from now to the valuation date.
    inverse : bool
        Whether the contracts settle in the underlying.
    entry_price : float or None
        The price of the underlying when the position was opened, which an
        inverse premium was paid at. Required when inverse.

    Returns
    -------
    list[float]
        The profit and loss at each price, in the quote currency.

    Raises
    ------
    ValueError
        If an inverse position is valued without the price it was opened at.
    """
    entry = net_cost(legs)

    if not inverse:
        return [position_value(legs, price, elapsed) - entry for price in prices]

    if not entry_price:
        raise ValueError(
            "An inverse position needs the price it was opened at, because its"
            " premium was paid in the coin at that price."
        )

    paid = entry / entry_price

    return [position_value(legs, price, elapsed) - paid * price for price in prices]


def breakevens(prices: "list[float]", values: "list[float]") -> "list[float]":
    """Return every price where a payoff crosses zero."""
    crossings: list[float] = []

    for index in range(1, len(values)):
        if (values[index - 1] < 0) == (values[index] < 0):
            continue

        low, high = values[index - 1], values[index]
        weight = abs(low) / (abs(low) + abs(high)) if (low or high) else 0
        crossings.append(
            prices[index - 1] + weight * (prices[index] - prices[index - 1])
        )

    return crossings
