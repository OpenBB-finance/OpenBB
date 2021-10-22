import json
import pandas as pd
from requests import Session
from requests.exceptions import Timeout, TooManyRedirects
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
        "s": since,
        "u": until,
    }

    session = Session()
    try:
        response = session.get(url, params=parameters)
    except (ConnectionError, Timeout, TooManyRedirects):
        return pd.DataFrame()

    df = pd.DataFrame(json.loads(response.text))
    df = df.set_index("t")
    df.index = pd.to_datetime(df.index, unit="s")
    df = df.loc[df.index > "2010-1-1"]
    df.reset_index(inplace=True)
    return df
