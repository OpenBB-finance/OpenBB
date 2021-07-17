""" Volume view """
__docformat__ = "numpy"

from bisect import bisect_left
from typing import List
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from gamestonk_terminal.helper_funcs import (
    plot_autoscale,
    check_non_negative,
    parse_known_args_and_warn,
)
from gamestonk_terminal import config_plot as cfgPlot
from gamestonk_terminal import feature_flags as gtff


def plot_volume_open_interest(
    other_args: List[str],
    ticker: str,
    exp_date: str,
    last_adj_close_price: float,
    op_calls: pd.DataFrame,
    op_puts: pd.DataFrame,
):
    """Plot volume open interest

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    ticker : str
        Main ticker to compare income
    exp_date : str
        Expiry date of the option
    last_adj_close_price: float
        Last adjusted closing price
    op_calls: pd.DataFrame
        Option data calls
    op_puts: pd.DataFrame
        Option data puts
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="voi",
        description="""
            Plots Volume + Open Interest of calls vs puts. [Source: Yahoo Finance]
        """,
    )
    parser.add_argument(
        "-v",
        "--minv",
        dest="min_vol",
        type=check_non_negative,
        default=-1,
        help="minimum volume (considering open interest) threshold of the plot.",
    )
    parser.add_argument(
        "-m",
        "--min",
        dest="min_sp",
        type=check_non_negative,
        default=-1,
        help="minimum strike price to consider in the plot.",
    )
    parser.add_argument(
        "-M",
        "--max",
        dest="max_sp",
        type=check_non_negative,
        default=-1,
        help="maximum strike price to consider in the plot.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_calls, df_puts, max_pain = get_calls_puts_maxpain(
            op_calls, op_puts, last_adj_close_price
        )

        if (
            ns_parser.min_vol == -1
            and ns_parser.min_sp == -1
            and ns_parser.max_sp == -1
        ):
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
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)

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
        spot_index = bisect_left(
            s, last_adj_close_price
        )  # find where the spot is on the graph
        spot_line = ax.axhline(spot_index, ls="--", color="dodgerblue", alpha=0.3)

        # draw max pain line
        max_pain_index = bisect_left(s, max_pain)
        max_pain_line = ax.axhline(max_pain_index, ls="-", color="black", alpha=0.3)
        max_pain_line.set_linewidth(5)

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
        print("")

    except Exception as e:
        print(e, "\n")


def get_calls_puts_maxpain(
    op_calls: pd.DataFrame, op_puts: pd.DataFrame, last_adj_close_price: float
):
    """Get calls and puts dataframes, and max pain

    Parameters
    ----------
    op_calls: pd.DataFrame
        Option data calls
    op_puts: pd.DataFrame
        Option data puts
    last_adj_close_price: float
        Last adjusted closing price

    Returns
    ----------
    pd.DataFrame
        Processed calls dataframe
    pd.DataFrame
        Processed puts dataframe
    float
        Max pain
    """
    df_calls = pd.DataFrame()
    df_puts = pd.DataFrame()
    max_pain = 0

    if not op_calls.empty:
        # Process Calls Data
        df_calls = op_calls.pivot_table(
            index="strike", values=["volume", "openInterest"], aggfunc="sum"
        ).reindex()
        df_calls["strike"] = df_calls.index
        df_calls["type"] = "calls"
        df_calls["openInterest"] = df_calls["openInterest"]
        df_calls["volume"] = df_calls["volume"]
        df_calls["oi+v"] = df_calls["openInterest"] + df_calls["volume"]
        df_calls["spot"] = round(last_adj_close_price, 2)

    if not op_puts.empty:
        # Process Puts Data
        df_puts = op_puts.pivot_table(
            index="strike", values=["volume", "openInterest"], aggfunc="sum"
        ).reindex()
        df_puts["strike"] = df_puts.index
        df_puts["type"] = "puts"
        df_puts["openInterest"] = df_puts["openInterest"]
        df_puts["volume"] = -df_puts["volume"]
        df_puts["openInterest"] = -df_puts["openInterest"]
        df_puts["oi+v"] = df_puts["openInterest"] + df_puts["volume"]
        df_puts["spot"] = round(last_adj_close_price, 2)

    if not op_calls.empty and not op_puts.empty:
        # Get max pain
        df_opt = pd.merge(df_calls, df_puts, left_index=True, right_index=True)
        df_opt = df_opt[["openInterest_x", "openInterest_y"]].rename(
            columns={"openInterest_x": "OI_call", "openInterest_y": "OI_put"}
        )
        max_pain = get_max_pain(df_opt)

    return df_calls, df_puts, max_pain


def plot_calls_volume_open_interest(
    other_args: List[str],
    ticker: str,
    exp_date: str,
    last_adj_close_price: float,
    op_calls: pd.DataFrame,
):
    """Plot calls volume open interest

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    ticker : str
        Main ticker to compare income
    exp_date : str
        Expiry date of the option
    last_adj_close_price: float
        Last adjusted closing price
    op_calls: pd.DataFrame
        Option data calls
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="vcalls",
        description="""
            Plots Calls Volume + Open Interest. [Source: Yahoo Finance]
        """,
    )
    parser.add_argument(
        "-m",
        "--min",
        dest="min_sp",
        type=check_non_negative,
        default=-1,
        help="minimum strike price to consider in the plot.",
    )
    parser.add_argument(
        "-M",
        "--max",
        dest="max_sp",
        type=check_non_negative,
        default=-1,
        help="maximum strike price to consider in the plot.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_calls, _, _ = get_calls_puts_maxpain(
            op_calls, pd.DataFrame(), last_adj_close_price
        )

        if ns_parser.min_sp == -1:
            min_strike = 0.75 * last_adj_close_price
        else:
            min_strike = ns_parser.min_sp

        if ns_parser.max_sp == -1:
            max_strike = 1.25 * last_adj_close_price
        else:
            max_strike = ns_parser.max_sp

        plt.figure(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)

        plt.axvline(last_adj_close_price, lw=2)
        plt.bar(
            df_calls["strike"],
            df_calls["volume"] + df_calls["openInterest"],
            color="lightgreen",
            width=0.45,
        )
        plt.bar(df_calls["strike"], df_calls["volume"], color="green", width=0.45)

        plt.title(f"{ticker} calls volumes for {exp_date} ")
        plt.legend(["Stock Price", "Open Interest", "Volume"])
        plt.xlabel("Strike Price")
        plt.ylabel("Volume")
        plt.xlim([min_strike, max_strike])

        if gtff.USE_ION:
            plt.ion()
        plt.show()

        print("")

    except Exception as e:
        print(e, "\n")


def plot_puts_volume_open_interest(
    other_args: List[str],
    ticker: str,
    exp_date: str,
    last_adj_close_price: float,
    op_puts: pd.DataFrame,
):
    """Plot puts volume open interest

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    ticker : str
        Main ticker to compare income
    exp_date : str
        Expiry date of the option
    last_adj_close_price: float
        Last adjusted closing price
    op_puts: pd.DataFrame
        Option data puts
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="vputs",
        description="""
            Plots Puts Volume + Open Interest. [Source: Yahoo Finance]
        """,
    )
    parser.add_argument(
        "-m",
        "--min",
        dest="min_sp",
        type=check_non_negative,
        default=-1,
        help="minimum strike price to consider in the plot.",
    )
    parser.add_argument(
        "-M",
        "--max",
        dest="max_sp",
        type=check_non_negative,
        default=-1,
        help="maximum strike price to consider in the plot.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        _, df_puts, _ = get_calls_puts_maxpain(
            pd.DataFrame(), op_puts, last_adj_close_price
        )

        if ns_parser.min_sp == -1:
            min_strike = 0.75 * last_adj_close_price
        else:
            min_strike = ns_parser.min_sp

        if ns_parser.max_sp == -1:
            max_strike = 1.25 * last_adj_close_price
        else:
            max_strike = ns_parser.max_sp

        plt.figure(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)

        plt.axvline(last_adj_close_price, lw=2)
        plt.bar(
            df_puts["strike"],
            -df_puts["volume"] - df_puts["openInterest"],
            color="pink",
            width=0.45,
        )
        plt.bar(df_puts["strike"], -df_puts["volume"], color="red", width=0.45)

        plt.title(f"{ticker} puts volumes for {exp_date} ")
        plt.legend(["Stock Price", "Open Interest", "Volume"])
        plt.xlabel("Strike Price")
        plt.ylabel("Volume")
        plt.xlim([min_strike, max_strike])

        if gtff.USE_ION:
            plt.ion()
        plt.show()

        print("")

    except Exception as e:
        print(e, "\n")


def get_loss_at_strike(strike: float, chain: pd.DataFrame) -> float:
    """Function to get the loss at the given expiry

    Parameters
    ----------
    strike: Union[int,float]
        Value to calculate total loss at
    chain: Dataframe:
        Dataframe containing at least strike and openInterest

    Returns
    -------
    loss: Union[float,int]
        Total loss
    """

    itm_calls = chain[chain.index < strike][["OI_call"]]
    itm_calls["loss"] = (strike - itm_calls.index) * itm_calls["OI_call"]
    call_loss = itm_calls["loss"].sum()
    # The *-1 below is due to a sign change for plotting in the _view code
    itm_puts = chain[chain.index > strike][["OI_put"]]
    itm_puts["loss"] = (itm_puts.index - strike) * itm_puts["OI_put"] * -1
    put_loss = itm_puts.loss.sum()
    loss = call_loss + put_loss

    return loss


def get_max_pain(chain: pd.DataFrame) -> int:
    """Returns the max pain for a given call/put dataframe

    Parameters
    ----------
    chain: DataFrame
        Dataframe to calculate value from

    Returns
    -------
    max_pain : int
        Max pain value
    """

    strikes = np.array(chain.index)
    if ("OI_call" not in chain.columns) or ("OI_put" not in chain.columns):
        print("Incorrect columns.  Unable to parse max pain")
        return np.nan

    loss = []
    for price_at_exp in strikes:
        loss.append(get_loss_at_strike(price_at_exp, chain))

    chain["loss"] = loss
    max_pain = chain["loss"].idxmin()

    return max_pain
