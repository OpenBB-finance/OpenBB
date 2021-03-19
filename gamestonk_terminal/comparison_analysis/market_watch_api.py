""" Comparison Analysis Market Watch View """
__docformat__ = "numpy"

import argparse
import requests
import pandas as pd
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple
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
        type=lambda s: [str(item) for item in s.split(",")],
        default=[],
        help="similar companies to compare with.",
    )
    parser.add_argument(
        "-a",
        "--also",
        dest="l_also",
        type=lambda s: [str(item) for item in s.split(",")],
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

        if ns_parser.l_similar:
            similar = ns_parser.l_similar

        similar += ns_parser.l_also

        # Add main ticker to similar list of companies
        similar.insert(0, ticker)

        l_timeframes, ddf_financials = prepare_comparison_financials(
            similar, "income", ns_parser.b_quarter
        )

        if ns_parser.s_timeframe:
            if ns_parser.s_timeframe not in l_timeframes:
                raise ValueError(
                    f"Timeframe {ns_parser.s_timeframe} should be one of {l_timeframes}"
                )
            s_timeframe = ns_parser.s_timeframe
        else:
            s_timeframe = l_timeframes[-1]

        df_financials_compared = combine_similar_financials(
            ddf_financials, similar, s_timeframe
        )

        if gtff.USE_COLOR:
            df_financials_compared = df_financials_compared.applymap(
                financials_colored_values
            )

            patch_pandas_text_adjustment()
            pd.set_option("display.max_colwidth", None)
            pd.set_option("display.max_rows", None)

        df_financials_compared.index.name = s_timeframe
        print(df_financials_compared.to_string())
        print("")

    except Exception as e:
        print(e)
        print("")
        return


def balance(l_args, s_ticker):
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="balance",
        description="""
            Prints either yearly or quarterly assets from balance sheet of the company.
            The following fields are expected: Cash & Short Term Investments, Cash & Short Term
            Investments Growth, Cash Only, Short-Term Investments, Cash & ST Investments / Total
            Assets, Total Accounts Receivable, Total Accounts Receivable Growth, Accounts
            Receivables, Net, Accounts Receivables, Gross, Bad Debt/Doubtful Accounts, Other
            Receivable, Accounts Receivable Turnover, Inventories, Finished Goods, Work in
            Progress, Raw Materials, Progress Payments & Other, Other Current Assets,
            Miscellaneous Current Assets, Net Property, Plant & Equipment, Property, Plant &
            Equipment - Gross, Buildings, Land & Improvements, Computer Software and Equipment,
            Other Property, Plant & Equipment, Accumulated Depreciation, Total Investments and
            Advances, Other Long-Term Investments, Long-Term Note Receivables, Intangible Assets,
            Net Goodwill, Net Other Intangibles, Other Assets.

            Prints either yearly or quarterly liabilities and shareholders' equity from balance
            sheet of the company. The following fields are expected: ST Debt & Current Portion LT
            Debt, Short Term Debt, Current Portion of Long Term Debt, Accounts Payable, Accounts
            Payable Growth, Income Tax Payable, Other Current Liabilities, Dividends Payable,
            Accrued Payroll, Miscellaneous Current Liabilities, Long-Term Debt, Long-Term Debt
            excl. Capitalized Leases, Non-Convertible Debt, Convertible Debt, Capitalized Lease
            Obligations, Provision for Risks & Charges, Deferred Taxes, Deferred Taxes - Credits,
            Deferred Taxes - Debit, Other Liabilities, Other Liabilities (excl. Deferred Income),
            Deferred Income, Non-Equity Reserves, Total Liabilities / Total Assets, Preferred Stock
            (Carrying Value), Redeemable Preferred Stock, Non-Redeemable Preferred Stock, Common
            Equity (Total), Common Equity/Total Assets, Common Stock Par/Carry Value, Retained
            Earnings, ESOP Debt Guarantee, Cumulative Translation Adjustment/Unrealized For. Exch.
            Gain, Unrealized Gain/Loss Marketable Securities, Revaluation Reserves, Treasury Stock,
            Total Shareholders' Equity, Total Shareholders' Equity / Total Assets, Accumulated
            Minority Interest, Total Equity, Total Current Assets, Total Assets, Total Current
            Liabilities, Total Liabilities, and Liabilities & Shareholders' Equity.
            [Source: Market Watch]
        """,
    )

    parser.add_argument(
        "-q",
        "--quarter",
        action="store_true",
        default=False,
        dest="b_quarter",
        help="Quarter fundamental data flag.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, l_args)
        if not ns_parser:
            return

        df_financials = prepare_df_financials(s_ticker, "balance", ns_parser.b_quarter)

        if gtff.USE_COLOR:
            df_financials = df_financials.applymap(financials_colored_values)

            patch_pandas_text_adjustment()
            pd.set_option("display.max_colwidth", None)
            pd.set_option("display.max_rows", None)

        print(df_financials.to_string(index=False))
        print("")

    except Exception as e:
        print(e)
        print("")
        return


def cash(l_args, s_ticker):
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="cash_flow",
        description="""
            Prints either yearly or quarterly cash flow operating activities of the company.
            The following fields are expected: Net Income before Extraordinaries, Net Income
            Growth, Depreciation, Depletion & Amortization, Depreciation and Depletion,
            Amortization of Intangible Assets, Deferred Taxes & Investment Tax Credit, Deferred
            Taxes, Investment Tax Credit, Other Funds, Funds from Operations, Extraordinaries,
            Changes in Working Capital, Receivables, Accounts Payable, Other Assets/Liabilities,
            and Net Operating Cash Flow Growth.
            Prints either yearly or quarterly cash flow investing activities of the company.
            The following fields are expected: Capital Expenditures, Capital Expenditures Growth,
            Capital Expenditures/Sales, Capital Expenditures (Fixed Assets), Capital Expenditures
            (Other Assets), Net Assets from Acquisitions, Sale of Fixed Assets & Businesses,
            Purchase/Sale of Investments, Purchase of Investments, Sale/Maturity of Investments,
            Other Uses, Other Sources, Net Investing Cash Flow Growth.
            Prints either yearly or quarterly cash flow financing activities of the company.
            The following fields are expected: Cash Dividends Paid - Total, Common Dividends,
            Preferred Dividends, Change in Capital Stock, Repurchase of Common & Preferred Stk.,
            Sale of Common & Preferred Stock, Proceeds from Stock Options, Other Proceeds from Sale
            of Stock, Issuance/Reduction of Debt, Net, Change in Current Debt, Change in Long-Term
            Debt, Issuance of Long-Term Debt, Reduction in Long-Term Debt, Other Funds, Other Uses,
            Other Sources, Net Financing Cash Flow Growth, Net Financing Cash Flow/Sales, Exchange
            Rate Effect, Miscellaneous Funds, Net Change in Cash, Free Cash Flow, Free Cash Flow
            Growth, Free Cash Flow Yield, Net Operating Cash Flow, Net Investing Cash Flow, Net
            Financing Cash Flow.
            [Source: Market Watch]
        """,
    )

    parser.add_argument(
        "-q",
        "--quarter",
        action="store_true",
        default=False,
        dest="b_quarter",
        help="Quarter fundamental data flag.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, l_args)
        if not ns_parser:
            return

        df_financials = prepare_df_financials(s_ticker, "cashflow", ns_parser.b_quarter)

        if gtff.USE_COLOR:
            df_financials = df_financials.applymap(financials_colored_values)

            patch_pandas_text_adjustment()
            pd.set_option("display.max_colwidth", None)
            pd.set_option("display.max_rows", None)

        print(df_financials.to_string(index=False))
        print("")

    except Exception as e:
        print(e)
        print("")
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
) -> pd.DataFrame:
    """Builds a DataFrame with financial statements from a certain timeframe of a list of tickers

    Parameters
    ----------
    Dict[str, pd.DataFrame]
        A dictionary of DataFrame with financial info from list of similar tickers
    similar : List[str]
        List of similar stock tickers
    statement : str
        Either income, balance or cashflow

    Returns
    -------
    pd.DataFrame
        A DataFrame with financial statements from a certain timeframe of a list of tickers
    """

    compare_financials = financials[similar[0]][timeframe].to_frame()
    compare_financials.rename(columns={timeframe: similar[0]}, inplace=True)

    for symbol in similar[1:]:
        compare_financials[symbol] = financials[symbol][timeframe]

    return compare_financials
