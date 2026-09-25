"""Multi-leg positions assembled from trade optimizer quotes."""

from __future__ import annotations

MONEYNESS = 0.05
SIDES = {"Naked Long": "long", "Naked Short": "short"}

MIN_VOL = 0.0001
MAX_VOL = 5.0
VOL_STEPS = 100


def intrinsic(price: float, strike: float, option_type: str) -> float:
    """Return the exercise value of one contract."""
    return max(0.0, price - strike) if option_type == "c" else max(0.0, strike - price)


def option_value(
    forward: float,
    strike: float,
    years: float,
    sigma: float,
    discount: float,
    option_type: str,
) -> float:
    """Value one contract off its forward price.

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
        Either 'c' or 'p'.

    Returns
    -------
    float
        The value of one contract.
    """
    from math import log, sqrt
    from statistics import NormalDist

    if years <= 0 or sigma <= 0 or forward <= 0 or strike <= 0:
        return discount * intrinsic(forward, strike, option_type)

    normal = NormalDist()
    deviation = sigma * sqrt(years)
    d1 = (log(forward / strike) + 0.5 * sigma**2 * years) / deviation
    d2 = d1 - deviation

    if option_type == "c":
        return discount * (forward * normal.cdf(d1) - strike * normal.cdf(d2))

    return discount * (strike * normal.cdf(-d2) - forward * normal.cdf(-d1))


def implied_vol(
    price: float,
    forward: float,
    strike: float,
    years: float,
    discount: float,
    option_type: str,
) -> float | None:
    """Return the volatility one quoted price implies.

    A chain publishes a volatility alongside a price, and the two do not always
    agree. Valuing a position at a volatility its own quote does not imply
    prices the exit off a different market than the entry, which shows a
    position as losing before it has moved.

    Parameters
    ----------
    price : float
        The quoted price of the contract.
    forward : float
        The forward price of the underlying at expiration.
    strike : float
        The strike of the contract.
    years : float
        The time to expiration, in years.
    discount : float
        The discount factor to expiration.
    option_type : str
        Either 'c' or 'p'.

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
    """Return what one leg is worth when the underlying trades at a price.

    Parameters
    ----------
    leg : dict
        The contract, its volatility, and its carry to expiration.
    price : float
        The price of the underlying at the valuation date.
    elapsed : int
        Days from now to the valuation date.

    Returns
    -------
    float
        The exercise value of a leg that has expired by the valuation date,
        otherwise its value at the volatility the chain published.

    Raises
    ------
    OpenBBError
        If a leg outliving the valuation date has no published volatility.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    remaining = int(leg.get("dte") or 0) - elapsed

    if remaining <= 0:
        return intrinsic(price, float(leg["strike"]), str(leg["type"]))

    if not leg.get("iv"):
        raise OpenBBError(
            f"Cboe publishes no implied volatility for the {leg['expiration']}"
            f" {leg['strike']:g} contract, which outlives this diagram."
        )

    return option_value(
        price * float(leg.get("carry") or 1),
        float(leg["strike"]),
        remaining / 365,
        float(leg["iv"]),
        float(leg.get("discount") or 1),
        str(leg["type"]),
    )


def payoff_from_legs(
    legs: list[dict], prices: list[float], elapsed: int = 0
) -> list[float]:
    """Return the profit and loss of a position across a price range.

    Parameters
    ----------
    legs : list[dict]
        Each leg's type, strike, quantity, price, expiration, and volatility.
    prices : list[float]
        The underlying prices to evaluate.
    elapsed : int
        Days from now to the valuation date.

    Returns
    -------
    list[float]
        The profit and loss of one contract per leg, at each price.
    """
    entry = net_cost(legs)

    return [
        100
        * (
            sum(float(leg["quantity"]) * leg_value(leg, price, elapsed) for leg in legs)
            - entry
        )
        for price in prices
    ]


def net_cost(legs: list[dict]) -> float:
    """Return what the position costs to open, negative when it is a credit."""
    return sum(float(leg["quantity"]) * float(leg["price"]) for leg in legs)


def naked_quotes(rows: list[dict], marks: dict) -> dict:
    """Index every single-leg quote in an optimizer response.

    Parameters
    ----------
    rows : list[dict]
        Strategies as the optimizer returns them.
    marks : dict
        What the chain publishes for the expiration.

    Returns
    -------
    dict
        The price, volatility, and model value of each
        ``(side, type, strike)`` quoted. A leg is priced at what the chain
        quotes the contract at - the ask to buy it, the bid to sell it -
        because the optimizer's 'current_price' belongs to the strategy it
        ranked, not to the contract on its own.
    """
    contracts = marks.get("contracts") or {}
    quotes: dict = {}

    for row in rows:
        side = SIDES.get(str(row.get("strategy") or ""))
        strike = float(row.get("strike1") or 0)
        option_type = str(row.get("type") or "c")
        price = float(row.get("current_price") or 0)

        if not side or strike <= 0 or price <= 0:
            continue

        published = contracts.get((option_type, strike)) or {}
        quoted = published.get("ask" if side == "long" else "bid")
        quotes.setdefault(
            (side, option_type, strike),
            {
                "price": float(quoted) if quoted else price,
                "dte": marks.get("dte") or 0,
                "expiration": str(row.get("expiry") or ""),
                "iv": published.get("iv"),
                "theoretical_price": published.get("theoretical_price"),
            },
        )

    return quotes


def _strikes(quotes: dict, side: str, option_type: str) -> set:
    """Return every strike quoted for one side of one contract type."""
    return {
        strike
        for quoted_side, quoted_type, strike in quotes
        if quoted_side == side and quoted_type == option_type
    }


def _nearest(strikes: set, target: float) -> float | None:
    """Return the quoted strike closest to a target price."""
    return min(strikes, key=lambda strike: abs(strike - target)) if strikes else None


def _leg(book: dict, side: str, option_type: str, strike: float) -> dict:
    """Describe one quoted contract as a leg of a position."""
    quote = book["quotes"][(side, option_type, strike)]

    return {
        "type": option_type,
        "strike": strike,
        "quantity": 1 if side == "long" else -1,
        "price": quote["price"],
        "dte": quote["dte"],
        "iv": quote["iv"],
        "theoretical_price": quote["theoretical_price"],
        "expiration": quote["expiration"],
    }


def build_naked(book: dict, spot: float, option_type: str, sell: bool = False) -> dict:
    """Build a single contract at the strike nearest the underlying price.

    Raises
    ------
    OpenBBError
        If the contract was not quoted.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    side = "short" if sell else "long"
    strike = _nearest(_strikes(book["quotes"], side, option_type), spot)

    if strike is None:
        raise OpenBBError("The optimizer quoted no contract at the money.")

    leg = _leg(book, side, option_type, strike)

    return {"legs": [leg], "elapsed": int(leg["dte"])}


def build_straddle(book: dict, spot: float, sell: bool = False) -> dict:
    """Build a straddle at the strike nearest the underlying price.

    Raises
    ------
    OpenBBError
        If no strike was quoted on both sides.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    side = "short" if sell else "long"
    quotes = book["quotes"]
    shared = sorted(
        _strikes(quotes, side, "c") & _strikes(quotes, side, "p"),
        key=lambda strike: abs(strike - spot),
    )

    if not shared:
        raise OpenBBError("The optimizer quoted no strike on both sides.")

    strike = shared[0]
    legs = [_leg(book, side, "c", strike), _leg(book, side, "p", strike)]

    return {"legs": legs, "elapsed": int(legs[0]["dte"])}


def build_strangle(
    book: dict, spot: float, moneyness: float = MONEYNESS, sell: bool = False
) -> dict:
    """Build a strangle the given distance out of the money on both sides.

    Raises
    ------
    OpenBBError
        If either wing was not quoted.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    side = "short" if sell else "long"
    quotes = book["quotes"]
    call = _nearest(_strikes(quotes, side, "c"), spot * (1 + moneyness))
    put = _nearest(_strikes(quotes, side, "p"), spot * (1 - moneyness))

    if call is None or put is None:
        raise OpenBBError("The optimizer quoted no wing for a strangle.")

    legs = [_leg(book, side, "c", call), _leg(book, side, "p", put)]

    return {"legs": legs, "elapsed": int(legs[0]["dte"])}


def build_calendar(
    near: dict,
    far: dict,
    spot: float,
    option_type: str = "c",
    sell: bool = False,
) -> dict:
    """Build a calendar spread, valued on the near expiration.

    Raises
    ------
    OpenBBError
        If no strike was quoted on both expirations, or the chain implies no
        forward for either.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    near_side, far_side = ("long", "short") if sell else ("short", "long")
    shared = sorted(
        _strikes(near["quotes"], near_side, option_type)
        & _strikes(far["quotes"], far_side, option_type),
        key=lambda strike: abs(strike - spot),
    )

    if not shared:
        raise OpenBBError("The optimizer quoted no strike on both expirations.")

    if not near.get("forward") or not far.get("forward"):
        raise OpenBBError(
            "The chain implies no forward price for one of these expirations."
        )

    strike = shared[0]
    near_leg = _leg(near, near_side, option_type, strike)
    far_leg = _leg(far, far_side, option_type, strike)
    far_leg["carry"] = far["forward"] / near["forward"]
    far_leg["discount"] = far["discount"] / near["discount"]

    for leg in (near_leg, far_leg):
        leg["iv"] = (
            implied_vol(
                float(leg["price"]),
                spot * float(leg.get("carry") or 1),
                strike,
                int(leg["dte"]) / 365,
                float(leg.get("discount") or 1),
                option_type,
            )
            or leg["iv"]
        )

    return {"legs": [near_leg, far_leg], "elapsed": int(near_leg["dte"])}
