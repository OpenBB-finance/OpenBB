""" Finviz Model """
__docformat__ = "numpy"

import logging
from ast import literal_eval

import pandas as pd
import requests
from finvizfinance.group import performance, spectrum, valuation

from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import get_user_agent

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_valuation_performance_data(group: str, data_type: str) -> pd.DataFrame:
    """Get group (sectors, industry or country) valuation/performance data. [Source: Finviz]

    Parameters
    ----------
    group : str
       sectors, industry or country
    data_type : str
       valuation or performance

    Returns
    ----------
    pd.DataFrame
        dataframe with valuation/performance data
    """
    if data_type == "valuation":
        return valuation.Valuation().screener_view(group=group)
    return performance.Performance().screener_view(group=group)


@log_start_end(log=logger)
def get_spectrum_data(group: str):
    """Get group (sectors, industry or country) valuation/performance data. [Source: Finviz]

    Parameters
    ----------
    group : str
       sectors, industry or country
    """
    spectrum.Spectrum().screener_view(group=group)


@log_start_end(log=logger)
def get_futures() -> dict:
    """Get futures data. [Source: Finviz]

    Parameters
    ----------
    futures : dict
       Indices, Energy, Metals, Meats, Grains, Softs, Bonds, Currencies
    """
    source = requests.get(
        "https://finviz.com/futures.ashx", headers={"User-Agent": get_user_agent()}
    ).text

    slice_source = source[
        source.find("var groups = ") : source.find(
            "\r\n\r\n                    groups.forEach(function(group) "
        )
    ]
    groups = literal_eval(
        slice_source[
            : slice_source.find("\r\n                    var tiles = ") - 1
        ].strip("var groups = ")
    )
    titles = literal_eval(
        slice_source[
            slice_source.find("\r\n                    var tiles = ") : -1
        ].strip("\r\n                    var tiles = ")
    )

    d_futures: dict = {}
    for future in groups:
        d_futures[future["label"]] = []
        for ticker in future["contracts"]:
            d_futures[future["label"]].append(titles[ticker["ticker"]])

    return d_futures
