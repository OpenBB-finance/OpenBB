# mypy: disable-error-code=arg-type

# IMPORTATION STANDARD
import logging
import os

# IMPORTATION THIRDPARTY
from copy import deepcopy
from typing import Optional, Union

import numpy as np
import pandas as pd
from scipy.spatial import Delaunay

# IMPORTATION INTERNAL
from openbb_terminal import OpenBBFigure
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.options import options_chains_model
from openbb_terminal.stocks.options.op_helpers import Options

logger = logging.getLogger(__name__)

# pylint: disable=C0302,R0913


@log_start_end(log=logger)
def display_surface(
    options: Options,
    option_type: str = "otm",
    dte_range: Optional[list[int]] = None,
    moneyness: Optional[float] = None,
    strike_range: Optional[list[float]] = None,
    oi: bool = False,
    volume: bool = False,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = "",
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
    """Chart the volatility as a 3-D surface.

    Parameters
    -----------
    options: Options
        The options data object.
    option_type: str
        The type of data to display. Default is "otm".
        Choices are: ["otm", "itm", "puts", "calls"]
    dte_range: list[int]
        Specify a min/max range of DTE to display.
    moneyness: float
        Specify a % moneyness to target for display.
    strike_range: list[float]
        Specify a min/max range of strike prices to display.
    oi: bool
        Filter for only options that have open interest. Default is False.
    volume: bool
        Filter for only options that have trading volume. Default is False.
    raw: bool
        Display the raw data instead of the chart.
    export: str
        Export dataframe data to csv,json,xlsx file.
    external_axes: bool
        Return the OpenBB Figure Object to a variable.

    Examples
    ----------
    >>> from openbb_terminal.stocks.options import options_chains_model, options_chains_view
    >>> spy = options_chains_model.load_options_chains("SPY")
    >>> options_chains_view.display_surface(spy)

    Display only calls:
    >>> options_chains_view.display_surface(spy, "calls")

    Display only puts:
    >>> options_chains_view.display_surface(spy, "puts")

    Display a range of expirations:
    >>> options_chains_view.display_surface(spy, dte_range=[7, 60])

    Filter for a range of strike prices and include only those with open interest and trading volume:
    >>> options_chains_view.display_surface(spy, strike_range=[400, 500], oi=True, volume=True)
    """

    if options_chains_model.validate_object(options, "object") is False:
        return None

    if options.hasIV is False:
        return console.print(
            "Options data object does not have Implied Volatility and is required for this function."
        )

    options = deepcopy(options)
    options.chains = options_chains_model.validate_object(options.chains, "chains")

    last_price = options.last_price  # noqa:F841

    calls = options.chains.query(
        "`optionType` == 'call' & `dte` >= 0 & `impliedVolatility` > 0"
    )
    puts = options.chains.query(
        "`optionType` == 'put' & `dte` >= 0 & `impliedVolatility` > 0"
    )

    if option_type not in ["otm", "itm", "puts", "calls"]:
        console.print("Invalid option type, defaulting to 'otm'.")
        option_type = "otm"

    if oi:
        calls = calls[calls["openInterest"] > 0]
        puts = puts[puts["openInterest"] > 0]

    if volume:
        calls = calls[calls["volume"] > 0]
        puts = puts[puts["volume"] > 0]

    if dte_range is not None:
        dte_range = [dte_range] if isinstance(dte_range, int) else dte_range  # type: ignore [list-item]
        if len(dte_range) > 1:
            far = (  # noqa:F841 pylint: disable=unused-variable
                dte_range[1] if dte_range[1] > dte_range[0] else dte_range[0]
            )
            near = (  # noqa:F841 pylint: disable=unused-variable
                dte_range[0] if dte_range[1] > dte_range[0] else dte_range[1]
            )
            calls = calls.query("@near <= `dte` <= @far")
            puts = puts.query("@near <= `dte` <= @far")

    if moneyness is not None and moneyness > 0:
        high = (  # noqa:F841 pylint: disable=unused-variable
            1 + (moneyness / 100)
        ) * last_price
        low = (  # noqa:F841 pylint: disable=unused-variable
            1 - (moneyness / 100)
        ) * last_price
        calls = calls.query("@low <= `strike` <= @high")
        puts = puts.query("@low <= `strike` <= @high")

    if strike_range is not None and len(strike_range) > 1:
        high = (  # noqa:F841 pylint: disable=unused-variable
            strike_range[1] if strike_range[1] > strike_range[0] else strike_range[0]
        )
        low = (  # noqa:F841 pylint: disable=unused-variable
            strike_range[0] if strike_range[1] > strike_range[0] else strike_range[1]
        )
        calls = calls.query("@low <= `strike` <= @high")
        puts = puts.query("@low <= `strike` <= @high")

    if option_type == "otm":
        otm_calls = calls.query("`strike` > @last_price").set_index(
            ["expiration", "strike", "optionType"]
        )
        otm_puts = puts.query("`strike` < @last_price").set_index(
            ["expiration", "strike", "optionType"]
        )
        data = pd.concat([otm_calls, otm_puts]).sort_index().reset_index()

    if option_type == "itm":
        itm_calls = calls.query("`strike` < @last_price").set_index(
            ["expiration", "strike", "optionType"]
        )
        itm_puts = puts.query("`strike` > @last_price").set_index(
            ["expiration", "strike", "optionType"]
        )
        data = pd.concat([itm_calls, itm_puts]).sort_index().reset_index()

    if option_type == "calls":
        data = calls
    if option_type == "puts":
        data = puts

    data = data[
        [
            "expiration",
            "strike",
            "optionType",
            "dte",
            "impliedVolatility",
            "openInterest",
            "volume",
        ]
    ]
    cols = ["Expiration", "Strike", "Type", "DTE", "IV", "OI", "Volume"]
    data.columns = cols

    label_dict = {"calls": "Call", "puts": "Put", "otm": "OTM", "itm": "ITM"}
    label = (
        label_dict[option_type] + " Options IV Surface"
        if not oi
        else label_dict[option_type] + " Options IV Surface With Open Interest"
    )
    label = label + " Excluding Untraded Contracts" if volume else label

    X = data["DTE"]
    Y = data["Strike"]
    Z = data["IV"]

    points3D = np.vstack((X, Y, Z)).T
    points2D = points3D[:, :2]
    tri = Delaunay(points2D)
    II, J, K = tri.simplices.T

    fig = OpenBBFigure()
    fig.set_title(f"{options.symbol} {label}")
    fig_kwargs = dict(z=Z, x=X, y=Y, i=II, j=J, k=K, intensity=Z)
    fig.add_mesh3d(
        **fig_kwargs,
        alphahull=0,
        opacity=1,
        contour=dict(color="black", show=True, width=15),
        colorscale=[
            [0, "darkred"],
            [0.001, "crimson"],
            [0.005, "red"],
            [0.0075, "orangered"],
            [0.015, "darkorange"],
            [0.025, "orange"],
            [0.04, "goldenrod"],
            [0.055, "gold"],
            [0.11, "magenta"],
            [0.15, "plum"],
            [0.4, "lightblue"],
            [0.7, "royalblue"],
            [0.9, "blue"],
            [1, "darkblue"],
        ],
        hovertemplate="<b>DTE</b>: %{x} <br><b>Strike</b>: %{y} <br><b>"
        + "IV"
        + "</b>: %{z}<extra></extra>",
        showscale=True,
        flatshading=True,
        lighting=dict(
            ambient=0.95,
            diffuse=0.9,
            roughness=0.8,
            specular=0.9,
            fresnel=0.001,
            vertexnormalsepsilon=0.0001,
            facenormalsepsilon=0.0001,
        ),
    )
    tick_kwargs = dict(tickfont=dict(size=12), titlefont=dict(size=14))
    fig.update_layout(
        scene=dict(
            xaxis=dict(title="DTE", autorange="reversed", **tick_kwargs),
            yaxis=dict(title="Strike", **tick_kwargs),
            zaxis=dict(title="IV", **tick_kwargs),
        ),
        title_x=0.5,
        scene_camera=dict(
            up=dict(x=0, y=0, z=0.75),
            center=dict(x=-0.01, y=0, z=-0.3),
            eye=dict(x=1.75, y=1.75, z=0.69),
        ),
    )
    fig.update_scenes(aspectmode="manual", aspectratio=dict(x=1.5, y=2.0, z=0.75))

    if raw:
        print_rich_table(
            data,
            title=label,
            show_index=False,
            export=bool(export),
        )
        return None

    if export and export != "":
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "surface",
            data,
            sheet_name,
            fig,
        )
        return None

    return fig.show(external=raw or external_axes)


@log_start_end(log=logger)
def display_stats(
    options: Options,
    by: str = "expiration",
    expiry: str = "",
    oi: Optional[bool] = False,
    percent: Optional[bool] = True,
    ratios: Optional[bool] = False,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = "",
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
    """Chart a variety of volume and open interest statistics.

    Parameters
    -----------
    options: Options
        The options data object.
    by: str
        Statistics can be displayed by either "expiration" or "strike". Default is "expiration".
    expiry: str
        The target expiration date to display. Only valid when `percent` is False.
    oi: bool
        Display open interest if True, else volume. Default is False.
    percent: bool
        Displays volume or open interest as a percentage of the total across all expirations. Default is False.
    ratios: bool
        Displays Put/Call ratios. This parameter overrides the others when True. Default is False.
    raw: bool
        Displays the raw data table instead of a chart.
    export: str
        Export the data to a csv,json,xlsx file.
    sheet_name: str
        Name of the sheet to save the data to. Only valid when `export` is a `xlsx` file.
    external_axes: bool
        Return the OpenBB Figure Object to a variable.

    Examples
    ----------
    >>> from openbb_terminal.sdk import openbb
    >>> from openbb_terminal.stocks.options import options_chains_model, options_chains_view
    >>> spy = options_chains_model.load_options_chains("SPY")

    Display volume by expiration:
    >>> options_chains_view.display_stats(spy)

    Display volume by strike:
    >>> options_chains_view.display_stats(spy, "strike")

    Display open interest by expiration:
    >>> options_chains_view.display_stats(spy, oi=True)

    Display open interest, by expiration, as a percentage of the total:
    >>> options_chains_view.display_stats(spy, oi=True, percent=True)

    Display volume and open interest put/call ratios:
    >>> options_chains_view.display_stats(spy, ratios=True)
    """

    by_type = ["expiration", "strike"]
    if by not in by_type:
        by = "expiration"

    if options_chains_model.validate_object(options, "object") is False:
        return None
    options = deepcopy(options)
    stats = options_chains_model.calculate_stats(options, by=by)

    if by == "strike" and expiry != "" and percent is False:
        expiry = options_chains_model.get_nearest_expiration(options, expiry)
        stats = options_chains_model.calculate_stats(
            options.chains[options.chains["expiration"] == expiry], "strike"
        )

    net_volume = stats.sum()["Total Volume"]
    net_oi = stats.sum()["Total OI"]

    stat_type = "Volume" if oi is False else "Open Interest"
    index_name = "Expiration" if by == "expiration" else "Strike"

    stats["Puts OI"] = stats["Puts OI"] * (-1)
    stats["Puts Volume"] = stats["Puts Volume"] * (-1)
    expiry = "" if oi is True and by == "expiration" else expiry
    title = (
        f"Percentage of Total {options.symbol} {stat_type}"
        if percent is True
        else f"{options.symbol} {stat_type}"
    )
    xtitle = (
        f"{index_name}s With {stat_type}  > 0.5% of Total {stat_type}"
        if percent is True
        else expiry
    )
    ytitle = f"% of Total {stat_type}" if percent is True else stat_type

    fig = OpenBBFigure()
    if ratios is False:
        if percent is True:
            stats["% of Total Volume"] = round(
                stats["Total Volume"] / net_volume * 100, 4
            )
            stats["% of Total OI"] = round(stats["Total OI"] / net_oi * 100, 4)
            stats_df = (
                stats.query("`% of Total Volume` > 0.5")
                if oi is False
                else stats.query("`% of Total OI` > 0.5")
            )
            fig.add_bar(
                x=stats_df.index,
                y=stats_df["% of Total Volume"]
                if oi is False
                else stats_df["% of Total OI"],
                name=f"% of Total {stat_type}",
                orientation="v",
            )
        if percent is False:
            fig.add_bar(
                x=stats.index,
                y=stats["Puts Volume"] if oi is False else stats["Puts OI"],
                name="Puts",
                orientation="v",
                marker=dict(color="red"),
            )
            fig.add_bar(
                x=stats.index,
                y=stats["Calls Volume"] if oi is False else stats["Calls OI"],
                name="Calls",
                orientation="v",
                marker=dict(color="blue"),
            )
        fig.update_layout(
            legend=dict(
                orientation="h",
                yanchor="top",
                y=1.125,
                xanchor="left",
                x=0.01,
            )
        )
    if ratios is True:
        title = f"{options.symbol} Ratios"
        ytitle = ""
        xtitle = ""
        if by != "expiration":
            by = "expiration"
        stats = options_chains_model.calculate_stats(options, by)
        fig.add_scatter(
            x=stats.index,
            y=stats["OI Ratio"].dropna(),
            mode="lines+markers",
            name="Put/Call OI Ratio",
            marker=dict(color="blue"),
        )
        fig.add_scatter(
            x=stats.index,
            y=stats["Vol-OI Ratio"].dropna(),
            mode="lines+markers",
            name="Volume/OI Ratio",
            marker=dict(color="red"),
        )
        fig.add_scatter(
            x=stats.index,
            y=stats["Volume Ratio"].dropna(),
            mode="lines+markers",
            name="Put/Call Volume Ratio",
            marker=dict(color="orange"),
        )

    fig.update_xaxes(type="category")
    fig.update_traces(width=0.98, selector=dict(type="bar"))
    fig.update_layout(
        title=dict(text=title, x=0.5, y=0.97),
        barmode="overlay",
        bargap=0,
        bargroupgap=0,
        yaxis=dict(
            title=dict(text=ytitle, font=dict(size=16)),
            ticklen=0,
            showgrid=True,
            tickfont=dict(size=14),
        ),
        xaxis=dict(
            title=dict(text=xtitle, font=dict(size=16)),
            showgrid=False,
            autorange=True,
            tickangle=90,
            tickfont=dict(size=11),
        ),
    )
    if raw:
        print_rich_table(
            stats,
            title=(
                f"{options.symbol} Stats"
                if expiry == "" or percent is True
                else f"{options.symbol} for {expiry} Expiration"
            ),
            show_index=True,
            index_name=index_name,
            floatfmt=".4f",
            export=bool(export),
        )
        return None

    if export and export != "":
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "stats",
            stats,
            sheet_name,
            fig,
        )
        return None

    return fig.show(external=raw or external_axes)


@log_start_end(log=logger)
def display_skew(
    options: Options,
    expirations: Optional[list[str]] = None,
    moneyness: Optional[float] = None,
    strike: Optional[float] = None,
    atm: Optional[bool] = False,
    otm_only: Optional[bool] = False,
    raw: Optional[bool] = False,
    export: Optional[str] = "",
    sheet_name: Optional[str] = "",
    external_axes: Optional[bool] = False,
) -> Union[None, OpenBBFigure]:
    """Chart the vertical skew of an option expiration, or the horizontal skew of equidistant % moneyness options.

    The vertical skew for each expiry and option is calculated by subtracting the IV of the ATM call or put.
    Returns only where the IV is greater than 0.

    Horizontal skew is returned if a value for moneyness, or a strike price, is supplied.
    With a strike price specified, both call and put IV skew are displayed. For moneyness,
    it is expressed as the difference between skews of two equidistant OTM strikes (the closest call and put).

    Parameters
    -----------
    options: Options
        The options data object.
    expirations: list[str]
        The expiration date, or a list of dates. The closest date will be returned for each entry.
        Format as YYYY-MM-DD.
    moneyness: float
        The % moneyess. When specified, this returns the forward skew curve at the target moneyness.
    strike: float
        A target strike price to observe the skew vs. contract. This argument overrides other parameters.
    atm: bool
        When true, returns the ATM skew curve. This will override other parameters, but is overridden by strike.
    otm_only: bool
        When true, returns only OTM portions of the put/call skew curves.
    raw: bool
        Returns a table instead of a plot.
    export: str
        Export the data to csv, json, xlsx file.
    sheet_name: str
        The name of the sheet to save the data to. Only valid when `export` is a `xlsx` file.
    external_axes: bool
        Returns the OpenBB Figure Object to a variable.
    """

    if options.hasIV is False:
        return console.print(
            "Options data object does not have Implied Volatility and is required for this function."
        )
    options = deepcopy(options)
    options.chains = options_chains_model.validate_object(options.chains, "chains")

    put_skew = pd.DataFrame()
    call_skew = pd.DataFrame()
    skew_df = pd.DataFrame()
    export_df = pd.DataFrame()
    colors = [
        "blue",
        "red",
        "burlywood",
        "orange",
        "green",
        "grey",
        "magenta",
        "cyan",
        "indigo",
        "yellowgreen",
    ]

    expirations = options.expirations[1] if expirations is None else expirations
    expirations = [expirations] if isinstance(expirations, str) else expirations  # type: ignore [list-item]
    if len(expirations) > 10 and otm_only is True:
        expirations = expirations[:10]  # type: ignore [index]
    elif len(expirations) > 5 and otm_only is False:
        expirations = expirations[:5]  # type: ignore [index]

    if moneyness is None:
        fig = OpenBBFigure()
        color = -1
        for expiration in expirations:  # type: ignore [union-attr]
            if expiration == "":
                expiration = options.expirations[1]  # noqa: PLW2901
            if expiration not in options.expirations:
                expiration = (  # noqa: PLW2901
                    options_chains_model.get_nearest_expiration(options, expiration)
                )
            color = color + 1
            skew = options_chains_model.calculate_skew(options, expiration, moneyness)[
                ["Expiration", "Strike", "Option Type", "IV", "ATM IV", "Skew"]
            ]
            if skew["IV"].sum() == 0 and len(expirations) == 1:
                return console.print("No IV data available for this expiration.")

            index_name = "Strike" if len(expirations) > 1 else expiration
            call_skew = skew.query("`Option Type` == 'call'").set_index("Strike")
            call_idx = call_skew.index
            call_skew = call_skew[~call_idx.duplicated(keep="first")]
            call_skew = call_skew["Skew"]
            put_skew = skew.query("`Option Type` == 'put'").set_index("Strike")
            put_idx = put_skew.index
            put_skew = put_skew[~put_idx.duplicated(keep="first")]
            put_skew = put_skew["Skew"]
            skew_df["Call Skew"] = call_skew
            skew_df["Put Skew"] = put_skew
            export_df = pd.concat([export_df, skew])
            if otm_only is True:
                calls = skew.query("`Option Type` == 'call'").reset_index()
                puts = skew.query("`Option Type` == 'put'").reset_index()
                put_idx = puts[puts["Skew"] == 0].index.values[0]
                call_idx = calls[calls["Skew"] == 0].index.values[0]
                call_skew = calls.iloc[call_idx - 1 : -1]
                call_skew = call_skew.set_index("Strike")["Skew"]
                call_idx = call_skew.index
                call_skew = call_skew[~call_idx.duplicated(keep="first")]
                put_skew = puts.iloc[0 : put_idx + 2]
                put_skew = put_skew.set_index("Strike")["Skew"]
                put_idx = put_skew.index
                put_skew = put_skew[~put_idx.duplicated(keep="first")]
                export_df = pd.concat([export_df, skew])
            fig.add_scatter(
                x=call_skew.index,
                y=call_skew.values,
                mode="lines+markers",
                name=f"{expiration} Calls" if len(expirations) > 1 else "Call IV Skew",
                marker_color=colors[color] if len(expirations) > 1 else "blue",
            )
            color = color + 1 if otm_only is False else color
            fig.add_scatter(
                x=put_skew.index,
                y=put_skew.values,
                mode="lines+markers",
                name=f"{expiration} Puts" if len(expirations) > 1 else "Put IV Skew",
                marker_color=colors[color] if len(expirations) > 1 else "red",
            )

        title = f"IV Skew for {options.symbol}"
        if otm_only is True:
            title = "OTM " + title
        fig.update_layout(title=title)

    if atm or moneyness or strike:
        if moneyness is None:
            moneyness = 0
        skew_df = options_chains_model.calculate_skew(options, moneyness=moneyness)
        skew = skew_df.copy()
        call_skew = skew_df["Call Skew"]
        put_skew = skew_df["Put Skew"]
        export_df = pd.concat([export_df, skew_df])
        title = (
            f"IV Skew for {options.symbol} at {moneyness}% OTM"
            if moneyness != 0 and atm is False
            else f"ATM IV Skew for {options.symbol}"
        )
        index_name = "Expiration"
        fig = OpenBBFigure()
        fig.add_scatter(
            x=skew_df.index,
            y=skew_df["IV Skew"],
            mode="lines+markers",
            name="OTM IV Skew",
            marker=dict(color="green"),
        )
        fig.update_xaxes(type="category")
        if atm:
            fig = OpenBBFigure()
            fig.add_scatter(
                x=skew_df.index,
                y=skew_df["ATM Skew"],
                mode="lines+markers",
                name="ATM IV Skew",
                marker=dict(color="green"),
            )
            fig.update_xaxes(type="category")
        if strike and strike > 0.25:
            fig = OpenBBFigure()
            strike = options_chains_model.get_nearest_call_strike(
                options, strike_price=strike
            )
            skew_df = options_chains_model.calculate_skew(options).query(
                "`Strike` == @strike"
            )
            call_df = skew_df.query("`Option Type` == 'call'").set_index("Expiration")
            call_idx = call_df.index
            call_df = call_df[~call_idx.duplicated(keep="first")]
            call_df = call_df.reset_index()
            put_df = skew_df.query("`Option Type` == 'put'").set_index("Expiration")
            put_idx = put_df.index
            put_df = put_df[~put_idx.duplicated(keep="first")]
            put_df = put_df.reset_index()
            title = f"IV Skew for {options.symbol} at ${strike}"
            expirations = skew_df.Expiration.unique().tolist()
            fig.add_scatter(
                x=expirations,
                y=call_df.Skew,
                mode="lines+markers",
                name="Call IV Skew",
                marker_color="blue",
            )
            fig.add_scatter(
                x=expirations,
                y=put_df.Skew,
                mode="lines+markers",
                name="Put IV Skew",
                marker_color="red",
            )
            fig.update_xaxes(type="category")

    fig.update_layout(
        title=dict(text=title, x=0.5, y=0.97),
        yaxis=dict(
            title=dict(
                text="IV Skew",
            ),
            ticklen=0,
        ),
        xaxis=dict(
            showgrid=False,
            autorange=True,
            title=dict(text=index_name),
        ),
        legend=dict(
            font=dict(size=12),
            orientation="v",
            yanchor="top",
            y=0.97,
            xanchor="center",
            x=0.525,
        ),
    )

    if raw:
        print_rich_table(
            export_df,
            title=title,
            show_index=True,
            index_name=index_name,
            floatfmt=".4f",
            export=bool(export),
        )
        return None

    if export and export != "":
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "skew",
            export_df,
            sheet_name,
            fig,
        )
        return None

    return fig.show(external=raw or external_axes)


@log_start_end(log=logger)
def display_volatility(
    options: Options,
    expirations: Optional[list[str]] = None,
    moneyness: Optional[float] = None,
    strike: Optional[float] = None,
    oi: bool = False,
    volume: bool = False,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = "",
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
    """Chart the implied volatility smile.

    Parameters
    -----------
    options: Options
        The options data object.
    expirations: list[str]
        Select up to five expiration(s) to display.  Overridden by moneyness or strike. Format as YYYY-MM-DD.
    moneyness: float
        Specify a target % moneyness to display vs. contract dates. This argument overrides expirations.
    strike: float
        Specify a target strike price to display vs. contract dates.
        Returned strike price is estimated as the closest one listed at approximately one year forward.
        This argument overrides moneyness and expirations.
    oi: bool
        Return only contracts with open interest. Only valid for IV vs. Strike charts. Default is False.
    volume: bool
        Return only contracts with trading volume. Only valid for IV vs. Strike charts. Default is False.
    raw: bool
        Display the raw data instead of the chart.
    export: str
        Export dataframe data to csv,json,xlsx file.
    external_axes: bool
        Return the OpenBB Figure Object to a variable.

    Examples
    ----------
    >>> from openbb_terminal.stocks.options import options_chains_model, options_chains_view
    >>> spy = options_chains_model.load_options_chains("SPY")
    >>> options_chains_view(spy)

    Plot IV @ Strike vs. contract dates:
    >>> options_chains_view(spy, strike=450)

    Plot IV @ % OTM vs. contract dates:
    >>> options_chains_view(spy, moneyness=20)

    Plot multiple expirations at once, and filter for only contracts with open interest:
    >>> options_chains_view(spy, expirations=["2024-12-30", "2025-12-30"], oi=True)
    """

    if options.hasIV is False:
        return console.print(
            "Options data object does not have Implied Volatility and is required for this function."
        )
    options = deepcopy(options)
    options.chains = options_chains_model.validate_object(options.chains, "chains")
    colors = [
        "blue",
        "red",
        "burlywood",
        "orange",
        "green",
        "grey",
        "magenta",
        "cyan",
        "indigo",
        "yellowgreen",
    ]

    index_name = ""
    title = f"{options.symbol} Volatility"
    export_df = pd.DataFrame()

    iv_df = options.chains[options.chains["impliedVolatility"] > 0][
        [
            "expiration",
            "strike",
            "optionType",
            "dte",
            "openInterest",
            "volume",
            "impliedVolatility",
        ]
    ]

    if moneyness is not None and strike is None:
        fig = OpenBBFigure()
        calls = pd.DataFrame()
        puts = pd.DataFrame()
        title = title + f" at {moneyness}% OTM" if strike is None else title
        strikes = options_chains_model.get_nearest_otm_strike(options, moneyness)
        if expirations is None:
            days = options.chains.dte.unique().tolist()
        for day in days:
            call_strike = options_chains_model.get_nearest_call_strike(
                options, day, strikes["call"]
            )
            call = (
                iv_df[iv_df["strike"] == call_strike]
                .query("`optionType` == 'call' & `dte` == @day")
                .set_index("expiration")
            )
            put_strike = options_chains_model.get_nearest_put_strike(
                options, day, strikes["put"]
            )
            put = (
                iv_df[iv_df["strike"] == put_strike]
                .query("`optionType` == 'put' & `dte` == @day")
                .set_index("expiration")
            )
            calls = pd.concat([calls, call])
            puts = pd.concat([puts, put])
        expirations = iv_df["expiration"].unique().tolist()
        export_df = pd.concat([export_df, calls, puts])
        fig.add_scatter(
            x=expirations,
            y=calls["impliedVolatility"],
            mode="lines+markers",
            name="Calls",
            marker_color="blue",
        )
        fig.add_scatter(
            x=expirations,
            y=puts["impliedVolatility"],
            mode="lines+markers",
            name="Puts",
            marker_color="red",
        )
        fig.update_xaxes(type="category")

    if moneyness is None and strike is None:
        expirations = options.expirations[1] if expirations is None else expirations

    if expirations is not None and moneyness is None:
        fig = OpenBBFigure()
        color = -1
        expirations = [expirations] if isinstance(expirations, str) else expirations  # type: ignore [list-item]
        if len(expirations) > 5:
            expirations = expirations[:5]
        if oi is True:
            iv_df = iv_df[iv_df["openInterest"] > 0]
        if volume is True:
            iv_df = iv_df[iv_df["volume"] > 0]
        for expiration in expirations:
            expiration = options_chains_model.get_nearest_expiration(  # noqa: PLW2901
                options, expiration
            )
            data = iv_df[iv_df["expiration"] == expiration]
            calls = data[data["optionType"] == "call"]
            puts = data[data["optionType"] == "put"]
            color = color + 1
            fig.add_scatter(
                x=calls["strike"].unique().tolist(),
                y=calls["impliedVolatility"],
                mode="lines+markers",
                name="Calls" if len(expirations) <= 1 else f"Calls at {expiration}",
                marker_color=colors[color] if len(expirations) > 1 else "blue",
            )
            color = color + 1
            fig.add_scatter(
                x=puts["strike"].unique().tolist(),
                y=puts["impliedVolatility"],
                mode="lines+markers",
                name="Puts" if len(expirations) <= 1 else f"Puts at {expiration}",
                marker_color=colors[color] if len(expirations) > 1 else "red",
            )
            export_df = pd.concat([export_df, data])
        index_name = expiration if len(expirations) <= 1 else ""
        title = title + " With Open Interest" if oi and not strike else title
        title = (
            title + " Excluding Untraded Contracts" if volume and not strike else title
        )

    if strike is not None:
        fig = OpenBBFigure()
        strike = (
            options_chains_model.get_nearest_call_strike(
                options, 300, strike_price=strike
            )
            if strike > options.last_price
            else options_chains_model.get_nearest_put_strike(
                options, 300, strike_price=strike
            )
        )
        title = title + f" at ${strike}"
        calls = iv_df[iv_df["strike"] == strike].query("`optionType` == 'call'")
        puts = iv_df[iv_df["strike"] == strike].query("`optionType` == 'put'")
        expirations = iv_df["expiration"].unique().tolist()
        export_df = pd.concat([export_df, calls, puts])
        fig.add_scatter(
            x=expirations,
            y=calls["impliedVolatility"],
            mode="lines+markers",
            name="Calls",
            marker_color="blue",
        )
        fig.add_scatter(
            x=expirations,
            y=puts["impliedVolatility"],
            mode="lines+markers",
            name="Puts",
            marker_color="red",
        )
        fig.update_xaxes(type="category")

    fig.update_layout(
        title=dict(text=title, x=0.5, y=0.97),
        yaxis=dict(
            title=dict(
                text="IV",
            ),
            ticklen=0,
        ),
        xaxis=dict(
            showgrid=False,
            autorange=True,
            title=dict(text=index_name),
        ),
        legend=dict(
            font=dict(size=12),
            orientation="v",
            yanchor="top",
            y=0.97,
            xanchor="center",
            x=0.525,
        ),
    )

    if raw:
        print_rich_table(
            export_df,
            title=title,
            show_index=False,
            floatfmt=".4f",
            export=bool(export),
        )
        return None

    if export and export != "":
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "volatility",
            export_df,
            sheet_name,
            fig,
        )
        return None

    return fig.show(external=raw or external_axes)
