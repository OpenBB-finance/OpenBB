""" Short Interest View """
__docformat__ = "numpy"

import logging

import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.stocks.discovery.disc_helpers import get_df

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_low_float() -> pd.DataFrame:
    """Returns low float DataFrame

    Returns
    -------
    DataFrame
        Low float DataFrame with the following columns:
        Ticker, Company, Exchange, ShortInt, Float, Outstd, Industry
    """
    df = get_df("https://www.lowfloat.com")[2]
    df.columns = [
        "Ticker",
        "Company",
        "Exchange",
        "Float",
        "Outstd",
        "ShortInt",
        "Industry",
    ]
    return df.drop([31])


@log_start_end(log=logger)
def get_today_hot_penny_stocks() -> pd.DataFrame:
    """Returns today hot penny stocks

    Returns
    -------
    DataFrame
        Today hot penny stocks DataFrame with the following columns:
        Ticker, Price, Change, $ Volume, Volume, # Trades
    """
    df = get_df("https://www.pennystockflow.com", 0)[1]
    return df.drop([10])
