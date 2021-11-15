import json
import pandas as pd
import requests
from gamestonk_terminal import config_terminal as cfg

api_url = "https://api.glassnode.com/v1/metrics/"

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
    until : int
        End date timestamp (e.g., 1_614_556_800)
    interval : str
        Interval frequency (e.g., 24h)

    Returns
    -------
    pd.DataFrame
        active addresses over time
    """

    url = api_url + "addresses/active_count"

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
        df["t"] = pd.to_datetime(df["t"], unit="s")
        df = df.set_index("t")
        return df
    return pd.DataFrame()

def get_exchange_balances(
    asset: str, exchange: str, interval: str, since: int, until: int
) -> pd.DataFrame:
    """Returns the total amount of coins held on exchange addresses in units and percentage. 
    [Source: https://glassnode.com]

    Parameters
    ----------
    asset : str
        Asset to search active addresses (e.g., BTC)
    exchange : str
        Exchange to check net position change (e.g., binance)
    since : int
        Initial date timestamp (e.g., 1_614_556_800)
    until : int
        End date timestamp (e.g., 1_614_556_800)
    interval : str
        Interval frequency (e.g., 24h)

    Returns
    -------
    pd.DataFrame
        total amount of coins in units/percentage and asset price over time
    """

    url = api_url + "distribution/balance_exchanges"
    url2 = api_url + "distribution/balance_exchanges_relative"
    url3 = api_url + "market/price_usd_close"


    parameters = {
        "api_key": cfg.API_GLASSNODE_KEY,
        "a": asset,
        "i": interval,
        "e": exchange,
        "s": str(since),
        "u": str(until),
    }

    r = requests.get(url, params=parameters) # get balances
    r2 = requests.get(url2, params=parameters) # get relative (percentage) balances 
    r3 = requests.get(url3, params=parameters) # get price TODO: grab data from loaded symbol


    if r.status_code == 200 and r2.status_code == 200 and r3.status_code ==200:
        df3 = pd.DataFrame(json.loads(r3.text))
        df2 = pd.DataFrame(json.loads(r2.text))
        df = pd.DataFrame(json.loads(r.text))
        df = df.set_index("t")
        df.index = pd.to_datetime(df.index, unit="s")
        df["percentage"] = df2["v"].values
        df["price"] = df3["v"].values
        df.rename(columns={'v':'stacked'}, inplace=True)
        return df

    return pd.DataFrame()


def get_exchange_net_position_change(
    asset: str, exchange: str, interval: str, since: int, until: int
) -> pd.DataFrame:
    """Returns 30d change of the supply held in exchange wallets of a certain asset.
    [Source: https://glassnode.com]

    Parameters
    ----------
    asset : str
        Asset symbol to search supply (e.g., BTC)
    exchange : str
        Exchange to check net position change (e.g., binance)
    since : int
        Initial date timestamp (e.g., 1_614_556_800)
    until : int
        End date timestamp (e.g., 1_614_556_800)
    interval : str
        Interval frequency (e.g., 24h)

    Returns
    -------
    pd.DataFrame
        supply change in exchange wallets of a certain symbol over time
    """

    url = api_url + "distribution/exchange_net_position_change"

    parameters = {
        "api_key": cfg.API_GLASSNODE_KEY,
        "a": asset,
        "i": interval,
        "e": exchange,
        "s": str(since),
        "u": str(until),
    }

    r = requests.get(url, params=parameters)

    if r.status_code == 200:
        df = pd.DataFrame(json.loads(r.text))
        df["t"] = pd.to_datetime(df["t"], unit="s")
        df = df.set_index("t")
        return df

    return pd.DataFrame()

