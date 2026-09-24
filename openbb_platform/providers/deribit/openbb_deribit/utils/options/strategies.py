"""Pricing the standard option structures at every expiration.

Prices are quoted in the chain's quote currency per unit of the underlying, so
a cost is comparable across expirations of the same underlying but not across
underlyings. The cost as a share of spot is, which is why it is reported too.
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pandas import DataFrame


def _closest(side: "DataFrame", target: float) -> "Any | None":
    """Return the contract whose strike is nearest a price."""
    if side.empty:
        return None

    return side.iloc[(side["strike"] - target).abs().argmin()]


def _sides(quotes: "DataFrame") -> tuple:
    """Split one expiration into its calls and its puts."""
    return (
        quotes[quotes["option_type"] == "call"],
        quotes[quotes["option_type"] == "put"],
    )


def straddles(frame: "DataFrame", spot: float) -> "list[dict]":
    """Price a long straddle at the money, at every expiration."""
    from openbb_deribit.utils.options.chain import expirations, quotes_at

    priced: list[dict] = []

    for expiration in expirations(frame):
        quotes = quotes_at(frame, expiration)
        calls, puts = _sides(quotes)
        call = _closest(calls, spot)
        put = _closest(puts, spot)

        if call is None or put is None:
            continue

        if float(call["strike"]) != float(put["strike"]):
            continue

        strike = float(call["strike"])
        cost = float(call["entry"]) + float(put["entry"])

        priced.append(
            {
                "expiration": expiration,
                "dte": int(call["dte"] or 0),
                "underlying_price": spot,
                "strike": strike,
                "call_premium": float(call["entry"]),
                "put_premium": float(put["entry"]),
                "cost": cost,
                "cost_percent": cost / spot if spot else None,
                "breakeven_lower": strike - cost,
                "breakeven_upper": strike + cost,
                "max_loss": -cost,
            }
        )

    return priced


def strangles(frame: "DataFrame", spot: float, moneyness: float) -> "list[dict]":
    """Price a long strangle the given distance out of the money."""
    from openbb_deribit.utils.options.chain import expirations, quotes_at

    priced: list[dict] = []

    for expiration in expirations(frame):
        quotes = quotes_at(frame, expiration)
        calls, puts = _sides(quotes)
        call = _closest(calls, spot * (1 + moneyness))
        put = _closest(puts, spot * (1 - moneyness))

        if call is None or put is None:
            continue

        upper = float(call["strike"])
        lower = float(put["strike"])

        if upper <= lower:
            continue

        cost = float(call["entry"]) + float(put["entry"])

        priced.append(
            {
                "expiration": expiration,
                "dte": int(call["dte"] or 0),
                "underlying_price": spot,
                "call_strike": upper,
                "put_strike": lower,
                "call_premium": float(call["entry"]),
                "put_premium": float(put["entry"]),
                "cost": cost,
                "cost_percent": cost / spot if spot else None,
                "breakeven_lower": lower - cost,
                "breakeven_upper": upper + cost,
                "max_loss": -cost,
            }
        )

    return priced


def verticals(frame: "DataFrame", spot: float, moneyness: float) -> "list[dict]":
    """Price a bull call and a bear put spread of the given width."""
    from openbb_deribit.utils.options.chain import expirations, quotes_at

    priced: list[dict] = []

    for expiration in expirations(frame):
        quotes = quotes_at(frame, expiration)
        calls, puts = _sides(quotes)

        for name, side, long_target, short_target in (
            ("Bull Call Spread", calls, spot, spot * (1 + moneyness)),
            ("Bear Put Spread", puts, spot, spot * (1 - moneyness)),
        ):
            bought = _closest(side, long_target)
            sold = _closest(side, short_target)

            if bought is None or sold is None:
                continue

            width = abs(float(sold["strike"]) - float(bought["strike"]))
            cost = float(bought["entry"]) - float(sold["exit"])

            if width <= 0 or cost <= 0:
                continue

            breakeven = (
                float(bought["strike"]) + cost
                if name.startswith("Bull")
                else float(bought["strike"]) - cost
            )
            priced.append(
                {
                    "strategy": name,
                    "expiration": expiration,
                    "dte": int(bought["dte"] or 0),
                    "underlying_price": spot,
                    "bought_strike": float(bought["strike"]),
                    "sold_strike": float(sold["strike"]),
                    "bought_premium": float(bought["entry"]),
                    "sold_premium": float(sold["exit"]),
                    "cost": cost,
                    "cost_percent": cost / spot if spot else None,
                    "breakeven": breakeven,
                    "max_profit": width - cost,
                    "max_loss": -cost,
                }
            )

    return priced
