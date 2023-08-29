"""Yfinance options view"""
__docformat__ = "numpy"

import logging
import os
import re
from typing import Any, Dict, List, Optional, Union

import numpy as np
from scipy.spatial import Delaunay
from scipy.stats import binom

from openbb_terminal import OpenBBFigure, theme
from openbb_terminal.core.plots.config.openbb_styles import (
    PLT_3DMESH_COLORSCALE,
    PLT_3DMESH_SCENE,
)
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    print_rich_table,
)
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.options import op_helpers, yfinance_model
from openbb_terminal.stocks.options.yfinance_model import (
    generate_data,
    get_option_chain,
    get_price,
)

# pylint: disable=C0302, R0913, too-many-arguments


logger = logging.getLogger(__name__)


def header_fmt(header: str) -> str:
    """
    Formats strings to appear as titles

    Parameters
    ----------
    header: str
        The string to be formatted

    Returns
    -------
    new_header: str
        The clean string to use as a header
    """

    words = re.findall("[A-Z][^A-Z]*", header)
    if words == []:
        words = [header]
    new_header = " ".join(words)
    new_header = new_header.replace("_", " ")
    return new_header.title()


@log_start_end(log=logger)
def plot_plot(
    symbol: str,
    expiry: str,
    put: bool = False,
    x: str = "s",
    y: str = "iv",
    custom: str = "",
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Generate a graph custom graph based on user input

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    expiry: str
        Option expiration
    x: str
        variable to display in x axis, choose from:
        ltd, s, lp, b, a, c, pc, v, oi, iv
    y: str
        variable to display in y axis, choose from:
        ltd, s, lp, b, a, c, pc, v, oi, iv
    custom: str
        type of plot
    put: bool
        put option instead of call
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        type of data to export
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    is_smile = custom == "smile"
    convert = {
        "ltd": "lastTradeDate",
        "s": "strike",
        "lp": "lastPrice",
        "b": "bid",
        "a": "ask",
        "c": "change",
        "pc": "percentChange",
        "v": "volume",
        "oi": "openInterest",
        "iv": "impliedVolatility",
    }

    if is_smile:
        x = "strike"
        y = "impliedVolatility"
    else:
        if x is None:
            return console.print("[red]Invalid option sent for x-axis[/red]\n")
        if y is None:
            return console.print("[red]Invalid option sent for y-axis[/red]\n")
        if x in convert:
            x = convert[x]
        else:
            x = "strike"
            console.print(
                f"[red]'{x}' is not a valid option. Defaulting to `strike`.[/red]\n"
            )
        if y in convert:
            y = convert[y]
        else:
            y = "impliedVolatility"
            console.print(
                f"[red]'{y}' is not a valid option. Defaulting to `impliedVolatility`.[/red]\n"
            )

    chain = yfinance_model.get_option_chain(symbol, expiry)

    fig = OpenBBFigure()
    if not is_smile:
        varis = op_helpers.opt_chain_cols
        values = chain.puts if put else chain.calls

        x_data = values[x]
        y_data = values[y]

        option = "puts" if put else "calls"
        title = f"{varis[y]['label']} vs. {varis[x]['label']} for {symbol} {option} on {expiry}"
        xaxis_title = varis[x]["label"]
        yaxis_title = varis[y]["label"]

        fig.add_scatter(x=x_data, y=y_data, mode="lines+markers")
    else:
        calls = chain.calls[chain.calls["impliedVolatility"] > 0.00002].dropna()
        puts = chain.puts[chain.puts["impliedVolatility"] > 0.00002].dropna()

        for data, name in zip([calls, puts], ["Calls", "Puts"]):
            fig.add_scatter(
                x=data["strike"],
                y=data["impliedVolatility"],
                mode="lines+markers",
                name=name,
                line_color=theme.up_color if name == "Calls" else theme.down_color,
            )

        title = f"Implied Volatility Smile for {symbol} on {expiry}"
        xaxis_title = "Strike"
        yaxis_title = "Implied Volatility"

    fig.set_title(title)
    fig.set_xaxis_title(xaxis_title)
    fig.set_yaxis_title(yaxis_title)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "plot",
        sheet_name=sheet_name,
        figure=fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def plot_payoff(
    current_price: float,
    options: List[Dict[Any, Any]],
    underlying: float,
    symbol: str,
    expiry: str,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Generate a graph showing the option payoff diagram"""
    x, yb, ya = generate_data(current_price, options, underlying)

    plot = OpenBBFigure(
        title=f"Option Payoff Diagram for {symbol} on {expiry}",
        xaxis=dict(tickformat="${x:.2f}", title="Underlying Asset Price at Expiration"),
        yaxis=dict(tickformat="${x:.2f}", title="Profit"),
    )
    plot.add_scatter(x=x, y=yb, name="Payoff Before Premium")
    if ya:
        plot.add_scatter(x=x, y=ya, name="Payoff After Premium")
    else:
        plot.data[0].name = "Payoff"

    return plot.show(external=external_axes)


@log_start_end(log=logger)
def plot_expected_prices(
    und_vals: List[List[float]],
    p: float,
    symbol: str,
    expiry: str,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plot expected prices of the underlying asset at expiration

    Parameters
    ----------
    und_vals : List[List[float]]
        The expected underlying values at the expiration date
    p : float
        The probability of the stock price moving upward each round
    symbol : str
        The ticker symbol of the option's underlying asset
    expiry : str
        The expiration for the option
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    up_moves = list(range(len(und_vals[-1])))
    up_moves.reverse()
    probs = [100 * binom.pmf(r, len(up_moves), p) for r in up_moves]

    fig = OpenBBFigure()

    fig.add_scatter(
        x=und_vals[-1],
        y=probs,
        mode="lines",
        name="Probabilities",
    )

    fig.update_layout(
        title=f"Probabilities for ending prices of {symbol} on {expiry}",
        xaxis_title="Price",
        yaxis_title="Probability",
        xaxis_tickformat="$,.2f",
        yaxis_tickformat=".0%",
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_vol_surface(
    symbol: str,
    export: str = "",
    sheet_name: Optional[str] = None,
    z: str = "IV",
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Display vol surface

    Parameters
    ----------
    symbol : str
        Ticker symbol to get surface for
    export : str
        Format to export data
    z : str
        The variable for the Z axis
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    data = yfinance_model.get_iv_surface(symbol)
    z = z.upper()

    if data.empty:
        return console.print(f"No options data found for {symbol}.\n")

    z_dict = {
        "IV": (data.impliedVolatility, "Volatility"),
        "OI": (data.openInterest, "Open Interest"),
        "LP": (data.lastPrice, "Last Price"),
    }
    label = z_dict[z][1]

    if z not in z_dict:
        return console.print(
            f"Invalid z value: {z}.\n Valid values are: IV, OI, LP. (case insensitive)\n"
        )

    X = data.dte
    Y = data.strike
    Z = z_dict[z][0]

    points3D = np.vstack((X, Y, Z)).T
    points2D = points3D[:, :2]
    tri = Delaunay(points2D)
    II, J, K = tri.simplices.T

    fig = OpenBBFigure()
    fig.set_title(f"{label} Surface for {symbol.upper()}")

    fig_kwargs = dict(z=Z, x=X, y=Y, i=II, j=J, k=K, intensity=Z)
    fig.add_mesh3d(
        **fig_kwargs,
        colorscale=PLT_3DMESH_COLORSCALE,
        hovertemplate="<b>DTE</b>: %{y} <br><b>Strike</b>: %{x} <br><b>"
        + z_dict[z][1]
        + "</b>: %{z}<extra></extra>",
        showscale=False,
        flatshading=True,
        lighting=dict(
            ambient=0.5, diffuse=0.5, roughness=0.5, specular=0.4, fresnel=0.4
        ),
    )

    tick_kwargs = dict(tickfont=dict(size=13), titlefont=dict(size=16))
    fig.update_layout(
        scene=dict(
            xaxis=dict(title="DTE", **tick_kwargs),
            yaxis=dict(title="Strike", **tick_kwargs),
            zaxis=dict(title=z, **tick_kwargs),
        )
    )
    fig.update_layout(
        margin=dict(l=5, r=10, t=40, b=20),
        title_x=0.5,
        scene_camera=dict(
            up=dict(x=0, y=0, z=2),
            center=dict(x=0, y=0, z=-0.3),
            eye=dict(x=1.25, y=1.25, z=0.69),
        ),
        scene=PLT_3DMESH_SCENE,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "vsurf",
        data,
        sheet_name,
        fig,
        margin=False,
    )

    return fig.show(external=external_axes, margin=False)


@log_start_end(log=logger)
def show_greeks(
    symbol: str,
    expiry: str,
    div_cont: float = 0,
    rf: Optional[float] = None,
    opt_type: int = 1,
    mini: float = -1,
    maxi: float = -1,
    show_all: bool = False,
) -> None:
    """
    Shows the greeks for a given option

    Parameters
    ----------
    symbol: str
        The ticker symbol value of the option
    div_cont: float
        The dividend continuous rate
    expiry: str
        The date of expiration, format "YYYY-MM-DD", i.e. 2010-12-31.
    rf: float
        The risk-free rate
    opt_type: Union[1, -1]
        The option type 1 is for call and -1 is for put
    mini: float
        The minimum strike price to include in the table
    maxi: float
        The maximum strike price to include in the table
    show_all: bool
        Whether to show all greeks
    """

    current_price = get_price(symbol)
    chain = get_option_chain(symbol, expiry)

    min_strike, max_strike = op_helpers.get_strikes(
        min_sp=mini, max_sp=maxi, chain=chain.puts
    )

    for option in ["calls", "puts"]:
        attr = getattr(chain, option)
        attr = attr[attr["strike"] >= min_strike]
        attr = attr[attr["strike"] <= max_strike]

    chain.puts["optionType"] = "put"
    chain.calls["optionType"] = "call"

    df = op_helpers.get_greeks(
        current_price=current_price,
        expire=expiry,
        calls=chain.calls,
        puts=chain.puts,
        div_cont=div_cont,
        rf=rf,
        opt_type=opt_type,
        show_extra_greeks=show_all,
    )

    column_formatting = [".1f", ".4f"] + [".6f"] * 4

    if show_all:
        additional_columns = ["Rho", "Phi", "Charm", "Vanna", "Vomma"]
        column_formatting += [".6f"] * len(additional_columns)

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title=f"{symbol} Greeks",
        floatfmt=column_formatting,
    )
