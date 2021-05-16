import argparse
from typing import List
from datetime import datetime, timedelta
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

        df_gov.groupby("Ticker")["upper"].sum().sort_values(ascending=False).head(
            n=ns_parser.top_num
        ).plot(kind="bar", rot=0)
        plt.ylabel("Amount [$]")
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

        df_gov.groupby("Ticker")["lower"].sum().sort_values().abs().head(
            n=ns_parser.top_num
        ).plot(kind="bar", rot=0)
        plt.ylabel("Amount [$]")
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
        prog=gov_type,
        description=f"{gov_type} trading. [Source: www.quiverquant.com]",
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
        ]

        print(df_gov.to_string(index=False))
        print("")

    except Exception as e:
        print(e, "\n")
