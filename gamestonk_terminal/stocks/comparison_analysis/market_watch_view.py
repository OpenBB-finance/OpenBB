""" Comparison Analysis Market Watch View """
__docformat__ = "numpy"

import argparse
from typing import List, Dict, Tuple
import requests
import pandas as pd
from bs4 import BeautifulSoup
from gamestonk_terminal.helper_funcs import (
    get_user_agent,
    parse_known_args_and_warn,
    patch_pandas_text_adjustment,
    financials_colored_values,
)
from gamestonk_terminal import feature_flags as gtff


def compare_income(other_args: List[str], ticker: str, similar: List[str]):
    """Compare income between companies

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    ticker : str
        Main ticker to compare income
    similar : List[str]
        Similar companies to compare income with
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="income",
        description="""
            Prints either yearly or quarterly income statement the company, and compares
            it against similar companies. [Source: Market Watch]
        """,
    )
    parser.add_argument(
        "-s",
        "--similar",
        dest="l_similar",
        type=lambda s: [str(item).upper() for item in s.split(",")],
        default=similar,
        help="similar companies to compare with.",
    )
    parser.add_argument(
        "-a",
        "--also",
        dest="l_also",
        type=lambda s: [str(item).upper() for item in s.split(",")],
        default=[],
        help="apart from loaded similar companies also compare with.",
    )
    parser.add_argument(
        "-q",
        "--quarter",
        action="store_true",
        default=False,
        dest="b_quarter",
        help="Quarter financial data flag.",
    )
    parser.add_argument(
        "-t",
        "--timeframe",
        dest="s_timeframe",
        type=str,
        default=None,
        help="Specify yearly/quarterly timeframe. Default is last.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        l_similar = ns_parser.l_similar
        l_similar += ns_parser.l_also

        # Add main ticker to similar list of companies
        l_similar = [ticker] + l_similar

        l_timeframes, ddf_financials = prepare_comparison_financials(
            l_similar, "income", ns_parser.b_quarter
        )

        if ns_parser.s_timeframe:
            if ns_parser.s_timeframe not in l_timeframes:
                raise ValueError(
                    f"Timeframe selected should be one of {', '.join(l_timeframes)}"
                )
            s_timeframe = ns_parser.s_timeframe
        else:
            s_timeframe = l_timeframes[-1]

        print(
            f"Other available {('yearly', 'quarterly')[ns_parser.b_quarter]} timeframes are: {', '.join(l_timeframes)}\n"
        )

        df_financials_compared = combine_similar_financials(
            ddf_financials, l_similar, s_timeframe, ns_parser.b_quarter
        )

        if gtff.USE_COLOR:
            df_financials_compared = df_financials_compared.applymap(
                financials_colored_values
            )

            patch_pandas_text_adjustment()
            pd.set_option("display.max_colwidth", None)
            pd.set_option("display.max_rows", None)

        if not ns_parser.b_quarter:
            df_financials_compared.index.name = s_timeframe

        print(df_financials_compared.to_string())
        print("")

    except Exception as e:
        print(e, "\n")
        return


def compare_balance(other_args: List[str], ticker: str, similar: List[str]):
    """Compare balance between companies

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    ticker : str
        Main ticker to compare income
    similar : List[str]
        Similar companies to compare income with
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="compare_balance",
        description="""
            Prints either yearly or quarterly balance statement the company, and compares
            it against similar companies. [Source: Market Watch]
        """,
    )
    parser.add_argument(
        "-s",
        "--similar",
        dest="l_similar",
        type=lambda s: [str(item).upper() for item in s.split(",")],
        default=similar,
        help="similar companies to compare with.",
    )
    parser.add_argument(
        "-a",
        "--also",
        dest="l_also",
        type=lambda s: [str(item).upper() for item in s.split(",")],
        default=[],
        help="apart from loaded similar companies also compare with.",
    )
    parser.add_argument(
        "-q",
        "--quarter",
        action="store_true",
        default=False,
        dest="b_quarter",
        help="Quarter financial data flag.",
    )
    parser.add_argument(
        "-t",
        "--timeframe",
        dest="s_timeframe",
        type=str,
        default=None,
        help="Specify yearly/quarterly timeframe. Default is last.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        l_similar = ns_parser.l_similar
        l_similar += ns_parser.l_also

        # Add main ticker to similar list of companies
        l_similar = [ticker] + l_similar

        l_timeframes, ddf_financials = prepare_comparison_financials(
            l_similar, "balance", ns_parser.b_quarter
        )

        if ns_parser.s_timeframe:
            if ns_parser.s_timeframe not in l_timeframes:
                raise ValueError(
                    f"Timeframe selected should be one of {', '.join(l_timeframes)}"
                )
            s_timeframe = ns_parser.s_timeframe
        else:
            s_timeframe = l_timeframes[-1]

        print(
            f"Other available {('yearly', 'quarterly')[ns_parser.b_quarter]} timeframes are: {', '.join(l_timeframes)}\n"
        )

        df_financials_compared = combine_similar_financials(
            ddf_financials, l_similar, s_timeframe, ns_parser.b_quarter
        )

        if gtff.USE_COLOR:
            df_financials_compared = df_financials_compared.applymap(
                financials_colored_values
            )

            patch_pandas_text_adjustment()
            pd.set_option("display.max_colwidth", None)
            pd.set_option("display.max_rows", None)

        if not ns_parser.b_quarter:
            df_financials_compared.index.name = s_timeframe

        print(df_financials_compared.to_string())
        print("")

    except Exception as e:
        print(e, "\n")
        return


def compare_cashflow(other_args: List[str], ticker: str, similar: List[str]):
    """Compare balance between companies

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    ticker : str
        Main ticker to compare income
    similar : List[str]
        Similar companies to compare income with
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="compare_cashflow",
        description="""
            Prints either yearly or quarterly cash statement the company, and compares
            it against similar companies. [Source: Market Watch]
        """,
    )
    parser.add_argument(
        "-s",
        "--similar",
        dest="l_similar",
        type=lambda s: [str(item).upper() for item in s.split(",")],
        default=similar,
        help="similar companies to compare with.",
    )
    parser.add_argument(
        "-a",
        "--also",
        dest="l_also",
        type=lambda s: [str(item).upper() for item in s.split(",")],
        default=[],
        help="apart from loaded similar companies also compare with.",
    )
    parser.add_argument(
        "-q",
        "--quarter",
        action="store_true",
        default=False,
        dest="b_quarter",
        help="Quarter financial data flag.",
    )
    parser.add_argument(
        "-t",
        "--timeframe",
        dest="s_timeframe",
        type=str,
        default=None,
        help="Specify yearly/quarterly timeframe. Default is last.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        l_similar = ns_parser.l_similar
        l_similar += ns_parser.l_also

        # Add main ticker to similar list of companies
        l_similar = [ticker] + l_similar

        l_timeframes, ddf_financials = prepare_comparison_financials(
            l_similar, "cashflow", ns_parser.b_quarter
        )

        if ns_parser.s_timeframe:
            if ns_parser.s_timeframe not in l_timeframes:
                raise ValueError(
                    f"Timeframe selected should be one of {', '.join(l_timeframes)}"
                )
            s_timeframe = ns_parser.s_timeframe
        else:
            s_timeframe = l_timeframes[-1]

        print(
            f"Other available {('yearly', 'quarterly')[ns_parser.b_quarter]} timeframes are: {', '.join(l_timeframes)}\n"
        )

        df_financials_compared = combine_similar_financials(
            ddf_financials, l_similar, s_timeframe, ns_parser.b_quarter
        )

        if gtff.USE_COLOR:
            df_financials_compared = df_financials_compared.applymap(
                financials_colored_values
            )

            patch_pandas_text_adjustment()
            pd.set_option("display.max_colwidth", None)
            pd.set_option("display.max_rows", None)

        if not ns_parser.b_quarter:
            df_financials_compared.index.name = s_timeframe

        print(df_financials_compared.to_string())
        print("")

    except Exception as e:
        print(e, "\n")
        return


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

    financials = {}
    # Get financial dataframe of each company
    for symbol in similar:
        financials[symbol] = prepare_df_financials(
            symbol, statement, quarter
        ).set_index("Item")

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
