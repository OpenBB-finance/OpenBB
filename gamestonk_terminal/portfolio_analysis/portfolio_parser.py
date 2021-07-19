"""Portfolio parser module"""
__docformat__ = "numpy"

import os
import argparse
from typing import List, Tuple
from tabulate import tabulate
import pandas as pd
import yfinance as yf
from gamestonk_terminal.helper_funcs import check_valid_path, parse_known_args_and_warn

# pylint: disable=no-member,unsupported-assignment-operation,unsubscriptable-object


def load_csv_portfolio(other_args: List[str]) -> Tuple[str, pd.DataFrame]:
    """Load portfolio from csv

    Parameters
    ----------
    other_args: List[str]
        Argparse arguments

    Returns
    ----------
    portfolio_name : str
        Portfolio name
    portfolio : pd.DataFrame
        Portfolio dataframe
    """
    parser = argparse.ArgumentParser(
        prog="load",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Function to get portfolio from predefined csv file inside portfolios folder",
    )
    parser.add_argument(
        "-p",
        "--path",
        default="my_portfolio",
        type=check_valid_path,
        help="Path to csv file",
        dest="path",
    )
    parser.add_argument(
        "--no_sector",
        action="store_true",
        default=False,
        help="Add sector to dataframe",
        dest="sector",
    )
    parser.add_argument(
        "--no_last_price",
        action="store_true",
        default=False,
        help="Add last price from yfinance",
        dest="last_price",
    )
    parser.add_argument(
        "--nan",
        action="store_true",
        default=False,
        help="Show nan entries from csv",
        dest="show_nan",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return "", pd.DataFrame()

        full_path = os.path.abspath(
            os.path.join(
                "gamestonk_terminal",
                "portfolio_analysis",
                "portfolios",
                f"{ns_parser.path}.csv",
            )
        )
        df = pd.read_csv(full_path)

        if not ns_parser.sector:
            df["sector"] = df.apply(
                lambda row: yf.Ticker(row.Ticker).info["sector"]
                if "sector" in yf.Ticker(row.Ticker).info.keys()
                else "yf Other",
                axis=1,
            )

        if not ns_parser.last_price:
            df["last_price"] = df.apply(
                lambda row: yf.Ticker(row.Ticker)
                .history(period="1d")["Close"][-1]
                .round(2),
                axis=1,
            )
            df["value"] = df["Shares"] * df["last_price"]

        if not ns_parser.show_nan:
            df = df.dropna(axis=1)

        print(tabulate(df, tablefmt="fancy_grid", headers=df.columns))
        print("")
        return ns_parser.path, df

    except Exception as e:
        print(e, "\n")
        return "", pd.DataFrame()


def breakdown_by_group(portfolio: pd.DataFrame, other_args: List[str]):
    """Breakdown of portfolio by a specified group

    Parameters
    ----------
    portfolio: pd.DataFrame
        Dataframe of portfolio generated from menu
    other_args: List[str]
        Argparse arguments
    """
    parser = argparse.ArgumentParser(
        prog="groupby",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Displays portfolio grouped by a given column",
    )
    parser.add_argument(
        "-g",
        "--group",
        type=str,
        dest="group",
        default="Ticker",
        help="Column to group by",
    )

    # The following arguments will be used in a later PR for customizable 'reports'

    # The --func flag will need to be tested that it exists for pandas groupby
    # parser.add_argument("-f",
    #                     "--func",
    #                     type=str,
    #                     dest="function",
    #                     help="Aggregate function to apply to groups"
    #                     )
    # parser.add_argument("-d",
    #                     "--display",
    #                     default = None,
    #                     help = "Columns to display",
    #                     dest="cols")

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        group_column = ns_parser.group
        if group_column not in portfolio.columns:
            print(f"The column {group_column} is not found in your portfolio data")
            return

        grouped_df = pd.DataFrame(portfolio.groupby(group_column).agg(sum)["value"])
        print(
            tabulate(grouped_df, headers=[group_column, "value"], tablefmt="fancy_grid")
        )
        print("")

        # The following will be used to display certain columns (i.e show Dollars or Percents)
        # valid_columns = []
        # if ns_parser.cols:
        #     for col in ns_parser.cols:
        #         if col in portfolio.columns:
        #             valid_columns.append(col)
        #         else:
        #             print(f"{col} not in portfolio columns")
        # if valid_columns:
        #     valid_columns = ["Shares"]

    except Exception as e:
        print(e, "\n")
