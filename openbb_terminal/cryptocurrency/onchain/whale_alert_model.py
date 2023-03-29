"""Whale Alert model"""
__docformat__ = "numpy"

import logging
import textwrap
from typing import Any, Optional, Tuple

import numpy as np
import pandas as pd

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import request
from openbb_terminal.rich_config import console

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
@check_api_key(["API_WHALE_ALERT_KEY"])
def make_request(params: Optional[dict] = None) -> Tuple[Optional[int], Any]:
    """Helper methods for requests [Source: https://docs.whale-alert.io/]

    Parameters
    ----------
    params: dict
        additional param

    Returns
    -------
    Tuple[Optional[int], Any]
        status code, response from api request
    """

    api_key = get_current_user().credentials.API_WHALE_ALERT_KEY or ""
    url = "https://api.whale-alert.io/v1/transactions?api_key=" + api_key
    try:
        response = request(url, params=params)
    except Exception:
        return None, None

    result = {}

    if response.status_code == 200:
        result = response.json()
    elif response.status_code == 401:
        console.print("[red]Invalid API Key[/red]\n")
        logger.error("Invalid Authentication: %s", response.text)
    elif response.status_code == 401:
        console.print("[red]API Key not authorized for Premium Feature[/red]\n")
        logger.error("Insufficient Authorization: %s", response.text)
    elif response.status_code == 429:
        console.print("[red]Exceeded number of calls per minute[/red]\n")
        logger.error("Calls limit exceeded: %s", response.text)
    else:
        console.print(response.json()["message"])
        logger.error("Error in request: %s", response.text)

    return response.status_code, result


@log_start_end(log=logger)
def get_whales_transactions(
    min_value: int = 800000,
    limit: int = 100,
    sortby: str = "date",
    ascend: bool = False,
) -> pd.DataFrame:
    """Whale Alert's API allows you to retrieve live and historical transaction data from major blockchains.
    Supported blockchain: Bitcoin, Ethereum, Ripple, NEO, EOS, Stellar and Tron. [Source: https://docs.whale-alert.io/]

    Parameters
    ----------
    min_value: int
        Minimum value of trade to track.
    limit: int
        Limit of transactions. Max 100
    sortby: str
        Key to sort by.
    ascend: str
        Sort in ascending order.

    Returns
    -------
    pd.DataFrame
        Crypto wales transactions
    """

    min_value = max(min_value, 800000)
    limit = max(limit, 100)

    params = {"limit": limit, "min_value": min_value}

    status_code, response = make_request(params)

    if status_code != 200:
        return pd.DataFrame()

    data = pd.json_normalize(response["transactions"]).sort_values(
        "timestamp", ascending=False
    )

    data["date"] = pd.to_datetime(data["timestamp"], unit="s")
    data.columns = [col.replace(".balance", "") for col in data.columns]
    data["to_address"] = data["to.address"].apply(
        lambda x: "\n".join(textwrap.wrap(x, width=45)) if isinstance(x, str) else x
    )
    data["from_address"] = data["from.address"].apply(
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

    df = data[
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
    df = df.sort_values(by=sortby, ascending=ascend)
    return df
