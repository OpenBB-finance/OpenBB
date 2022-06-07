"""Screener model"""
__docformat__ = "numpy"

import configparser
import logging
import os

import pandas as pd

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def etf_screener(preset: str):
    """
    Screens the etfs pulled from my repo (https://github.com/jmaslek/etf_scraper),
    which is updated hourly through the market day

    Parameters
    ----------
    preset: str
        Screener to use from presets

    Returns
    ----------
    df : pd.DataFrame
        Screened dataframe
    """

    # pylint: disable=no-member

    df = pd.read_csv(
        "https://raw.githubusercontent.com/jmaslek/etf_scraper/main/etf_overviews.csv",
        index_col=0,
    )

    cf = configparser.ConfigParser()
    path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "presets", preset + ".ini"
    )

    cf.read(path)
    cols = cf.sections()

    for col in cols:
        if cf[col]["Min"] != "None":
            query = f"{col} > {cf[col]['Min']} "
            df = df.query(query)
        if cf[col]["Max"] != "None":
            query = f"{col} < {cf[col]['Max']} "
            df = df.query(query)

    return df
