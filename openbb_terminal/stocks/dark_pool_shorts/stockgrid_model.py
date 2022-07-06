""" Stockgrid View """
__docformat__ = "numpy"

import logging
from typing import List, Tuple

import pandas as pd
import requests

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_dark_pool_short_positions(sort_field: str, ascending: bool) -> pd.DataFrame:
    """Get dark pool short positions. [Source: Stockgrid]

    Parameters
    ----------
    sort_field : str
        Field for which to sort by, where 'sv': Short Vol. [1M],
        'sv_pct': Short Vol. %%, 'nsv': Net Short Vol. [1M],
        'nsv_dollar': Net Short Vol. ($100M), 'dpp': DP Position [1M],
        'dpp_dollar': DP Position ($1B)
    ascending : bool
        Data in ascending order

    Returns
    ----------
    pd.DataFrame
        Dark pool short position data
    """
    d_fields_endpoints = {
        "sv": "Short+Volume",
        "sv_pct": "Short+Volume+%25",
        "nsv": "Net+Short+Volume",
        "nsv_dollar": "Net+Short+Volume+$",
        "dpp": "Dark+Pools+Position",
        "dpp_dollar": "Dark+Pools+Position+$",
    }

    field = d_fields_endpoints[sort_field]

    if ascending:
        order = "asc"
    else:
        order = "desc"

    link = f"https://stockgridapp.herokuapp.com/get_dark_pool_data?top={field}&minmax={order}"

    response = requests.get(link)
    df = pd.DataFrame(response.json()["data"])

    df = df[
        [
            "Ticker",
            "Date",
            "Short Volume",
            "Short Volume %",
            "Net Short Volume",
            "Net Short Volume $",
            "Dark Pools Position",
            "Dark Pools Position $",
        ]
    ]

    return df


@log_start_end(log=logger)
def get_short_interest_days_to_cover(sort_field: str) -> pd.DataFrame:
    """Get short interest and days to cover. [Source: Stockgrid]

    Parameters
    ----------
    sort_field : str
        Field for which to sort by, where 'float': Float Short %%,
        'dtc': Days to Cover, 'si': Short Interest

    Returns
    ----------
    pd.DataFrame
        Short interest and days to cover data
    """
    link = "https://stockgridapp.herokuapp.com/get_short_interest?top=days"
    r = requests.get(link)
    df = pd.DataFrame(r.json()["data"])

    d_fields = {
        "float": "%Float Short",
        "dtc": "Days To Cover",
        "si": "Short Interest",
    }

    df = df[
        ["Ticker", "Date", "%Float Short", "Days To Cover", "Short Interest"]
    ].sort_values(
        by=d_fields[sort_field],
        ascending=bool(sort_field == "dtc"),
    )

    return df


@log_start_end(log=logger)
def get_short_interest_volume(ticker: str) -> Tuple[pd.DataFrame, List]:
    """Get price vs short interest volume. [Source: Stockgrid]

    Parameters
    ----------
    ticker : str
        Stock to get data from

    Returns
    ----------
    pd.DataFrame
        Short interest volume data
    List
        Price data
    """
    link = f"https://stockgridapp.herokuapp.com/get_dark_pool_individual_data?ticker={ticker}"
    response = requests.get(link)
    response_json = response.json()

    df = pd.DataFrame(response_json["individual_short_volume_table"]["data"])
    df["date"] = pd.to_datetime(df["date"])

    return df, response_json["prices"]["prices"]


@log_start_end(log=logger)
def get_net_short_position(ticker: str) -> pd.DataFrame:
    """Get net short position. [Source: Stockgrid]

    Parameters
    ----------
    ticker: str
        Stock to get data from

    Returns
    ----------
    pd.DataFrame
        Net short position
    """
    link = f"https://stockgridapp.herokuapp.com/get_dark_pool_individual_data?ticker={ticker}"
    response = requests.get(link)

    df = pd.DataFrame(response.json()["individual_dark_pool_position_data"])
    df["dates"] = pd.to_datetime(df["dates"])

    return df
