""" Comparison Analysis Marketwatch Model """
__docformat__ = "numpy"

from typing import Dict, List, Tuple

import pandas as pd
import requests
from bs4 import BeautifulSoup

from gamestonk_terminal.helper_funcs import get_user_agent


def get_financial_comparisons(
    all_stocks: List[str], data: str, timeframe: str, quarter: bool
) -> pd.DataFrame:
    """Get dataframe of income data from marketwatch

    Parameters
    ----------
    all_stocks : List[str]
        List of all stocks to get income for
    data : str
        Data to get. Can be income, balance or cashflow
    timeframe : str
        Quarterly or annual data or None
    quarter : bool
        Flag to use quarterly data.

    Returns
    -------
    pd.DataFrame
        Dataframe of income statements

    Raises
    ------
    ValueError
        Timeframe not valid
    """
    l_timeframes, ddf_financials = prepare_comparison_financials(
        all_stocks, data, quarter
    )

    if timeframe:
        if timeframe not in l_timeframes:
            raise ValueError(
                f"Timeframe selected should be one of {', '.join(l_timeframes)}"
            )
        s_timeframe = timeframe
    else:
        s_timeframe = l_timeframes[-1]

    print(
        f"Other available {('yearly', 'quarterly')[quarter]} timeframes are: {', '.join(l_timeframes)}\n"
    )

    return combine_similar_financials(ddf_financials, all_stocks, s_timeframe, quarter)


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

    if statement not in financial_urls:
        raise ValueError(f"type {statement} is not in {financial_urls.keys()}")

    period = "quarter" if quarter else "annual"
    text_soup_financials = BeautifulSoup(
        requests.get(
            financial_urls[statement][period].format(ticker),
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


def prepare_comparison_financials(
    similar: List[str], statement: str, quarter: bool
) -> Tuple[List[str], Dict[str, pd.DataFrame]]:
    """Builds a dictionary of DataFrame with financial statements for list of tickers

    Parameters
    ----------
    similar : List[str]
        List of similar stock tickers
    statement : str
        Either income, balance or cashflow
    quarter : bool
        Return quarterly financial statements instead of annual, by default False

    Returns
    -------
    List[str]
        List of index headers
    Dict[str, pd.DataFrame]
        A dictionary of DataFrame with financial info from list of similar tickers
    """

    financials = {
        symbol: prepare_df_financials(symbol, statement, quarter).set_index("Item")
        for symbol in similar
    }
    if quarter:
        items = financials[similar[0]].columns

    else:
        items = []
        # Get common headers between tickers
        for symbol in similar:
            if len(financials[symbol].columns) > len(items):
                items = financials[symbol].columns

        # Add columns with N/A when data is not available, to have similar columns
        for symbol in similar:
            if len(financials[symbol].columns) < len(items):
                for item in items:
                    if item not in financials[symbol].columns:
                        financials[symbol][item] = "N/A"
            financials[symbol] = financials[symbol].reindex(sorted(items), axis=1)

    return list(items), financials


def combine_similar_financials(
    financials: Dict[str, pd.DataFrame],
    similar: List[str],
    timeframe: str,
    quarter: bool,
) -> pd.DataFrame:
    """Builds a DataFrame with financial statements from a certain timeframe of a list of tickers

    Parameters
    ----------
    financials : Dict[str, pd.DataFrame]
        A dictionary of DataFrame with financial info from list of similar tickers
    similar : List[str]
        List of similar stock tickers
    statement : str
        Either income, balance or cashflow
    quarter : bool
        False for yearly data, True for quarterly
    Returns
    -------
    pd.DataFrame
        A DataFrame with financial statements from a certain timeframe of a list of tickers
    """

    # Quarter data is a bit more confusing for comparison due to the fact that
    # the reports may occur at slight different moments. Hence we rely on the
    # order set by the Market Watch website

    if quarter:
        compare_financials = financials[similar[0]][timeframe].to_frame()
        compare_financials.rename(columns={timeframe: similar[0]}, inplace=True)
        earnings_dates = [timeframe]
        idx = len(financials[similar[0]].columns) - list(
            financials[similar[0]].columns
        ).index(timeframe)

        for symbol in similar[1:]:
            report_quarter_date = list(financials[symbol].columns)[-idx]
            earnings_dates.append(report_quarter_date)
            compare_financials[symbol] = financials[symbol][report_quarter_date]

        compare_financials.columns = pd.MultiIndex.from_tuples(
            zip(earnings_dates, compare_financials.columns),
        )

    else:
        compare_financials = financials[similar[0]][timeframe].to_frame()
        compare_financials.rename(columns={timeframe: similar[0]}, inplace=True)

        for symbol in similar[1:]:
            compare_financials[symbol] = financials[symbol][timeframe]

    return compare_financials
