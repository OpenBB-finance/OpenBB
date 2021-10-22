import json
import pandas as pd
import requests
from gamestonk_terminal import config_terminal as cfg


def get_active_addresses(
    asset: str, interval: str, since: int, until: int
) -> pd.DataFrame:
    """Returns active addresses of a certain asset
    [Source: https://glassnode.com]

    Parameters
    ----------
    asset : str
        Asset to search active addresses (e.g., BTC)
    since : int
        Initial date timestamp (e.g., 1_614_556_800)
    until : str
        End date timestamp (e.g., 1_614_556_800)
    interval : str
        Interval frequency (e.g., 24h)

    Returns
    -------
    pd.DataFrame
        active addresses over time
    """

    url = "https://api.glassnode.com/v1/metrics/addresses/active_count"

    parameters = {
        "api_key": cfg.API_GLASSNODE_KEY,
        "a": asset,
        "i": interval,
        "s": str(since),
        "u": str(until),
    }

    r = requests.get(url, params=parameters)

    if r.status_code == 200:
        df = pd.DataFrame(json.loads(r.text))
        df = df.set_index("t")
        df.index = pd.to_datetime(df.index, unit="s")
        df = df.loc[df.index > "2010-1-1"]
        df.reset_index(inplace=True)
        return df
    return pd.DataFrame()
