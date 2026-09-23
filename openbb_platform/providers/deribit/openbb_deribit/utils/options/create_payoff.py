"""The payoff diagram of one Deribit option position."""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from openbb_core.app.model.obbject import OBBject


def _mark(figure, price: float, text: str, color: str, height: float) -> None:
    """Draw one labelled vertical marker at a price."""
    figure.add_vline(x=price, line_width=1, line_dash="dash", line_color=color)
    figure.add_annotation(
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


def create_payoff(data: dict, theme: str = "dark", **kwargs) -> "OBBject":
    """Draw what one position returns across a range of underlying prices.

    Parameters
    ----------
    data : dict
        The sized position, the prices it was valued at, the profit at each,
        the spot and target prices, and what it settles in.
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

    from openbb_deribit.utils.options.theme import finalize, new_figure

    prices = data["prices"]
    values = data["payoff"]
    spot = float(data.get("spot") or 0)
    target = float(data.get("target") or spot)
    settles = str(data.get("settles") or "")
    quote = str(data.get("quote") or "USD")
    figure, text_color, background = new_figure(theme)

    figure.add_scatter(
        x=prices,
        y=[max(value, 0) for value in values],
        mode="lines",
        name="Profit",
        line=dict(width=0),
        fill="tozeroy",
        fillcolor="rgba(63, 185, 80, 0.22)",
        hoverinfo="skip",
    )
    figure.add_scatter(
        x=prices,
        y=[min(value, 0) for value in values],
        mode="lines",
        name="Loss",
        line=dict(width=0),
        fill="tozeroy",
        fillcolor="rgba(227, 93, 106, 0.22)",
        hoverinfo="skip",
    )
    figure.add_scatter(
        x=prices,
        y=values,
        mode="lines",
        name="P/L",
        line=dict(color="#2f6fed", width=2),
        hovertemplate="<b>%{y:,.6f}</b><extra></extra>",
    )

    low, high = min(prices), max(prices)
    markers = [(spot, f"Spot {spot:,.6g}", "#8b949e")]

    if abs(target - spot) > (high - low) / 50:
        markers.append((target, f"Target {target:,.6g}", "#8b949e"))

    markers += [
        (level, f"B/E {level:,.6g}", "#e35d6a")
        for level in data.get("breakevens") or []
    ]
    markers = sorted(marker for marker in markers if low <= marker[0] <= high)

    for index, (price, text, color) in enumerate(markers):
        _mark(figure, price, text, color, 0.95 if index % 2 == 0 else 0.83)

    profit = float(data.get("expected_profit") or 0)
    cost = float(data.get("cost") or 0)
    coin = f" &nbsp;|&nbsp; settled in {settles}" if settles != quote else ""
    priced = (
        f"for {cost:,.0f} {quote}"
        if cost >= 0
        else f"for a {abs(cost):,.0f} {quote} credit"
    )
    listed = f" &nbsp;|&nbsp; {data['combo']}" if data.get("combo") else ""
    figure.set_title(
        f"{data.get('strategy', '')} {priced}"
        f"<br><span style='font-size:12px'>{data.get('legs', '')}{listed}"
        f" &nbsp;|&nbsp; expected {profit:+,.0f} {quote}"
        f" &nbsp;|&nbsp; spot {spot:,.6g}{coin}</span>",
        x=0.5,
        font=dict(size=15),
    )
    figure.update_layout(
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
            hoverformat=",.6g",
            autorange=False,
            range=[low, high],
        ),
        yaxis=dict(
            title=f"Profit and loss ({quote})",
            side="left",
            showgrid=True,
            zeroline=True,
            zerolinecolor=text_color,
            linecolor=text_color,
        ),
    )
    frame = DataFrame({"underlying_price": prices, "profit_or_loss": values})
    output: Any = OBBject(results=df_to_basemodel(frame))

    return finalize(output, figure, theme)
