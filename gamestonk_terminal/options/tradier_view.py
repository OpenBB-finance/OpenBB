"""Tradier options view"""
__docformat__ = "numpy"

import argparse
from typing import List
from bisect import bisect_left
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import mplfinance as mpf
from colorama import Fore, Style
from tabulate import tabulate

from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    check_non_negative,
    export_data,
    plot_autoscale,
    patch_pandas_text_adjustment,
)
from gamestonk_terminal.options import op_helpers, tradier_model
from gamestonk_terminal import config_plot as cfp
from gamestonk_terminal import feature_flags as gtff

column_map = {"mid_iv": "iv", "open_interest": "oi", "volume": "vol"}


def red_highlight(val):
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


def green_highlight(val):
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


def display_chains(ticker: str, expiry: str, other_args: List[str]):
    """Display option chain

    Parameters
    ----------
    ticker: str
        Stock ticker
    expiry: str
        Expiration date of option
    other_args: List[str]
        Argparse arguments
    """
    parser = argparse.ArgumentParser(
        prog="chains",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Display option chains",
    )
    parser.add_argument(
        "--calls",
        action="store_true",
        default=False,
        dest="calls_only",
        help="Flag to show calls only",
    )
    parser.add_argument(
        "--puts",
        action="store_true",
        default=False,
        dest="puts_only",
        help="Flag to show puts only",
    )
    parser.add_argument(
        "-m",
        "--min",
        dest="min_sp",
        type=check_non_negative,
        default=-1,
        help="minimum strike price to consider.",
    )
    parser.add_argument(
        "-M",
        "--max",
        dest="max_sp",
        type=check_non_negative,
        default=-1,
        help="maximum strike price to consider.",
    )
    parser.add_argument(
        "-d",
        "--display",
        dest="to_display",
        default=tradier_model.default_columns,
        type=check_valid_option_chains_headers,
        help="columns to look at.  Columns can be:  {bid, ask, strike, bidsize, asksize, volume, open_interest, delta, "
        "gamma, theta, vega, ask_iv, bid_iv, mid_iv} ",
    )
    parser.add_argument(
        "--export",
        choices=["csv", "json", "xlsx"],
        default="",
        dest="export",
        help="Export dataframe data to csv,json,xlsx file",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        chains_df = tradier_model.get_option_chains(ticker, expiry)
        columns = ns_parser.to_display + ["strike", "option_type"]
        chains_df = chains_df[columns].rename(columns=column_map)

        if ns_parser.min_sp == -1:
            min_strike = np.percentile(chains_df["strike"], 25)
        else:
            min_strike = ns_parser.min_sp

        if ns_parser.max_sp == -1:
            max_strike = np.percentile(chains_df["strike"], 75)
        else:
            max_strike = ns_parser.max_sp

        print(f"The strike prices are displayed between {min_strike} and {max_strike}")

        chains_df = chains_df[chains_df["strike"] >= min_strike]
        chains_df = chains_df[chains_df["strike"] <= max_strike]

        if ns_parser.export:
            # Note the extra dirname needed due to the subfolder in options
            export_data(
                ns_parser.export,
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                f"chains_{ticker}_{expiry}",
                chains_df,
            )

        calls_df = chains_df[chains_df.option_type == "call"].drop(
            columns=["option_type"]
        )
        puts_df = chains_df[chains_df.option_type == "put"].drop(
            columns=["option_type"]
        )

        if ns_parser.calls_only:
            print(
                tabulate(
                    calls_df,
                    headers=calls_df.columns,
                    tablefmt="grid",
                    showindex=False,
                    floatfmt=".2f",
                )
            )

        elif ns_parser.puts_only:
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
                )
            )
            print("")

    except Exception as e:
        print(e, "\n")


def plot_oi(
    options: pd.DataFrame,
    ticker: str,
    expiry: str,
    ns_parser: argparse.Namespace,
):
    """Plot open interest

    Parameters
    ----------
    options: pd.DataFrame
        Options dataframe with both calls and puts
    ticker: str
        Ticker
    expiry: str
        Expiry date for options
    ns_parser: argparse.Namespace
        Parsed namespace
    """

    current_price = tradier_model.last_price(ticker)

    if ns_parser.min == -1:
        min_strike = 0.75 * current_price
    else:
        min_strike = ns_parser.min

    if ns_parser.max == -1:
        max_strike = 1.25 * current_price
    else:
        max_strike = ns_parser.max

    if ns_parser.calls and ns_parser.puts:
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

    if not ns_parser.calls:
        put_oi.plot(
            x="strike",
            y="open_interest",
            label="Puts",
            ax=ax,
            marker="o",
            ls="-",
            c="r",
        )
    if not ns_parser.puts:
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
    options: pd.DataFrame,
    ticker: str,
    expiry: str,
    ns_parser: argparse.Namespace,
):
    """Plot volume

    Parameters
    ----------
    options: pd.DataFrame
        Options dataframe with both calls and puts
    ticker: str
        Ticker
    expiry: str
        Expiry date for options
    ns_parser: argparse.Namespace
        Parsed namespace
    """

    current_price = tradier_model.last_price(ticker)

    if ns_parser.min == -1:
        min_strike = 0.75 * current_price
    else:
        min_strike = ns_parser.min

    if ns_parser.max == -1:
        max_strike = 1.25 * current_price
    else:
        max_strike = ns_parser.max

    if ns_parser.calls and ns_parser.puts:
        print("Both flags selected, please select one", "\n")
        return

    calls = options[options.option_type == "call"][["strike", "volume"]]
    puts = options[options.option_type == "put"][["strike", "volume"]]
    call_v = calls.set_index("strike")["volume"] / 1000
    put_v = puts.set_index("strike")["volume"] / 1000
    plt.style.use("classic")
    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfp.PLOT_DPI)

    if not ns_parser.calls:
        put_v.plot(
            x="strike",
            y="volume",
            label="Puts",
            ax=ax,
            marker="o",
            ls="-",
            c="r",
        )
    if not ns_parser.puts:
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
    ticker: str, exp_date: str, options: pd.DataFrame, ns_parser: argparse.Namespace
):
    """Plot volume and open interest

    Parameters
    ----------
    ticker : str
        Main ticker to compare income
    exp_date : str
        Expiry date of the option
    Options: pd.DataFrame
        Options dataframe with both calls and puts
    ns_parser: argparse.Namespace
        Parsed namespace
    """

    current_price = tradier_model.last_price(ticker)
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

    if ns_parser.min_vol == -1 and ns_parser.min_sp == -1 and ns_parser.max_sp == -1:
        # If no argument provided, we use the percentile 50 to get 50% of upper volume data
        volume_percentile_threshold = 50
        min_vol_calls = np.percentile(df_calls["oi+v"], volume_percentile_threshold)
        min_vol_puts = np.percentile(df_puts["oi+v"], volume_percentile_threshold)

        df_calls = df_calls[df_calls["oi+v"] > min_vol_calls]
        df_puts = df_puts[df_puts["oi+v"] < min_vol_puts]

    else:
        if ns_parser.min_vol > -1:
            df_calls = df_calls[df_calls["oi+v"] > ns_parser.min_vol]
            df_puts = df_puts[df_puts["oi+v"] < -ns_parser.min_vol]

        if ns_parser.min_sp > -1:
            df_calls = df_calls[df_calls["strike"] > ns_parser.min_sp]
            df_puts = df_puts[df_puts["strike"] > ns_parser.min_sp]

        if ns_parser.max_sp > -1:
            df_calls = df_calls[df_calls["strike"] < ns_parser.max_sp]
            df_puts = df_puts[df_puts["strike"] < ns_parser.max_sp]

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
        f"{ticker} volumes for {exp_date} (open interest displayed only during market hours)"
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


def display_historical(ticker: str, expiry: str, other_args: List[str]):
    """Plot historical option data

    Parameters
    ----------
    ticker: str
        Ticker
    expiry: str
        Expiration of option
    other_args: List[str]
        Argparse arguments
    """

    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="hist",
        description="Gets historical quotes for given option chain",
    )
    parser.add_argument(
        "-s",
        "--strike",
        dest="strike",
        type=float,
        required="--chain" not in other_args or "-h" not in other_args,
        help="Strike price to look at",
    )
    parser.add_argument(
        "--put",
        dest="put",
        action="store_true",
        default=False,
        help="Flag for showing put option",
    )
    parser.add_argument("--chain", dest="chain_id", type=str, help="OCC option symbol")

    parser.add_argument(
        "--raw", dest="raw", action="store_true", default=False, help="Display raw data"
    )

    parser.add_argument(
        "--export",
        choices=["csv", "json", "xlsx"],
        default="",
        dest="export",
        help="Export dataframe data to csv,json,xlsx file",
    )

    try:

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if not ns_parser.chain_id:
            strike = float(ns_parser.strike)
            op_type = ["call", "put"][ns_parser.put]
            chain = tradier_model.get_option_chains(ticker, expiry)
            try:
                symbol = chain[
                    (chain.strike == strike) & (chain.option_type == op_type)
                ]["symbol"].values[0]
            except IndexError:
                print(f"Strike: {strike}, Option type: {op_type} not not found \n")
                return
        else:
            symbol = ns_parser.chain_id

        df_hist = tradier_model.historical_prices(symbol)
        df_hist.index = pd.DatetimeIndex(df_hist.index)

        if ns_parser.raw:
            print(df_hist)

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

        if ns_parser.export:
            export_data(
                ns_parser.export,
                os.path.dirname(os.path.abspath(__file__)),
                f"historical_op_{ticker}_{expiry}_{str(strike).replace('.','p')}_{op_type}",
                df_hist,
            )

    except Exception as e:
        print(e, "\n")

    except SystemExit:
        print("")
