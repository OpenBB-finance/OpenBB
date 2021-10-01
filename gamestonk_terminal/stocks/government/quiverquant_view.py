"""Quiverquant View"""
__docformat__ = "numpy"
import argparse
import os
from typing import List
import textwrap

from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from tabulate import tabulate
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from gamestonk_terminal.stocks.government import quiverquant_model
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    check_positive,
    plot_autoscale,
    export_data,
)
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal import feature_flags as gtff

# pylint: disable=C0302


def display_last_government(
    gov_type: str, past_days: int = 5, representative: str = ""
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
    """
    df_gov = quiverquant_model.get_government_trading(gov_type)

    if df_gov.empty:
        print(f"No {gov_type} trading data found\n")
        return
    print(f"\nLast transactions for {gov_type.upper()}\n")
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
            print(
                f"No representative {representative} found in the past {past_days}"
                f" days. The following are available: "
                f"{', '.join(df_gov['Representative'].str.split().str[0].unique())}"
            )
        else:
            if gtff.USE_TABULATE_DF:
                print(
                    tabulate(
                        df_gov_rep,
                        headers=df_gov_rep.columns,
                        tablefmt="fancy_grid",
                        showindex=False,
                    )
                )
            else:
                print(df_gov_rep.to_string(index=False))
    else:
        if gtff.USE_TABULATE_DF:
            print(
                tabulate(
                    df_gov,
                    headers=df_gov.columns,
                    tablefmt="fancy_grid",
                    showindex=False,
                )
            )
        else:
            print(df_gov.to_string(index=False))
    print("")


def display_government_buys(
    gov_type: str,
    past_transactions_months: int = 6,
    num: int = 10,
    raw: bool = False,
    export: str = "",
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
    """
    df_gov = quiverquant_model.get_government_trading(gov_type)

    if df_gov.empty:
        print(f"No {gov_type} trading data found\n")
        return

    df_gov = df_gov.sort_values("TransactionDate", ascending=False)

    start_date = datetime.now() - timedelta(days=past_transactions_months * 30)

    df_gov["TransactionDate"] = pd.to_datetime(df_gov["TransactionDate"])

    df_gov = df_gov[df_gov["TransactionDate"] > start_date].dropna()

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
        if gtff.USE_TABULATE_DF:
            print(
                tabulate(
                    df, headers=["Amount ($1k)"], tablefmt="fancy_grid", showindex=True
                )
            )
        else:
            print(df.to_string())
    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

    df_gov.groupby("Ticker")["upper"].sum().div(1000).sort_values(ascending=False).head(
        n=num
    ).plot(kind="bar", rot=0, ax=ax)

    ax.set_ylabel("Amount [1k $]")
    ax.set_title(
        f"Top {num} purchased stocks over last {past_transactions_months} "
        f"months (upper bound) for {gov_type.upper()}"
    )
    plt.gcf().axes[0].yaxis.get_major_formatter().set_scientific(False)
    if gtff.USE_ION:
        plt.ion()
    fig.tight_layout()
    plt.show()
    print("")
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "top_buys", df_gov)


def display_government_sells(
    gov_type: str,
    past_transactions_months: int = 6,
    num: int = 10,
    raw: bool = False,
    export: str = "",
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
    """
    df_gov = quiverquant_model.get_government_trading(gov_type)

    if df_gov.empty:
        print(f"No {gov_type} trading data found\n")
        return

    df_gov = df_gov.sort_values("TransactionDate", ascending=False)

    start_date = datetime.now() - timedelta(days=past_transactions_months * 30)

    df_gov["TransactionDate"] = pd.to_datetime(df_gov["TransactionDate"])

    df_gov = df_gov[df_gov["TransactionDate"] > start_date].dropna()

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
        if gtff.USE_TABULATE_DF:
            print(
                tabulate(
                    df, headers=["Amount ($1k)"], tablefmt="fancy_grid", showindex=True
                )
            )
        else:
            print(df.to_string())
    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

    df_gov.groupby("Ticker")["lower"].sum().div(1000).sort_values().abs().head(
        n=num
    ).plot(kind="bar", rot=0, ax=ax)
    ax.set_ylabel("Amount ($1k)")
    ax.set_title(
        f"{num} most sold stocks over last {past_transactions_months} months"
        f" (upper bound) for {gov_type}"
    )
    plt.gcf().axes[0].yaxis.get_major_formatter().set_scientific(False)
    if gtff.USE_ION:
        plt.ion()
    fig.tight_layout()
    plt.show()
    print("")
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "top_sells", df_gov)


def plot_government(government: pd.DataFrame, ticker: str, gov_type: str):
    """Plot government trading

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    ticker: str
        Ticker to plot government trading
    gov_type: str
        Type of government data between: congress, senate and house
    """
    plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

    plt.gca().fill_between(
        government["TransactionDate"].unique(),
        government.groupby("TransactionDate")["lower"].sum().values / 1000,
        government.groupby("TransactionDate")["upper"].sum().values / 1000,
    )

    plt.xlim(
        [
            government["TransactionDate"].values[0],
            government["TransactionDate"].values[-1],
        ]
    )
    plt.grid()
    plt.title(f"{gov_type.capitalize()} trading on {ticker}")
    plt.xlabel("Date")
    plt.ylabel("Amount [1k $]")
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y/%m/%d"))
    plt.gcf().autofmt_xdate()

    if gtff.USE_ION:
        plt.ion()

    plt.show()


def government_trading(other_args: List[str], ticker: str, gov_type: str):
    """Government trading

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    ticker: str
        Ticker to get congress trading data from
    gov_type: str
        Type of government data between: congress, senate and house
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog=gov_type,
        description=f"{gov_type} trading. [Source: www.quiverquant.com]",
    )
    parser.add_argument(
        "-p",
        "--past_transactions_months",
        action="store",
        dest="past_transactions_months",
        type=check_positive,
        default=6,
        help="Past transaction months",
    )

    try:
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-p")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_gov = quiverquant_model.get_government_trading(gov_type, ticker)

        if df_gov.empty:
            print(f"No {gov_type} trading data found\n")
            return

        df_gov = df_gov.sort_values("TransactionDate", ascending=False)

        start_date = datetime.now() - timedelta(
            days=ns_parser.past_transactions_months * 30
        )

        df_gov["TransactionDate"] = pd.to_datetime(df_gov["TransactionDate"])

        df_gov = df_gov[df_gov["TransactionDate"] > start_date]

        if df_gov.empty:
            print(f"No recent {gov_type} trading data found\n")
            return

        df_gov["min"] = df_gov["Range"].apply(
            lambda x: x.split("-")[0].strip("$").replace(",", "").strip()
        )
        df_gov["max"] = df_gov["Range"].apply(
            lambda x: x.split("-")[1].replace(",", "").strip().strip("$")
            if "-" in x
            else x.strip("$").replace(",", "")
        )

        df_gov["lower"] = df_gov[["min", "max", "Transaction"]].apply(
            lambda x: int(x["min"])
            if x["Transaction"] == "Purchase"
            else -int(x["max"]),
            axis=1,
        )
        df_gov["upper"] = df_gov[["min", "max", "Transaction"]].apply(
            lambda x: int(x["max"])
            if x["Transaction"] == "Purchase"
            else -int(x["min"]),
            axis=1,
        )

        df_gov = df_gov.sort_values("TransactionDate", ascending=True)

        plot_government(df_gov, ticker, gov_type)
        print("")

    except Exception as e:
        print(e, "\n")


def display_last_contracts(
    past_transaction_days: int = 2,
    num: int = 20,
    sum_contracts: bool = False,
    export: str = "",
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
    """
    df_contracts = quiverquant_model.get_government_trading("contracts")

    if df_contracts.empty:
        print("No government contracts found\n")
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
    if gtff.USE_TABULATE_DF:
        df_contracts["Description"] = df_contracts["Description"].apply(
            lambda x: "\n".join(textwrap.wrap(x, 50))
        )
        print(
            tabulate(
                df_contracts,
                headers=df_contracts.columns,
                tablefmt="fancy_grid",
                showindex=False,
                floatfmt=".2f",
            )
        )
    else:
        print(df_contracts.to_string(index=False))
    if sum_contracts:
        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        df["Date"] = pd.to_datetime(df["Date"]).dt.date
        df.groupby("Date").sum().div(1000).plot(kind="bar", rot=0, ax=ax)
        ax.set_ylabel("Amount ($1k)")
        ax.set_title("Total amount of government contracts given")

        if gtff.USE_ION:
            plt.ion()
        fig.tight_layout()
        plt.show()
    print("")
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "last_contracts", df
    )


def raw_government(other_args: List[str], ticker: str, gov_type: str):
    """Raw government trading

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    ticker: str
        Ticker to get congress trading data from
    gov_type: str
        Type of government data between: congress, senate and house
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog=gov_type,
        description=f"Raw {gov_type} trading. [Source: www.quiverquant.com]",
    )
    parser.add_argument(
        "-p",
        "--past_transactions_days",
        action="store",
        dest="past_transactions_days",
        type=check_positive,
        default=10,
        help="Past transaction days",
    )

    try:

        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-p")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_gov = quiverquant_model.get_government_trading(gov_type, ticker)

        if df_gov.empty:
            print(f"No {gov_type} trading data found\n")
            return

        df_gov = df_gov.sort_values("TransactionDate", ascending=False)
        if gov_type == "congress":
            df_gov = df_gov[
                ["TransactionDate", "Representative", "House", "Transaction", "Range"]
            ]
        else:
            df_gov = df_gov[
                ["TransactionDate", "Representative", "Transaction", "Range"]
            ]

        df_gov = df_gov[
            df_gov["TransactionDate"].isin(
                df_gov["TransactionDate"].unique()[: ns_parser.past_transactions_days]
            )
        ].rename(
            columns={
                "TransactionDate": "Transaction Date",
            }
        )

        print(df_gov.to_string(index=False))
        print("")

    except Exception as e:
        print(e, "\n")


def raw_contracts(other_args: List[str], ticker: str):
    """Raw contracts

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    ticker: str
        Ticker to get congress trading data from
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="raw_contracts",
        description="Raw contracts. [Source: www.quiverquant.com]",
    )
    parser.add_argument(
        "-p",
        "--past_transactions_days",
        action="store",
        dest="past_transactions_days",
        type=check_positive,
        default=10,
        help="Past transaction days",
    )

    try:
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-p")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_contracts = quiverquant_model.get_government_trading("contracts", ticker)

        if df_contracts.empty:
            print("No government contracts found\n")
            return

        df_contracts["Date"] = pd.to_datetime(df_contracts["Date"]).dt.date

        df_contracts.drop_duplicates(inplace=True)

        df_contracts = df_contracts[
            df_contracts["Date"].isin(
                df_contracts["Date"].unique()[: ns_parser.past_transactions_days]
            )
        ]

        df_contracts.drop_duplicates(inplace=True)

        print(df_contracts.to_string(index=False))
        print("")

    except Exception as e:
        print(e, "\n")


def contracts(other_args: List[str], ticker: str):
    """Contracts

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    ticker: str
        Ticker to get congress trading data from
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="contracts",
        description="Contracts associated with ticker. [Source: www.quiverquant.com]",
    )
    parser.add_argument(
        "-p",
        "--past_transactions_days",
        action="store",
        dest="past_transactions_days",
        type=check_positive,
        default=10,
        help="Past transaction days",
    )

    try:
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-p")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_contracts = quiverquant_model.get_government_trading("contracts", ticker)

        if df_contracts.empty:
            print("No government contracts found\n")
            return

        df_contracts["Date"] = pd.to_datetime(df_contracts["Date"]).dt.date

        df_contracts = df_contracts[
            df_contracts["Date"].isin(
                df_contracts["Date"].unique()[: ns_parser.past_transactions_days]
            )
        ]

        df_contracts.drop_duplicates(inplace=True)

        plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

        df_contracts.groupby("Date").sum().div(1000).plot(
            kind="bar", rot=0, ax=plt.gca()
        )
        plt.ylabel("Amount [1k $]")
        plt.title(f"Sum of latest government contracts to {ticker}")

        if gtff.USE_ION:
            plt.ion()

        plt.show()
        print("")

    except Exception as e:
        print(e, "\n")


def display_qtr_contracts(analysis: str, num: int):
    """Quarter contracts

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    """
    df_contracts = quiverquant_model.get_government_trading("quarter-contracts")

    if df_contracts.empty:
        print("No quarterly government contracts found\n")
        return

    tickers = quiverquant_model.analyze_qtr_contracts(analysis, num)
    if analysis in {"upmom", "downmom"}:
        if gtff.USE_TABULATE_DF:
            print(
                tabulate(
                    pd.DataFrame(tickers.values),
                    headers=["tickers"],
                    tablefmt="fancy_grid",
                    showindex=False,
                )
            )
        else:
            print(tickers.to_string())
        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
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

            ax.plot(np.arange(0, len(amounts)), amounts / 1_000_000, "-*", lw=2, ms=15)

            if len(amounts) > max_amount:
                max_amount = len(amounts)
                quarter_ticks = [
                    f"{quarter[0]} - Q{quarter[1]} " for quarter in zip(year, qtr)
                ]

        ax.set_xlim([-0.5, max_amount - 0.5])
        ax.set_xticks(np.arange(0, max_amount))
        ax.set_xticklabels(quarter_ticks)
        ax.grid()
        ax.legend(tickers)
        titles = {
            "upmom": "Highest increasing quarterly Government Contracts",
            "downmom": "Highest decreasing quarterly Government Contracts",
        }
        ax.set_title(titles[analysis])
        ax.set_xlabel("Date")
        ax.set_ylabel("Amount ($1M)")
        fig.tight_layout()
        if gtff.USE_ION:
            plt.ion()

        plt.show()

    elif analysis == "total":
        if gtff.USE_TABULATE_DF:
            print(
                tabulate(
                    tickers, headers=["Total"], tablefmt="fancy_grid", floatfmt=".2e"
                )
            )
        else:
            print(tickers.to_string())
    print("")


def qtr_contracts_hist(other_args: List[str], ticker: str):
    """Quarter contracts

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    ticker: str
        Ticker to get congress trading data from
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="qtr_contracts_hist",
        description="Quarterly-contracts historical [Source: www.quiverquant.com]",
    )
    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_contracts = quiverquant_model.get_government_trading(
            "quarter-contracts", ticker=ticker
        )

        if df_contracts.empty:
            print("No quarterly government contracts found\n")
            return

        plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

        amounts = df_contracts.sort_values(by=["Year", "Qtr"])["Amount"].values

        qtr = df_contracts.sort_values(by=["Year", "Qtr"])["Qtr"].values
        year = df_contracts.sort_values(by=["Year", "Qtr"])["Year"].values

        quarter_ticks = [
            f"{quarter[0]}" if quarter[1] == 1 else "" for quarter in zip(year, qtr)
        ]

        plt.plot(np.arange(0, len(amounts)), amounts / 1000, "-*", lw=2, ms=15)

        plt.xlim([-0.5, len(amounts) - 0.5])
        plt.xticks(np.arange(0, len(amounts)), quarter_ticks)
        plt.grid()
        plt.title(f"Quarterly Government Contracts Historical on {ticker.upper()}")
        plt.xlabel("Date")
        plt.ylabel("Amount [1k $]")

        if gtff.USE_ION:
            plt.ion()

        plt.show()
        print("")

    except Exception as e:
        print(e, "\n")


def display_top_lobbying(num: int, raw: bool = False, export: str = ""):
    """Top lobbying based on tickers that have biggest amounts for the past couple months

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    """
    df_lobbying = quiverquant_model.get_government_trading("corporate-lobbying")

    if df_lobbying.empty:
        print("No corporate lobbying found\n")
        return

    df_lobbying["Amount"] = df_lobbying.Amount.astype(float).fillna(0) / 100_000

    lobbying_by_ticker = pd.DataFrame(
        df_lobbying.groupby("Ticker")["Amount"].agg("sum")
    ).sort_values(by="Amount", ascending=False)
    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    lobbying_by_ticker.head(num).plot(kind="bar", ax=ax)
    ax.set_xlabel("Ticker")
    ax.set_ylabel("Total Amount ($100k)")
    ax.set_title(f"Corporate Lobbying Spent since {df_lobbying['Date'].min()}")
    fig.tight_layout()
    if gtff.USE_ION:
        plt.ion()

    plt.show()

    if raw:
        if gtff.USE_TABULATE_DF:
            print(
                tabulate(
                    lobbying_by_ticker.head(num),
                    headers=["Amount ($100k)"],
                    tablefmt="fancy_grid",
                    showindex=True,
                    floatfmt=".2f",
                )
            )
        else:
            print(lobbying_by_ticker.head(num).to_string())
    print("")
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "top_lobbying", df_lobbying
    )


def lobbying(other_args: List[str], ticker: str):
    """Corporate lobbying details

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    ticker: str
        Ticker to get corporate lobbying data from
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="lobbying",
        description="Lobbying details [Source: www.quiverquant.com]",
    )
    parser.add_argument(
        "-l",
        "--last",
        action="store",
        dest="last",
        type=check_positive,
        default=10,
        help="Last corporate lobbying details",
    )
    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_lobbying = quiverquant_model.get_government_trading(
            "corporate-lobbying", ticker=ticker
        )

        if df_lobbying.empty:
            print("No corporate lobbying found\n")
            return

        for _, row in (
            df_lobbying.sort_values(by=["Date"], ascending=False)
            .head(ns_parser.last)
            .iterrows()
        ):
            amount = (
                "$" + str(int(float(row["Amount"])))
                if row["Amount"] is not None
                else "N/A"
            )
            print(f"{row['Date']}: {row['Client']} {amount}")
            if row["Amount"] is not None:
                print("\t" + row["Specific_Issue"].replace("\n", " ").replace("\r", ""))
            print("")
        print("")

    except Exception as e:
        print(e, "\n")
