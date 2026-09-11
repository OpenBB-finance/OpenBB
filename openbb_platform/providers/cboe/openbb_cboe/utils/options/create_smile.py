"""Cboe implied-volatility smile and skew chart."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from openbb_core.app.model.obbject import OBBject
    from openbb_core.provider.standard_models.options_chains import OptionsChainsData

MAX_EXPIRATIONS = 5

COLORS = [
    "royalblue",
    "red",
    "orange",
    "green",
    "grey",
    "burlywood",
    "magenta",
    "cyan",
    "indigo",
    "yellowgreen",
]


def _first_priced_expiration(data: OptionsChainsData) -> str:
    """Return the front expiration that still carries non-zero implied volatility.

    Parameters
    ----------
    data : OptionsChainsData
        The loaded Cboe options chain.

    Returns
    -------
    str
        The earliest expiration with usable implied volatility.
    """
    df = data.dataframe
    priced = df[df["implied_volatility"] > 0]

    if priced.empty:
        from openbb_cboe.utils.options.data_handler import chain_expirations

        expirations = chain_expirations(data)

        return expirations[0] if expirations else data.expirations[0]

    return sorted(priced["expiration"].astype(str).unique())[0]


def create_smile(
    data: OptionsChainsData,
    expirations: str | None = None,
    otm: bool = False,
    skew: bool = False,
    **kwargs,
) -> OBBject:
    """Build the IV smile/skew across strikes for up to five expirations.

    Parameters
    ----------
    data : OptionsChainsData
        The loaded Cboe options chain.
    expirations : str | None
        Up to five comma-separated expiration dates. Defaults to the front expiry.
    otm : bool
        When True, restrict each curve to out-of-the-money contracts.
    skew : bool
        When True, plot the skew relative to ATM instead of raw implied volatility.

    Returns
    -------
    OBBject
        The plotted rows, with the Plotly figure attached to ``chart``.

    Raises
    ------
    OpenBBError
        If the chain carries no implied volatility, or more than five expirations
        were requested.
    """
    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_core.app.model.obbject import OBBject
    from openbb_core.app.utils import df_to_basemodel
    from pandas import DataFrame, concat, to_datetime

    from openbb_cboe.utils.options.theme import finalize, new_figure

    if data.has_iv is False:
        raise OpenBBError(
            "Implied Volatility was not found in the data and is required here."
        )

    exp_list = (
        expirations.split(",")
        if isinstance(expirations, str)
        else expirations
        if isinstance(expirations, list)
        else [_first_priced_expiration(data)]
    )
    exp_list = [data._get_nearest_expiration(e) for e in exp_list]

    if len(exp_list) > MAX_EXPIRATIONS:
        raise OpenBBError("Too many dates! Up to five can be selected.")

    df = concat(
        [data.skew(date=cast(str, to_datetime(exp).date())) for exp in exp_list]
    )
    output_df = DataFrame()
    symbol = data.underlying_symbol[0]
    index_name = exp_list[0] if len(exp_list) <= 1 else None
    target_col = "Skew" if skew is True else "IV"
    title = (
        f"{symbol} {'OTM ' if otm is True else ''}"
        f"{'IV Skew' if skew is True else 'Implied Volatility'}"
    )
    theme = kwargs.get("theme") or "dark"
    fig, text_color, background = new_figure(theme)
    color = -1

    for expiration in exp_list:
        calls = (
            df.query("`Expiration` == @expiration & `Option Type` == 'call'")
            .copy()
            .reset_index(drop=True)
        )
        puts = (
            df.query("`Expiration` == @expiration & `Option Type` == 'put'")
            .copy()
            .reset_index(drop=True)
        )

        if otm is True:
            put_idx = puts[puts["Skew"] == 0].index.values[0]
            call_idx = calls[calls["Skew"] == 0].index.values[0]
            puts = puts.iloc[0 : put_idx + 1].reset_index(drop=True)
            calls = calls.iloc[call_idx:-1].reset_index(drop=True)

        output_df = (
            concat([output_df, calls, puts], axis=0)
            if not output_df.empty
            else concat([calls, puts], axis=0)
        )
        color = color + 1
        fig.add_scatter(
            x=calls["Strike"].unique().tolist(),
            y=calls[target_col],
            mode="lines+markers",
            name="Calls" if len(exp_list) <= 1 else f"Calls at {expiration}",
            marker_color=COLORS[color],
            hoverinfo="x+y+name",
        )
        color = color + 1
        fig.add_scatter(
            x=puts["Strike"].unique().tolist(),
            y=puts[target_col],
            mode="lines+markers",
            name="Puts" if len(exp_list) <= 1 else f"Puts at {expiration}",
            marker_color=COLORS[color],
            hoverinfo="x+y+name",
        )

    fig.update_layout(
        title=dict(text=title, x=0.5, font=dict(size=18)),
        yaxis=dict(
            ticklen=0,
            showline=False,
            linecolor=text_color,
            tickfont=dict(size=14),
            nticks=7,
        ),
        xaxis=dict(
            showgrid=False,
            autorange=True,
            ticklen=5,
            showline=False,
            linecolor=text_color,
            title=dict(text=index_name if index_name else "", font=dict(size=16)),
            tickfont=dict(size=16),
            nticks=7,
            showspikes=False,
            tickprefix="$",
        ),
        legend=dict(
            font=dict(size=14),
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="center",
            x=0.5,
            itemdoubleclick="toggleothers",
        ),
        font=dict(color=text_color),
        paper_bgcolor=background,
        plot_bgcolor=background,
        hoverdistance=1,
        hovermode="x unified",
        dragmode="pan",
    )
    output_df = (
        output_df.set_index(["Expiration", "Strike", "Option Type"])
        .sort_index()
        .reset_index()
    )
    output: Any = OBBject(results=df_to_basemodel(output_df))

    return finalize(output, fig, theme)
