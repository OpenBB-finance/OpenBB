"""Whale Alert model"""
__docformat__ = "numpy"

import logging
import textwrap
from typing import Optional

import numpy as np
import pandas as pd
import requests

import gamestonk_terminal.config_terminal as cfg
from gamestonk_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)

FILTERS = [
    "date",
    "symbol",
    "blockchain",
    "amount",
    "amount_usd",
    "from",
    "to",
]


class ApiKeyException(Exception):
    """Api Key Exception object"""

    @log_start_end(log=logger)
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    @log_start_end(log=logger)
    def __str__(self) -> str:
        return f"ApiKeyException: {self.message}"


@log_start_end(log=logger)
def make_request(params: Optional[dict] = None) -> dict:
    """Helper methods for requests [Source: https://docs.whale-alert.io/]

    Parameters
    ----------
    params: dict
        additional param

    Returns
    -------
    dict:
        response from api request
    """

    api_key = cfg.API_WHALE_ALERT_KEY or ""
    url = "https://api.whale-alert.io/v1/transactions?api_key=" + api_key
    response = requests.get(url, params=params)

    if not 200 <= response.status_code < 300:
        raise ApiKeyException(f"Invalid Authentication: {response.text}")
    try:
        return response.json()
    except Exception as e:
        raise ValueError(f"Invalid Response: {response.text}") from e


@log_start_end(log=logger)
def get_whales_transactions(min_value: int = 800000, limit: int = 100) -> pd.DataFrame:
    """Whale Alert's API allows you to retrieve live and historical transaction data from major blockchains.
    Supported blockchain: Bitcoin, Ethereum, Ripple, NEO, EOS, Stellar and Tron. [Source: https://docs.whale-alert.io/]

    Parameters
    ----------
    min_value: int
        Minimum value of trade to track.
    limit: int
        Limit of transactions. Max 100

    Returns
    -------
    pd.DataFrame
        Crypto wales transactions
    """

    min_value = max(min_value, 800000)
    limit = max(limit, 100)

    params = {"limit": limit, "min_value": min_value}

    response = make_request(params)
    data = pd.json_normalize(response["transactions"]).sort_values(
        "timestamp", ascending=False
    )

    data["date"] = pd.to_datetime(data["timestamp"], unit="s")
    data.columns = [col.replace(".balance", "") for col in data.columns]
    data["to_address"] = data["to"].apply(
        lambda x: "\n".join(textwrap.wrap(x, width=45)) if isinstance(x, str) else x
    )
    data["from_address"] = data["from"].apply(
        lambda x: "\n".join(textwrap.wrap(x, width=45)) if isinstance(x, str) else x
    )

    data["from"] = data.apply(
        lambda x: x["from.owner"]
        if x["from.owner"] not in [np.nan, None, np.NaN]
        else x["from.owner_type"],
        axis=1,
    )
    data["to"] = data.apply(
        lambda x: x["to.owner"]
        if x["to.owner"] not in [np.nan, None, np.NaN]
        else x["to.owner_type"],
        axis=1,
    )
    data.drop(
        [
            "id",
            "transaction_count",
            "from.owner_type",
            "to.owner_type",
            "to.owner",
            "from.owner",
            "transaction_type",
            "hash",
            "timestamp",
        ],
        axis=1,
        inplace=True,
    )
    return data[
        [
            "date",
            "symbol",
            "blockchain",
            "amount",
            "amount_usd",
            "from",
            "to",
            "from_address",
            "to_address",
        ]
    ]
