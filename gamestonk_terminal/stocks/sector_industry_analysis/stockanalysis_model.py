"""Finance Database Model"""
__docformat__ = "numpy"
# pylint:disable=too-many-arguments,unexpected-keyword-arg

import logging
from typing import Dict, Any

import numpy as np
import pandas as pd
from tqdm import tqdm

from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.stocks.fundamental_analysis.dcf_model import create_dataframe

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_stocks_data(
    stocks: list, finance_key: str, sa_keys: dict, stocks_data: dict, period: str
):
    """Get stocks data based on a list of stocks and the finance key. The function searches for the correct
     financial statement automatically. [Source: StockAnalysis]

    Parameters
    ----------
    stocks: list
        A list of tickers that will be used to collect data for.
    finance_key: str
        The finance key used to search within the sa_keys for the correct name of item
        on the financial statement
    sa_keys: dict
        A dictionary that includes BS, IS and CF, the abbreviations and names of items
        on the financial statements. I.e: {"BS": {"ce": "Cash & Equivalents"}}
    stocks_data : dict
        A dictionary that is empty on initialisation but filled once data is collected
        for the first time.
    period : str
        Whether you want annually, quarterly or trailing financial statements.

    Returns
    -------
    dict
        Dictionary of filtered stocks data separated by financial statement
    """
    for symbol in tqdm(stocks):
        for statement in sa_keys.keys():
            if finance_key in sa_keys[statement]:
                if statement not in stocks_data:
                    stocks_data[statement] = {}
                used_statement = statement
                symbol_statement = create_dataframe(symbol, statement, period.lower())
                stocks_data[statement][symbol] = (
                    change_type_dataframes(symbol_statement[0]) * symbol_statement[1]
                )

    if period in ["Quarterly", "Trailing"]:
        for symbol in stocks_data[used_statement]:
            stocks_data[used_statement][symbol].columns = (
                stocks_data[used_statement][symbol]
                .columns.map(lambda x: pd.Period(x, "Q"))
                .astype(str)
            )

    stocks_data[used_statement] = match_length_dataframes(stocks_data[used_statement])

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


@log_start_end(log=logger)
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
