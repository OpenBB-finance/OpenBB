"""The volatility or greek surface of a Deribit underlying."""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from openbb_core.app.model.obbject import OBBject

SURFACES = {
    "implied_volatility": "Implied volatility (%)",
    "delta": "Delta",
    "gamma": "Gamma",
    "theta": "Theta",
    "vega": "Vega",
    "rho": "Rho",
}


def surface_rows(
    frame, spot: float, measure: str, moneyness: float, dte_min: int, dte_max: int
) -> list:
    """Return one record per contract inside the window being drawn.

    Parameters
    ----------
    frame : DataFrame
        The chain.
    spot : float
        The current price of the underlying.
    measure : str
        The column to raise into the third dimension.
    moneyness : float
        How far either side of spot to keep, as a share of it.
    dte_min : int
        The nearest expiration to keep, in days.
    dte_max : int
        The furthest expiration to keep, in days.

    Returns
    -------
    list
        One record per surviving contract.
    """
    inside = frame[
        frame[measure].notna()
        & (frame["dte"] >= dte_min)
        & (frame["dte"] <= dte_max)
        & (frame["strike"] >= spot * (1 - moneyness))
        & (frame["strike"] <= spot * (1 + moneyness))
    ]
    inside = inside[
        ((inside["option_type"] == "call") & (inside["strike"] >= spot))
        | ((inside["option_type"] == "put") & (inside["strike"] < spot))
    ]

    return [
        {
            "expiration": row["expiration"],
            "dte": int(row["dte"] or 0),
            "strike": float(row["strike"]),
            "moneyness": float(row["strike"]) / spot - 1 if spot else None,
            "option_type": row["option_type"],
            measure: float(row[measure]),
        }
        for _, row in inside.sort_values(["dte", "strike"]).iterrows()
    ]


def create_surface(data: dict, theme: str = "dark", **kwargs) -> "OBBject":
    """Draw a measure over time to expiration and strike."""
    from openbb_core.app.model.obbject import OBBject
    from openbb_core.app.utils import df_to_basemodel
    from pandas import DataFrame

    from openbb_deribit import CHARTING_INSTALLED
    from openbb_deribit.utils.options.theme import finalize

    measure = data.get("measure", "implied_volatility")
    label = SURFACES.get(measure, measure)
    frame = DataFrame(data["rows"])
    output: Any = OBBject(results=df_to_basemodel(frame))

    if not CHARTING_INSTALLED or frame.empty:
        return output

    from openbb_charting.charts.generic_charts import surface3d

    figure = surface3d(
        X=frame["dte"],
        Y=frame["strike"],
        Z=frame[measure],
        xtitle="DTE",
        ytitle="Strike",
        ztitle=label,
        title=f"{data.get('symbol', '')} {label} surface",
        theme="light" if theme == "light" else "dark",
    )
    text_color = "white" if theme == "dark" else "black"
    scene_axis = dict(
        color=text_color,
        gridcolor="rgba(255,255,255,0.15)" if theme == "dark" else "rgba(0,0,0,0.15)",
        backgroundcolor="rgba(255,255,255,0.04)"
        if theme == "dark"
        else "rgba(0,0,0,0.04)",
    )
    figure.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=text_color),
        title=dict(font=dict(color=text_color)),
        scene=dict(xaxis=scene_axis, yaxis=scene_axis, zaxis=scene_axis),
    )

    return finalize(output, figure, theme)
