""" Finviz Model """
__docformat__ = "numpy"

import logging
from ast import literal_eval
import webbrowser

import pandas as pd
import requests
from finvizfinance.group import performance, spectrum, valuation

from openbb_terminal.rich_config import console
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_user_agent

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_performance_map(period: str = "1d", filter: str = "sp500"):
    """Opens Finviz map website in a browser. [Source: Finviz]

    Parameters
    ----------
    period : str
        Performance period. Available periods are 1d, 1w, 1m, 3m, 6m, 1y.
    scope : str
        Map filter. Available map filters are sp500, world, full, etf.
    """
    # Conversion from period and type, to fit url requirements
    d_period = {"1d": "", "1w": "w1", "1m": "w4", "3m": "w13", "6m": "w26", "1y": "w52"}
    d_type = {"sp500": "sec", "world": "geo", "full": "sec_all", "etf": "etf"}
    # TODO: Try to get this image and output it instead of opening browser
    url = f"https://finviz.com/map.ashx?t={d_type[filter]}&st={d_period[period]}"
    webbrowser.open(url)
    console.print("")


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

    try:
        if data_type == "valuation":
            return valuation.Valuation().screener_view(group=group)
        if data_type == "performance":
            return performance.Performance().screener_view(group=group)
        return pd.DataFrame()
    except IndexError:
        console.print("Data not found.\n")
        return pd.DataFrame()


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
        source.find("var groups = ") : source.find(  # noqa: E203
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
            slice_source.find("\r\n                    var tiles = ") : -1  # noqa: E203
        ].strip("\r\n                    var tiles = ")
    )

    d_futures: dict = {}
    for future in groups:
        d_futures[future["label"]] = []
        for ticker in future["contracts"]:
            d_futures[future["label"]].append(titles[ticker["ticker"]])

    return d_futures
