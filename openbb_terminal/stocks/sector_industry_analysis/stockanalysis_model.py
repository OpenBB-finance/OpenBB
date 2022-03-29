"""StockAnalysis Model"""
__docformat__ = "numpy"
# pylint:disable=too-many-arguments,unexpected-keyword-arg

import logging
from typing import Dict, Any

import numpy as np
import pandas as pd
from tqdm import tqdm
import yfinance as yf

from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.fundamental_analysis.dcf_model import create_dataframe

logger = logging.getLogger(__name__)

sa_keys = {
    "BS": {
        "ce": "Cash & Equivalents",
        "sti": "Short-Term Investments",
        "cce": "Cash & Cash Equivalents",
        "rec": "Receivables",
        "inv": "Inventory",
        "oca": "Other Current Assets",
        "tca": "Total Current Assets",
        "ppe": "Property, Plant & Equipment",
        "lti": "Long-Term Investments",
        "gai": "Goodwill and Intangibles",
        "olta": "Other Long-Term Assets",
        "tlta": "Total Long-Term Assets",
        "ta": "Total Assets",
        "ap": "Accounts Payable",
        "dr": "Deferred Revenue",
        "cd": "Current Debt",
        "ocl": "Other Current Liabilities",
        "tcl": "Total Current Liabilities",
        "ltd": "Long-Term Debt",
        "oltl": "Other Long-Term Liabilities",
        "tltl": "Total Long-Term Liabilities",
        "tl": "Total Liabilities",
        "ret": "Retained Earnings",
        "ci": "Comprehensive Income",
        "se": "Shareholders' Equity",
        "tle": "Total Liabilities and Equity",
    },
    "IS": {
        "re": "Revenue",
        "cr": "Cost of Revenue",
        "gp": "Gross Profit",
        "sga": "Selling, Genera & Admin",
        "rd": "Research & Development",
        "ooe": "Other Operating Expenses",
        "oi": "Operating Income",
        "ie": "Interest Expense / Income",
        "oe": "Other Expense / Income",
        "it": "Income Tax",
        "ni": "Net Income",
        "pd": "Preferred Dividends",
    },
    "CF": {
        "ninc": "Net Income",
        "da": "Depreciation & Amortization",
        "sbc": "Share-Based Compensation",
        "ooa": "Other Operating Activities",
        "ocf": "Operating Cash Flow",
        "cex": "Capital Expenditures",
        "acq": "Acquisitions",
        "cii": "Change in Investments",
        "oia": "Other Investing Activities",
        "icf": "Investing Cash Flow",
        "dp": "Dividends Paid",
        "si": "Share Insurance / Repurchase",
        "di": "Debt Issued / Paid",
        "ofa": "Other Financing Activities",
        "fcf": "Financing Cash Flow",
        "ncf": "Net Cash Flow",
    },
}


@log_start_end(log=logger)
def get_stocks_data(
    stocks: list,
    finance_key: str,
    sa_dict: dict,
    stocks_data: dict,
    period: str,
    convert_currency: str = "USD",
):
    """Get stocks data based on a list of stocks and the finance key. The function searches for the correct
     financial statement automatically. [Source: StockAnalysis]

    Parameters
    ----------
    stocks: list
        A list of tickers that will be used to collect data for.
    finance_key: str
        The finance key used to search within the sa_dict for the correct name of item
        on the financial statement
    sa_dict: dict
        A dictionary that includes BS, IS and CF, the abbreviations and names of items
        on the financial statements. I.e: {"BS": {"ce": "Cash & Equivalents"}}
    stocks_data : dict
        A dictionary that is empty on initialisation but filled once data is collected
        for the first time.
    period : str
        Whether you want annually, quarterly or trailing financial statements.
    convert_currency : str
        Choose in what currency you wish to convert each company's financial statement. Default is USD (US Dollars).

    Returns
    -------
    dict
        Dictionary of filtered stocks data separated by financial statement
    """
    no_data = []
    for symbol in tqdm(stocks):
        for statement in sa_dict.keys():
            if finance_key in sa_dict[statement]:
                if statement not in stocks_data:
                    stocks_data[statement] = {}
                used_statement = statement
                symbol_statement, rounding, currency = create_dataframe(
                    symbol, statement, period.lower()
                )

                if symbol_statement.empty:
                    no_data.append(symbol)
                    continue

                symbol_statement_rounded = (
                    change_type_dataframes(symbol_statement) * rounding
                )

                if convert_currency and convert_currency != currency:
                    currency_data = yf.download(
                        f"{currency}{convert_currency}=X",
                        start=f"{symbol_statement_rounded.columns[0]}-01-01",
                        end=f"{symbol_statement_rounded.columns[-1]}-12-31",
                        progress=False,
                    )["Adj Close"]

                    for year in symbol_statement_rounded:
                        # Since fiscal year can differ, I take the median of the currency and not the last value
                        # of the year
                        symbol_statement_rounded[year] = (
                            symbol_statement_rounded[year]
                            * currency_data.loc[year].median()
                        )

                stocks_data[statement][symbol] = symbol_statement_rounded

    if period in ["Quarterly", "Trailing"]:
        for symbol in stocks_data[used_statement]:
            stocks_data[used_statement][symbol].columns = (
                stocks_data[used_statement][symbol]
                .columns.map(lambda x: pd.Period(x, "Q"))
                .astype(str)
            )

    stocks_data[used_statement] = match_length_dataframes(stocks_data[used_statement])

    if no_data:
        console.print(
            f"No data available for {', '.join(str(symbol) for symbol in no_data)}"
        )

    return stocks_data


@log_start_end(log=logger)
def match_length_dataframes(dataframes: Dict[pd.DataFrame, Any]):
    """
    All unique columns are collected and filled for each DataFrame to
    ensure equal length of columns.

    Parameters
    ----------
    dataframes : dict
        Dict of dataframes to match length

    Returns
    -------
    dataframes : dict
        Dict of DataFrames with equal column length
    """
    columns = []

    for symbol in dataframes:
        for column in dataframes[symbol].columns:
            if column not in columns:
                columns.append(column)

    for symbol in dataframes:
        for column in columns:
            if column not in dataframes[symbol].columns:
                dataframes[symbol][column] = np.nan
        dataframes[symbol] = dataframes[symbol].sort_index(axis=1)

    return dataframes


def change_type_dataframes(dataframe) -> pd.DataFrame:
    """
    Adjusts comma-seperated strings to floats

    Parameters
    ----------
    dataframe : pd.DataFrame
        DataFrame with comma-seperated strings

    Returns
    -------
    dataframe : pd.DataFrame
        Adjusted DataFrame
    """
    dataframe = dataframe.apply(lambda x: x.str.replace(",", "").astype(float), axis=1)

    return dataframe
