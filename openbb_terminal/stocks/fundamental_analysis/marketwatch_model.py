""" Fundamental Analysis Market Watch Model """
__docformat__ = "numpy"

import logging
import re
from typing import List, Tuple

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    get_user_agent,
    lambda_clean_data_values_to_float,
    lambda_int_or_round_float,
    request,
)

# pylint: disable=too-many-branches


logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def prepare_df_financials(
    symbol: str, statement: str, quarter: bool = False
) -> pd.DataFrame:
    """Builds a DataFrame with financial statements for a given company

    Parameters
    ----------
    symbol : str
        Company's stock symbol
    statement : str
        Either income, balance or cashflow
    quarter : bool, optional
        Return quarterly financial statements instead of annual, by default False

    Returns
    -------
    pd.DataFrame
        A DataFrame with financial info

    Raises
    ------
    ValueError
        If statement is not income, balance or cashflow
    """
    financial_urls = {
        "income": {
            "quarter": "https://www.marketwatch.com/investing/stock/{}/financials/income/quarter",
            "annual": "https://www.marketwatch.com/investing/stock/{}/financials/income",
        },
        "balance": {
            "quarter": "https://www.marketwatch.com/investing/stock/{}/financials/balance-sheet/quarter",
            "annual": "https://www.marketwatch.com/investing/stock/{}/financials/balance-sheet",
        },
        "cashflow": {
            "quarter": "https://www.marketwatch.com/investing/stock/{}/financials/cash-flow/quarter",
            "annual": "https://www.marketwatch.com/investing/stock/{}/financials/cash-flow",
        },
    }

    if statement not in financial_urls:
        raise ValueError(f"type {statement} is not in {financial_urls.keys()}")

    period = "quarter" if quarter else "annual"

    text_soup_financials = BeautifulSoup(
        request(
            financial_urls[statement][period].format(symbol),
            headers={"User-Agent": get_user_agent()},
        ).text,
        "lxml",
    )

    # Define financials columns
    a_financials_header = [
        financials_header.text.strip("\n").split("\n")[0]
        for financials_header in text_soup_financials.findAll(
            "th", {"class": "overflow__heading"}
        )
    ]

    s_header_end_trend = ("5-year trend", "5- qtr trend")[quarter]

    if s_header_end_trend not in a_financials_header:
        return pd.DataFrame()

    if s_header_end_trend in a_financials_header:
        df_financials = pd.DataFrame(
            columns=a_financials_header[
                0 : a_financials_header.index(s_header_end_trend)
            ]
        )
    else:
        return pd.DataFrame()

    find_table = text_soup_financials.findAll(
        "div", {"class": "element element--table table--fixed financials"}
    )

    if not find_table:
        return df_financials

    financials_rows = find_table[0].findAll(
        "tr", {"class": ["table__row is-highlighted", "table__row"]}
    )

    for a_row in financials_rows:
        constructed_row = []
        financial_columns = a_row.findAll(
            "td", {"class": ["overflow__cell", "overflow__cell fixed--column"]}
        )

        if not financial_columns:
            continue

        for a_column in financial_columns:
            column_to_text = a_column.text.strip()
            if "\n" in column_to_text:
                column_to_text = column_to_text.split("\n")[0]

            if column_to_text == "":
                continue
            constructed_row.append(column_to_text)

        df_financials.loc[len(df_financials)] = constructed_row

    return df_financials


@log_start_end(log=logger)
def get_sean_seah_warnings(
    symbol: str, debug: bool = False
) -> Tuple[pd.DataFrame, List[str], List[str]]:
    """Get financial statements and prepare Sean Seah warnings

    Parameters
    ----------
    symbol : str
        Ticker to look at
    debug : bool, optional
        Whether or not to return debug messages.
        Defaults to False.

    Returns
    -------
    pd.DataFrame
        Dataframe of financials
    List[str]
        List of warnings
    List[str]
        List of debug messages
    """

    # From INCOME STATEMENT, get: 'EPS (Basic)', 'Net Income', 'Interest Expense', 'EBITDA'
    url_financials = (
        f"https://www.marketwatch.com/investing/stock/{symbol}/financials/income"
    )
    text_soup_financials = BeautifulSoup(
        request(url_financials, headers={"User-Agent": get_user_agent()}).text,
        "lxml",
    )

    # Define financials columns
    a_financials_header = [
        financials_header.text.strip("\n").split("\n")[0]
        for financials_header in text_soup_financials.findAll(
            "th", {"class": "overflow__heading"}
        )
    ]

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
        return pd.DataFrame(), [], []

    # Set item name as index
    df_financials = df_financials.set_index("Item")

    df_sean_seah = df_financials.loc[l_fin]

    # From BALANCE SHEET, get: 'Liabilities & Shareholders\' Equity', 'Long-Term Debt'
    url_financials = (
        f"https://www.marketwatch.com/investing/stock/{symbol}/financials/balance-sheet"
    )
    text_soup_financials = BeautifulSoup(
        request(url_financials, headers={"User-Agent": get_user_agent()}).text,
        "lxml",
    )

    # Define financials columns
    a_financials_header = []
    for financials_header in text_soup_financials.findAll(
        "th", {"class": "overflow__heading"}
    ):
        a_financials_header.append(financials_header.text.strip("\n").split("\n")[0])

    s_header_end_trend = "5-year trend"
    df_financials = pd.DataFrame(
        columns=a_financials_header[0 : a_financials_header.index(s_header_end_trend)]
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
    transfer_cols = [
        "Total Shareholders' Equity",
        "Liabilities & Shareholders' Equity",
        "Long-Term Debt",
    ]
    df_sean_seah = pd.concat([df_sean_seah, df_financials.loc[transfer_cols]])

    # Clean these metrics by parsing their values to float
    df_sean_seah = df_sean_seah.applymap(lambda x: lambda_clean_data_values_to_float(x))
    df_sean_seah = df_sean_seah.T

    # Add additional necessary metrics
    df_sean_seah["ROE"] = (
        df_sean_seah["Net Income"] / df_sean_seah["Total Shareholders' Equity"]
    )

    df_sean_seah["Interest Coverage Ratio"] = (
        df_sean_seah["EBITDA"] / df_sean_seah["Interest Expense"]
    )

    df_sean_seah["ROA"] = (
        df_sean_seah["Net Income"] / df_sean_seah["Liabilities & Shareholders' Equity"]
    )
    df_sean_seah = df_sean_seah.sort_index()
    df_sean_seah = df_sean_seah.T

    n_warnings = 0
    warnings = []
    debugged_warnings = []

    if np.any(df_sean_seah.loc["EPS (Basic)"].diff().dropna().values < 0):
        warnings.append("No consistent historical earnings per share")
        n_warnings += 1
        if debug:
            sa_eps = np.array2string(
                df_sean_seah.loc["EPS (Basic)"].values,
                formatter={"float_kind": lambda x: lambda_int_or_round_float(x)},
            )
            sa_growth = np.array2string(
                df_sean_seah.loc["EPS (Basic)"].diff().dropna().values,
                formatter={"float_kind": lambda x: lambda_int_or_round_float(x)},
            )
            debugged_warnings.append(f"\tEPS: {sa_eps}\n\tGrowth: {sa_growth} < 0")

    if np.any(df_sean_seah.loc["ROE"].values < 0.15):
        warnings.append("NOT consistently high return on equity")
        n_warnings += 1
        if debug:
            sa_roe = np.array2string(
                df_sean_seah.loc["ROE"].values,
                formatter={"float_kind": lambda x: lambda_int_or_round_float(x)},
            )
            debugged_warnings.append(f"\tROE: {sa_roe} < 0.15")

    if np.any(df_sean_seah.loc["ROA"].values < 0.07):
        warnings.append("NOT consistently high return on assets")
        n_warnings += 1
        if debug:
            sa_roa = np.array2string(
                df_sean_seah.loc["ROA"].values,
                formatter={"float_kind": lambda x: lambda_int_or_round_float(x)},
            )
            debugged_warnings.append(f"\tROA: {sa_roa} < 0.07")

    if np.any(
        df_sean_seah.loc["Long-Term Debt"].values
        > 5 * df_sean_seah.loc["Net Income"].values
    ):
        warnings.append("5x Net Income < Long-Term Debt")
        n_warnings += 1
        if debug:
            sa_5_net_income = np.array2string(
                5 * df_sean_seah.loc["Net Income"].values,
                formatter={"float_kind": lambda x: lambda_int_or_round_float(x)},
            )
            sa_long_term_debt = np.array2string(
                df_sean_seah.loc["Long-Term Debt"].values,
                formatter={"float_kind": lambda x: lambda_int_or_round_float(x)},
            )
            debugged_warnings.append(
                f"\t5x NET Income: {sa_5_net_income}\n\tlower than Long-Term Debt: {sa_long_term_debt}"
            )

    if np.any(df_sean_seah.loc["Interest Coverage Ratio"].values < 3):
        warnings.append("Interest coverage ratio less than 3")
        n_warnings += 1
        if debug:
            sa_interest_coverage_ratio = np.array2string(
                100 * df_sean_seah.loc["Interest Coverage Ratio"].values,
                formatter={"float_kind": lambda x: lambda_int_or_round_float(x)},
            )
            debugged_warnings.append(
                f"\tInterest Coverage Ratio: {sa_interest_coverage_ratio} < 3"
            )

    return (
        df_sean_seah.applymap(lambda x: lambda_int_or_round_float(x)),
        warnings,
        debugged_warnings,
    )
