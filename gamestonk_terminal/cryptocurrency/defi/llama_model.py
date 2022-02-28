"""Llama model"""
__docformat__ = "numpy"

import logging
import textwrap
from datetime import datetime

import numpy as np
import pandas as pd
import requests

from gamestonk_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)

API_URL = "https://api.llama.fi"

LLAMA_FILTERS = [
    "tvl",
    "symbol",
    "category",
    "chains",
    "change_1h",
    "change_1d",
    "change_7d",
    "name",
]


@log_start_end(log=logger)
def get_defi_protocols() -> pd.DataFrame:
    """Returns information about listed DeFi protocols, their current TVL and changes to it in the last hour/day/week.
    [Source: https://docs.llama.fi/api]

    Returns
    -------
    pd.DataFrame
        Information about DeFi protocols
    """

    response = requests.get(API_URL + "/protocols")
    columns = [
        "name",
        "symbol",
        "category",
        "chains",
        "change_1h",
        "change_1d",
        "change_7d",
        "tvl",
        "url",
        "description",
        "chain",
    ]
    if response.status_code != 200:
        raise Exception(f"Status code: {response.status_code}. Reason: {response.text}")
    try:
        df = pd.DataFrame(response.json())
        df.replace({float(np.nan): None}, inplace=True)
        df["chains"] = df["chains"].apply(
            lambda x: "\n".join(textwrap.wrap(", ".join(x), width=50))
        )
        df["description"] = df["description"].apply(
            lambda x: "\n".join(textwrap.wrap(x, width=70)) if isinstance(x, str) else x
        )
        return df[columns]

    except Exception as e:
        logger.exception("Wrong response type: %s", str(e))
        raise ValueError("Wrong response type\n") from e


@log_start_end(log=logger)
def get_defi_protocol(protocol: str) -> pd.DataFrame:
    """Returns information about historical tvl of a defi protocol.
    [Source: https://docs.llama.fi/api]

    Returns
    -------
    pd.DataFrame
        Historical tvl
    """
    url = f"{API_URL}/protocol/{protocol}"
    r = requests.get(url)
    data = r.json()

    df = pd.DataFrame(data["tvl"])
    df.date = pd.to_datetime(df.date, unit="s")
    df = df.set_index("date")
    return df


@log_start_end(log=logger)
def get_defi_tvl() -> pd.DataFrame:
    """Returns historical values of the total sum of TVLs from all listed protocols.
    [Source: https://docs.llama.fi/api]

    Returns
    -------
    pd.DataFrame
        Historical values of total sum of Total Value Locked from all listed protocols.
    """
    response = requests.get(API_URL + "/charts")
    if response.status_code != 200:
        raise Exception(f"Status code: {response.status_code}. Reason: {response.text}")
    try:
        df = pd.DataFrame(response.json())
        df["date"] = df["date"].apply(lambda x: datetime.fromtimestamp(int(x)).date())
        return df
    except Exception as e:
        logger.exception("Wrong response data: %s", str(e))
        raise ValueError("Wrong response data") from e
