""" Fundamental Analysis Market Watch Model """
__docformat__ = "numpy"

import requests
import pandas as pd
from bs4 import BeautifulSoup

from gamestonk_terminal.helper_funcs import (
    get_user_agent,
)


def prepare_df_financials(
    ticker: str, statement: str, quarter: bool = False
) -> pd.DataFrame:
    """Builds a DataFrame with financial statements for a given company

    Parameters
    ----------
    ticker : str
        Company's stock ticker
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

    if statement not in financial_urls.keys():
        raise ValueError(f"type {statement} is not in {financial_urls.keys()}")

    if quarter:
        period = "quarter"
    else:
        period = "annual"

    text_soup_financials = BeautifulSoup(
        requests.get(
            financial_urls[statement][period].format(ticker),
            headers={"User-Agent": get_user_agent()},
        ).text,
        "lxml",
    )

    # Define financials columns
    a_financials_header = list()
    for financials_header in text_soup_financials.findAll(
        "th", {"class": "overflow__heading"}
    ):
        a_financials_header.append(financials_header.text.strip("\n").split("\n")[0])

    s_header_end_trend = ("5-year trend", "5- qtr trend")[quarter]

    if s_header_end_trend not in a_financials_header:
        return pd.DataFrame()

    df_financials = pd.DataFrame(
        columns=a_financials_header[0 : a_financials_header.index(s_header_end_trend)]
    )

    find_table = text_soup_financials.findAll(
        "div", {"class": "element element--table table--fixed financials"}
    )

    if not find_table:
        return df_financials

    financials_rows = find_table[0].findAll(
        "tr", {"class": ["table__row is-highlighted", "table__row"]}
    )

    for a_row in financials_rows:
        constructed_row = list()
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
