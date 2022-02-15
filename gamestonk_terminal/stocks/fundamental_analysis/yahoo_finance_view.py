""" Yahoo Finance View """
__docformat__ = "numpy"

import logging
import os
import webbrowser
from typing import List, Optional

import matplotlib.pyplot as plt
import pandas as pd

from gamestonk_terminal.config_terminal import theme
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
)
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.stocks.fundamental_analysis import yahoo_finance_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def open_headquarters_map(ticker: str):
    """Headquarters location of the company
    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    """
    webbrowser.open(yahoo_finance_model.get_hq(ticker))
    console.print("")


@log_start_end(log=logger)
def open_web(ticker: str):
    """Website of the company
    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    """
    webbrowser.open(yahoo_finance_model.get_website(ticker))
    console.print("")


@log_start_end(log=logger)
def display_info(ticker: str):
    """Yahoo Finance ticker info
    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    """
    summary = ""
    df_info = yahoo_finance_model.get_info(ticker)
    if "Long business summary" in df_info.index:
        summary = df_info.loc["Long business summary"].values[0]
        df_info = df_info.drop(index=["Long business summary"])

    print_rich_table(df_info, headers=[], show_index=True, title="Ticker Info")

    if summary:
        console.print("Business Summary:")
        console.print(summary)

    console.print("")


@log_start_end(log=logger)
def display_shareholders(ticker: str):
    """Yahoo Finance ticker shareholders
    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    """
    (
        df_major_holders,
        df_institutional_shareholders,
        df_mutualfund_shareholders,
    ) = yahoo_finance_model.get_shareholders(ticker)

    dfs = [df_major_holders, df_institutional_shareholders, df_mutualfund_shareholders]
    titles = ["Major Holders:\n", "Institutuinal Holders:\n", "Mutual Fund Holders:\n"]
    console.print("")
    for df, title in zip(dfs, titles):
        console.print(title)
        print_rich_table(
            df, headers=list(df.columns), show_index=False, title="Ticker Shareholders"
        )
        console.print("")


@log_start_end(log=logger)
def display_sustainability(ticker: str):
    """Yahoo Finance ticker sustainability
    Parameters
    ----------
    other_args : List[str]
        argparse other args
    ticker : str
        Fundamental analysis ticker symbol
    """

    df_sustainability = yahoo_finance_model.get_sustainability(ticker)

    if df_sustainability.empty:
        console.print("No sustainability data found.", "\n")
        return

    print_rich_table(
        df_sustainability,
        headers=[],
        title="Ticker Sustainability",
        show_index=True,
    )
    console.print("")


@log_start_end(log=logger)
def display_calendar_earnings(ticker: str):
    """Yahoo Finance ticker calendar earnings
    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    """
    df_calendar = yahoo_finance_model.get_calendar_earnings(ticker).T
    if df_calendar.empty:
        console.print("No calendar events found.\n")
        return
    print_rich_table(
        df_calendar,
        show_index=False,
        headers=list(df_calendar.columns),
        title="Ticker Calendar Earnings",
    )
    console.print("")


@log_start_end(log=logger)
def display_dividends(
    ticker: str,
    limit: int = 12,
    plot: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display historical dividends
    Parameters
    ----------
    ticker: str
        Stock ticker
    limit: int
        Number to show
    plot: bool
        Plots hitsorical data
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    div_history = yahoo_finance_model.get_dividends(ticker)
    if div_history.empty:
        console.print("No dividends found.\n")
        return
    div_history["Dif"] = div_history.diff()
    div_history = div_history[::-1]
    if plot:

        # This plot has 1 axis
        if not external_axes:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        else:
            if len(external_axes) != 1:
                console.print("[red]Expected list of one axis item./n[/red]")
                return
            (ax,) = external_axes

        ax.plot(
            div_history.index,
            div_history["Dividends"],
            ls="-",
            linewidth=0.75,
            marker=".",
            markersize=4,
            mfc=theme.down_color,
            mec=theme.down_color,
            alpha=1,
            label="Dividends Payout",
        )
        ax.set_ylabel("Amount ($)")
        ax.set_title(f"Dividend History for {ticker}")
        ax.set_xlim(div_history.index[-1], div_history.index[0])
        ax.legend()
        theme.style_primary_axis(ax)

        if not external_axes:
            theme.visualize_output()

    else:
        div_history.index = pd.to_datetime(div_history.index, format="%Y%m%d").strftime(
            "%Y-%m-%d"
        )
        print_rich_table(
            div_history.head(limit),
            headers=["Amount Paid ($)", "Change"],
            title="Ticker Historical Dividends",
        )
    console.print("")
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "divs", div_history)
