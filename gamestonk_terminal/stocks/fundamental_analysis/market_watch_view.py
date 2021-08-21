""" Fundamental Analysis Market Watch View. LEGACY.

MarketWatch now requires a user to be a subscriber in order to have access to the financials...
So this code is not being used for the time being, it may be at a later stage.
"""
__docformat__ = "numpy"

import argparse
import re
from typing import List
import requests
import pandas as pd
from bs4 import BeautifulSoup
import numpy as np

from gamestonk_terminal.stocks.fundamental_analysis import market_watch_model as mwm
from gamestonk_terminal.helper_funcs import (
    get_user_agent,
    parse_known_args_and_warn,
    patch_pandas_text_adjustment,
    financials_colored_values,
    clean_data_values_to_float,
    int_or_round_float,
)
from gamestonk_terminal import feature_flags as gtff

# pylint: disable=too-many-branches


def income(other_args: List[str], ticker: str):
    """Market Watch ticker income statement

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    ticker : str
        Fundamental analysis ticker symbol
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="income",
        description="""
            Prints either yearly or quarterly income statement the company. The following fields
            are expected: Sales Growth, Cost of Goods Sold (COGS) incl. D&A, COGS Growth, COGS
            excluding D&A, Depreciation & Amortization Expense, Depreciation, Amortization of
            Intangibles, Gross Income, Gross Income Growth, Gross Profit Margin, SG&A Expense, SGA
            Growth, Research & Development, Other SG&A, Other Operating Expense, Unusual Expense,
            EBIT after Unusual Expense, Non Operating Income/Expense, Non-Operating Interest
            Income, Equity in Affiliates (Pretax), Interest Expense, Interest Expense Growth,
            Gross Interest Expense, Interest Capitalized, Pretax Income, Pretax Income Growth,
            Pretax Margin, Income Tax, Income Tax - Current Domestic, Income Tax - Current Foreign,
            Income Tax - Deferred Domestic, Income Tax - Deferred Foreign, Income Tax Credits,
            Equity in Affiliates, Other After Tax Income (Expense), Consolidated Net Income,
            Minority Interest Expense, Net Income Growth, Net Margin Growth, Extraordinaries &
            Discontinued Operations, Extra Items & Gain/Loss Sale Of Assets, Cumulative Effect -
            Accounting Chg, Discontinued Operations, Net Income After Extraordinaries,
            Preferred Dividends, Net Income Available to Common, EPS (Basic), EPS (Basic) Growth,
            Basic Shares Outstanding, EPS (Diluted), EPS (Diluted) Growth, Diluted Shares
            Outstanding, EBITDA, EBITDA Growth, EBITDA Margin, Sales/Revenue, and Net Income.
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
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_financials = mwm.prepare_df_financials(ticker, "income", ns_parser.b_quarter)

        if gtff.USE_COLOR:
            df_financials = df_financials.applymap(financials_colored_values)

            patch_pandas_text_adjustment()
            pd.set_option("display.max_colwidth", None)
            pd.set_option("display.max_rows", None)

        if df_financials.empty:
            print("Marketwatch does not yet provide financials for this ticker")
        else:
            print(df_financials.to_string(index=False))
        print("")

    except Exception as e:
        print(e, "\n")


def balance(other_args: List[str], ticker: str):
    """Market Watch ticker balance statement

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    ticker : str
        Fundamental analysis ticker symbol
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
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
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_financials = mwm.prepare_df_financials(
            ticker, "balance", ns_parser.b_quarter
        )

        if gtff.USE_COLOR:
            df_financials = df_financials.applymap(financials_colored_values)

            patch_pandas_text_adjustment()
            pd.set_option("display.max_colwidth", None)
            pd.set_option("display.max_rows", None)

        if df_financials.empty:
            print("Marketwatch does not yet provide financials for this ticker")
        else:
            print(df_financials.to_string(index=False))
        print("")

    except Exception as e:
        print(e, "\n")


def cash(other_args: List[str], ticker: str):
    """Market Watch ticker cash flow statement

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    ticker : str
        Fundamental analysis ticker symbol
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
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
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_financials = mwm.prepare_df_financials(
            ticker, "cashflow", ns_parser.b_quarter
        )

        if gtff.USE_COLOR:
            df_financials = df_financials.applymap(financials_colored_values)

            patch_pandas_text_adjustment()
            pd.set_option("display.max_colwidth", None)
            pd.set_option("display.max_rows", None)

        if df_financials.empty:
            print("Marketwatch does not yet provide financials for this ticker")
        else:
            print(df_financials.to_string(index=False))
        print("")

    except Exception as e:
        print(e, "\n")


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
        a_financials_header = []
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
        a_financials_header = []
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
