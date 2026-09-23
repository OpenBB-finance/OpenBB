"""Ranking option strategies against a view.

Deribit's own wizard runs in the browser, so there is no ranking to fetch. Every
contract on the expiration is combined into the strategies it can form, each is
sized to the budget, and each is valued at the price the view expects.

Scoring a strategy at the target takes one valuation, while drawing its payoff
takes hundreds, so the field is scored first and only the survivors are drawn.
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pandas import DataFrame

PROBE_STEPS = 400
PROBE_SPREAD = 0.6
SCOUT_STEPS = 300
WINDOW_PAD = 0.06
MIN_PAD = 0.0025
FLAT_SLOPE = 0.02
ANCHOR_REACH = 0.35
SHORTLIST = 12
STRIKE_WINDOW = 0.35


def _leg(row: Any, quantity: int) -> dict:
    """Describe one contract as a leg of a position.

    The chain publishes a volatility in percent, which is what the grid shows,
    while the valuation takes it as a decimal, so it is converted here at the
    one point where a quote becomes a modelled position.
    """
    quoted = row["implied_volatility"]

    return {
        "symbol": str(row["contract_symbol"]),
        "strike": float(row["strike"]),
        "option_type": str(row["option_type"]),
        "quantity": quantity,
        "size": float(row["contract_size"] or 1),
        "price": float(row["entry"] if quantity > 0 else row["exit"]),
        "dte": int(row["dte"] or 0),
        "implied_volatility": None if quoted is None else float(quoted) / 100,
    }


def _describe(strategy: str, legs: "list[dict]") -> str:
    """Name the contracts a strategy trades."""
    return " / ".join(
        f"{'Buy' if leg['quantity'] > 0 else 'Sell'} {leg['symbol']}" for leg in legs
    )


def rebuild(described: str, quotes: "DataFrame") -> "list[dict]":
    """Return the legs a description names, priced at the current quotes.

    A position is its contracts, so what names one is the contracts it trades
    and the side each is taken on -- exactly what the ranking already prints.
    Reading that back needs no identifier of its own and no second ranking.

    Parameters
    ----------
    described : str
        The legs, as ``_describe`` writes them: 'Buy SYMBOL / Sell SYMBOL'.
    quotes : DataFrame
        The tradeable contracts of the expiration the position is on.

    Returns
    -------
    list[dict]
        One leg per contract named.

    Raises
    ------
    ValueError
        If the description names no contract, or one not listed here.
    """
    legs: list[dict] = []

    for part in described.split("/"):
        words = part.split()

        if len(words) != 2 or words[0].lower() not in ("buy", "sell"):
            raise ValueError(
                f"{part.strip()!r} does not name a leg. A position reads"
                " 'Buy SYMBOL / Sell SYMBOL', which is what the optimizer"
                " prints in its Legs column."
            )

        side, symbol = words
        listed = quotes[quotes["contract_symbol"] == symbol]

        if listed.empty:
            raise ValueError(
                f"{symbol} is not a contract on this expiration, so the position"
                " cannot be priced. Pick a strategy from the optimizer."
            )

        legs.append(_leg(listed.iloc[0], 1 if side.lower() == "buy" else -1))

    return legs


def candidates(quotes: "DataFrame", spot: float) -> "list[dict]":
    """Build every strategy the expiration can form.

    Strikes far from the money are left out: they price at the tick and rank on
    rounding rather than on the view.

    Parameters
    ----------
    quotes : DataFrame
        The tradeable contracts of one expiration.
    spot : float
        The current price of the underlying.

    Returns
    -------
    list[dict]
        Each strategy, named, with the legs that make it up.
    """
    near = quotes[
        (quotes["strike"] >= spot * (1 - STRIKE_WINDOW))
        & (quotes["strike"] <= spot * (1 + STRIKE_WINDOW))
    ]
    calls = [row for _, row in near[near["option_type"] == "call"].iterrows()]
    puts = [row for _, row in near[near["option_type"] == "put"].iterrows()]
    built: list[dict] = []

    for row in calls:
        built.append({"strategy": "Long Call", "legs": [_leg(row, 1)]})

    for row in puts:
        built.append({"strategy": "Long Put", "legs": [_leg(row, 1)]})

    for index, lower in enumerate(calls):
        for upper in calls[index + 1 :]:
            built.append(
                {
                    "strategy": "Bull Call Spread",
                    "legs": [_leg(lower, 1), _leg(upper, -1)],
                }
            )

    for index, lower in enumerate(puts):
        for upper in puts[index + 1 :]:
            built.append(
                {
                    "strategy": "Bear Put Spread",
                    "legs": [_leg(upper, 1), _leg(lower, -1)],
                }
            )

    strikes = {float(row["strike"]): row for row in puts}

    for row in calls:
        paired = strikes.get(float(row["strike"]))

        if paired is not None:
            built.append(
                {
                    "strategy": "Long Straddle",
                    "legs": [_leg(row, 1), _leg(paired, 1)],
                }
            )

    for call in calls:
        for put in puts:
            if float(put["strike"]) < float(call["strike"]):
                built.append(
                    {
                        "strategy": "Long Strangle",
                        "legs": [_leg(call, 1), _leg(put, 1)],
                    }
                )

    return built


def score(strategy: dict, spot: float, target: float, inverse: bool) -> "dict | None":
    """Size one strategy to one unit of premium and value it at the target.

    Both settlement styles are sized by what the position costs in the quote
    currency, so a budget means the same thing on a coin-settled contract as on
    a linear one.
    """
    from openbb_deribit.utils.options.legs import net_cost, payoff

    legs = strategy["legs"]
    unit_cost = net_cost(legs)

    if unit_cost <= 0:
        return None

    lots = 1.0 / unit_cost
    sized = [{**leg, "quantity": leg["quantity"] * lots} for leg in legs]
    elapsed = max(int(legs[0]["dte"] or 0), 0)
    expected = payoff(sized, [target], elapsed, inverse, spot)[0]

    return {
        **strategy,
        "sized": sized,
        "lots": lots,
        "elapsed": elapsed,
        "expected": expected,
    }


def _grid(low: float, high: float, steps: int) -> "list[float]":
    """Return an evenly spaced range of prices."""
    return [low + (high - low) * step / steps for step in range(steps + 1)]


def _moving(prices: "list[float]", curve: "list[float]") -> tuple:
    """Return the price range over which a payoff is still changing.

    Steepness is measured against the steepest part of the curve, so a shoulder
    that is merely gentle still reads as flat.
    """
    slopes = [
        abs((curve[step] - curve[step - 1]) / (prices[step] - prices[step - 1]))
        for step in range(1, len(prices))
    ]
    steepest = max(slopes)
    moving = [
        step for step, slope in enumerate(slopes) if slope > steepest * FLAT_SLOPE
    ]

    if not moving:
        return prices[0], prices[-1]

    return prices[moving[0]], prices[moving[-1] + 1]


def _window(
    legs: "list[dict]", spot: float, target: float, elapsed: int, inverse: bool
) -> tuple:
    """Return the price range worth drawing for one position.

    Drawn over a fixed span either side of spot, a payoff spends most of its
    width on a straight line and squeezes everything that happens into the
    middle. The range is taken from the position instead: a coarse pass finds
    where what it pays out is actually changing, and the price the view expects
    and any breakeven are added when they sit within reach of that.

    What the position pays out is what is measured, not the profit. An inverse
    position's premium is coin, so its cost slopes with the price and the
    profit is never flat anywhere, while the payout still has the shoulders
    that say where the position stops responding.

    A position with an uncapped side has no shoulder there at all, so that side
    is drawn out only as far as the price the view expects.

    Parameters
    ----------
    legs : list[dict]
        The sized position.
    spot : float
        The current price of the underlying.
    target : float
        The price the view expects.
    elapsed : int
        Days from now to the valuation date.
    inverse : bool
        Whether the contracts settle in the underlying.

    Returns
    -------
    tuple
        The lowest and highest price to draw.
    """
    from openbb_deribit.utils.options.legs import breakevens, payoff, position_value

    scout = _grid(spot * (1 - PROBE_SPREAD), spot * (1 + PROBE_SPREAD), SCOUT_STEPS)
    curve = payoff(legs, scout, elapsed, inverse, spot)
    low, high = _moving(
        scout, [position_value(legs, price, elapsed) for price in scout]
    )
    anchors = [target, *breakevens(scout, curve)]

    if low <= scout[0]:
        low = min([anchor for anchor in anchors if anchor < high] or [spot])

    if high >= scout[-1]:
        high = max([anchor for anchor in anchors if anchor > low] or [spot])

    reach = max(high - low, spot * MIN_PAD) * ANCHOR_REACH
    nearby = [anchor for anchor in anchors if low - reach <= anchor <= high + reach]
    low, high = min([low, *nearby]), max([high, *nearby])
    pad = max((high - low) * WINDOW_PAD, spot * MIN_PAD)

    return max(low - pad, 0.0), high + pad


def draw(
    scored: dict, spot: float, target: float, budget: float, inverse: bool
) -> dict:
    """Value one scored strategy across the price range worth drawing."""
    from openbb_deribit.utils.options.legs import breakevens, payoff

    legs = [{**leg, "quantity": leg["quantity"] * budget} for leg in scored["sized"]]
    elapsed = scored["elapsed"]
    low, high = _window(legs, spot, target, elapsed, inverse)
    probe = _grid(low, high, PROBE_STEPS)
    curve = payoff(legs, probe, elapsed, inverse, spot)

    return {
        "strategy": scored["strategy"],
        "legs": _describe(scored["strategy"], scored["legs"]),
        "contracts": scored["lots"] * budget,
        "cost": budget,
        "expected_profit": scored["expected"] * budget,
        "expected_return": scored["expected"],
        "max_profit": max(curve),
        "max_loss": min(curve),
        "breakevens": breakevens(probe, curve),
        "position": legs,
        "elapsed": elapsed,
        "prices": probe,
        "payoff": curve,
    }


def rank(
    quotes: "DataFrame",
    spot: float,
    target: float,
    budget: float,
    inverse: bool,
    limit: int = SHORTLIST,
) -> "list[dict]":
    """Return the strategies that serve a view best, most profitable first.

    Parameters
    ----------
    quotes : DataFrame
        The tradeable contracts of one expiration.
    spot : float
        The current price of the underlying.
    target : float
        The price the view expects.
    budget : float
        What there is to spend, in the settlement currency.
    inverse : bool
        Whether the contracts settle in the underlying.
    limit : int
        How many strategies to return.

    Returns
    -------
    list[dict]
        Each strategy sized to the budget, with its payoff.
    """
    scored = [
        result
        for strategy in candidates(quotes, spot)
        if (result := score(strategy, spot, target, inverse))
    ]
    scored.sort(key=lambda item: item["expected"], reverse=True)

    return [draw(item, spot, target, budget, inverse) for item in scored[:limit]]
