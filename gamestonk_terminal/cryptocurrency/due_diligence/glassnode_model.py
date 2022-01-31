import json
import logging

import pandas as pd
import requests

from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)

api_url = "https://api.glassnode.com/v1/metrics/"

GLASSNODE_SUPPORTED_HASHRATE_ASSETS = ["BTC", "ETH"]

GLASSNODE_SUPPORTED_EXCHANGES = [
    "aggregated",
    "binance",
    "bittrex",
    "coinex",
    "gate.io",
    "gemini",
    "huobi",
    "kucoin",
    "poloniex",
    "bibox",
    "bigone",
    "bitfinex",
    "hitbtc",
    "kraken",
    "okex",
    "bithumb",
    "zb.com",
    "cobinhood",
    "bitmex",
    "bitstamp",
    "coinbase",
    "coincheck",
    "luno",
]

GLASSNODE_SUPPORTED_ASSETS = [
    "BTC",
    "ETH",
    "LTC",
    "AAVE",
    "ABT",
    "AMPL",
    "ANT",
    "ARMOR",
    "BADGER",
    "BAL",
    "BAND",
    "BAT",
    "BIX",
    "BNT",
    "BOND",
    "BRD",
    "BUSD",
    "BZRX",
    "CELR",
    "CHSB",
    "CND",
    "COMP",
    "CREAM",
    "CRO",
    "CRV",
    "CVC",
    "CVP",
    "DAI",
    "DDX",
    "DENT",
    "DGX",
    "DHT",
    "DMG",
    "DODO",
    "DOUGH",
    "DRGN",
    "ELF",
    "ENG",
    "ENJ",
    "EURS",
    "FET",
    "FTT",
    "FUN",
    "GNO",
    "GUSD",
    "HEGIC",
    "HOT",
    "HPT",
    "HT",
    "HUSD",
    "INDEX",
    "KCS",
    "LAMB",
    "LBA",
    "LDO",
    "LEO",
    "LINK",
    "LOOM",
    "LRC",
    "MANA",
    "MATIC",
    "MCB",
    "MCO",
    "MFT",
    "MIR",
    "MKR",
    "MLN",
    "MTA",
    "MTL",
    "MX",
    "NDX",
    "NEXO",
    "NFTX",
    "NMR",
    "Nsure",
    "OCEAN",
    "OKB",
    "OMG",
    "PAX",
    "PAY",
    "PERP",
    "PICKLE",
    "PNK",
    "PNT",
    "POLY",
    "POWR",
    "PPT",
    "QASH",
    "QKC",
    "QNT",
    "RDN",
    "REN",
    "REP",
    "RLC",
    "ROOK",
    "RPL",
    "RSR",
    "SAI",
    "SAN",
    "SNT",
    "SNX",
    "STAKE",
    "STORJ",
    "sUSD",
    "SUSHI",
    "TEL",
    "TOP",
    "UBT",
    "UMA",
    "UNI",
    "USDC",
    "USDK",
    "USDT",
    "UTK",
    "VERI",
    "WaBi",
    "WAX",
    "WBTC",
    "WETH",
    "wNMX",
    "WTC",
    "YAM",
    "YFI",
    "ZRX",
]

INTERVALS_HASHRATE = ["24h", "1w", "1month"]
INTERVALS_ACTIVE_ADDRESSES = ["24h", "1w", "1month"]
INTERVALS_NON_ZERO_ADDRESSES = ["24h"]
INTERVALS_DISPLAY_EXCHANGE_NET_POSITION_CHANGE = ["24h"]
INTERVALS_EXCHANGE_BALANCES = ["24h"]


@log_start_end(log=logger)
def get_close_price(asset: str, interval: str, since: int, until: int) -> pd.DataFrame:
    """Returns the price of a cryptocurrency
    [Source: https://glassnode.com]

    Parameters
    ----------
    asset : str
        Crypto to check close price (BTC or ETH)
    since : int
        Initial date timestamp (e.g., 1_614_556_800)
    until : int
        End date timestamp (e.g., 1_641_227_783_561)
    interval : str
        Interval frequency (e.g., 24h)

    Returns
    -------
    pd.DataFrame
        price over time
    """

    url = api_url + "market/price_usd_close"

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
        return df

    return pd.DataFrame()


@log_start_end(log=logger)
def get_non_zero_addresses(
    asset: str, interval: str, since: int, until: int
) -> pd.DataFrame:
    """Returns addresses with non-zero balance of a certain asset
    [Source: https://glassnode.com]

    Parameters
    ----------
    asset : str
        Asset to search (e.g., BTC)
    since : int
        Initial date timestamp (e.g., 1_577_836_800)
    until : int
        End date timestamp (e.g., 1_609_459_200)
    interval : str
        Interval frequency (e.g., 24h)

    Returns
    -------
    pd.DataFrame
        addresses with non-zero balances
    """

    url = api_url + "addresses/non_zero_count"

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


@log_start_end(log=logger)
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


@log_start_end(log=logger)
def get_hashrate(asset: str, interval: str, since: int, until: int) -> pd.DataFrame:
    """Returns dataframe with mean hashrate of btc or eth blockchain and asset price
    [Source: https://glassnode.com]

    Parameters
    ----------
    asset : str
        Blockchain to check hashrate (BTC or ETH)
    since : int
        Initial date timestamp (e.g., 1_614_556_800)
    until : int
        End date timestamp (e.g., 1_614_556_800)
    interval : str
        Interval frequency (e.g., 24h)

    Returns
    -------
    pd.DataFrame
        mean hashrate and asset price over time
    """

    url = api_url + "mining/hash_rate_mean"
    url2 = api_url + "market/price_usd_close"

    parameters = {
        "api_key": cfg.API_GLASSNODE_KEY,
        "a": asset,
        "i": interval,
        "s": str(since),
        "u": str(until),
    }

    r = requests.get(url, params=parameters)
    r2 = requests.get(url2, params=parameters)
    if r.status_code == 200 and r2.status_code == 200:
        df2 = pd.DataFrame(json.loads(r2.text))
        df = pd.DataFrame(json.loads(r.text))
        df = df.set_index("t")
        df.index = pd.to_datetime(df.index, unit="s")
        df["price"] = df2["v"].values
        df.rename(columns={"v": "hashrate"}, inplace=True)
        return df

    return pd.DataFrame()


@log_start_end(log=logger)
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

    r = requests.get(url, params=parameters)  # get balances
    r2 = requests.get(url2, params=parameters)  # get relative (percentage) balances
    r3 = requests.get(
        url3, params=parameters
    )  # get price TODO: grab data from loaded symbol

    if r.status_code == 200 and r2.status_code == 200 and r3.status_code == 200:
        df3 = pd.DataFrame(json.loads(r3.text))
        df2 = pd.DataFrame(json.loads(r2.text))
        df = pd.DataFrame(json.loads(r.text))
        df = df.set_index("t")
        df.index = pd.to_datetime(df.index, unit="s")
        df["percentage"] = df2["v"].values
        df["price"] = df3["v"].values
        df.rename(columns={"v": "stacked"}, inplace=True)
        return df

    return pd.DataFrame()


@log_start_end(log=logger)
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
