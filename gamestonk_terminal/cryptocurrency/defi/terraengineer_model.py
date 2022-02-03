"""Terra Engineer model"""
__docformat__ = "numpy"

import logging

import pandas as pd
import requests

from gamestonk_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)

api_url = "https://terra.engineer/en"

ASSETS = ["ust", "luna", "sdt"]


@log_start_end(log=logger)
def get_history_asset_from_terra_address(
    asset: str = "ust", address: str = ""
) -> pd.DataFrame:
    """Returns historical data of an asset in a certain terra address
    [Source: https://terra.engineer/]

    Parameters
    ----------
    asset : str
        Terra asset {ust,luna,sdt}
    address : str
        Terra address. Valid terra addresses start with 'terra'
    Returns
    -------
    pd.DataFrame
        historical data
    """

    if asset.lower() not in ASSETS:
        raise Exception(f"Select a valid asset from {', '.join(ASSETS)}")

    if not address.startswith("terra"):
        raise Exception(
            "Select a valid address. Valid terra addresses start with 'terra'"
        )

    response = requests.get(
        f"{api_url}/terra_addresses/{address}/show_snapshot_data.json?asset={asset.lower()}"
    )
    if response.status_code != 200:
        raise Exception(f"Status code: {response.status_code}. Reason: {response.text}")

    data = response.json()
    df = pd.DataFrame(data[0]["data"])
    df["x"] = pd.to_datetime(df["x"])

    return df
