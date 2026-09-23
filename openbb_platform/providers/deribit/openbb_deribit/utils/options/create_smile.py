"""The volatility smile of a Deribit expiration."""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from openbb_core.app.model.obbject import OBBject

COLORS = [
    "#2f6fed",
    "#d29922",
    "#3fb950",
    "#e35d6a",
    "#a371f7",
    "#1f9cb3",
    "#f0883e",
    "#db61a2",
]

MAX_LINES = 8


def chosen_expirations(frame, asked: "str | None") -> list:
    """Return the expirations to draw.

    A chain lists eleven expirations and drawing them all makes a thicket no
    reader can follow, so one is drawn unless more are asked for by name. The
    one drawn by default is the nearest that still has a day to run: the one
    expiring within hours is quoted, but its smile is the last hours of a
    contract rather than the shape of the market.

    Parameters
    ----------
    frame : DataFrame
        The chain.
    asked : str or None
        The expirations asked for, comma separated. None draws the default.

    Returns
    -------
    list
        The expirations to draw, nearest first.
    """
    from openbb_deribit.utils.options.chain import expirations

    listed = expirations(frame)
    live = [
        day
        for day in listed
        if int(frame[frame["expiration"] == day]["dte"].max() or 0) > 0
    ]
    default = (live or listed)[:1]

    if not asked:
        return default

    wanted = {part.strip() for part in str(asked).split(",") if part.strip()}
    picked = [day for day in listed if str(day) in wanted]

    return (picked or default)[:MAX_LINES]


def smile_rows(frame, spot: float, otm: bool, moneyness: float = 0.25) -> list:
    """Return the quoted volatility of each strike, by expiration.

    Far out of the money the exchange stops publishing a distinct volatility
    and pins whole runs of strikes to one clamped value -- 107.96 across every
    BTC strike from 39% to 120% above spot on one read. Those are not market
    observations, and drawing them puts a flat shelf on the smile and stretches
    the axis past where anything trades, so the strikes drawn are held to a
    band either side of spot.

    Parameters
    ----------
    frame : DataFrame
        The chain.
    spot : float
        The current price of the underlying.
    otm : bool
        When True, keeps only the out-of-the-money side of each strike, which
        is the side that carries the liquidity.
    moneyness : float
        How far either side of spot to keep, as a share of it.

    Returns
    -------
    list
        One record per contract that published a volatility.
    """
    quoted = frame[frame["implied_volatility"].notna()]
    quoted = quoted[quoted["implied_volatility"] > 0]

    if spot and moneyness:
        quoted = quoted[
            (quoted["strike"] >= spot * (1 - moneyness))
            & (quoted["strike"] <= spot * (1 + moneyness))
        ]

    if otm:
        quoted = quoted[
            ((quoted["option_type"] == "call") & (quoted["strike"] >= spot))
            | ((quoted["option_type"] == "put") & (quoted["strike"] < spot))
        ]

    return [
        {
            "expiration": row["expiration"],
            "dte": int(row["dte"] or 0),
            "strike": float(row["strike"]),
            "moneyness": float(row["strike"]) / spot - 1 if spot else None,
            "option_type": row["option_type"],
            "implied_volatility": float(row["implied_volatility"]),
            "open_interest": row["open_interest"],
            "volume": row["volume"],
        }
        for _, row in quoted.sort_values(["expiration", "strike"]).iterrows()
    ]


def create_smile(data: dict, theme: str = "dark", **kwargs) -> "OBBject":
    """Draw implied volatility against strike, one line per expiration.

    Parameters
    ----------
    data : dict
        The rows to draw, the spot price, and the underlying's name.
    theme : str
        Either 'dark' or 'light'.

    Returns
    -------
    OBBject
        The figure, with the plotted rows as its results.
    """
    from openbb_core.app.model.obbject import OBBject
    from openbb_core.app.utils import df_to_basemodel
    from pandas import DataFrame

    from openbb_deribit.utils.options.theme import finalize, new_figure

    rows = data["rows"]
    spot = float(data.get("spot") or 0)
    frame = DataFrame(rows)
    figure, text_color, background = new_figure(theme)
    drawn = sorted(frame["expiration"].unique())

    for index, expiration in enumerate(drawn):
        at = frame[frame["expiration"] == expiration].sort_values("strike")
        figure.add_scatter(
            x=at["strike"],
            y=at["implied_volatility"],
            mode="lines+markers",
            name=f"{expiration}  ({int(at['dte'].iloc[0])}d)",
            line=dict(color=COLORS[index % len(COLORS)], width=2),
            marker=dict(size=4),
            hovertemplate="%{x:,.0f}<b> %{y:.2f}%</b><extra></extra>",
        )

    figure.add_vline(
        x=spot,
        line_width=1,
        line_dash="dash",
        line_color="#8b949e",
        annotation_text=f"Spot {spot:,.6g}",
        annotation_font=dict(size=10, color="#8b949e"),
    )
    figure.set_title(
        f"{data.get('symbol', '')} implied volatility by strike",
        x=0.5,
        font=dict(size=15),
    )
    figure.update_layout(
        paper_bgcolor=background,
        plot_bgcolor=background,
        font=dict(color=text_color),
        margin=dict(l=10, r=132, t=56, b=10),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.01,
            font=dict(size=10),
            bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(
            title="Strike",
            showgrid=False,
            linecolor=text_color,
            hoverformat=",.6g",
        ),
        yaxis=dict(
            title="Implied volatility (%)",
            side="left",
            showgrid=True,
            linecolor=text_color,
        ),
    )
    output: Any = OBBject(results=df_to_basemodel(frame))

    return finalize(output, figure, theme)
