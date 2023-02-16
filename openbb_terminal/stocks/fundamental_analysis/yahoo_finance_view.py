""" Yahoo Finance View """
__docformat__ = "numpy"

import logging
import os
from fractions import Fraction
from typing import List, Optional

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf

from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    is_valid_axes_count,
    lambda_long_number_format,
    plot_autoscale,
    print_rich_table,
)
from openbb_terminal.helpers_denomination import transform as transform_by_denomination
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.fundamental_analysis import yahoo_finance_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_info(symbol: str, export: str = "", sheet_name: Optional[str] = None):
    """Yahoo Finance ticker info
    Parameters
    ----------
    symbol : str
        Fundamental analysis ticker symbol
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    """
    summary = ""
    df_info = yahoo_finance_model.get_info(symbol)
    if "Long business summary" in df_info.index:
        summary = df_info.loc["Long business summary"].values[0]
        df_info = df_info.drop(index=["Long business summary"])

    if not df_info.empty:
        print_rich_table(
            df_info,
            headers=list(df_info.columns),
            show_index=True,
            title=f"{symbol.upper()} Info",
        )
    else:
        logger.error("Invalid data")
        console.print("[red]Invalid data[/red]\n")
        return

    if summary:
        console.print("Business Summary:")
        console.print(summary)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "info",
        df_info,
        sheet_name,
    )


@log_start_end(log=logger)
def display_shareholders(
    symbol: str,
    holder: str = "institutional",
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Yahoo Finance ticker shareholders
    Parameters
    ----------
    symbol : str
        Fundamental analysis ticker symbol
    holder: str
        Shareholder table to get.  Can be major/institutional/mutualfund
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    """
    df = yahoo_finance_model.get_shareholders(symbol, holder)
    if holder == "major":
        df.columns = ["", ""]
    if "Date Reported" in df.columns:
        df["Date Reported"] = df["Date Reported"].apply(
            lambda x: x.strftime("%Y-%m-%d")
        )
    title = f"{holder.title()} Holders"
    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title=f"{symbol.upper()} {title}",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"{holder}_holders",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
def display_dividends(
    symbol: str,
    limit: int = 12,
    plot: bool = True,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display historical dividends

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    limit: int
        Number to show
    plot: bool
        Plots historical data
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.fa.divs_chart("AAPL")
    """
    div_history = yahoo_finance_model.get_dividends(symbol)
    if div_history.empty:
        return

    if plot:
        # This plot has 1 axis
        if not external_axes:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        elif is_valid_axes_count(external_axes, 1):
            (ax,) = external_axes
        else:
            return

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
        ax.set_ylabel("Amount Paid ($)")
        ax.set_title(f"Dividend History for {symbol}")
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
            title=f"{symbol.upper()} Historical Dividends",
            show_index=True,
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "divs",
        div_history,
        sheet_name,
    )


@log_start_end(log=logger)
def display_splits(
    symbol: str,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display splits and reverse splits events. [Source: Yahoo Finance]

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df_splits = yahoo_finance_model.get_splits(symbol)
    if df_splits.empty:
        console.print("No splits or reverse splits events found.\n")
        return

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    # Get all stock data since IPO
    df_data = yf.download(symbol, progress=False, threads=False)
    if df_data.empty:
        console.print("No stock price data available.\n")
        return

    ax.plot(df_data.index, df_data["Adj Close"], color="#FCED00")
    ax.set_ylabel("Price")
    ax.set_title(f"{symbol} splits and reverse splits events")

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
        title=f"{symbol.upper()} splits and reverse splits",
        show_index=True,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "splits",
        df_splits,
        sheet_name,
    )


@log_start_end(log=logger)
def display_mktcap(
    symbol: str,
    start_date: Optional[str] = None,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display market cap over time. [Source: Yahoo Finance]

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    start_date: Optional[str]
        Initial date (e.g., 2021-10-01). Defaults to 3 years back
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    df_mktcap, currency = yahoo_finance_model.get_mktcap(symbol, start_date)
    if df_mktcap.empty:
        console.print("No Market Cap data available.\n")
        return

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    ax.stackplot(df_mktcap.index, df_mktcap.values / 1e9, colors=[theme.up_color])
    ax.set_ylabel(f"Market Cap in Billion ({currency})")
    ax.set_title(f"{symbol} Market Cap")
    ax.set_xlim(df_mktcap.index[0], df_mktcap.index[-1])
    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "mktcap",
        df_mktcap,
        sheet_name,
    )


@log_start_end(log=logger)
def display_fundamentals(
    symbol: str,
    statement: str,
    limit: int = 12,
    ratios: bool = False,
    plot: Optional[list] = None,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Display tickers balance sheet, income statement or cash-flow

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    statement: str
        Possible values are:

        - cash-flow
        - financials for Income
        - balance-sheet

    limit: int
        Number of periods to show
    ratios: bool
        Shows percentage change
    plot: list
        List of row labels to plot
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    """

    fundamentals = yahoo_finance_model.get_financials(symbol, statement, ratios)

    if statement == "balance-sheet":
        title_str = "Balance Sheet"
    elif statement == "financials":
        title_str = "Income Statement"
    elif statement == "cash-flow":
        title_str = "Cash Flow Statement"

    if fundamentals is None:
        return

    if fundamentals.empty:
        # The empty data frame error handling done in model
        return

    symbol_currency = yahoo_finance_model.get_currency(symbol)

    if plot:
        plot = [x.lower() for x in plot]
        rows_plot = len(plot)
        fundamentals_plot_data = fundamentals.transpose().fillna(-1)
        fundamentals_plot_data.columns = fundamentals_plot_data.columns.str.lower()
        if "ttm" in list(fundamentals_plot_data.index):
            fundamentals_plot_data = fundamentals_plot_data.drop(["ttm"])
        fundamentals_plot_data = fundamentals_plot_data.sort_index()

        if not ratios:
            maximum_value = fundamentals_plot_data[plot[0].replace("_", " ")].max()
            (df_rounded, denomination) = transform_by_denomination(
                fundamentals_plot_data, maxValue=maximum_value
            )
            if denomination == "Units":
                denomination = ""
        else:
            df_rounded = fundamentals_plot_data
            denomination = ""

        if rows_plot == 1:
            fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
            ax.bar(df_rounded.index, df_rounded[plot[0].replace("_", " ")])
            title = (
                f"{plot[0].replace('_', ' ').capitalize()} QoQ Growth of {symbol.upper()}"
                if ratios
                else f"{plot[0].replace('_', ' ').capitalize()} of {symbol.upper()} {denomination}"
            )
            plt.title(title)
            theme.style_primary_axis(ax)
            theme.visualize_output()
        else:
            fig, axes = plt.subplots(rows_plot)
            for i in range(rows_plot):
                axes[i].bar(
                    df_rounded.index, df_rounded[plot[i].replace("_", " ")], width=0.5
                )
                axes[i].set_title(f"{plot[i].replace('_', ' ')} {denomination}")
            theme.style_primary_axis(axes[0])
            fig.autofmt_xdate()
    else:
        # Snake case to english
        fundamentals.index = fundamentals.index.to_series().apply(
            lambda x: x.replace("_", " ").title()
        )
        # Readable numbers
        formatted_df = fundamentals.applymap(lambda_long_number_format).fillna("-")
        print_rich_table(
            formatted_df.iloc[:, :limit].applymap(lambda x: "-" if x == "nan" else x),
            show_index=True,
            title=f"{symbol} {title_str} Currency: {symbol_currency}",
        )
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        statement,
        fundamentals,
        sheet_name,
    )


@log_start_end(log=logger)
def display_earnings(
    symbol: str, limit: int, export: str = "", sheet_name: Optional[str] = None
):
    """

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    limit: int
        Number of periods to show
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data

    """
    earnings = yahoo_finance_model.get_earnings_history(symbol)
    if earnings.empty:
        return
    print_rich_table(
        earnings.head(limit),
        headers=earnings.columns,
        title=f"Historical Earnings for {symbol}",
    )
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "earnings_yf",
        earnings,
        sheet_name,
    )
