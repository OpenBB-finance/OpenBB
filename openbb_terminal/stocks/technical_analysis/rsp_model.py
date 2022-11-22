""" Relative Strength Percentile Model """
__docformat__ = "numpy"

import logging
from typing import Tuple
import os

import pandas as pd
import certifi

from openbb_terminal.decorators import log_start_end


logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_rsp(
    s_ticker: str = "",
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Relative strength percentile [Source: https://github.com/skyte/relative-strength]
    Currently takes from https://github.com/soggyomelette/rs-log in order to get desired output

    Parameters
    ----------
    s_ticker : str
        Stock Ticker

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]
        Dataframe of stock percentile, Dataframe of industry percentile,
        Raw stock dataframe for export, Raw industry dataframe for export
    """

    # Necessary for installer so that it can locate the correct certificates for
    # API calls and https
    # https://stackoverflow.com/questions/27835619/urllib-and-ssl-certificate-verify-failed-error/73270162#73270162
    os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
    os.environ["SSL_CERT_FILE"] = certifi.where()

    df_stock_p = pd.read_csv(
        "https://raw.githubusercontent.com/soggyomelette/rs-log/main/output/rs_stocks.csv"
    )
    df_industries_p = pd.read_csv(
        "https://raw.githubusercontent.com/soggyomelette/rs-log/main/output/rs_industries.csv"
    )
    rsp_stock = pd.DataFrame()
    rsp_industry = pd.DataFrame()

    if s_ticker != "":
        rsp_stock = df_stock_p[df_stock_p["Ticker"].str.match(s_ticker)]
        for i in range(len(df_industries_p)):
            if s_ticker in df_industries_p.iloc[i]["Tickers"]:
                rsp_industry = df_industries_p.iloc[[i]]

    return (rsp_stock, rsp_industry, df_stock_p, df_industries_p)  # type: ignore
