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
    """Get stocks data based on country, sector, industry, market cap and exclude exchanges. [Source: Finance Database]

    Parameters
    ----------
    country: str
        Search by country to find stocks matching the criteria.
    sector : str
        Search by sector to find stocks matching the criteria.
    industry : str
        Search by industry to find stocks matching the criteria.
    marketcap : str
        Select stocks based on the market cap.
    exclude_exchanges: bool
        When you wish to include different exchanges use this boolean.
    period

    Returns
    -------
    dict
        Dictionary of filtered stocks data
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
