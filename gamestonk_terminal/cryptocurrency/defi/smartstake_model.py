"""SmartStake Model"""
__docformat__ = "numpy"

from typing import Union, Dict
import requests
import pandas as pd


def get_luna_supply_stats(supply_type: str, days: int) -> pd.DataFrame:
    """Get supply history of the Terra ecosystem

    Source: [Smartstake.io]

    Parameters
    ----------
    days: int
        Day count to fetch data
    supply_type: str
        Supply type to unpack json

    Returns
    -------
    pd.DataFrame
        Dataframe of supply history data
    """

    payload: Dict[str, Union[int, str]] = {"type": "history", "dayCount": days}

    response = requests.get(
        "https://prod.smartstakeapi.com/"
        "listData?key=2mwTEDr9zXJH323M&token=1643550425&app=TERRA",
        params=payload,
    )

    if response.status_code == 200:
        result = response.json()[supply_type]

        # check if result is not empty
        if result:
            df = pd.DataFrame(result)
            df = df.set_index("title")
            df.index.name = "timestamp_date"
            df.index = pd.to_datetime(df.index)

            return df

    return pd.DataFrame()
