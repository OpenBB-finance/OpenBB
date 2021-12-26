"""Llama model"""
__docformat__ = "numpy"

from datetime import datetime
import textwrap
import requests
import pandas as pd
import numpy as np

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


def get_defi_protocols() -> pd.DataFrame:
    """Returns information about listed DeFi protocols, their current TVL and changes to it in the last hour/day/week.
    [Source: https://docs.llama.fi/api]

    Returns
    -------
    pd.DataFrame
        Information about DeFi protocols
    """

    response = requests.get("https://api.llama.fi/protocols")
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
        raise ValueError("Wrong response type\n") from e


def get_defi_tvl() -> pd.DataFrame:
    """Returns historical values of the total sum of TVLs from all listed protocols.
    [Source: https://docs.llama.fi/api]

    Returns
    -------
    pd.DataFrame
        Historical values of total sum of Total Value Locked from all listed protocols.
    """
    response = requests.get("https://api.llama.fi/charts", timeout=5)
    if response.status_code != 200:
        raise Exception(f"Status code: {response.status_code}. Reason: {response.text}")
    try:
        df = pd.DataFrame(response.json())
        df["date"] = df["date"].apply(lambda x: datetime.fromtimestamp(int(x)).date())
        return df
    except Exception as e:
        raise ValueError("Wrong response data") from e
