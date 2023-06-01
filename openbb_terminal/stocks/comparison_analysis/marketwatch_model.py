""" Comparison Analysis Marketwatch Model """
__docformat__ = "numpy"

import logging
from datetime import datetime
from typing import Dict, List, Tuple

import pandas as pd
from bs4 import BeautifulSoup

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_user_agent, request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_financial_comparisons(
    symbols: List[str],
    data: str = "income",
    timeframe: str = str(datetime.now().year - 1),
    quarter: bool = False,
) -> pd.DataFrame:
    """Get dataframe of income data from marketwatch.

    Parameters
    ----------
    symbols : List[str]
        List of tickers to compare. Enter tickers you want to see as shown below:
        ["TSLA", "AAPL", "NFLX", "BBY"]
    data : str
        Data to get. Can be income, balance or cashflow
    timeframe : str
        What year/quarter to look at
    quarter : bool
        Flag to use quarterly data.

    Returns
    -------
    pd.DataFrame
        Dataframe of financial statements

    Raises
    ------
    ValueError
        Timeframe not valid
    """
    l_timeframes, ddf_financials = prepare_comparison_financials(symbols, data, quarter)

    if timeframe and l_timeframes:
        if (timeframe == str(datetime.now().year - 1)) and quarter:
            timeframe = l_timeframes[-1]
        elif timeframe not in l_timeframes:
            raise ValueError(
                f"Timeframe selected should be one of {', '.join(l_timeframes)}"
            )
        s_timeframe = timeframe
    else:
        if len(l_timeframes) == 0:
            return pd.DataFrame()
        s_timeframe = l_timeframes[-1]

    console.print(
        f"Other available {('yearly', 'quarterly')[quarter]} timeframes are:"
        f" {', '.join(l_timeframes)}\n"
    )

    return combine_similar_financials(ddf_financials, symbols, s_timeframe, quarter)


@log_start_end(log=logger)
def get_income_comparison(
    similar: List[str],
    timeframe: str = str(datetime.today().year - 1),
    quarter: bool = False,
) -> pd.DataFrame:
    """Get income data. [Source: Marketwatch].

    Parameters
    ----------
    similar : List[str]
        List of tickers to compare.
        Comparable companies can be accessed through
        finnhub_peers(), finviz_peers(), polygon_peers().
    timeframe : str
        Column header to compare
    quarter : bool, optional
        Whether to use quarterly statements, by default False
    export : str, optional
        Format to export data

    Returns
    -------
    pd.DataFrame
        Dataframe of income statements
    """
    df_financials_compared = get_financial_comparisons(
        similar, "income", timeframe, quarter
    )

    return df_financials_compared


@log_start_end(log=logger)
def get_balance_comparison(
    similar: List[str],
    timeframe: str = str(datetime.today().year - 1),
    quarter: bool = False,
) -> pd.DataFrame:
    """Get balance data. [Source: Marketwatch].

    Parameters
    ----------
    similar : List[str]
        List of tickers to compare.
        Comparable companies can be accessed through
        finnhub_peers(), finviz_peers(), polygon_peers().
    timeframe : str
        Column header to compare
    quarter : bool, optional
        Whether to use quarterly statements, by default False
    export : str, optional
        Format to export data

    Returns
    -------
    pd.DataFrame
        Dataframe of balance comparisons
    """
    df_financials_compared = get_financial_comparisons(
        similar, "balance", timeframe, quarter
    )

    return df_financials_compared


@log_start_end(log=logger)
def get_cashflow_comparison(
    similar: List[str],
    timeframe: str = str(datetime.today().year - 1),
    quarter: bool = False,
) -> pd.DataFrame:
    """Get cashflow data. [Source: Marketwatch]

    Parameters
    ----------
    similar : List[str]
        List of tickers to compare.
        Comparable companies can be accessed through
        finnhub_peers(), finviz_peers(), polygon_peers().
    timeframe : str
        Column header to compare
    quarter : bool, optional
        Whether to use quarterly statements, by default False
    export : str, optional
        Format to export data

    Returns
    -------
    pd.DataFrame
        Dataframe of cashflow comparisons
    """
    df_financials_compared = get_financial_comparisons(
        similar, "cashflow", timeframe, quarter
    )

    return df_financials_compared


@log_start_end(log=logger)
def prepare_df_financials(
    ticker: str, statement: str, quarter: bool = False
) -> pd.DataFrame:
    """Builds a DataFrame with financial statements for a given company.

    Parameters
    ----------
    ticker: str
        Company's stock ticker
    statement: str
        Financial statement to get. Can be income, balance or cashflow
    quarter: bool, optional
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

    try:
        period = "quarter" if quarter else "annual"
        text_soup_financials = BeautifulSoup(
            request(
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
        if s_header_end_trend in a_financials_header:
            df_financials = pd.DataFrame(
                columns=a_financials_header[
                    0 : a_financials_header.index(s_header_end_trend)
                ]
            )
        else:
            # We don't have the data we need for whatever reason, so return an empty DataFrame
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
    except Exception:
        df_financials = pd.DataFrame()

    return df_financials


@log_start_end(log=logger)
def prepare_comparison_financials(
    similar: List[str], statement: str, quarter: bool = False
) -> Tuple[List[str], Dict[str, pd.DataFrame]]:
    """Builds a dictionary of DataFrame with financial statements for list of tickers

    Parameters
    ----------
    similar : List[str]
        List of similar stock tickers
    statement : str
        Financial statement to get. Can be income, balance or cashflow
    quarter : bool
        Return quarterly financial statements instead of annual, by default False

    Returns
    -------
    Tuple[List[str], Dict[str, pd.DataFrame]]
        List of index headers,
        A dictionary of DataFrame with financial info from list of similar tickers
    """

    if not similar:
        console.print("[red]No similar tickers found.")
        return [], {}

    financials = {}
    # We need a copy since we are modifying the original potentially
    for symbol in similar.copy():
        results = prepare_df_financials(symbol, statement, quarter)
        if results.empty:
            # If we have an empty result set, don't do further analysis on this symbol and remove it from consideration
            console.print(
                "Didn't get data for ticker "
                + symbol
                + ". Removing from further processing."
            )
            similar.remove(symbol)
            continue
        financials[symbol] = results.set_index("Item")

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


@log_start_end(log=logger)
def combine_similar_financials(
    datasets: Dict[str, pd.DataFrame],
    similar: List[str],
    timeframe: str,
    quarter: bool = False,
) -> pd.DataFrame:
    """Builds a DataFrame with financial statements from a certain timeframe of a list of tickers

    Parameters
    ----------
    datasets: Dict[str, pd.DataFrame]
        A dictionary of DataFrame with financial info from list of similar tickers
    similar: List[str]
        List of similar stock tickers
    timeframe: str
        Column label, which is a timeframe
    quarter: bool
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
        compare_financials = datasets[similar[0]][timeframe].to_frame()
        compare_financials.rename(columns={timeframe: similar[0]}, inplace=True)
        earnings_dates = [timeframe]
        idx = len(datasets[similar[0]].columns) - list(
            datasets[similar[0]].columns
        ).index(timeframe)

        for symbol in similar:
            report_quarter_date = list(datasets[symbol].columns)[-idx]
            earnings_dates.append(report_quarter_date)
            compare_financials[symbol + " (" + report_quarter_date + ")"] = datasets[
                symbol
            ][report_quarter_date]

        compare_financials.drop(
            columns=compare_financials.columns[0], axis=1, inplace=True
        )

    else:
        compare_financials = datasets[similar[0]][timeframe].to_frame()
        compare_financials.rename(columns={timeframe: similar[0]}, inplace=True)

        for symbol in similar[1:]:
            compare_financials[symbol] = datasets[symbol][timeframe]

    return compare_financials.fillna("-").replace("-", "")
