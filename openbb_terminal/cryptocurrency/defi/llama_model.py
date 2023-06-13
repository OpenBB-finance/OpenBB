"""Llama model"""
__docformat__ = "numpy"

import logging
import textwrap
from datetime import datetime

import numpy as np
import pandas as pd

from openbb_terminal.cryptocurrency.dataframe_helpers import (
    lambda_replace_underscores_in_column_names,
)
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import request

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
def get_chains() -> pd.DataFrame:
    """Returns information about chains supported by Llama.fi.
    [Source: https://docs.llama.fi/api]

    Returns
    -------
    pd.DataFrame
        Information about chains
    """
    response = request(API_URL + "/chains")
    if response.status_code != 200:
        raise Exception(f"Status code: {response.status_code}. Reason: {response.text}")
    try:
        df = pd.DataFrame(response.json())
        df.fillna(value=None, inplace=True)
        df = df.set_index("name")
    except Exception as e:
        logger.exception("Wrong response type: %s", str(e))
        raise ValueError("Wrong response type\n") from e
    return df


@log_start_end(log=logger)
def get_defi_protocols(
    limit: int = 100,
    sortby: str = "",
    ascend: bool = False,
    description: bool = False,
    drop_chain: bool = True,
) -> pd.DataFrame:
    """Returns information about listed DeFi protocols, their current TVL and changes to it in the last hour/day/week.
    [Source: https://docs.llama.fi/api]

    Parameters
    ----------
    limit: int
        The number of dApps to display
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data descending
    description: bool
        Flag to display description of protocol
    drop_chain: bool
        Whether to drop the chain column

    Returns
    -------
    pd.DataFrame
        Information about DeFi protocols
    """

    response = request(API_URL + "/protocols")
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
        df = df[columns]

    except Exception as e:
        logger.exception("Wrong response type: %s", str(e))
        raise ValueError("Wrong response type\n") from e

    df = df.set_index("name")
    if sortby:
        df = df.sort_values(by=sortby, ascending=ascend)
    if drop_chain:
        df = df.drop(columns="chain")

    if description:
        orig = ["name", "symbol", "category", "description", "url"]
        selection = [x for x in orig if x in df.columns]
        df = df[selection]
    else:
        df.drop(["description", "url"], axis=1, inplace=True)

    df.columns = [lambda_replace_underscores_in_column_names(val) for val in df.columns]
    df.rename(
        columns={
            "Change 1H": "Change 1H (%)",
            "Change 1D": "Change 1D (%)",
            "Change 7D": "Change 7D (%)",
            "Tvl": "TVL ($)",
        },
        inplace=True,
    )
    return df.head(limit)


@log_start_end(log=logger)
def get_defi_protocol(protocol: str) -> pd.DataFrame:
    """Returns information about historical tvl of a defi protocol.
    [Source: https://docs.llama.fi/api]

    Parameters
    ----------
    protocol: str
        Name of the protocol

    Returns
    -------
    pd.DataFrame
        Historical tvl
    """
    url = f"{API_URL}/protocol/{protocol}"
    r = request(url)
    data = r.json()

    df = pd.DataFrame(data["tvl"])
    df.date = pd.to_datetime(df.date, unit="s")
    df = df.set_index("date")
    return df


@log_start_end(log=logger)
def get_grouped_defi_protocols(
    limit: int = 50,
) -> pd.DataFrame:
    """Display top dApps (in terms of TVL) grouped by chain.
    [Source: https://docs.llama.fi/api]

    Parameters
    ----------
    limit: int
        Number of top dApps to display

    Returns
    -------
    pd.DataFrame
        Information about DeFi protocols grouped by chain
    """
    df = get_defi_protocols(limit, drop_chain=False)
    return df.groupby("Chain").size().index.values.tolist()


@log_start_end(log=logger)
def get_defi_tvl() -> pd.DataFrame:
    """Returns historical values of the total sum of TVLs from all listed protocols.
    [Source: https://docs.llama.fi/api]

    Returns
    -------
    pd.DataFrame
        Historical values of total sum of Total Value Locked from all listed protocols.
    """
    response = request(API_URL + "/charts")
    if response.status_code != 200:
        raise Exception(f"Status code: {response.status_code}. Reason: {response.text}")
    try:
        df = pd.DataFrame(response.json())
        df["date"] = df["date"].apply(lambda x: datetime.fromtimestamp(int(x)).date())
        return df
    except Exception as e:
        logger.exception("Wrong response data: %s", str(e))
        raise ValueError("Wrong response data") from e
