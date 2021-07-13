""" Market Watch View """
__docformat__ = "numpy"

import argparse
from typing import List
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
import numpy as np
from gamestonk_terminal.helper_funcs import (
    check_positive,
    get_user_agent,
    clean_data_values_to_float,
    int_or_round_float,
    parse_known_args_and_warn,
)

# pylint: disable=too-many-branches


def sec_fillings(other_args: List[str], ticker: str):
    """Display SEC filings for a given stock ticker

    Parameters
    ----------
    other_args : List[str]
        argparse other args - ["-n", "10"]
    ticker : str
        Stock ticker
    """

    parser = argparse.ArgumentParser(
        add_help=False,
        prog="sec",
        description="""
            Prints SEC filings of the company. The following fields are expected: Filing Date,
            Document Date, Type, Category, Amended, and Link. [Source: Market Watch]
        """,
    )

    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="n_num",
        type=check_positive,
        default=5,
        help="number of latest SEC filings.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        pd.set_option("display.max_colwidth", None)

        url_financials = f"https://www.marketwatch.com/investing/stock/{ticker}/financials/secfilings"

        text_soup_financials = BeautifulSoup(
            requests.get(url_financials, headers={"User-Agent": get_user_agent()}).text,
            "lxml",
        )

        # a_financials_header = list()
        df_financials = None
        b_ready_to_process_info = False
        soup_financials = text_soup_financials.findAll("tr", {"class": "table__row"})
        for financials_info in soup_financials:
            a_financials = financials_info.text.split("\n")

            # If header has been processed and dataframe created ready to populate the SEC information
            if b_ready_to_process_info:
                l_financials_info = [a_financials[2]]
                l_financials_info.extend(a_financials[5:-1])
                l_financials_info.append(financials_info.a["href"])
                # Append data values to financials
                df_financials.loc[len(df_financials.index)] = l_financials_info  # type: ignore

            if "Filing Date" in a_financials:
                l_financials_header = [a_financials[2]]
                l_financials_header.extend(a_financials[5:-1])
                l_financials_header.append("Link")

                df_financials = pd.DataFrame(columns=l_financials_header)
                df_financials.set_index("Filing Date")
                b_ready_to_process_info = True

        # Set Filing Date as index
        df_financials = df_financials.set_index("Filing Date")  # type: ignore

        print(df_financials.head(n=ns_parser.n_num).to_string())
        print("")

    except Exception as e:
        print(e)
        print("")
        return


def sean_seah_warnings(other_args: List[str], ticker: str):
    """Display Sean Seah warnings

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    ticker : str
        Stock ticker
    """

    parser = argparse.ArgumentParser(
        add_help=False,
        prog="warnings",
        description="""
            Sean Seah warnings. Check: Consistent historical earnings per share;
            Consistently high return on equity; Consistently high return on assets; 5x Net
            Income > Long-Term Debt; and Interest coverage ratio more than 3. See
            https://www.drwealth.com/gone-fishing-with-buffett-by-sean-seah/comment-page-1/
            [Source: Market Watch]
        """,
    )

    parser.add_argument(
        "-i",
        "--info",
        action="store_true",
        default=False,
        dest="b_info",
        help="provide more information about Sean Seah warning rules.",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        default=False,
        dest="b_debug",
        help="print insights into warnings calculation.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if ns_parser.b_info:
            filepath = "fundamental_analysis/info_sean_seah.txt"
            with open(filepath) as fp:
                line = fp.readline()
                while line:
                    print(f"{line.strip()}")
                    line = fp.readline()
                print("")

        # From INCOME STATEMENT, get: 'EPS (Basic)', 'Net Income', 'Interest Expense', 'EBITDA'
        url_financials = (
            f"https://www.marketwatch.com/investing/stock/{ticker}/financials/income"
        )
        text_soup_financials = BeautifulSoup(
            requests.get(url_financials, headers={"User-Agent": get_user_agent()}).text,
            "lxml",
        )

        # Define financials columns
        a_financials_header = list()
        for financials_header in text_soup_financials.findAll(
            "th", {"class": "overflow__heading"}
        ):
            a_financials_header.append(
                financials_header.text.strip("\n").split("\n")[0]
            )
        df_financials = pd.DataFrame(columns=a_financials_header[0:-1])

        # Add financials values
        soup_financials = text_soup_financials.findAll(
            lambda tag: tag.name == "tr" and tag.get("class") == ["table__row"]
        )
        soup_financials += text_soup_financials.findAll(
            "tr", {"class": "table__row is-highlighted"}
        )
        for financials_info in soup_financials:
            financials_row = financials_info.text.split("\n")
            if len(financials_row) > 5:
                for item in financials_row:
                    if bool(re.search(r"\d", item)):
                        a_financials_info = financials_info.text.split("\n")
                        l_financials = [a_financials_info[2]]
                        l_financials.extend(a_financials_info[5:-2])
                        # Append data values to financials
                        df_financials.loc[len(df_financials.index)] = l_financials
                        break

        l_fin = ["EPS (Basic)", "Net Income", "Interest Expense", "EBITDA"]

        if not all(elem in df_financials["Item"].values for elem in l_fin):
            print("The source doesn't contain all necessary financial data")
            print(url_financials, "\n")
            return

        # Set item name as index
        df_financials = df_financials.set_index("Item")

        df_sean_seah = df_financials.loc[l_fin]

        # From BALANCE SHEET, get: 'Liabilities & Shareholders\' Equity', 'Long-Term Debt'
        url_financials = f"https://www.marketwatch.com/investing/stock/{ticker}/financials/balance-sheet"
        text_soup_financials = BeautifulSoup(
            requests.get(url_financials, headers={"User-Agent": get_user_agent()}).text,
            "lxml",
        )

        # Define financials columns
        a_financials_header = list()
        for financials_header in text_soup_financials.findAll(
            "th", {"class": "overflow__heading"}
        ):
            a_financials_header.append(
                financials_header.text.strip("\n").split("\n")[0]
            )

        s_header_end_trend = "5-year trend"
        df_financials = pd.DataFrame(
            columns=a_financials_header[
                0 : a_financials_header.index(s_header_end_trend)
            ]
        )

        # Add financials values
        soup_financials = text_soup_financials.findAll(
            lambda tag: tag.name == "tr" and tag.get("class") == ["table__row"]
        )
        soup_financials += text_soup_financials.findAll(
            "tr", {"class": "table__row is-highlighted"}
        )
        for financials_info in soup_financials:
            financials_row = financials_info.text.split("\n")
            if len(financials_row) > 5:
                for item in financials_row:
                    if bool(re.search(r"\d", item)):
                        a_financials_info = financials_info.text.split("\n")
                        l_financials = [a_financials_info[2]]
                        l_financials.extend(a_financials_info[5:-2])
                        # Append data values to financials
                        df_financials.loc[len(df_financials.index)] = l_financials
                        break

        # Set item name as index
        df_financials = df_financials.set_index("Item")

        # Create dataframe to compute meaningful metrics from sean seah book
        df_sean_seah = df_sean_seah.append(
            df_financials.loc[
                [
                    "Total Shareholders' Equity",
                    "Liabilities & Shareholders' Equity",
                    "Long-Term Debt",
                ]
            ]
        )

        # Clean these metrics by parsing their values to float
        df_sean_seah = df_sean_seah.applymap(lambda x: clean_data_values_to_float(x))

        # Add additional necessary metrics
        series = (
            df_sean_seah.loc["Net Income"]
            / df_sean_seah.loc["Total Shareholders' Equity"]
        )
        series.name = "ROE"
        df_sean_seah = df_sean_seah.append(series)

        series = df_sean_seah.loc["EBITDA"] / df_sean_seah.loc["Interest Expense"]
        series.name = "Interest Coverage Ratio"
        df_sean_seah = df_sean_seah.append(series)

        series = (
            df_sean_seah.loc["Net Income"]
            / df_sean_seah.loc["Liabilities & Shareholders' Equity"]
        )
        series.name = "ROA"
        df_sean_seah = df_sean_seah.append(series)

        print(df_sean_seah.applymap(lambda x: int_or_round_float(x)).to_string())

        n_warnings = 0
        print("\nWARNINGS:")

        if np.any(df_sean_seah.loc["EPS (Basic)"].diff().dropna().values < 0):
            print("NO consistent historical earnings per share")
            n_warnings += 1
            if ns_parser.b_debug:
                sa_eps = np.array2string(
                    df_sean_seah.loc["EPS (Basic)"].values,
                    formatter={"float_kind": lambda x: int_or_round_float(x)},
                )
                print(f"   EPS: {sa_eps}")
                sa_growth = np.array2string(
                    df_sean_seah.loc["EPS (Basic)"].diff().dropna().values,
                    formatter={"float_kind": lambda x: int_or_round_float(x)},
                )
                print(f"   Growth: {sa_growth} < 0")

        if np.any(df_sean_seah.loc["ROE"].values < 0.15):
            print("NOT consistently high return on equity")
            n_warnings += 1
            if ns_parser.b_debug:
                sa_roe = np.array2string(
                    df_sean_seah.loc["ROE"].values,
                    formatter={"float_kind": lambda x: int_or_round_float(x)},
                )
                print(f"   ROE: {sa_roe} < 0.15")

        if np.any(df_sean_seah.loc["ROA"].values < 0.07):
            print("NOT consistently high return on assets")
            n_warnings += 1
            if ns_parser.b_debug:
                sa_roa = np.array2string(
                    df_sean_seah.loc["ROA"].values,
                    formatter={"float_kind": lambda x: int_or_round_float(x)},
                )
                print(f"   ROA: {sa_roa} < 0.07")

        if np.any(
            df_sean_seah.loc["Long-Term Debt"].values
            > 5 * df_sean_seah.loc["Net Income"].values
        ):
            print("5x Net Income < Long-Term Debt")
            n_warnings += 1
            if ns_parser.b_debug:
                sa_5_net_income = np.array2string(
                    5 * df_sean_seah.loc["Net Income"].values,
                    formatter={"float_kind": lambda x: int_or_round_float(x)},
                )
                print(f"   5x NET Income: {sa_5_net_income}")
                sa_long_term_debt = np.array2string(
                    df_sean_seah.loc["Long-Term Debt"].values,
                    formatter={"float_kind": lambda x: int_or_round_float(x)},
                )
                print(f"   lower than Long-Term Debt: {sa_long_term_debt}")

        if np.any(df_sean_seah.loc["Interest Coverage Ratio"].values < 3):
            print("Interest coverage ratio less than 3")
            n_warnings += 1
            if ns_parser.b_debug:
                sa_interest_coverage_ratio = np.array2string(
                    100 * df_sean_seah.loc["Interest Coverage Ratio"].values,
                    formatter={"float_kind": lambda x: int_or_round_float(x)},
                )
                print(f"   Interest Coverage Ratio: {sa_interest_coverage_ratio} < 3")

        if n_warnings == 0:
            print("None. Good stonk")

        print("")

    except Exception as e:
        print(e)
        print("")
        return
