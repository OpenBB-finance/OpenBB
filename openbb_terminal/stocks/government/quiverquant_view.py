"""Quiverquant View"""
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib

from openbb_terminal.config_terminal import theme
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
    is_valid_axes_count,
)
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.government import quiverquant_model

# pylint: disable=C0302


logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_last_government(
    gov_type: str = "congress",
    limit: int = 5,
    representative: str = "",
    export: str = "",
):
    """Display last government trading [Source: quiverquant.com]

    Parameters
    ----------
    gov_type: str
        Type of government data between: congress, senate and house
    limit: int
        Number of days to look back
    representative: str
        Specific representative to look at
    export: str
        Format to export data
    """
    df_gov = quiverquant_model.get_last_government(gov_type, limit, representative)

    if df_gov.empty:
        if representative:
            console.print(
                f"No representative {representative} found in the past {limit}"
                f" days. The following are available: "
                f"{', '.join(df_gov['Representative'].str.split().str[0].unique())}"
            )
        else:
            console.print(f"No {gov_type} trading data found\n")
        return

    console.print(f"\nLast transactions for {gov_type.upper()}\n")

    print_rich_table(
        df_gov,
        headers=list(df_gov.columns),
        show_index=False,
        title="Representative Trading",
    )

    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "lasttrades", df_gov
    )


@log_start_end(log=logger)
def display_government_buys(
    gov_type: str = "congress",
    past_transactions_months: int = 6,
    limit: int = 10,
    raw: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Top buy government trading [Source: quiverquant.com]

    Parameters
    ----------
    gov_type: str
        Type of government data between: congress, senate and house
    past_transactions_months: int
        Number of months to get trading for
    limit: int
        Number of tickers to show
    raw: bool
        Display raw data
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None

    """
    df_gov = quiverquant_model.get_government_buys(gov_type, past_transactions_months)

    if df_gov.empty:
        console.print(f"No {gov_type} trading data found\n")
        return

    if raw:
        df = pd.DataFrame(
            df_gov.groupby("Ticker")["upper"]
            .sum()
            .div(1000)
            .sort_values(ascending=False)
            .head(n=limit)
        )
        print_rich_table(
            df, headers=["Amount ($1k)"], show_index=True, title="Top Government Buys"
        )

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    colors = theme.get_colors()
    df_gov.groupby("Ticker")["upper"].sum().div(1000).sort_values(ascending=False).head(
        n=limit
    ).plot(kind="bar", rot=0, ax=ax, color=colors)

    ax.set_ylabel("Amount [1k $]")
    ax.set_title(
        f"{gov_type.upper()}'s top {limit} purchased stocks (upper) in last {past_transactions_months} months"
    )
    # plt.gcf().axes[0].yaxis.get_major_formatter().set_scientific(False)

    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "topbuys", df_gov)


@log_start_end(log=logger)
def display_government_sells(
    gov_type: str = "congress",
    past_transactions_months: int = 6,
    limit: int = 10,
    raw: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Top sell government trading [Source: quiverquant.com]

    Parameters
    ----------
    gov_type: str
        Type of government data between: congress, senate and house
    past_transactions_months: int
        Number of months to get trading for
    limit: int
        Number of tickers to show
    raw: bool
        Display raw data
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df_gov = quiverquant_model.get_government_sells(gov_type, past_transactions_months)

    if df_gov.empty:
        console.print(f"No {gov_type} trading data found\n")
        return

    if raw:
        df = pd.DataFrame(
            df_gov.groupby("Ticker")["upper"]
            .sum()
            .div(1000)
            .sort_values(ascending=True)
            .abs()
            .head(n=limit)
        )
        print_rich_table(
            df,
            headers=["Amount ($1k)"],
            show_index=True,
            title="Top Government Trades",
        )

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    colors = theme.get_colors()
    df_gov.groupby("Ticker")["upper"].sum().div(1000).sort_values().abs().head(
        n=limit
    ).plot(kind="bar", rot=0, ax=ax, color=colors)
    ax.set_ylabel("Amount ($1k)")
    ax.set_title(
        f"{limit} most sold stocks over last {past_transactions_months} months"
        f" (upper bound) for {gov_type}"
    )

    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "topsells", df_gov)


@log_start_end(log=logger)
def display_last_contracts(
    past_transaction_days: int = 2,
    limit: int = 20,
    sum_contracts: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Last government contracts [Source: quiverquant.com]

    Parameters
    ----------
    past_transaction_days: int
        Number of days to look back
    limit: int
        Number of contracts to show
    sum_contracts: bool
        Flag to show total amount of contracts given out.
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df = quiverquant_model.get_last_contracts(past_transaction_days)

    if df.empty:
        return

    print_rich_table(
        df[:limit],
        headers=list(df.columns),
        show_index=False,
        title="Last Government Contracts",
    )
    if sum_contracts:

        # This plot has 1 axis
        if not external_axes:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        elif is_valid_axes_count(external_axes, 1):
            (ax,) = external_axes
        else:
            return

        df["Date"] = pd.to_datetime(df["Date"]).dt.date
        df.groupby("Date").sum().div(1000).plot(kind="bar", rot=0, ax=ax)
        ax.set_ylabel("Amount ($1k)")
        ax.set_title("Total amount of government contracts given")

        theme.style_primary_axis(ax)

        if not external_axes:
            theme.visualize_output()

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "lastcontracts", df)


@log_start_end(log=logger)
def plot_government(
    government: pd.DataFrame,
    symbol: str,
    gov_type: str,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Helper for plotting government trading

    Parameters
    ----------
    government: pd.DataFrame
        Data to plot
    symbol: str
        Ticker symbol to plot government trading
    gov_type: str
        Type of government data between: congress, senate and house
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    ax.fill_between(
        government["TransactionDate"].unique(),
        government.groupby("TransactionDate")["lower"].sum().values / 1000,
        government.groupby("TransactionDate")["upper"].sum().values / 1000,
    )

    ax.set_xlim(
        [
            government["TransactionDate"].values[0],
            government["TransactionDate"].values[-1],
        ]
    )
    ax.set_title(f"{gov_type.capitalize()} trading on {symbol}")
    ax.set_ylabel("Amount ($1k)")

    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()


@log_start_end(log=logger)
def display_government_trading(
    symbol: str,
    gov_type: str = "congress",
    past_transactions_months: int = 6,
    raw: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Government trading for specific ticker [Source: quiverquant.com]

    Parameters
    ----------
    symbol: str
        Ticker symbol to get congress trading data from
    gov_type: str
        Type of government data between: congress, senate and house
    past_transactions_months: int
        Number of months to get transactions for
    raw: bool
        Show raw output of trades
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df_gov = quiverquant_model.get_cleaned_government_trading(
        symbol=symbol,
        gov_type=gov_type,
        past_transactions_months=past_transactions_months,
    )

    if df_gov.empty:
        console.print(f"No {gov_type} trading data found\n")
        return

    if raw:
        print_rich_table(
            df_gov,
            headers=list(df_gov.columns),
            show_index=False,
            title=f"Government Trading for {symbol.upper()}",
        )
    else:
        plot_government(df_gov, symbol, gov_type, external_axes)

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "gtrades", df_gov)


@log_start_end(log=logger)
def display_contracts(
    symbol: str,
    past_transaction_days: int = 10,
    raw: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Show government contracts for ticker [Source: quiverquant.com]

    Parameters
    ----------
    symbol: str
        Ticker to get congress trading data from
    past_transaction_days: int
        Number of days to get transactions for
    raw: bool
        Flag to display raw data
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df_contracts = quiverquant_model.get_contracts(symbol, past_transaction_days)

    if df_contracts.empty:
        return

    if raw:
        print_rich_table(
            df_contracts,
            headers=list(df_contracts.columns),
            show_index=False,
            title=f"Government Contracts for {symbol.upper()}",
        )

    if df_contracts.Amount.abs().sum() != 0:

        # This plot has 1 axis
        if not external_axes:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        elif is_valid_axes_count(external_axes, 1):
            (ax,) = external_axes
        else:
            return

        df_contracts.groupby("Date").sum(numeric_only=True).div(1000).plot(
            kind="bar", rot=0, ax=ax
        )
        ax.set_ylabel("Amount ($1k)")
        ax.set_title(f"Sum of latest government contracts to {symbol}")

        ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(4))

        theme.style_primary_axis(ax)

        if not external_axes:
            theme.visualize_output()

    if df_contracts.Amount.abs().sum() == 0:
        console.print("Contracts found, but they are all equal to $0.00.\n")
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "contracts", df_contracts
    )


@log_start_end(log=logger)
def display_qtr_contracts(
    analysis: str = "total",
    limit: int = 5,
    raw: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Quarterly contracts [Source: quiverquant.com]

    Parameters
    ----------
    analysis: str
        Analysis to perform.  Either 'total', 'upmom' 'downmom'
    limit: int
        Number to show
    raw: bool
        Flag to display raw data
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    symbols = quiverquant_model.get_qtr_contracts(analysis, limit)

    if symbols.empty:
        return

    if analysis in ("upmom", "downmom"):
        if raw:
            print_rich_table(
                pd.DataFrame(symbols.values),
                headers=["symbols"],
                show_index=True,
                title="Quarterly Contracts",
            )
        else:
            # This plot has 1 axis
            if not external_axes:
                _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
            elif is_valid_axes_count(external_axes, 1):
                (ax,) = external_axes
            else:
                return

            max_amount = 0
            quarter_ticks = []
            df_contracts = quiverquant_model.get_government_trading("quarter-contracts")
            for symbol in symbols:
                amounts = (
                    df_contracts[df_contracts["Ticker"] == symbol]
                    .sort_values(by=["Year", "Qtr"])["Amount"]
                    .values
                )

                qtr = (
                    df_contracts[df_contracts["Ticker"] == symbol]
                    .sort_values(by=["Year", "Qtr"])["Qtr"]
                    .values
                )
                year = (
                    df_contracts[df_contracts["Ticker"] == symbol]
                    .sort_values(by=["Year", "Qtr"])["Year"]
                    .values
                )

                ax.plot(
                    np.arange(0, len(amounts)), amounts / 1_000_000, "-*", lw=2, ms=15
                )

                if len(amounts) > max_amount:
                    max_amount = len(amounts)
                    quarter_ticks = [
                        f"{quarter[0]} - Q{quarter[1]} " for quarter in zip(year, qtr)
                    ]

            ax.set_xlim([-0.5, max_amount - 0.5])
            ax.set_xticks(np.arange(0, max_amount))
            ax.set_xticklabels(quarter_ticks)
            ax.legend(symbols)
            titles = {
                "upmom": "Highest increasing quarterly Government Contracts",
                "downmom": "Highest decreasing quarterly Government Contracts",
            }
            ax.set_title(titles[analysis])
            ax.set_ylabel("Amount ($1M)")

            if not external_axes:
                theme.visualize_output()

    elif analysis == "total":
        print_rich_table(
            symbols, headers=["Total"], title="Quarterly Contracts", show_index=True
        )

    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "qtrcontracts", symbols
    )


@log_start_end(log=logger)
def display_hist_contracts(
    symbol: str,
    raw: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Show historical quarterly government contracts [Source: quiverquant.com]

    Parameters
    ----------
    symbol: str
        Ticker symbol to get congress trading data from
    raw: bool
        Flag to display raw data
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df_contracts = quiverquant_model.get_hist_contracts(symbol)

    if df_contracts.empty:
        return

    if raw:
        print_rich_table(
            df_contracts,
            headers=list(df_contracts.columns),
            floatfmt=[".0f", ".0f", ".2f"],
            title="Historical Quarterly Government Contracts",
        )

    else:
        amounts = df_contracts.sort_values(by=["Year", "Qtr"])["Amount"].values

        qtr = df_contracts.sort_values(by=["Year", "Qtr"])["Qtr"].values
        year = df_contracts.sort_values(by=["Year", "Qtr"])["Year"].values

        quarter_ticks = [
            f"{quarter[0]}" if quarter[1] == 1 else "" for quarter in zip(year, qtr)
        ]

        # This plot has 1 axis
        if not external_axes:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        elif is_valid_axes_count(external_axes, 1):
            (ax,) = external_axes
        else:
            return

        ax.plot(
            np.arange(0, len(amounts)),
            amounts / 1000,
            marker=".",
            markerfacecolor=theme.down_color,
            lw=2,
            ms=15,
        )

        ax.set_xlim([-0.5, len(amounts) - 0.5])
        ax.set_xticks(np.arange(0, len(amounts)))
        ax.set_xticklabels(quarter_ticks)

        ax.set_title(f"Historical Quarterly Government Contracts for {symbol.upper()}")
        ax.set_ylabel("Amount ($1k)")

        theme.style_primary_axis(ax)

        if not external_axes:
            theme.visualize_output()

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "histcont")


@log_start_end(log=logger)
def display_top_lobbying(
    limit: int = 10,
    raw: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Top lobbying tickers based on total spent

    Parameters
    ----------
    limit: int
        Number of tickers to show
    raw: bool
        Show raw data
    export:
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None

    """
    df_lobbying = quiverquant_model.get_top_lobbying()

    if df_lobbying.empty:
        return

    df_lobbying["Amount"] = df_lobbying.Amount.astype(float).fillna(0) / 100_000

    lobbying_by_ticker = pd.DataFrame(
        df_lobbying.groupby("Ticker")["Amount"].agg("sum")
    ).sort_values(by="Amount", ascending=False)

    if raw:
        print_rich_table(
            lobbying_by_ticker.head(limit),
            headers=["Amount ($100k)"],
            show_index=True,
            title="Top Lobbying Tickers",
        )
    else:

        # This plot has 1 axis
        if not external_axes:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        elif is_valid_axes_count(external_axes, 1):
            (ax,) = external_axes
        else:
            return

        colors = theme.get_colors()
        lobbying_by_ticker.head(limit).plot(kind="bar", ax=ax, color=colors)
        ax.set_xlabel("Ticker")
        ax.set_ylabel("Total Amount ($100k)")
        ax.set_title(f"Corporate Lobbying Spent since {df_lobbying['Date'].min()}")

        theme.style_primary_axis(ax)

        if not external_axes:
            theme.visualize_output()

    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "lobbying", df_lobbying
    )


@log_start_end(log=logger)
def display_lobbying(symbol: str, limit: int = 10):
    """Corporate lobbying details

    Parameters
    ----------
    symbol: str
        Ticker symbol to get corporate lobbying data from
    limit: int
        Number of events to show
    """
    df_lobbying = quiverquant_model.get_lobbying(symbol, limit)

    if df_lobbying.empty:
        return

    for _, row in df_lobbying.iterrows():
        amount = (
            "$" + str(int(float(row["Amount"]))) if row["Amount"] is not None else "N/A"
        )
        console.print(f"{row['Date']}: {row['Client']} {amount}")
        if (row["Amount"] is not None) and (row["Specific_Issue"] is not None):
            console.print(
                "\t" + row["Specific_Issue"].replace("\n", " ").replace("\r", "")
            )
        console.print("")
    console.print("")
