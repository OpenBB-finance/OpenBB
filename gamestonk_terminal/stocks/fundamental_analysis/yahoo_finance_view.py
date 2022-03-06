""" Yahoo Finance View """
__docformat__ = "numpy"

import logging
import os
import webbrowser
from datetime import datetime, timedelta
from typing import List, Optional
from fractions import Fraction

import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
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

    if not df_info.empty:
        print_rich_table(
            df_info,
            headers=list(df_info.columns),
            show_index=True,
            title=f"{ticker.upper()} Info",
        )
    else:
        logger.error("Invalid data")
        console.print("[red]Invalid data[/red]\n")
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
    df_major_holders.columns = ["", ""]
    dfs = [df_major_holders, df_institutional_shareholders, df_mutualfund_shareholders]
    titles = ["Major Holders", "Institutional Holders", "Mutual Fund Holders"]
    console.print()

    for df, title in zip(dfs, titles):
        if "Date Reported" in df.columns:
            df["Date Reported"] = df["Date Reported"].apply(
                lambda x: x.strftime("%Y-%m-%d")
            )
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title=f"{ticker.upper()} {title}",
        )
        console.print()


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

    if not df_sustainability.empty:
        print_rich_table(
            df_sustainability,
            headers=list(df_sustainability),
            title=f"{ticker.upper()} Sustainability",
            show_index=True,
        )
        console.print("")
    else:
        logger.error("Invalid data")
        console.print("[red]Invalid data[/red]\n")


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
        title=f"{ticker.upper()} Calendar Earnings",
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
        Plots historical data
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
                logger.error("Expected list of one axis item.")
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
            title=f"{ticker.upper()} Historical Dividends",
            show_index=True,
        )
    console.print()
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "divs", div_history)


@log_start_end(log=logger)
def display_splits(
    ticker: str,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display splits and reverse splits events. [Source: Yahoo Finance]

    Parameters
    ----------
    ticker: str
        Stock ticker
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df_splits = yahoo_finance_model.get_splits(ticker)
    if df_splits.empty:
        console.print("No splits or reverse splits events found.\n")
        return

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of one axis item./n[/red]")
            return
        (ax,) = external_axes

    # Get all stock data since IPO
    df_data = yf.download(ticker, progress=False, threads=False)
    if df_data.empty:
        console.print("No stock price data available.\n")
        return

    ax.plot(df_data.index, df_data["Adj Close"], color="#FCED00")
    ax.set_ylabel("Price")
    ax.set_title(f"{ticker} splits and reverse splits events")

    ax.plot(df_data.index, df_data["Adj Close"].values)
    for index, row in df_splits.iterrows():
        val = row.values[0]
        frac = Fraction(val).limit_denominator(1000000)
        if val > 1:
            ax.axvline(index, color=theme.up_color)
            ax.annotate(
                f"{frac.numerator}:{frac.denominator}",
                (mdates.date2num(index), df_data["Adj Close"].max()),
                xytext=(10, 0),
                textcoords="offset points",
                color=theme.up_color,
            )
        else:
            ax.axvline(index, color=theme.down_color)
            ax.annotate(
                f"{frac.numerator}:{frac.denominator}",
                (mdates.date2num(index), df_data["Adj Close"].max()),
                xytext=(10, 0),
                textcoords="offset points",
                color=theme.down_color,
            )

    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()

    print_rich_table(
        df_splits,
        title=f"{ticker.upper()} splits and reverse splits",
        show_index=True,
    )
    console.print()
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "splits", df_splits)


@log_start_end(log=logger)
def display_mktcap(
    ticker: str,
    start: datetime = (datetime.now() - timedelta(days=3 * 366)),
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display market cap over time. [Source: Yahoo Finance]

    Parameters
    ----------
    ticker: str
        Stock ticker
    start: datetime
        Start date to display market cap
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df_mktcap, currency = yahoo_finance_model.get_mktcap(ticker, start)
    if df_mktcap.empty:
        console.print("No Market Cap data available.\n")
        return

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of one axis item./n[/red]")
            return
        (ax,) = external_axes

    ax.stackplot(df_mktcap.index, df_mktcap.values / 1e9, colors=[theme.up_color])
    ax.set_ylabel(f"Market Cap in Billion ({currency})")
    ax.set_title(f"{ticker} Market Cap")
    ax.set_xlim(df_mktcap.index[0], df_mktcap.index[-1])
    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "mktcap", df_mktcap)
