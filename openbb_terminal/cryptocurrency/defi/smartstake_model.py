"""SmartStake Model"""
__docformat__ = "numpy"

from typing import Dict, Union

import pandas as pd

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import check_api_key
from openbb_terminal.helper_funcs import request
from openbb_terminal.rich_config import console


@check_api_key(["API_SMARTSTAKE_KEY", "API_SMARTSTAKE_TOKEN"])
def get_luna_supply_stats(
    supply_type: str = "lunaSupplyChallengeStats", days: int = 30
) -> pd.DataFrame:
    """Get supply history of the Terra ecosystem

    Source: [Smartstake.io]

    Parameters
    ----------
    supply_type: str
        Supply type to unpack json
    days: int
        Day count to fetch data

    Returns
    -------
    pd.DataFrame
        Dataframe of supply history data
    """

    current_user = get_current_user()

    payload: Dict[str, Union[int, str]] = {
        "type": "history",
        "dayCount": days,
        "key": current_user.credentials.API_SMARTSTAKE_KEY,
        "token": current_user.credentials.API_SMARTSTAKE_TOKEN,
    }

    response = request(
        "https://prod.smartstakeapi.com/listData?app=TERRA",
        params=payload,
    )
    response_json = response.json()

    df = pd.DataFrame()

    if "errors" in response_json:
        if "DENIED" in response_json["errors"]:
            console.print("[red]Invalid API Key[/red]\n")
        else:
            console.print(response_json["errors"])

    else:
        result = response_json[supply_type]

        # check if result is not empty
        if result:
            df = pd.DataFrame(result)
            df = df.set_index("title")
            df.index.name = "timestamp_date"
            df.index = pd.to_datetime(df.index)

        else:
            console.print("No data found")

    return df
