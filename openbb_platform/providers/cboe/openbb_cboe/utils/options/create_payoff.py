"""Cboe trade optimizer payoff diagram."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from openbb_core.app.model.obbject import OBBject

SPREAD = 0.06

STRATEGY_LABELS = {
    ("Long Spread", "c"): "Buy Call Spread",
    ("Long Spread", "p"): "Buy Put Spread",
    ("Short Spread", "c"): "Sell Call Spread",
    ("Short Spread", "p"): "Sell Put Spread",
    ("Naked Short", "c"): "Sell Call",
    ("Naked Short", "p"): "Sell Put",
    ("Naked Long", "c"): "Buy Call",
    ("Naked Long", "p"): "Buy Put",
}


def _intrinsic(price: float, strike: float, option_type: str) -> float:
    """Return the value of one contract at expiration."""
    return max(0.0, price - strike) if option_type == "c" else max(0.0, strike - price)


def payoff_curve(row: dict, prices: list[float]) -> list[float]:
    """Return the profit and loss of one strategy across a price range.

    Parameters
    ----------
    row : dict
        One trade optimizer result, carrying its legs and its cost.
    prices : list[float]
        The underlying prices to evaluate.

    Returns
    -------
    list[float]
        The profit and loss of a single contract at each price.
    """
    option_type = str(row.get("type") or "c")
    strategy = str(row.get("strategy") or "")
    cost = float(row.get("current_price") or 0)
    long_strike = float(row.get("strike1") or 0)
    short_strike = float(row.get("strike2") or 0)

    if strategy == "Naked Short":
        return [100 * (cost - _intrinsic(p, long_strike, option_type)) for p in prices]

    if strategy == "Naked Long":
        return [100 * (_intrinsic(p, long_strike, option_type) - cost) for p in prices]

    spread = [
        _intrinsic(p, long_strike, option_type)
        - _intrinsic(p, short_strike, option_type)
        for p in prices
    ]

    if strategy == "Short Spread":
        return [100 * (cost - value) for value in spread]

    return [100 * (value - cost) for value in spread]


def _breakevens(prices: list[float], payoff: list[float]) -> list[float]:
    """Return every price where the payoff crosses zero."""
    crossings: list[float] = []

    for index in range(1, len(payoff)):
        if (payoff[index - 1] < 0) == (payoff[index] < 0):
            continue

        low, high = payoff[index - 1], payoff[index]
        weight = abs(low) / (abs(low) + abs(high)) if (low or high) else 0
        crossings.append(
            prices[index - 1] + weight * (prices[index] - prices[index - 1])
        )

    return crossings


def _breakeven_labels(count: int) -> list[str]:
    """Name each breakeven for the chart."""
    return ["Lower B/E", "Upper B/E"] if count == 2 else ["B/E"] * count


def _label(row: dict) -> str:
    """Name the strategy the way the optimizer presents it."""
    strategy = str(row.get("strategy") or "")
    option_type = str(row.get("type") or "c")

    return STRATEGY_LABELS.get((strategy, option_type), strategy)


def _legs(row: dict) -> str:
    """Describe the contracts the strategy trades."""
    symbol = str(row.get("symbol") or "")
    expiry = str(row.get("expiry") or "")
    option_type = "Call" if str(row.get("type")) == "c" else "Put"
    strategy = str(row.get("strategy") or "")
    first = float(row.get("strike1") or 0)
    second = float(row.get("strike2") or 0)
    buy, sell = ("Buy", "Sell") if strategy == "Long Spread" else ("Sell", "Buy")

    if strategy in ("Naked Short", "Naked Long"):
        verb = "Sell" if strategy == "Naked Short" else "Buy"

        return f"{verb} {symbol} {expiry} {first:g} {option_type}"

    return (
        f"{buy} {symbol} {expiry} {first:g} {option_type},"
        f" {sell} {symbol} {expiry} {second:g} {option_type}"
    )


def _position_legs(position: dict, symbol: str) -> str:
    """Describe the contracts a multi-leg position trades."""
    described: list[str] = []

    for leg in position["legs"]:
        verb = "Buy" if float(leg["quantity"]) > 0 else "Sell"
        option_type = "Call" if str(leg["type"]) == "c" else "Put"
        described.append(
            f"{verb} {symbol} {leg['expiration']} {float(leg['strike']):g}"
            f" {option_type}"
        )

    return ", ".join(described)


def _bounds(
    spot: float,
    target: float,
    strikes: list[float],
    breakevens: list[float],
) -> tuple[float, float]:
    """Return the price range the diagram is drawn over."""
    marks = [*strikes, spot, target, *breakevens]
    low, high = min(marks), max(marks)
    pad = max((high - low) * 0.35, spot * SPREAD, 0.5)

    return max(low - pad, 0.01), high + pad


def _mark(fig, price: float, text: str, color: str, height: float) -> None:
    """Draw one labelled vertical marker at a price."""
    fig.add_vline(x=price, line_width=1, line_dash="dash", line_color=color)
    fig.add_annotation(
        x=price,
        y=height,
        yref="paper",
        text=text,
        showarrow=False,
        font=dict(size=10, color=color),
        bordercolor=color,
        borderwidth=1,
        borderpad=3,
        bgcolor="rgba(255, 255, 255, 0.85)",
        yanchor="middle",
    )


def create_payoff(
    data: dict,
    theme: str = "dark",
    **kwargs,
) -> OBBject:
    """Build the payoff diagram for one trade optimizer strategy.

    Parameters
    ----------
    data : dict
        Either the optimizer row to draw, under 'strategy', or a position
        assembled from its quotes, under 'position', with the spot price of
        the underlying and the target price it was ranked against.
    theme : str
        Either 'dark' or 'light'.

    Returns
    -------
    OBBject
        The figure, with the evaluated curve as its results.
    """
    from openbb_core.app.model.obbject import OBBject
    from openbb_core.app.utils import df_to_basemodel
    from pandas import DataFrame

    from openbb_cboe.utils.options.legs import net_cost, payoff_from_legs
    from openbb_cboe.utils.options.theme import finalize, new_figure

    row = data.get("strategy") or {}
    position = data.get("position") or {}
    spot = float(data.get("spot") or 0)

    if position:
        legs = position["legs"]
        elapsed = int(position.get("elapsed") or 0)

        def curve(points: list[float]) -> list[float]:
            """Value the assembled position across a price range."""
            return payoff_from_legs(legs, points, elapsed)

        strikes = [float(leg["strike"]) for leg in legs]
        cost = net_cost(legs)
        title = str(position.get("label") or "")
        detail = _position_legs(position, str(data.get("symbol") or ""))
    else:

        def curve(points: list[float]) -> list[float]:
            """Value the ranked strategy across a price range."""
            return payoff_curve(row, points)

        strikes = [float(row.get(f"strike{leg}") or 0) for leg in (1, 2, 3, 4)]
        strikes = [strike for strike in strikes if strike > 0]
        credit = str(row.get("strategy")) in ("Short Spread", "Naked Short")
        cost = float(row.get("current_price") or 0) * (-1 if credit else 1)
        title = _label(row)
        detail = _legs(row)

    target = float(data.get("target") or row.get("target_stock_price") or spot)
    probe = [spot * (0.5 + i / 400) for i in range(401)]
    breakevens = _breakevens(probe, curve(probe))
    low, high = _bounds(spot, target, strikes, breakevens)
    steps = 400
    prices = [low + (high - low) * i / steps for i in range(steps + 1)]
    payoff = curve(prices)

    fig, text_color, background = new_figure(theme)
    fig.add_scatter(
        x=prices,
        y=[max(value, 0) for value in payoff],
        mode="lines",
        name="Profit",
        line=dict(width=0),
        fill="tozeroy",
        fillcolor="rgba(63, 185, 80, 0.22)",
        hoverinfo="skip",
    )
    fig.add_scatter(
        x=prices,
        y=[min(value, 0) for value in payoff],
        mode="lines",
        name="Loss",
        line=dict(width=0),
        fill="tozeroy",
        fillcolor="rgba(227, 93, 106, 0.22)",
        hoverinfo="skip",
    )
    fig.add_scatter(
        x=prices,
        y=payoff,
        mode="lines",
        name="P/L",
        line=dict(color="#2f6fed", width=2),
        hovertemplate="<b>$%{y:,.2f}</b><extra></extra>",
    )
    markers = [(spot, f"Spot ${spot:,.2f}", "#8b949e")]

    if abs(target - spot) > (high - low) / 50:
        markers.append((target, f"Target ${target:,.2f}", "#8b949e"))

    markers += [
        (level, f"{label} ${level:,.2f}", "#e35d6a")
        for label, level in zip(_breakeven_labels(len(breakevens)), breakevens)
    ]
    markers.sort()

    for index, (price, text, color) in enumerate(markers):
        _mark(fig, price, text, color, 0.95 if index % 2 == 0 else 0.83)

    priced = f"for ${cost:,.2f}" if cost >= 0 else f"for a ${abs(cost):,.2f} credit"
    fig.set_title(
        f"{title} {priced}<br><span style='font-size:12px'>{detail}</span>",
        x=0.5,
        font=dict(size=15),
    )
    fig.update_layout(
        paper_bgcolor=background,
        plot_bgcolor=background,
        font=dict(color=text_color),
        margin=dict(l=10, r=10, t=76, b=10),
        hovermode="x",
        showlegend=False,
        xaxis=dict(
            title="Underlying price",
            showgrid=False,
            linecolor=text_color,
            hoverformat="$,.2f",
            range=[low, high],
        ),
        yaxis=dict(
            title="P/L",
            side="left",
            showgrid=True,
            zeroline=True,
            zerolinecolor=text_color,
            linecolor=text_color,
        ),
    )
    frame = DataFrame({"underlying_price": prices, "profit_or_loss": payoff})
    output: Any = OBBject(results=df_to_basemodel(frame))

    return finalize(output, fig, theme)
