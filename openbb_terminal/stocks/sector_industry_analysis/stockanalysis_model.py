"""StockAnalysis Model"""
__docformat__ = "numpy"
# pylint:disable=too-many-arguments,unexpected-keyword-arg

import logging
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import yfinance as yf
from tqdm import tqdm

from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.fundamental_analysis.dcf_model import create_dataframe

logger = logging.getLogger(__name__)

SA_KEYS = {
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
    symbols: Optional[List[str]] = None,
    finance_key: str = "ncf",
    stocks_data: Optional[dict] = None,
    period: str = "annual",
    symbol: str = "USD",
):
    """Get stocks data based on a list of stocks and the finance key. The function searches for the
    correct financial statement automatically. [Source: StockAnalysis]

    Parameters
    ----------
    symbols: list
        A list of tickers that will be used to collect data for.
    finance_key: str
        The finance key used to search within the SA_KEYS for the correct name of item
        on the financial statement
    stocks_data : dict
        A dictionary that is empty on initialisation but filled once data is collected
        for the first time.
    period : str
        Whether you want annually, quarterly or trailing financial statements.
    symbol : str
        Choose in what currency you wish to convert each company's financial statement.
        Default is USD (US Dollars).

    Returns
    -------
    dict
        Dictionary of filtered stocks data separated by financial statement
    """
    if symbols is None:
        symbols = ["FB", "TSLA", "MSFT"]

    if stocks_data is None:
        stocks_data = {}

    no_data = []

    for top_item in tqdm(symbols):
        for item, description in SA_KEYS.items():
            if finance_key in description:
                if item not in stocks_data:
                    stocks_data[item] = {}
                used_statement = item
                symbol_statement, rounding, currency_dcf = create_dataframe(
                    top_item, item, period.lower()
                )
                if symbol_statement.empty:
                    no_data.append(top_item)
                    continue

                symbol_statement_rounded = (
                    change_type_dataframes(symbol_statement) * rounding
                )

                if symbol and symbol != currency_dcf:
                    currency_data = yf.download(
                        f"{currency_dcf}{top_item}=X",
                        start=f"{symbol_statement_rounded.columns[0]}-01-01",
                        end=f"{symbol_statement_rounded.columns[-1]}-12-31",
                        progress=False,
                        ignore_tz=True,
                    )["Adj Close"]

                    for year in symbol_statement_rounded:
                        # Since fiscal years differ, take the median and not the last value
                        # of the year
                        symbol_statement_rounded[year] = (
                            symbol_statement_rounded[year]
                            * currency_data.loc[year].median()
                        )

                stocks_data[item][top_item] = symbol_statement_rounded

    if period in ["Quarterly", "Trailing"]:
        for item in stocks_data[used_statement]:
            stocks_data[used_statement][symbol].columns = (
                stocks_data[used_statement][item]
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


def change_type_dataframes(data: pd.DataFrame) -> pd.DataFrame:
    """
    Adjusts comma-seperated strings to floats

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame with comma-seperated strings

    Returns
    -------
    pd.DataFrame
        Adjusted DataFrame
    """

    data.replace("-", 0, inplace=True)
    dataframe = data.apply(
        lambda x: x.astype(str).str.replace(",", "").astype(float), axis=1
    )

    return dataframe
