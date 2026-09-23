"""Ranking every Deribit combo structure against a view."""

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
SHORTLIST = 40
WING_REACH = 4
STRIKE_WINDOW = 0.35
STRESS_MOVE = 3.0
STRESS_STEPS = 60
DIAGONAL_REACH = 3

NAMES = {
    ("C", 1): "Long Call",
    ("C", -1): "Short Call",
    ("P", 1): "Long Put",
    ("P", -1): "Short Put",
    ("CS", 1): "Bull Call Spread",
    ("CS", -1): "Bear Call Spread",
    ("PS", 1): "Bear Put Spread",
    ("PS", -1): "Bull Put Spread",
    ("STRD", 1): "Long Straddle",
    ("STRD", -1): "Short Straddle",
    ("STRG", 1): "Long Strangle",
    ("STRG", -1): "Short Strangle",
    ("RR", 1): "Bearish Risk Reversal",
    ("RR", -1): "Bullish Risk Reversal",
    ("REV", 1): "Synthetic Long",
    ("REV", -1): "Synthetic Short",
    ("CSR12", 1): "Call Ratio Spread",
    ("CSR12", -1): "Call Backspread",
    ("PSR12", 1): "Put Ratio Spread",
    ("PSR12", -1): "Put Backspread",
    ("CBUT", 1): "Long Call Butterfly",
    ("CBUT", -1): "Short Call Butterfly",
    ("PBUT", 1): "Long Put Butterfly",
    ("PBUT", -1): "Short Put Butterfly",
    ("IBUT", 1): "Iron Butterfly",
    ("IBUT", -1): "Reverse Iron Butterfly",
    ("CCOND", 1): "Long Call Condor",
    ("CCOND", -1): "Short Call Condor",
    ("PCOND", 1): "Long Put Condor",
    ("PCOND", -1): "Short Put Condor",
    ("ICOND", 1): "Iron Condor",
    ("ICOND", -1): "Reverse Iron Condor",
    ("CCAL", 1): "Long Call Calendar",
    ("CCAL", -1): "Short Call Calendar",
    ("PCAL", 1): "Long Put Calendar",
    ("PCAL", -1): "Short Put Calendar",
    ("CDIAG", 1): "Long Call Diagonal",
    ("CDIAG", -1): "Short Call Diagonal",
    ("PDIAG", 1): "Long Put Diagonal",
    ("PDIAG", -1): "Short Put Diagonal",
}


def _leg(row: Any, quantity: int) -> dict:
    """Describe one contract as a leg of a position, volatility as a decimal."""
    quoted = row["implied_volatility"]

    return {
        "symbol": str(row["contract_symbol"]),
        "expiration": str(row["expiration"]),
        "strike": float(row["strike"]),
        "option_type": str(row["option_type"]),
        "quantity": quantity,
        "size": float(row["contract_size"] or 1),
        "price": float(row["entry"] if quantity > 0 else row["exit"]),
        "dte": int(row["dte"] or 0),
        "implied_volatility": None if quoted is None else float(quoted) / 100,
    }


def _describe(legs: "list[dict]") -> str:
    """Name the contracts a position trades, and how many of each."""
    parts: list[str] = []

    for leg in legs:
        side = "Buy" if leg["quantity"] > 0 else "Sell"
        count = abs(int(leg["quantity"]))
        parts.append(
            f"{side} {leg['symbol']}"
            if count == 1
            else f"{side} {count} {leg['symbol']}"
        )

    return " / ".join(parts)


def _key(legs: "list[dict]") -> frozenset:
    """Return what identifies a position: each contract and how much of it."""
    return frozenset((leg["symbol"], int(leg["quantity"])) for leg in legs)


def _sign(value: float) -> int:
    """Return the direction of a quantity."""
    return 1 if value > 0 else -1


def _two_legs(first: dict, second: dict) -> tuple:
    """Classify a two-legged position on one expiration."""
    kinds = {first["option_type"][0], second["option_type"][0]}

    if len(kinds) == 2:
        call, put = (
            (first, second) if first["option_type"][0] == "c" else (second, first)
        )

        if abs(call["quantity"]) != 1 or abs(put["quantity"]) != 1:
            return "", 1

        together = call["quantity"] == put["quantity"]

        if put["strike"] == call["strike"]:
            return (
                ("STRD", _sign(call["quantity"]))
                if together
                else (
                    "REV",
                    _sign(call["quantity"]),
                )
            )

        if put["strike"] < call["strike"]:
            return (
                ("STRG", _sign(call["quantity"]))
                if together
                else (
                    "RR",
                    _sign(put["quantity"]),
                )
            )

        return "", 1

    low, high = sorted((first, second), key=lambda leg: leg["strike"])
    kind = "C" if low["option_type"][0] == "c" else "P"
    units = (int(low["quantity"]), int(high["quantity"]))

    if low["strike"] == high["strike"]:
        return "", 1

    if units in ((1, -1), (-1, 1)):
        return f"{kind}S", _sign(units[0] if kind == "C" else units[1])

    ratios = {"C": ((1, -2), (-1, 2)), "P": ((-2, 1), (2, -1))}

    if units in ratios[kind]:
        return f"{kind}SR12", 1 if units == ratios[kind][0] else -1

    return "", 1


def classify(legs: "list[dict]") -> tuple:
    """Return the Deribit combo code of a position and the side it is taken on.

    Parameters
    ----------
    legs : list[dict]
        The unit legs of the position.

    Returns
    -------
    tuple
        The code, such as 'CS' or 'ICOND', and 1 when the combo is bought or -1
        when it is sold. An unrecognised position has an empty code.
    """
    terms = sorted({int(leg["dte"]) for leg in legs})
    ordered = sorted(legs, key=lambda leg: (leg["strike"], leg["option_type"]))
    kinds = {leg["option_type"][0] for leg in legs}

    if len(legs) == 1:
        leg = legs[0]

        return ("C" if leg["option_type"][0] == "c" else "P"), _sign(leg["quantity"])

    if len(terms) == 2 and len(legs) == 2 and len(kinds) == 1:
        near, far = sorted(legs, key=lambda leg: leg["dte"])
        kind = "C" if near["option_type"][0] == "c" else "P"

        if near["quantity"] != -far["quantity"] or abs(far["quantity"]) != 1:
            return "", 1

        shape = "CAL" if near["strike"] == far["strike"] else "DIAG"

        return f"{kind}{shape}", _sign(far["quantity"])

    if len(terms) != 1:
        return "", 1

    if len(legs) == 2:
        return _two_legs(*legs)

    units = tuple(int(leg["quantity"]) for leg in ordered)
    strikes = [leg["strike"] for leg in ordered]

    if len(legs) == 3 and len(kinds) == 1 and len(set(strikes)) == 3:
        kind = "C" if ordered[0]["option_type"][0] == "c" else "P"
        even = strikes[1] - strikes[0] == strikes[2] - strikes[1]

        if even and units in ((1, -2, 1), (-1, 2, -1)):
            return f"{kind}BUT", units[0]

    if len(legs) == 4 and len(kinds) == 1 and len(set(strikes)) == 4:
        kind = "C" if ordered[0]["option_type"][0] == "c" else "P"

        if units in ((1, -1, -1, 1), (-1, 1, 1, -1)):
            return f"{kind}COND", units[0]

    if len(legs) == 4 and len(kinds) == 2:
        puts = sorted(
            (leg for leg in legs if leg["option_type"][0] == "p"),
            key=lambda leg: leg["strike"],
        )
        calls = sorted(
            (leg for leg in legs if leg["option_type"][0] == "c"),
            key=lambda leg: leg["strike"],
        )
        shape = (
            [int(leg["quantity"]) for leg in puts],
            [int(leg["quantity"]) for leg in calls],
        )

        if len(puts) == 2 and puts[1]["strike"] <= calls[0]["strike"]:
            body = "IBUT" if puts[1]["strike"] == calls[0]["strike"] else "ICOND"

            if shape == ([1, -1], [-1, 1]):
                return body, 1

            if shape == ([-1, 1], [1, -1]):
                return body, -1

    return "", 1


def _position(pairs: "list[tuple]", book: dict) -> dict:
    """Build one position from contracts and quantities, priced off a combo book."""
    legs = [_leg(row, quantity) for row, quantity in pairs]
    code, side = classify(legs)
    listed = book.get(_key(legs))

    return {
        "strategy": NAMES.get((code, side), "Custom"),
        "code": code or None,
        "combo": listed[0] if listed else None,
        "premium": listed[1] * legs[0]["size"] if listed else None,
        "legs": legs,
    }


def _both(pairs: "list[tuple]", book: dict) -> "list[dict]":
    """Return a position bought and the same position sold."""
    flipped = [(row, -quantity) for row, quantity in pairs]

    return [_position(pairs, book), _position(flipped, book)]


def combo_book(books: "list | tuple", spot: float, inverse: bool) -> dict:
    """Return each listed combo's price, keyed by the legs that make it up.

    Parameters
    ----------
    books : list or tuple
        The listed combos, as ``load_combos`` returns them.
    spot : float
        The current price of the underlying, which a coin quote is carried at.
    inverse : bool
        Whether the combos are quoted in the coin.

    Returns
    -------
    dict
        The combo name and what one unit costs in the quote currency, for the
        combo bought at its offer and for it sold at its bid.
    """
    carry = spot if inverse else 1.0
    lookup: dict = {}

    for book in books:
        bought = frozenset(book["legs"])
        sold = frozenset((name, -amount) for name, amount in book["legs"])

        if book["ask"] is not None:
            lookup[bought] = (book["name"], float(book["ask"]) * carry)

        if book["bid"] is not None:
            lookup[sold] = (book["name"], -float(book["bid"]) * carry)

    return lookup


def _spaced(rows: list) -> "list[tuple]":
    """Return every pair of strikes, lower first."""
    return [(low, high) for index, low in enumerate(rows) for high in rows[index + 1 :]]


def _single_expiry(calls: list, puts: list, book: dict) -> "list[dict]":
    """Build every structure that trades one expiration."""
    built: list[dict] = []
    call_at = {float(row["strike"]): row for row in calls}
    put_at = {float(row["strike"]): row for row in puts}

    for row in [*calls, *puts]:
        built += _both([(row, 1)], book)

    for low, high in _spaced(calls):
        built += _both([(low, 1), (high, -1)], book)
        built += _both([(low, 1), (high, -2)], book)

    for low, high in _spaced(puts):
        built += _both([(high, 1), (low, -1)], book)
        built += _both([(high, 1), (low, -2)], book)

    for strike, call in call_at.items():
        if strike in put_at:
            built += _both([(call, 1), (put_at[strike], 1)], book)
            built += _both([(call, 1), (put_at[strike], -1)], book)

    for put in puts:
        for call in calls:
            if float(put["strike"]) < float(call["strike"]):
                built += _both([(put, 1), (call, 1)], book)
                built += _both([(put, 1), (call, -1)], book)

    for rows, at in ((calls, call_at), (puts, put_at)):
        for low, middle in _spaced(rows):
            width = float(middle["strike"]) - float(low["strike"])
            high = at.get(float(middle["strike"]) + width)

            if high is not None:
                built += _both([(low, 1), (middle, -2), (high, 1)], book)

        for index, first in enumerate(rows):
            for second in rows[index + 1 : index + 1 + WING_REACH]:
                wing = float(second["strike"]) - float(first["strike"])

                for third in rows:
                    fourth = at.get(float(third["strike"]) + wing)

                    if float(third["strike"]) > float(second["strike"]) and fourth:
                        built += _both(
                            [(first, 1), (second, -1), (third, -1), (fourth, 1)],
                            book,
                        )

    for index, low in enumerate(puts):
        for high in puts[index + 1 : index + 1 + WING_REACH]:
            wing = float(high["strike"]) - float(low["strike"])

            for call in calls:
                upper = call_at.get(float(call["strike"]) + wing)

                if float(call["strike"]) >= float(high["strike"]) and upper:
                    built += _both([(low, 1), (high, -1), (call, -1), (upper, 1)], book)

    return built


def _two_expiries(near: list, far: list, book: dict) -> "list[dict]":
    """Build every calendar and diagonal between two expirations."""
    built: list[dict] = []

    for kind in ("call", "put"):
        later = [row for row in far if row["option_type"] == kind]
        strikes = [float(row["strike"]) for row in later]

        for row in (row for row in near if row["option_type"] == kind):
            position = min(
                range(len(strikes)),
                key=lambda index: abs(strikes[index] - float(row["strike"])),
                default=None,
            )

            if position is None:
                continue

            reach = later[
                max(position - DIAGONAL_REACH, 0) : position + DIAGONAL_REACH + 1
            ]

            for other in reach:
                built += _both([(row, -1), (other, 1)], book)

    return built


def _window_rows(quotes: "DataFrame", spot: float) -> list:
    """Return the tradeable contracts near the money, as records."""
    near = quotes[
        (quotes["strike"] >= spot * (1 - STRIKE_WINDOW))
        & (quotes["strike"] <= spot * (1 + STRIKE_WINDOW))
    ]

    return near.sort_values("strike").to_dict("records")


def candidates(
    frame: "DataFrame",
    expiration: Any,
    spot: float,
    books: "list | tuple" = (),
    inverse: bool = False,
) -> "list[dict]":
    """Build every combo structure an expiration can form, both bought and sold.

    Parameters
    ----------
    frame : DataFrame
        The chain.
    expiration : Any
        The expiration the position is held to.
    spot : float
        The current price of the underlying.
    books : list or tuple
        The listed combos, as ``load_combos`` returns them.
    inverse : bool
        Whether the contracts settle in the underlying.

    Returns
    -------
    list[dict]
        Each position, named and coded, with its legs and any listed combo that
        trades it as one instrument.
    """
    from openbb_deribit.utils.options.chain import far_expiration, quotes_at

    book = combo_book(books, spot, inverse)
    near = _window_rows(quotes_at(frame, expiration), spot)
    calls = [row for row in near if row["option_type"] == "call"]
    puts = [row for row in near if row["option_type"] == "put"]
    built = _single_expiry(calls, puts, book)
    later = far_expiration(frame, expiration)

    if later is not None:
        built += _two_expiries(near, _window_rows(quotes_at(frame, later), spot), book)

    tradeable = {
        str(row["contract_symbol"]): row for row in quotes_at(frame).to_dict("records")
    }

    for listed in books:
        rows = [
            tradeable[name] for name, _amount in listed["legs"] if name in tradeable
        ]

        if len(rows) != len(listed["legs"]) or (
            min(row["expiration"] for row in rows) != expiration
        ):
            continue

        built += _both(
            [
                (row, amount)
                for row, (_name, amount) in zip(rows, listed["legs"], strict=True)
            ],
            book,
        )

    unique: dict = {}

    for item in built:
        unique.setdefault(_key(item["legs"]), item)

    return list(unique.values())


def rebuild(
    described: str,
    quotes: "DataFrame",
    books: "list | tuple" = (),
    spot: float = 0.0,
    inverse: bool = False,
) -> dict:
    """Return the position a description names, priced at the current quotes.

    Parameters
    ----------
    described : str
        The legs, as ``_describe`` writes them: 'Buy SYMBOL / Sell 2 SYMBOL'.
    quotes : DataFrame
        The tradeable contracts of every expiration.
    books : list or tuple
        The listed combos, as ``load_combos`` returns them.
    spot : float
        The current price of the underlying.
    inverse : bool
        Whether the contracts settle in the underlying.

    Returns
    -------
    dict
        The position, named and coded, with its legs.

    Raises
    ------
    ValueError
        If the description names no contract, or one not listed.
    """
    pairs: list[tuple] = []

    for part in described.split("/"):
        words = part.split()
        count = words[1] if len(words) == 3 else "1"

        if (
            len(words) not in (2, 3)
            or words[0].lower() not in ("buy", "sell")
            or not count.isdigit()
            or int(count) < 1
        ):
            raise ValueError(
                f"{part.strip()!r} does not name a leg. A position reads"
                " 'Buy SYMBOL / Sell SYMBOL', with a count before the symbol"
                " when there is more than one, which is what the optimizer"
                " prints in its Legs column."
            )

        symbol = words[-1]
        listed = quotes[quotes["contract_symbol"] == symbol]

        if listed.empty:
            raise ValueError(
                f"{symbol} is not a listed contract, so the position cannot be"
                " priced. Pick a strategy from the optimizer."
            )

        quantity = int(count) if words[0].lower() == "buy" else -int(count)
        pairs.append((listed.to_dict("records")[0], quantity))

    return _position(pairs, combo_book(books, spot, inverse))


def _stress(legs: "list[dict]", spot: float, elapsed: int) -> "list[float]":
    """Return the prices a position's worst loss is sought over."""
    low, high = spot / STRESS_MOVE, spot * STRESS_MOVE
    points = {low, spot, high, *(leg["strike"] for leg in legs)}

    if any(int(leg["dte"] or 0) > elapsed for leg in legs):
        points.update(_grid(low, high, STRESS_STEPS))

    return sorted(point for point in points if low <= point <= high)


def score(strategy: dict, spot: float, target: float, inverse: bool) -> "dict | None":
    """Size one position to one unit of capital at risk and value it at the target.

    Parameters
    ----------
    strategy : dict
        The position, with its legs and any combo premium.
    spot : float
        The current price of the underlying.
    target : float
        The price the view expects.
    inverse : bool
        Whether the contracts settle in the underlying.

    Returns
    -------
    dict or None
        The position sized so its worst loss across a threefold move either way
        is one unit, or None when it has nothing at risk.
    """
    from openbb_deribit.utils.options.legs import net_cost, payoff

    legs = strategy["legs"]
    premium = strategy.get("premium")
    unit_cost = net_cost(legs) if premium is None else premium
    elapsed = max(min(int(leg["dte"] or 0) for leg in legs), 0)
    points = _stress(legs, spot, elapsed)
    losses = payoff(legs, points, elapsed, inverse, spot, unit_cost)

    if inverse:
        losses = [
            loss / price * spot for loss, price in zip(losses, points, strict=True)
        ]

    risk = -min(losses)

    if risk <= 0:
        return None

    lots = 1.0 / risk
    sized = [{**leg, "quantity": leg["quantity"] * lots} for leg in legs]
    expected = payoff(sized, [target], elapsed, inverse, spot, unit_cost * lots)[0]

    return {
        **strategy,
        "sized": sized,
        "lots": lots,
        "elapsed": elapsed,
        "cost": unit_cost * lots,
        "expected": expected,
    }


def _grid(low: float, high: float, steps: int) -> "list[float]":
    """Return an evenly spaced range of prices."""
    return [low + (high - low) * step / steps for step in range(steps + 1)]


def _moving(prices: "list[float]", curve: "list[float]") -> tuple:
    """Return the price range over which a payoff is still changing."""
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
    legs: "list[dict]",
    spot: float,
    target: float,
    elapsed: int,
    inverse: bool,
    cost: "float | None" = None,
) -> tuple:
    """Return the price range worth drawing for one position.

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
    cost : float or None
        What the position was opened for, when traded as one combo.

    Returns
    -------
    tuple
        The lowest and highest price to draw.
    """
    from openbb_deribit.utils.options.legs import breakevens, payoff, position_value

    scout = _grid(spot * (1 - PROBE_SPREAD), spot * (1 + PROBE_SPREAD), SCOUT_STEPS)
    curve = payoff(legs, scout, elapsed, inverse, spot, cost)
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
    """Value one scored position across the price range worth drawing."""
    from openbb_deribit.utils.options.legs import breakevens, payoff

    legs = [{**leg, "quantity": leg["quantity"] * budget} for leg in scored["sized"]]
    cost = scored["cost"] * budget
    elapsed = scored["elapsed"]
    low, high = _window(legs, spot, target, elapsed, inverse, cost)
    probe = _grid(low, high, PROBE_STEPS)
    curve = payoff(legs, probe, elapsed, inverse, spot, cost)

    return {
        "strategy": scored["strategy"],
        "code": scored["code"],
        "combo": scored["combo"],
        "legs": _describe(scored["legs"]),
        "contracts": scored["lots"] * budget,
        "cost": cost,
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
    frame: "DataFrame",
    expiration: Any,
    spot: float,
    target: float,
    budget: float,
    inverse: bool,
    limit: int = SHORTLIST,
    books: "list | tuple" = (),
) -> "list[dict]":
    """Return the best position of each structure, most profitable first.

    Parameters
    ----------
    frame : DataFrame
        The chain.
    expiration : Any
        The expiration the position is held to.
    spot : float
        The current price of the underlying.
    target : float
        The price the view expects.
    budget : float
        The capital to put at risk, in the quote currency.
    inverse : bool
        Whether the contracts settle in the underlying.
    limit : int
        How many structures to return.
    books : list or tuple
        The listed combos, as ``load_combos`` returns them.

    Returns
    -------
    list[dict]
        The best-returning position of each structure, sized to the budget,
        with its payoff.
    """
    scored = [
        result
        for strategy in candidates(frame, expiration, spot, books, inverse)
        if (result := score(strategy, spot, target, inverse))
    ]
    scored.sort(key=lambda item: item["expected"], reverse=True)
    best: dict = {}

    for item in scored:
        best.setdefault(item["strategy"], item)

    return [
        draw(item, spot, target, budget, inverse)
        for item in list(best.values())[:limit]
    ]
