"""The volatility term structure of a Deribit underlying."""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from openbb_core.app.model.obbject import OBBject


def term_rows(frame, spot: float) -> list:
    """Return the at-the-money volatility of every expiration.

    The strike nearest the underlying carries the volatility the market quotes
    for that expiration, averaged across the call and the put so neither side's
    skew dominates.

    An expiration already inside its last day is left out. Its reading is real
    but it sits at zero on a time axis, where it draws as a vertical drop that
    compresses the term the chart exists to show.
    """
    rows: list = []

    for expiration in sorted(frame["expiration"].dropna().unique()):
        at = frame[
            (frame["expiration"] == expiration)
            & (frame["dte"] > 0)
            & frame["implied_volatility"].notna()
            & (frame["implied_volatility"] > 0)
        ]

        if at.empty:
            continue

        strike = float(at.iloc[(at["strike"] - spot).abs().argmin()]["strike"])
        pair = at[at["strike"] == strike]
        rows.append(
            {
                "expiration": expiration,
                "dte": int(pair.iloc[0]["dte"] or 0),
                "strike": strike,
                "underlying_price": spot,
                "implied_volatility": float(pair["implied_volatility"].mean()),
                "open_interest": float(pair["open_interest"].fillna(0).sum()),
                "volume": float(pair["volume"].fillna(0).sum()),
            }
        )

    return rows


def create_term_structure(data: dict, theme: str = "dark", **kwargs) -> "OBBject":
    """Draw at-the-money implied volatility against time to expiration."""
    from openbb_core.app.model.obbject import OBBject
    from openbb_core.app.utils import df_to_basemodel
    from pandas import DataFrame

    from openbb_deribit.utils.options.theme import finalize, new_figure

    frame = DataFrame(data["rows"])
    figure, text_color, background = new_figure(theme)

    figure.add_scatter(
        x=frame["dte"],
        y=frame["implied_volatility"],
        mode="lines+markers",
        name="ATM IV",
        line=dict(color="#2f6fed", width=2),
        marker=dict(size=7),
        customdata=frame["expiration"].astype(str),
        hovertemplate="%{customdata} (%{x}d)<b> %{y:.2f}%</b><extra></extra>",
    )
    figure.set_title(
        f"{data.get('symbol', '')} at-the-money volatility term structure",
        x=0.5,
        font=dict(size=15),
    )
    figure.update_layout(
        paper_bgcolor=background,
        plot_bgcolor=background,
        font=dict(color=text_color),
        margin=dict(l=10, r=10, t=60, b=10),
        showlegend=False,
        xaxis=dict(title="Days to expiration", showgrid=False, linecolor=text_color),
        yaxis=dict(
            title="Implied volatility (%)",
            side="left",
            showgrid=True,
            linecolor=text_color,
        ),
    )
    output: Any = OBBject(results=df_to_basemodel(frame))

    return finalize(output, figure, theme)
