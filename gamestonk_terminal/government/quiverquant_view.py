import argparse
from typing import List
import pandas as pd
from datetime import datetime, timedelta
from gamestonk_terminal.government import quiverquant_model
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    check_positive,
    plot_autoscale,
)
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal import feature_flags as gtff


def last_congress(other_args: List[str]):
    """Last congress trading

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="last_congress",
        description="""
            Last congress trading. [Source: www.quiverquant.com]
        """,
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
        help="Congress representative",
    )

    try:
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-p")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_congress = quiverquant_model.get_congress_trading()

        if df_congress.empty:
            print("No congress trading data found\n")
            return

        df_congress = df_congress.sort_values("TransactionDate", ascending=False)

        df_congress = df_congress[
            df_congress["TransactionDate"].isin(
                df_congress["TransactionDate"].unique()[
                    : ns_parser.past_transactions_days
                ]
            )
        ]

        df_congress = df_congress[
            [
                "TransactionDate",
                "Ticker",
                "Representative",
                "Transaction",
                "House",
                "Range",
                "ReportDate",
            ]
        ].rename(
            columns={"TransactionDate": "Transaction Date", "ReportDate": "Report Date"}
        )

        if ns_parser.representative:
            df_congress_rep = df_congress[
                df_congress["Representative"].str.split().str[0]
                == ns_parser.representative
            ]

            if df_congress_rep.empty:
                print(
                    f"No representative {ns_parser.representative} found in the past {ns_parser.past_transactions_days}"
                    f" days. The following are available: "
                    f"{', '.join(df_congress['Representative'].str.split().str[0].unique())}"
                )
            else:
                print(df_congress_rep.to_string(index=False))
        else:
            print(df_congress.to_string(index=False))
        print("")

    except Exception as e:
        print(e, "\n")


def buy_congress(other_args: List[str]):
    """Top buy congress trading

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="buy_congress",
        description="""
            Top buy congress trading. [Source: www.quiverquant.com]
        """,
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

        df_congress = quiverquant_model.get_congress_trading()

        if df_congress.empty:
            print("No congress trading data found\n")
            return

        df_congress = df_congress.sort_values("TransactionDate", ascending=False)

        start_date = datetime.now() - timedelta(
            days=ns_parser.past_transactions_months * 30
        )

        df_congress["TransactionDate"] = pd.to_datetime(df_congress["TransactionDate"])

        df_congress = df_congress[df_congress["TransactionDate"] > start_date].dropna()

        df_congress["min"] = df_congress["Range"].apply(
            lambda x: x.split("-")[0].strip("$").replace(",", "").strip()
        )
        df_congress["max"] = df_congress["Range"].apply(
            lambda x: x.split("-")[1].replace(",", "").strip().strip("$")
            if "-" in x
            else x.strip("$").replace(",", "")
        )

        df_congress["lower"] = df_congress[["min", "max", "Transaction"]].apply(
            lambda x: float(x["min"])
            if x["Transaction"] == "Purchase"
            else -float(x["max"]),
            axis=1,
        )
        df_congress["upper"] = df_congress[["min", "max", "Transaction"]].apply(
            lambda x: float(x["max"])
            if x["Transaction"] == "Purchase"
            else -float(x["min"]),
            axis=1,
        )

        df_congress = df_congress.sort_values("TransactionDate", ascending=True)

        plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

        df_congress.groupby("Ticker")["upper"].sum().sort_values(ascending=False).head(
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


def sell_congress(other_args: List[str]):
    """Top sell congress trading

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="sell_congress",
        description="""
            Top sell congress trading. [Source: www.quiverquant.com]
        """,
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

        df_congress = quiverquant_model.get_congress_trading()

        if df_congress.empty:
            print("No congress trading data found\n")
            return

        df_congress = df_congress.sort_values("TransactionDate", ascending=False)

        start_date = datetime.now() - timedelta(
            days=ns_parser.past_transactions_months * 30
        )

        df_congress["TransactionDate"] = pd.to_datetime(df_congress["TransactionDate"])

        df_congress = df_congress[df_congress["TransactionDate"] > start_date].dropna()

        df_congress["min"] = df_congress["Range"].apply(
            lambda x: x.split("-")[0].strip("$").replace(",", "").strip()
        )
        df_congress["max"] = df_congress["Range"].apply(
            lambda x: x.split("-")[1].replace(",", "").strip().strip("$")
            if "-" in x
            else x.strip("$").replace(",", "")
        )

        df_congress["lower"] = df_congress[["min", "max", "Transaction"]].apply(
            lambda x: float(x["min"])
            if x["Transaction"] == "Purchase"
            else -float(x["max"]),
            axis=1,
        )
        df_congress["upper"] = df_congress[["min", "max", "Transaction"]].apply(
            lambda x: float(x["max"])
            if x["Transaction"] == "Purchase"
            else -float(x["min"]),
            axis=1,
        )

        df_congress = df_congress.sort_values("TransactionDate", ascending=True)

        plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

        df_congress.groupby("Ticker")["lower"].sum().sort_values().abs().head(
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


def plot_congress(congress: pd.DataFrame, ticker: str):
    """Plot congress trading

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    ticker: str
        Ticker to plot congress trading
    """
    plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

    plt.gca().fill_between(
        congress["TransactionDate"].unique(),
        congress.groupby("TransactionDate")["lower"].sum().values / 1000,
        congress.groupby("TransactionDate")["upper"].sum().values / 1000,
    )

    plt.xlim(
        [congress["TransactionDate"].values[0], congress["TransactionDate"].values[-1]]
    )
    plt.grid()
    plt.title(f"Congress trading on {ticker}")
    plt.xlabel("Date")
    plt.ylabel("Amount [1k $]")
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y/%m/%d"))
    plt.gcf().autofmt_xdate()

    if gtff.USE_ION:
        plt.ion()

    plt.show()


def congress(other_args: List[str], ticker: str):
    """Congress trading

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    ticker: str
        Ticker to get congress trading data from
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="congress",
        description="""
            Congress trading. [Source: www.quiverquant.com]
        """,
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

        df_congress = quiverquant_model.get_congress_trading(ticker)

        if df_congress.empty:
            print("No congress trading data found\n")
            return

        df_congress = df_congress.sort_values("TransactionDate", ascending=False)

        start_date = datetime.now() - timedelta(
            days=ns_parser.past_transactions_months * 30
        )

        df_congress["TransactionDate"] = pd.to_datetime(df_congress["TransactionDate"])

        df_congress = df_congress[df_congress["TransactionDate"] > start_date]

        df_congress["min"] = df_congress["Range"].apply(
            lambda x: x.split("-")[0].strip("$").replace(",", "").strip()
        )
        df_congress["max"] = df_congress["Range"].apply(
            lambda x: x.split("-")[1].replace(",", "").strip().strip("$")
            if "-" in x
            else x.strip("$").replace(",", "")
        )

        df_congress["lower"] = df_congress[["min", "max", "Transaction"]].apply(
            lambda x: int(x["min"])
            if x["Transaction"] == "Purchase"
            else -int(x["max"]),
            axis=1,
        )
        df_congress["upper"] = df_congress[["min", "max", "Transaction"]].apply(
            lambda x: int(x["max"])
            if x["Transaction"] == "Purchase"
            else -int(x["min"]),
            axis=1,
        )

        df_congress = df_congress.sort_values("TransactionDate", ascending=True)

        plot_congress(df_congress, ticker)

        print("")

    except Exception as e:
        print(e, "\n")
