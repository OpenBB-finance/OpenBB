"""Tradier options view"""
__docformat__ = "numpy"

import argparse
import os
from bisect import bisect_left
from typing import List

import matplotlib.pyplot as plt
import mplfinance as mpf
import numpy as np
import pandas as pd
import seaborn as sns
from colorama import Fore, Style
from tabulate import tabulate

from gamestonk_terminal import config_plot as cfp
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    export_data,
    patch_pandas_text_adjustment,
    plot_autoscale,
)
from gamestonk_terminal.stocks.options import op_helpers, tradier_model

column_map = {"mid_iv": "iv", "open_interest": "oi", "volume": "vol"}


def red_highlight(val) -> str:
    """Red highlight

    Parameters
    ----------
    val
        dataframe values to color

    Returns
    ----------
    str
        colored dataframes values
    """
    return f"{Fore.RED}{val}{Style.RESET_ALL}"


def green_highlight(val) -> str:
    """Green highlight

    Parameters
    ----------
    values : List[str]
        dataframe values to color

    Returns
    ----------
    List[str]
        colored dataframes values
    """
    return f"{Fore.GREEN}{val}{Style.RESET_ALL}"


def check_valid_option_chains_headers(headers: str) -> List[str]:
    """Check valid option chains headers

    Parameters
    ----------
    headers : str
        Option chains headers

    Returns
    ----------
    List[str]
        List of columns string
    """
    columns = [str(item) for item in headers.split(",")]

    for header in columns:
        if header not in tradier_model.df_columns:
            raise argparse.ArgumentTypeError("Invalid option chains header selected!")

    return columns


def display_chains(
    ticker: str,
    expiry: str,
    to_display: List[str],
    min_sp: float,
    max_sp: float,
    calls_only: bool,
    puts_only: bool,
    export: str,
):
    """Display option chain

    Parameters
    ----------
    ticker: str
        Stock ticker
    expiry: str
        Expiration date of option
    to_display: List[str]
        List of columns to display
    min_sp: float
        Min strike price to display
    max_sp: float
        Max strike price to display
    calls_only: bool
        Only display calls
    puts_only: bool
        Only display puts
    export: str
        Format to  export file
    """

    chains_df = tradier_model.get_option_chains(ticker, expiry)
    columns = to_display + ["strike", "option_type"]
    chains_df = chains_df[columns].rename(columns=column_map)

    if export:
        export_data(
            export,
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "chains",
            chains_df,
        )

    if min_sp == -1:
        min_strike = np.percentile(chains_df["strike"], 25)
    else:
        min_strike = min_sp

    if max_sp == -1:
        max_strike = np.percentile(chains_df["strike"], 75)
    else:
        max_strike = max_sp

    print(f"The strike prices are displayed between {min_strike} and {max_strike}")

    chains_df = chains_df[chains_df["strike"] >= min_strike]
    chains_df = chains_df[chains_df["strike"] <= max_strike]

    calls_df = chains_df[chains_df.option_type == "call"].drop(columns=["option_type"])
    puts_df = chains_df[chains_df.option_type == "put"].drop(columns=["option_type"])

    if calls_only:
        print(
            tabulate(
                calls_df,
                headers=calls_df.columns,
                tablefmt="grid",
                showindex=False,
                floatfmt=".2f",
            )
        )

    elif puts_only:
        print(
            tabulate(
                puts_df,
                headers=puts_df.columns,
                tablefmt="grid",
                showindex=False,
                floatfmt=".2f",
            )
        )

    else:
        puts_df = puts_df[puts_df.columns[::-1]]
        chain_table = calls_df.merge(puts_df, on="strike")

        if gtff.USE_COLOR:
            call_cols = [col for col in chain_table if col.endswith("_x")]
            put_cols = [col for col in chain_table if col.endswith("_y")]
            patch_pandas_text_adjustment()
            pd.set_option("display.max_colwidth", 0)
            pd.set_option("display.max_rows", None)
            for cc in call_cols:
                chain_table[cc] = chain_table[cc].astype(str).apply(green_highlight)
            for pc in put_cols:
                chain_table[pc] = chain_table[pc].astype(str).apply(red_highlight)
        headers = [
            col.strip("_x")
            if col.endswith("_x")
            else col.strip("_y")
            if col.endswith("_y")
            else col
            for col in chain_table.columns
        ]
        print(
            tabulate(
                chain_table,
                headers=headers,
                tablefmt="fancy_grid",
                showindex=False,
                floatfmt=".2f",
            ),
            "\n",
        )


def plot_oi(
    ticker: str,
    expiry: str,
    min_sp: float,
    max_sp: float,
    calls_only: bool,
    puts_only: bool,
    export: str,
):
    """Plot open interest

    Parameters
    ----------
    ticker: str
        Ticker
    expiry: str
        Expiry date for options
    min_sp: float
        Min strike to consider
    max_sp: float
        Max strike to consider
    calls_only: bool
        Show calls only
    puts_only: bool
        Show puts only
    export: str
        Format to export file
    """

    options = tradier_model.get_option_chains(ticker, expiry)
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "oi_tr",
        options,
    )
    current_price = tradier_model.last_price(ticker)

    if min_sp == -1:
        min_strike = 0.75 * current_price
    else:
        min_strike = min_sp

    if max_sp == -1:
        max_strike = 1.25 * current_price
    else:
        max_strike = max_sp

    if calls_only and puts_only:
        print("Both flags selected, please select one", "\n")
        return

    calls = options[options.option_type == "call"][["strike", "open_interest"]]
    puts = options[options.option_type == "put"][["strike", "open_interest"]]
    call_oi = calls.set_index("strike")["open_interest"] / 1000
    put_oi = puts.set_index("strike")["open_interest"] / 1000

    df_opt = pd.merge(call_oi, put_oi, left_index=True, right_index=True)
    df_opt = df_opt.rename(
        columns={"open_interest_x": "OI_call", "open_interest_y": "OI_put"}
    )

    max_pain = op_helpers.calculate_max_pain(df_opt)
    plt.style.use("classic")
    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfp.PLOT_DPI)

    if not calls_only:
        put_oi.plot(
            x="strike",
            y="open_interest",
            label="Puts",
            ax=ax,
            marker="o",
            ls="-",
            c="r",
        )
    if not puts_only:
        call_oi.plot(
            x="strike",
            y="open_interest",
            label="Calls",
            ax=ax,
            marker="o",
            ls="-",
            c="g",
        )
        ax.axvline(
            current_price, lw=2, c="k", ls="--", label="Current Price", alpha=0.7
        )
        ax.axvline(max_pain, lw=3, c="k", label=f"Max Pain: {max_pain}", alpha=0.7)
        ax.grid("on")
        ax.set_xlabel("Strike Price")
        ax.set_ylabel("Open Interest (1k) ")
        ax.set_xlim(min_strike, max_strike)

        if gtff.USE_ION:
            plt.ion()

        ax.set_title(f"Open Interest for {ticker.upper()} expiring {expiry}")
        plt.legend(loc=0)
        fig.tight_layout(pad=1)

    plt.show()
    plt.style.use("default")
    print("")


def plot_vol(
    ticker: str,
    expiry: str,
    min_sp: float,
    max_sp: float,
    calls_only: bool,
    puts_only: bool,
    export: str,
):
    """Plot volume

    Parameters
    ----------
    ticker: str
        Ticker
    expiry: str
        Expiry date for options
    min_sp: float
        Min strike to consider
    max_sp: float
        Max strike to consider
    calls_only: bool
        Show calls only
    puts_only: bool
        Show puts only
    export: str
        Format to export file
    """

    options = tradier_model.get_option_chains(ticker, expiry)
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "vol_tr",
        options,
    )
    current_price = tradier_model.last_price(ticker)

    if min_sp == -1:
        min_strike = 0.75 * current_price
    else:
        min_strike = min_sp

    if max_sp == -1:
        max_strike = 1.25 * current_price
    else:
        max_strike = max_sp

    if calls_only and puts_only:
        print("Both flags selected, please select one", "\n")
        return

    calls = options[options.option_type == "call"][["strike", "volume"]]
    puts = options[options.option_type == "put"][["strike", "volume"]]
    call_v = calls.set_index("strike")["volume"] / 1000
    put_v = puts.set_index("strike")["volume"] / 1000
    plt.style.use("classic")
    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfp.PLOT_DPI)

    if not calls_only:
        put_v.plot(
            x="strike",
            y="volume",
            label="Puts",
            ax=ax,
            marker="o",
            ls="-",
            c="r",
        )
    if not puts_only:
        call_v.plot(
            x="strike",
            y="volume",
            label="Calls",
            ax=ax,
            marker="o",
            ls="-",
            c="g",
        )
    ax.axvline(current_price, lw=2, c="k", ls="--", label="Current Price", alpha=0.7)
    ax.grid("on")
    ax.set_xlabel("Strike Price")
    ax.set_ylabel("Volume (1k) ")
    ax.set_xlim(min_strike, max_strike)

    if gtff.USE_ION:
        plt.ion()

    ax.set_title(f"Volume for {ticker.upper()} expiring {expiry}")
    plt.legend(loc=0)
    fig.tight_layout(pad=1)

    plt.show()
    plt.style.use("default")
    print("")


def plot_volume_open_interest(
    ticker: str,
    expiry: str,
    min_sp: float,
    max_sp: float,
    min_vol: float,
    export: str,
):
    """Plot volume and open interest

    Parameters
    ----------
    ticker: str
        Stock ticker
    expiry: str
        Option expiration
    min_sp: float
        Min strike price
    max_sp: float
        Max strike price
    min_vol: float
        Min volume to consider
    export: str
        Format for exporting data
    """
    current_price = tradier_model.last_price(ticker)
    options = tradier_model.get_option_chains(ticker, expiry)
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "voi_tr",
        options,
    )

    calls = options[options.option_type == "call"][
        ["strike", "volume", "open_interest"]
    ]
    puts = options[options.option_type == "put"][["strike", "volume", "open_interest"]]

    # Process Calls Data
    df_calls = calls.pivot_table(
        index="strike", values=["volume", "open_interest"], aggfunc="sum"
    ).reindex()
    df_calls["strike"] = df_calls.index
    df_calls["type"] = "calls"
    df_calls["open_interest"] = df_calls["open_interest"]
    df_calls["volume"] = df_calls["volume"]
    df_calls["oi+v"] = df_calls["open_interest"] + df_calls["volume"]
    df_calls["spot"] = round(current_price, 2)

    df_puts = puts.pivot_table(
        index="strike", values=["volume", "open_interest"], aggfunc="sum"
    ).reindex()
    df_puts["strike"] = df_puts.index
    df_puts["type"] = "puts"
    df_puts["open_interest"] = df_puts["open_interest"]
    df_puts["volume"] = -df_puts["volume"]
    df_puts["open_interest"] = -df_puts["open_interest"]
    df_puts["oi+v"] = df_puts["open_interest"] + df_puts["volume"]
    df_puts["spot"] = round(current_price, 2)

    call_oi = calls.set_index("strike")["open_interest"] / 1000
    put_oi = puts.set_index("strike")["open_interest"] / 1000

    df_opt = pd.merge(call_oi, put_oi, left_index=True, right_index=True)
    df_opt = df_opt.rename(
        columns={"open_interest_x": "OI_call", "open_interest_y": "OI_put"}
    )

    max_pain = op_helpers.calculate_max_pain(df_opt)

    if min_vol == -1 and min_sp == -1 and max_sp == -1:
        # If no argument provided, we use the percentile 50 to get 50% of upper volume data
        volume_percentile_threshold = 50
        min_vol_calls = np.percentile(df_calls["oi+v"], volume_percentile_threshold)
        min_vol_puts = np.percentile(df_puts["oi+v"], volume_percentile_threshold)

        df_calls = df_calls[df_calls["oi+v"] > min_vol_calls]
        df_puts = df_puts[df_puts["oi+v"] < min_vol_puts]

    else:
        if min_vol > -1:
            df_calls = df_calls[df_calls["oi+v"] > min_vol]
            df_puts = df_puts[df_puts["oi+v"] < -min_vol]

        if min_sp > -1:
            df_calls = df_calls[df_calls["strike"] > min_sp]
            df_puts = df_puts[df_puts["strike"] > min_sp]

        if max_sp > -1:
            df_calls = df_calls[df_calls["strike"] < max_sp]
            df_puts = df_puts[df_puts["strike"] < max_sp]

    if df_calls.empty and df_puts.empty:
        print(
            "The filtering applied is too strong, there is no data available for such conditions.\n"
        )
        return

    # Initialize the matplotlib figure
    _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfp.PLOT_DPI)

    # make x axis symmetric
    axis_origin = max(abs(max(df_puts["oi+v"])), abs(max(df_calls["oi+v"])))
    ax.set_xlim(-axis_origin, +axis_origin)

    sns.set_style(style="darkgrid")

    g = sns.barplot(
        x="oi+v",
        y="strike",
        data=df_calls,
        label="Calls: Open Interest",
        color="lightgreen",
        orient="h",
    )

    g = sns.barplot(
        x="volume",
        y="strike",
        data=df_calls,
        label="Calls: Volume",
        color="green",
        orient="h",
    )

    g = sns.barplot(
        x="oi+v",
        y="strike",
        data=df_puts,
        label="Puts: Open Interest",
        color="pink",
        orient="h",
    )

    g = sns.barplot(
        x="volume",
        y="strike",
        data=df_puts,
        label="Puts: Volume",
        color="red",
        orient="h",
    )

    # draw spot line
    s = [float(strike.get_text()) for strike in ax.get_yticklabels()]
    spot_index = bisect_left(s, current_price)  # find where the spot is on the graph
    spot_line = ax.axhline(spot_index, ls="--", color="dodgerblue", alpha=0.3)

    # draw max pain line
    max_pain_index = bisect_left(s, max_pain)
    max_pain_line = ax.axhline(max_pain_index, ls="-", color="black", alpha=0.3)
    max_pain_line.set_linewidth(3)

    # format ticklabels without - for puts
    g.set_xticks(g.get_xticks())
    xlabels = [f"{x:,.0f}".replace("-", "") for x in g.get_xticks()]
    g.set_xticklabels(xlabels)

    plt.title(
        f"{ticker} volumes for {expiry} (open interest displayed only during market hours)"
    )
    ax.invert_yaxis()

    _ = ax.legend()
    handles, _ = ax.get_legend_handles_labels()
    handles.append(spot_line)
    handles.append(max_pain_line)

    # create legend labels + add to graph
    labels = [
        "Calls open interest",
        "Calls volume ",
        "Puts open interest",
        "Puts volume",
        "Current stock price",
        f"Max pain = {max_pain}",
    ]

    plt.legend(handles=handles[:], labels=labels)
    sns.despine(left=True, bottom=True)

    if gtff.USE_ION:
        plt.ion()
    plt.show()
    plt.style.use("default")
    print("")


def display_historical(
    ticker: str,
    expiry: str,
    strike: float,
    put: bool,
    export: str,
    raw: bool,
    chain_id: str,
):
    """Plot historical option prices

    Parameters
    ----------
    ticker: str
        Stock ticker
    expiry: str
        Expiry date of option
    strike: float
        Option strike price
    put: bool
        Is this a put option?
    export: str
        Format of export file
    raw: bool
        Print raw data
    chain_id: str
        OCC option symbol
    """

    df_hist = tradier_model.get_historical_options(
        ticker, expiry, strike, put, chain_id
    )

    if raw:
        print(tabulate(df_hist, headers=df_hist.columns, tablefmt="fancy_grid"))

    op_type = ["call", "put"][put]

    mc = mpf.make_marketcolors(
        up="green", down="red", edge="black", wick="black", volume="in", ohlc="i"
    )

    s = mpf.make_mpf_style(marketcolors=mc, gridstyle=":", y_on_right=True)

    if gtff.USE_ION:
        plt.ion()

    mpf.plot(
        df_hist,
        type="candle",
        volume=True,
        title=f"\n{ticker.upper()} {strike} {op_type} expiring {expiry} Historical",
        style=s,
        figratio=(10, 7),
        figscale=1.10,
        figsize=(plot_autoscale()),
        update_width_config=dict(
            candle_linewidth=1.0, candle_width=0.8, volume_linewidth=1.0
        ),
    )

    print("")

    if export:
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "hist",
            df_hist,
        )
