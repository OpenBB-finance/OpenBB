"""CollectAPI Model"""
__docformat__ = "numpy"


import logging
import pandas as pd
import requests

from openbb_terminal import config_terminal as cfg
from openbb_terminal.decorators import check_api_key

logger = logging.getLogger(__name__)


@check_api_key(["API_COLLECTAPI_KEY"])
def get_european_gas_prices() -> pd.DataFrame:
    """Get European gas prices. [Source: https://collectapi.com/api/gasPrice]

    Parameters
    ----------

    Returns
    -------
    pd.DataFrame
        DataFrame with data
    """
    res = requests.get(
        "https://api.collectapi.com/gasPrice/europeanCountries",
        headers={
            "content-type": "application/json",
            "authorization": f"{cfg.API_COLLECTAPI_KEY}",
        },
    )
    if res.status_code == 200:
        data = res.json()
        df = pd.DataFrame(data["results"])

        for col in ["diesel", "gasoline", "lpg"]:
            df[col] = df[col].replace("-", "0.0")
            df[col] = df[col].str.replace(",", ".").astype(float)
            df[col] = df[col].fillna(0.0)
        df = df.drop(columns=["currency"])
        df = df.set_index("country")
        df.index.name = "country"
        df = df[(df.T != 0.0).any()]
        return df
    return pd.DataFrame()
