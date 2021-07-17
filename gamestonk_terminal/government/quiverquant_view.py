import argparse
from typing import List
from datetime import datetime, timedelta
import numpy as np
from sklearn import linear_model
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from gamestonk_terminal.government import quiverquant_model
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    check_positive,
    plot_autoscale,
)
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal import feature_flags as gtff

# pylint: disable=C0302


def last_government(other_args: List[str], gov_type: str):
    """Last government trading

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    gov_type: str
        Type of government data between: congress, senate and house
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="last_" + gov_type,
        description=f"Last {gov_type} trading. [Source: www.quiverquant.com]",
    )
    parser.add_argument(
        "-p",
        "--past_transactions_days",
        action="store",
        dest="past_transactions_days",
        type=check_positive,
        default=5,
        help="Past transaction days",
    )
    parser.add_argument(
        "-r",
        "--representative",
        action="store",
        dest="representative",
        type=str,
        default="",
        help="Representative",
    )

    try:
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-p")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_gov = quiverquant_model.get_government_trading(gov_type)

        if df_gov.empty:
            print(f"No {gov_type} trading data found\n")
            return

        df_gov = df_gov.sort_values("TransactionDate", ascending=False)

        df_gov = df_gov[
            df_gov["TransactionDate"].isin(
                df_gov["TransactionDate"].unique()[: ns_parser.past_transactions_days]
            )
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

        if ns_parser.representative:
            df_gov_rep = df_gov[
                df_gov["Representative"].str.split().str[0] == ns_parser.representative
            ]

            if df_gov_rep.empty:
                print(
                    f"No representative {ns_parser.representative} found in the past {ns_parser.past_transactions_days}"
                    f" days. The following are available: "
                    f"{', '.join(df_gov['Representative'].str.split().str[0].unique())}"
                )
            else:
                print(df_gov_rep.to_string(index=False))
        else:
            print(df_gov.to_string(index=False))
        print("")

    except Exception as e:
        print(e, "\n")


def buy_government(other_args: List[str], gov_type: str):
    """Top buy government trading

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    gov_type: str
        Type of government data between: congress, senate and house
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="buy_" + gov_type,
        description=f"Top buy {gov_type} trading. [Source: www.quiverquant.com]",
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
    parser.add_argument(
        "-t",
        "--top",
        action="store",
        dest="top_num",
        type=check_positive,
        default=10,
        help="Number of top tickers",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_gov = quiverquant_model.get_government_trading(gov_type)

        if df_gov.empty:
            print(f"No {gov_type} trading data found\n")
            return

        df_gov = df_gov.sort_values("TransactionDate", ascending=False)

        start_date = datetime.now() - timedelta(
            days=ns_parser.past_transactions_months * 30
        )

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

        plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

        df_gov.groupby("Ticker")["upper"].sum().div(1000).sort_values(
            ascending=False
        ).head(n=ns_parser.top_num).plot(kind="bar", rot=0)
        plt.ylabel("Amount [1k $]")
        plt.title(
            f"Top {ns_parser.top_num} most bought stocks since last {ns_parser.past_transactions_months} "
            "months (upper bound)"
        )
        plt.gcf().axes[0].yaxis.get_major_formatter().set_scientific(False)
        if gtff.USE_ION:
            plt.ion()

        plt.show()
        print("")

    except Exception as e:
        print(e, "\n")


def sell_government(other_args: List[str], gov_type: str):
    """Top sell government trading

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    gov_type: str
        Type of government data between: congress, senate and house
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="sell_" + gov_type,
        description=f"Top sell {gov_type} trading. [Source: www.quiverquant.com]",
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
    parser.add_argument(
        "-t",
        "--top",
        action="store",
        dest="top_num",
        type=check_positive,
        default=10,
        help="Number of top tickers",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_gov = quiverquant_model.get_government_trading(gov_type)

        if df_gov.empty:
            print(f"No {gov_type} trading data found\n")
            return

        df_gov = df_gov.sort_values("TransactionDate", ascending=False)

        start_date = datetime.now() - timedelta(
            days=ns_parser.past_transactions_months * 30
        )

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

        plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

        df_gov.groupby("Ticker")["lower"].sum().div(1000).sort_values().abs().head(
            n=ns_parser.top_num
        ).plot(kind="bar", rot=0)
        plt.ylabel("Amount [1k $]")
        plt.title(
            f"Top {ns_parser.top_num} most sold stocks since last {ns_parser.past_transactions_months} months"
            " (upper bound)"
        )
        plt.gcf().axes[0].yaxis.get_major_formatter().set_scientific(False)
        if gtff.USE_ION:
            plt.ion()

        plt.show()
        print("")

    except Exception as e:
        print(e, "\n")


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


def last_contracts(other_args: List[str]):
    """Last contracts

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="last_contracts",
        description="Last contracts. [Source: www.quiverquant.com]",
    )
    parser.add_argument(
        "-p",
        "--past_transactions_days",
        action="store",
        dest="past_transactions_days",
        type=check_positive,
        default=2,
        help="Past transaction days",
    )
    parser.add_argument(
        "-l",
        "--limit",
        action="store",
        dest="limit_contracts",
        type=check_positive,
        default=20,
        help="Limit of contracts to display",
    )

    try:
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-p")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_contracts = quiverquant_model.get_government_trading("contracts")

        if df_contracts.empty:
            print("No government contracts found\n")
            return

        df_contracts.sort_values("Date", ascending=False)

        df_contracts["Date"] = pd.to_datetime(df_contracts["Date"])

        df_contracts.drop_duplicates(inplace=True)

        df_contracts = df_contracts[
            df_contracts["Date"].isin(
                df_contracts["Date"].unique()[: ns_parser.past_transactions_days]
            )
        ]

        df_contracts = df_contracts[
            ["Date", "Ticker", "Amount", "Description", "Agency"]
        ][: ns_parser.limit_contracts]

        print(df_contracts.to_string(index=False))
        print("")

    except Exception as e:
        print(e, "\n")


def sum_contracts(other_args: List[str]):
    """Sum contracts

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="sum_contracts",
        description="Sum latest contracts. [Source: www.quiverquant.com]",
    )

    try:
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-p")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_contracts = quiverquant_model.get_government_trading("contracts")

        if df_contracts.empty:
            print("No government contracts found\n")
            return

        df_contracts["Date"] = pd.to_datetime(df_contracts["Date"]).dt.date

        df_contracts.drop_duplicates(inplace=True)

        plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

        df_contracts.groupby("Date").sum().div(1000).plot(
            kind="bar", rot=0, ax=plt.gca()
        )
        plt.ylabel("Amount [1k $]")
        plt.title("Sum of latest government contracts")

        if gtff.USE_ION:
            plt.ion()

        plt.show()
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


def qtr_contracts(other_args: List[str]):
    """Quarter contracts

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="qtr_contracts",
        description="Quarterly-contracts, best regression slope. [Source: www.quiverquant.com]",
    )
    parser.add_argument(
        "-t",
        "--top",
        action="store",
        dest="top",
        type=check_positive,
        default=5,
        help="Top promising stocks with best quarterly-contracts momentum",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_contracts = quiverquant_model.get_government_trading("quarter-contracts")

        if df_contracts.empty:
            print("No quarterly government contracts found\n")
            return

        df_coef = pd.DataFrame(columns=["Ticker", "Coef"])

        for symbol in df_contracts["Ticker"].unique():
            # Create linear regression object
            regr = linear_model.LinearRegression()

            amounts = (
                df_contracts[df_contracts["Ticker"] == symbol]
                .sort_values(by=["Year", "Qtr"])["Amount"]
                .values
            )

            # Train the model using the training sets
            regr.fit(np.arange(0, len(amounts)).reshape(-1, 1), amounts)

            df_coef = df_coef.append(
                {"Ticker": symbol, "Coef": regr.coef_[0]}, ignore_index=True
            )

        plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

        tickers = df_coef.sort_values(by=["Coef"], ascending=False).head(ns_parser.top)[
            "Ticker"
        ]

        max_amount = 0
        quarter_ticks = list()
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

            plt.plot(np.arange(0, len(amounts)), amounts / 1000, "-*", lw=2, ms=15)

            if len(amounts) > max_amount:
                max_amount = len(amounts)
                quarter_ticks = [
                    f"{quarter[0]} - {quarter[1]} Qtr" for quarter in zip(year, qtr)
                ]

        plt.xlim([-0.5, max_amount - 0.5])
        plt.xticks(np.arange(0, max_amount), quarter_ticks)
        plt.grid()
        plt.legend(tickers)
        plt.title("Quarterly Government Contracts - Top promising stocks")
        plt.xlabel("Date")
        plt.ylabel("Amount [1k $]")

        if gtff.USE_ION:
            plt.ion()

        plt.show()
        print("")

    except Exception as e:
        print(e, "\n")


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


def top_lobbying(other_args: List[str]):
    """Top lobbying based on tickers that have biggest amounts for the past couple months

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="top_lobbying",
        description="Top lobbying. [Source: www.quiverquant.com]",
    )
    parser.add_argument(
        "-t",
        "--top",
        action="store",
        dest="top",
        type=check_positive,
        default=10,
        help="Top corporate lobbying tickers with biggest amounts",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_lobbying = quiverquant_model.get_government_trading("corporate-lobbying")

        if df_lobbying.empty:
            print("No corporate lobbying found\n")
            return

        d_lobbying = {}
        for symbol in df_lobbying["Ticker"].unique():
            d_lobbying[symbol] = sum(
                float(amount)
                for amount in df_lobbying[df_lobbying["Ticker"] == symbol]
                .replace(np.nan, 0)["Amount"]
                .values
            )

        df_amount = pd.DataFrame.from_dict(
            d_lobbying, orient="index", columns=["Amount"]
        ).sort_values(by=["Amount"], ascending=False)

        plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

        plt.bar(
            df_amount.head(ns_parser.top).index,
            df_amount.head(ns_parser.top).values.flatten() / 1000,
        )
        plt.xlabel("Ticker")
        plt.ylabel("Sum Amount [1k $]")
        plt.title(
            f"Total amount spent on corporate lobbying since {df_lobbying['Date'].min()}"
        )

        if gtff.USE_ION:
            plt.ion()

        plt.show()
        print("")

    except Exception as e:
        print(e, "\n")


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
