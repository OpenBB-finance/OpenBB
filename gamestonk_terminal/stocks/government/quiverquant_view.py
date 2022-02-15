"""Quiverquant View"""
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

import textwrap
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib

from gamestonk_terminal.config_terminal import theme
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
)
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.stocks.government import quiverquant_model

# pylint: disable=C0302


logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_last_government(
    gov_type: str, past_days: int = 5, representative: str = "", export: str = ""
):
    """Display last government trading [Source: quiverquant.com]

    Parameters
    ----------
    gov_type: str
        Type of government data between: congress, senate and house
    past_days: int
        Number of days to look back
    representative: str
        Specific representative to look at
    export: str
        Format to export data
    """
    df_gov = quiverquant_model.get_government_trading(gov_type)

    if df_gov.empty:
        console.print(f"No {gov_type} trading data found\n")
        return
    console.print(f"\nLast transactions for {gov_type.upper()}\n")
    df_gov = df_gov.sort_values("TransactionDate", ascending=False)

    df_gov = df_gov[
        df_gov["TransactionDate"].isin(df_gov["TransactionDate"].unique()[:past_days])
    ]

    if gov_type == "congress":
        df_gov = df_gov[
            [
                "TransactionDate",
                "Ticker",
                "Representative",
                "Transaction",
                "Range",
                "House",
                "ReportDate",
            ]
        ].rename(
            columns={
                "TransactionDate": "Transaction Date",
                "ReportDate": "Report Date",
            }
        )
    else:
        df_gov = df_gov[
            [
                "TransactionDate",
                "Ticker",
                "Representative",
                "Transaction",
                "Range",
            ]
        ].rename(columns={"TransactionDate": "Transaction Date"})

    if representative:
        df_gov_rep = df_gov[
            df_gov["Representative"].str.split().str[0] == representative
        ]

        if df_gov_rep.empty:
            console.print(
                f"No representative {representative} found in the past {past_days}"
                f" days. The following are available: "
                f"{', '.join(df_gov['Representative'].str.split().str[0].unique())}"
            )
        else:
            print_rich_table(
                df_gov_rep,
                headers=list(df_gov_rep.columns),
                show_index=False,
                title="Representative Trading",
            )
    else:
        print_rich_table(
            df_gov,
            headers=list(df_gov.columns),
            show_index=False,
            title="Representative Trading",
        )
    console.print("")
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "lasttrades", df_gov
    )


@log_start_end(log=logger)
def display_government_buys(
    gov_type: str,
    past_transactions_months: int = 6,
    num: int = 10,
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
    num: int
        Number of tickers to show
    raw: bool
        Display raw data
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None

    """
    df_gov = quiverquant_model.get_government_trading(gov_type)

    if df_gov.empty:
        console.print(f"No {gov_type} trading data found\n")
        return

    df_gov = df_gov.sort_values("TransactionDate", ascending=False)
    start_date = datetime.now() - timedelta(days=past_transactions_months * 30)

    df_gov["TransactionDate"] = pd.to_datetime(df_gov["TransactionDate"])

    df_gov = df_gov[df_gov["TransactionDate"] > start_date].dropna()
    # Catch bug where error shown for purchase of >5,000,000
    df_gov["Range"] = df_gov["Range"].apply(
        lambda x: "$5,000,001-$5,000,001" if x == ">$5,000,000" else x
    )
    df_gov["min"] = df_gov["Range"].apply(
        lambda x: x.split("-")[0].strip("$").replace(",", "").strip()
    )
    df_gov["max"] = df_gov["Range"].apply(
        lambda x: x.split("-")[1].replace(",", "").strip().strip("$")
        if "-" in x
        else x.strip("$").replace(",", "")
    )
    df_gov["lower"] = df_gov[["min", "max", "Transaction"]].apply(
        lambda x: float(x["min"])
        if x["Transaction"] == "Purchase"
        else -float(x["max"]),
        axis=1,
    )
    df_gov["upper"] = df_gov[["min", "max", "Transaction"]].apply(
        lambda x: float(x["max"])
        if x["Transaction"] == "Purchase"
        else -float(x["min"]),
        axis=1,
    )

    df_gov = df_gov.sort_values("TransactionDate", ascending=True)
    if raw:
        df = pd.DataFrame(
            df_gov.groupby("Ticker")["upper"]
            .sum()
            .div(1000)
            .sort_values(ascending=False)
            .head(n=num)
        )
        print_rich_table(
            df, headers=["Amount ($1k)"], show_index=True, title="Top Government Buys"
        )

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if len(external_axes) != 1:
            console.print("[red]Expected list of one axis item./n[/red]")
            return
        (ax,) = external_axes

    colors = theme.get_colors()
    df_gov.groupby("Ticker")["upper"].sum().div(1000).sort_values(ascending=False).head(
        n=num
    ).plot(kind="bar", rot=0, ax=ax, color=colors)

    ax.set_ylabel("Amount [1k $]")
    ax.set_title(
        f"Top {num} purchased stocks over last {past_transactions_months} "
        f"months (upper bound) for {gov_type.upper()}"
    )
    # plt.gcf().axes[0].yaxis.get_major_formatter().set_scientific(False)

    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()

    console.print("")

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "topbuys", df_gov)


@log_start_end(log=logger)
def display_government_sells(
    gov_type: str,
    past_transactions_months: int = 6,
    num: int = 10,
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
    num: int
        Number of tickers to show
    raw: bool
        Display raw data
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df_gov = quiverquant_model.get_government_trading(gov_type)

    if df_gov.empty:
        console.print(f"No {gov_type} trading data found\n")
        return

    df_gov = df_gov.sort_values("TransactionDate", ascending=False)

    start_date = datetime.now() - timedelta(days=past_transactions_months * 30)

    df_gov["TransactionDate"] = pd.to_datetime(df_gov["TransactionDate"])

    df_gov = df_gov[df_gov["TransactionDate"] > start_date].dropna()
    df_gov["Range"] = df_gov["Range"].apply(
        lambda x: "$5,000,001-$5,000,001" if x == ">$5,000,000" else x
    )
    df_gov["min"] = df_gov["Range"].apply(
        lambda x: x.split("-")[0]
        .strip("$")
        .replace(",", "")
        .strip()
        .replace(">$", "")
        .strip()
    )
    df_gov["max"] = df_gov["Range"].apply(
        lambda x: x.split("-")[1]
        .replace(",", "")
        .strip()
        .strip("$")
        .replace(">$", "")
        .strip()
        if "-" in x
        else x.strip("$").replace(",", "").replace(">$", "").strip()
    )

    df_gov["lower"] = df_gov[["min", "max", "Transaction"]].apply(
        lambda x: float(x["min"])
        if x["Transaction"] == "Purchase"
        else -float(x["max"]),
        axis=1,
    )
    df_gov["upper"] = df_gov[["min", "max", "Transaction"]].apply(
        lambda x: float(x["max"])
        if x["Transaction"] == "Purchase"
        else -float(x["min"]),
        axis=1,
    )

    df_gov = df_gov.sort_values("TransactionDate", ascending=True)
    if raw:
        df = pd.DataFrame(
            df_gov.groupby("Ticker")["upper"]
            .sum()
            .div(1000)
            .sort_values(ascending=True)
            .abs()
            .head(n=num)
        )
        print_rich_table(
            df, headers=["Amount ($1k)"], show_index=True, title="Top Government Trades"
        )

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if len(external_axes) != 1:
            console.print("[red]Expected list of one axis item./n[/red]")
            return
        (ax,) = external_axes

    colors = theme.get_colors()
    df_gov.groupby("Ticker")["upper"].sum().div(1000).sort_values().abs().head(
        n=num
    ).plot(kind="bar", rot=0, ax=ax, color=colors)
    ax.set_ylabel("Amount ($1k)")
    ax.set_title(
        f"{num} most sold stocks over last {past_transactions_months} months"
        f" (upper bound) for {gov_type}"
    )

    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()

    console.print("")
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "topsells", df_gov)


@log_start_end(log=logger)
def display_last_contracts(
    past_transaction_days: int = 2,
    num: int = 20,
    sum_contracts: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Last government contracts [Source: quiverquant.com]

    Parameters
    ----------
    past_transaction_days: int
        Number of days to look back
    num: int
        Number of contracts to show
    sum_contracts: bool
        Flag to show total amount of contracts given out.
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df_contracts = quiverquant_model.get_government_trading("contracts")

    if df_contracts.empty:
        console.print("No government contracts found\n")
        return

    df_contracts.sort_values("Date", ascending=False)

    df_contracts["Date"] = pd.to_datetime(df_contracts["Date"])

    df_contracts.drop_duplicates(inplace=True)
    df = df_contracts.copy()
    df_contracts = df_contracts[
        df_contracts["Date"].isin(df_contracts["Date"].unique()[:past_transaction_days])
    ]

    df_contracts = df_contracts[["Date", "Ticker", "Amount", "Description", "Agency"]][
        :num
    ]
    df_contracts["Description"] = df_contracts["Description"].apply(
        lambda x: "\n".join(textwrap.wrap(x, 50))
    )
    print_rich_table(
        df_contracts,
        headers=list(df_contracts.columns),
        show_index=False,
        title="Last Government Contracts",
    )
    if sum_contracts:

        # This plot has 1 axis
        if not external_axes:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        else:
            if len(external_axes) != 1:
                console.print("[red]Expected list of one axis item./n[/red]")
                return
            (ax,) = external_axes

        df["Date"] = pd.to_datetime(df["Date"]).dt.date
        df.groupby("Date").sum().div(1000).plot(kind="bar", rot=0, ax=ax)
        ax.set_ylabel("Amount ($1k)")
        ax.set_title("Total amount of government contracts given")

        theme.style_primary_axis(ax)

        if not external_axes:
            theme.visualize_output()

    console.print("")
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "lastcontracts", df)


@log_start_end(log=logger)
def plot_government(
    government: pd.DataFrame,
    ticker: str,
    gov_type: str,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Helper for plotting government trading

    Parameters
    ----------
    government: pd.DataFrame
        Data to plot
    ticker: str
        Ticker to plot government trading
    gov_type: str
        Type of government data between: congress, senate and house
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if len(external_axes) != 1:
            console.print("[red]Expected list of one axis item./n[/red]")
            return
        (ax,) = external_axes

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
    ax.set_title(f"{gov_type.capitalize()} trading on {ticker}")
    ax.set_ylabel("Amount ($1k)")

    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()


@log_start_end(log=logger)
def display_government_trading(
    ticker: str,
    gov_type: str,
    past_transactions_months: int = 6,
    raw: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Government trading for specific ticker [Source: quiverquant.com]

    Parameters
    ----------
    ticker: str
        Ticker to get congress trading data from
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
    df_gov = quiverquant_model.get_government_trading(gov_type, ticker)

    if df_gov.empty:
        console.print(f"No {gov_type} trading data found\n")
        return

    df_gov = df_gov.sort_values("TransactionDate", ascending=False)

    start_date = datetime.now() - timedelta(days=past_transactions_months * 30)

    df_gov["TransactionDate"] = pd.to_datetime(df_gov["TransactionDate"])

    df_gov = df_gov[df_gov["TransactionDate"] > start_date]

    if df_gov.empty:
        console.print(f"No recent {gov_type} trading data found\n")
        return

    df_gov["min"] = df_gov["Range"].apply(
        lambda x: x.split("-")[0].strip("$").replace(",", "").strip()
    )
    df_gov["max"] = df_gov["Range"].apply(
        lambda x: x.split("-")[1].replace(",", "").strip().strip("$")
        if "-" in x
        else x.strip("$").replace(",", "").split("\n")[0]
    )

    df_gov["lower"] = df_gov[["min", "max", "Transaction"]].apply(
        lambda x: int(float(x["min"]))
        if x["Transaction"] == "Purchase"
        else -int(float(x["max"])),
        axis=1,
    )
    df_gov["upper"] = df_gov[["min", "max", "Transaction"]].apply(
        lambda x: int(float(x["max"]))
        if x["Transaction"] == "Purchase"
        else -1 * int(float(x["min"])),
        axis=1,
    )

    df_gov = df_gov.sort_values("TransactionDate", ascending=True)

    if raw:
        print_rich_table(
            df_gov,
            headers=list(df_gov.columns),
            show_index=False,
            title=f"Government Trading for {ticker.upper()}",
        )
    else:
        plot_government(df_gov, ticker, gov_type, external_axes)

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "gtrades", df_gov)
    console.print("")


@log_start_end(log=logger)
def display_contracts(
    ticker: str,
    past_transaction_days: int,
    raw: bool,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Show government contracts for ticker [Source: quiverquant.com]

    Parameters
    ----------
    ticker: str
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
    df_contracts = quiverquant_model.get_government_trading("contracts", ticker)

    if df_contracts.empty:
        console.print("No government contracts found\n")
        return

    df_contracts["Date"] = pd.to_datetime(df_contracts["Date"]).dt.date

    df_contracts = df_contracts[
        df_contracts["Date"].isin(df_contracts["Date"].unique()[:past_transaction_days])
    ]

    df_contracts.drop_duplicates(inplace=True)

    if raw:
        print_rich_table(
            df_contracts,
            headers=list(df_contracts.columns),
            show_index=False,
            title=f"Government Contracts for {ticker.upper()}",
        )

    else:

        # This plot has 1 axis
        if not external_axes:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        else:
            if len(external_axes) != 1:
                console.print("[red]Expected list of one axis item./n[/red]")
                return
            (ax,) = external_axes

        df_contracts.groupby("Date").sum().div(1000).plot(kind="bar", rot=0, ax=ax)
        ax.set_ylabel("Amount ($1k)")
        ax.set_title(f"Sum of latest government contracts to {ticker}")

        ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(4))

        theme.style_primary_axis(ax)

        if not external_axes:
            theme.visualize_output()

    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "contracts", df_contracts
    )
    console.print("")


@log_start_end(log=logger)
def display_qtr_contracts(
    analysis: str,
    num: int,
    raw: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Quarterly contracts [Source: quiverquant.com]

    Parameters
    ----------
    analysis: str
        Analysis to perform.  Either 'total', 'upmom' 'downmom'
    num: int
        Number to show
    raw: bool
        Flag to display raw data
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df_contracts = quiverquant_model.get_government_trading("quarter-contracts")

    if df_contracts.empty:
        console.print("No quarterly government contracts found\n")
        return

    tickers = quiverquant_model.analyze_qtr_contracts(analysis, num)
    if analysis in ("upmom", "downmom"):
        if raw:
            print_rich_table(
                pd.DataFrame(tickers.values),
                headers=["tickers"],
                show_index=False,
                title="Quarterly Contracts",
            )
        else:
            # This plot has 1 axis
            if not external_axes:
                _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
            else:
                if len(external_axes) != 1:
                    console.print("[red]Expected list of one axis item./n[/red]")
                    return
                (ax,) = external_axes

            max_amount = 0
            quarter_ticks = []
            for symbol in tickers:
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
            ax.legend(tickers)
            titles = {
                "upmom": "Highest increasing quarterly Government Contracts",
                "downmom": "Highest decreasing quarterly Government Contracts",
            }
            ax.set_title(titles[analysis])
            ax.set_ylabel("Amount ($1M)")

            if not external_axes:
                theme.visualize_output()

    elif analysis == "total":
        print_rich_table(tickers, headers=["Total"], title="Quarterly Contracts")

    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "qtrcontracts", df_contracts
    )
    console.print("")


@log_start_end(log=logger)
def display_hist_contracts(
    ticker: str,
    raw: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Show historical quarterly government contracts [Source: quiverquant.com]

    Parameters
    ----------
    ticker: str
        Ticker to get congress trading data from
    raw: bool
        Flag to display raw data
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df_contracts = quiverquant_model.get_government_trading(
        "quarter-contracts", ticker=ticker
    )

    if df_contracts.empty:
        console.print("No quarterly government contracts found\n")
        return

    amounts = df_contracts.sort_values(by=["Year", "Qtr"])["Amount"].values

    qtr = df_contracts.sort_values(by=["Year", "Qtr"])["Qtr"].values
    year = df_contracts.sort_values(by=["Year", "Qtr"])["Year"].values

    quarter_ticks = [
        f"{quarter[0]}" if quarter[1] == 1 else "" for quarter in zip(year, qtr)
    ]

    if raw:
        print_rich_table(
            df_contracts,
            headers=list(df_contracts.columns),
            title="Historical Quarterly Government Contracts",
        )

    else:

        # This plot has 1 axis
        if not external_axes:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        else:
            if len(external_axes) != 1:
                console.print("[red]Expected list of one axis item./n[/red]")
                return
            (ax,) = external_axes

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

        ax.set_title(f"Historical Quarterly Government Contracts for {ticker.upper()}")
        ax.set_ylabel("Amount ($1k)")

        theme.style_primary_axis(ax)

        if not external_axes:
            theme.visualize_output()

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "histcont")
    console.print("")


@log_start_end(log=logger)
def display_top_lobbying(
    num: int,
    raw: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Top lobbying tickers based on total spent

    Parameters
    ----------
    num: int
        Number of tickers to show
    raw: bool
        Show raw data
    export:
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None

    """
    df_lobbying = quiverquant_model.get_government_trading("corporate-lobbying")

    if df_lobbying.empty:
        console.print("No corporate lobbying found\n")
        return

    df_lobbying["Amount"] = df_lobbying.Amount.astype(float).fillna(0) / 100_000

    lobbying_by_ticker = pd.DataFrame(
        df_lobbying.groupby("Ticker")["Amount"].agg("sum")
    ).sort_values(by="Amount", ascending=False)

    if raw:
        print_rich_table(
            lobbying_by_ticker.head(num),
            headers=["Amount ($100k)"],
            show_index=True,
            title="Top Lobbying Tickers",
        )
    else:

        # This plot has 1 axis
        if not external_axes:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        else:
            if len(external_axes) != 1:
                console.print("[red]Expected list of one axis item./n[/red]")
                return
            (ax,) = external_axes

        colors = theme.get_colors()
        lobbying_by_ticker.head(num).plot(kind="bar", ax=ax, color=colors)
        ax.set_xlabel("Ticker")
        ax.set_ylabel("Total Amount ($100k)")
        ax.set_title(f"Corporate Lobbying Spent since {df_lobbying['Date'].min()}")

        theme.style_primary_axis(ax)

        if not external_axes:
            theme.visualize_output()

    console.print("")
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "lobbying", df_lobbying
    )


@log_start_end(log=logger)
def display_lobbying(ticker: str, num: int = 10):
    """Corporate lobbying details

    Parameters
    ----------
    ticker: str
        Ticker to get corporate lobbying data from
    num: int
        Number of events to show
    """
    df_lobbying = quiverquant_model.get_government_trading(
        "corporate-lobbying", ticker=ticker
    )

    if df_lobbying.empty:
        console.print("No corporate lobbying found\n")
        return

    for _, row in (
        df_lobbying.sort_values(by=["Date"], ascending=False).head(num).iterrows()
    ):
        amount = (
            "$" + str(int(float(row["Amount"]))) if row["Amount"] is not None else "N/A"
        )
        console.print(f"{row['Date']}: {row['Client']} {amount}")
        if row["Amount"] is not None:
            console.print(
                "\t" + row["Specific_Issue"].replace("\n", " ").replace("\r", "")
            )
        console.print("")
    console.print("")
