""" Stockgrid View """
__docformat__ = "numpy"

import logging
from json import JSONDecodeError
from typing import List, Tuple

import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import request

logger = logging.getLogger(__name__)
# pylint: disable=unsupported-assignment-operation


@log_start_end(log=logger)
def get_dark_pool_short_positions(
    sortby: str = "dpp_dollar", ascend: bool = False
) -> pd.DataFrame:
    """Get dark pool short positions. [Source: Stockgrid]

    Parameters
    ----------
    sortby : str
        Field for which to sort by, where 'sv': Short Vol. [1M],
        'sv_pct': Short Vol. %%, 'nsv': Net Short Vol. [1M],
        'nsv_dollar': Net Short Vol. ($100M), 'dpp': DP Position [1M],
        'dpp_dollar': DP Position ($1B)
    ascend : bool
        Data in ascending order

    Returns
    -------
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

    field = d_fields_endpoints[sortby]

    order = "asc" if ascend else "desc"

    link = f"https://stockgridapp.herokuapp.com/get_dark_pool_data?top={field}&minmax={order}"

    response = request(link)
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
def get_short_interest_days_to_cover(sortby: str = "float") -> pd.DataFrame:
    """Get short interest and days to cover. [Source: Stockgrid]

    Parameters
    ----------
    sortby : str
        Field for which to sort by, where 'float': Float Short %%,
        'dtc': Days to Cover, 'si': Short Interest

    Returns
    -------
    pd.DataFrame
        Short interest and days to cover data
    """
    link = "https://stockgridapp.herokuapp.com/get_short_interest?top=days"
    r = request(link)
    df = pd.DataFrame(r.json()["data"])

    d_fields = {
        "float": "%Float Short",
        "dtc": "Days To Cover",
        "si": "Short Interest",
    }

    df = df[
        ["Ticker", "Date", "%Float Short", "Days To Cover", "Short Interest"]
    ].sort_values(
        by=d_fields[sortby],
        ascending=bool(sortby == "dtc"),
    )

    df["Short Interest"] = df["Short Interest"] / 1_000_000
    df.head()
    df.columns = [
        "Ticker",
        "Date",
        "Float Short %",
        "Days to Cover",
        "Short Interest [1M]",
    ]

    return df


@log_start_end(log=logger)
def get_short_interest_volume(symbol: str) -> Tuple[pd.DataFrame, List]:
    """Get price vs short interest volume. [Source: Stockgrid]

    Parameters
    ----------
    symbol : str
        Stock to get data from

    Returns
    -------
    Tuple[pd.DataFrame, List]
        Short interest volume data, Price data
    """
    link = f"https://stockgridapp.herokuapp.com/get_dark_pool_individual_data?ticker={symbol}"
    response = request(link)
    try:
        response_json = response.json()
    except JSONDecodeError:
        return pd.DataFrame(), [None]

    df = pd.DataFrame(response_json["individual_short_volume_table"]["data"])
    df["date"] = pd.to_datetime(df["date"])

    df = df.sort_values(by="date", ascending=False)

    df["Short Vol. [1M]"] = df["short_volume"] / 1_000_000
    df["Short Vol. %"] = df["short_volume%"] * 100
    df["Short Exempt Vol. [1k]"] = df["short_exempt_volume"] / 1_000
    df["Total Vol. [1M]"] = df["total_volume"] / 1_000_000

    df = df[
        [
            "date",
            "Short Vol. [1M]",
            "Short Vol. %",
            "Short Exempt Vol. [1k]",
            "Total Vol. [1M]",
        ]
    ]

    return df, response_json["prices"]["prices"]


@log_start_end(log=logger)
def get_net_short_position(symbol: str) -> pd.DataFrame:
    """Get net short position. [Source: Stockgrid]

    Parameters
    ----------
    symbol: str
        Stock to get data from

    Returns
    -------
    pd.DataFrame
        Net short position
    """
    link = f"https://stockgridapp.herokuapp.com/get_dark_pool_individual_data?ticker={symbol}"
    response = request(link)

    try:
        df = pd.DataFrame(response.json()["individual_dark_pool_position_data"])
    except JSONDecodeError:
        return pd.DataFrame()
    df["dates"] = pd.to_datetime(df["dates"])

    df = df.sort_values(by="dates", ascending=False)

    df["Net Short Vol. (1k $)"] = df["dollar_net_volume"] / 1_000
    df["Position (1M $)"] = df["dollar_dp_position"]

    df = df[
        [
            "dates",
            "Net Short Vol. (1k $)",
            "Position (1M $)",
        ]
    ]

    return df
