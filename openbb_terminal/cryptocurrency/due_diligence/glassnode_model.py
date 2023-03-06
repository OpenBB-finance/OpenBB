import json
import logging
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import request, str_date_to_timestamp
from openbb_terminal.rich_config import console

# pylint: disable=unsupported-assignment-operation

logger = logging.getLogger(__name__)
# pylint: disable=unsupported-assignment-operation

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


@log_start_end(log=logger)
@check_api_key(["API_GLASSNODE_KEY"])
def get_close_price(
    symbol: str,
    start_date: str = "2010-01-01",
    end_date: Optional[str] = None,
    print_errors: bool = True,
) -> pd.DataFrame:
    """Returns the price of a cryptocurrency
    [Source: https://glassnode.com]

    Parameters
    ----------
    symbol : str
        Crypto to check close price (BTC or ETH)
    start_date : str
        Initial date, format YYYY-MM-DD
    end_date : str
        Final date, format YYYY-MM-DD
    print_errors: bool
        Flag to print errors. Default: True

    Returns
    -------
    pd.DataFrame
        price over time
    """

    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    ts_start_date = str_date_to_timestamp(start_date)
    ts_end_date = str_date_to_timestamp(end_date)

    url = api_url + "market/price_usd_close"

    parameters = {
        "api_key": get_current_user().credentials.API_GLASSNODE_KEY,
        "a": symbol,
        "i": "24h",
        "s": str(ts_start_date),
        "u": str(ts_end_date),
    }

    r = request(url, params=parameters)

    df = pd.DataFrame()

    if r.status_code == 200:
        df = pd.DataFrame(json.loads(r.text))

        if df.empty:
            if print_errors:
                console.print(f"No data found for {symbol} price.\n")
        else:
            df = df.set_index("t")
            df.index = pd.to_datetime(df.index, unit="s")

    elif r.status_code == 401:
        if print_errors:
            console.print("[red]Invalid API Key[/red]\n")
    else:
        if print_errors:
            console.print(r.text)

    return df


@log_start_end(log=logger)
@check_api_key(["API_GLASSNODE_KEY"])
def get_non_zero_addresses(
    symbol: str,
    start_date: str = "2010-01-01",
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Returns addresses with non-zero balance of a certain symbol
    [Source: https://glassnode.com]

    Parameters
    ----------
    symbol : str
        Asset to search (e.g., BTC)
    start_date : str
        Initial date, format YYYY-MM-DD
    end_date : str
        Final date, format YYYY-MM-DD

    Returns
    -------
    pd.DataFrame
        addresses with non-zero balances
    """

    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    ts_start_date = str_date_to_timestamp(start_date)
    ts_end_date = str_date_to_timestamp(end_date)

    url = api_url + "addresses/non_zero_count"

    parameters = {
        "api_key": get_current_user().credentials.API_GLASSNODE_KEY,
        "a": symbol,
        "i": "24h",
        "s": str(ts_start_date),
        "u": str(ts_end_date),
    }

    r = request(url, params=parameters)

    df = pd.DataFrame()

    if r.status_code == 200:
        df = pd.DataFrame(json.loads(r.text))

        if df.empty:
            console.print(f"No data found for {symbol}'s non-zero addresses.\n")
        else:
            df["t"] = pd.to_datetime(df["t"], unit="s")
            df = df.set_index("t")

    elif r.status_code == 401:
        console.print("[red]Invalid API Key[/red]\n")
    else:
        console.print(r.text)

    return df


@log_start_end(log=logger)
@check_api_key(["API_GLASSNODE_KEY"])
def get_active_addresses(
    symbol: str,
    interval: str = "24h",
    start_date: str = "2010-01-01",
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Returns active addresses of a certain symbol
    [Source: https://glassnode.com]

    Parameters
    ----------
    symbol : str
        Asset to search active addresses (e.g., BTC)
    interval : str
        Interval frequency (e.g., 24h)
    start_date : str
        Initial date, format YYYY-MM-DD
    end_date : str
        Final date, format YYYY-MM-DD

    Returns
    -------
    pd.DataFrame
        active addresses over time
    """

    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    ts_start_date = str_date_to_timestamp(start_date)
    ts_end_date = str_date_to_timestamp(end_date)

    url = api_url + "addresses/active_count"

    parameters = {
        "api_key": get_current_user().credentials.API_GLASSNODE_KEY,
        "a": symbol,
        "i": interval,
        "s": str(ts_start_date),
        "u": str(ts_end_date),
    }

    r = request(url, params=parameters)
    df = pd.DataFrame()

    if r.status_code == 200:
        df = pd.DataFrame(json.loads(r.text))

        if df.empty:
            console.print(f"No data found for {symbol}'s active addresses.\n")
        else:
            df["t"] = pd.to_datetime(df["t"], unit="s")
            df = df.set_index("t")

    elif r.status_code == 401:
        console.print("[red]Invalid API Key[/red]\n")
    else:
        console.print(r.text)

    return df


@log_start_end(log=logger)
@check_api_key(["API_GLASSNODE_KEY"])
def get_hashrate(
    symbol: str,
    interval: str = "24h",
    start_date: str = "2010-01-01",
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Returns dataframe with mean hashrate of btc or eth blockchain and symbol price
    [Source: https://glassnode.com]

    Parameters
    ----------
    symbol : str
        Blockchain to check hashrate (BTC or ETH)
    start_date : str
        Initial date, format YYYY-MM-DD
    end_date : str
        Final date, format YYYY-MM-DD
    interval : str
        Interval frequency (e.g., 24h)

    Returns
    -------
    pd.DataFrame
        mean hashrate and symbol price over time
    """

    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    ts_start_date = str_date_to_timestamp(start_date)
    ts_end_date = str_date_to_timestamp(end_date)

    url = api_url + "mining/hash_rate_mean"
    url2 = api_url + "market/price_usd_close"

    parameters = {
        "api_key": get_current_user().credentials.API_GLASSNODE_KEY,
        "a": symbol,
        "i": interval,
        "s": str(ts_start_date),
        "u": str(ts_end_date),
    }

    df = pd.DataFrame()

    r = request(url, params=parameters)
    r2 = request(url2, params=parameters)

    if r.status_code == 200 and r2.status_code == 200:
        df = pd.DataFrame(json.loads(r.text))
        df2 = pd.DataFrame(json.loads(r2.text))

        if df.empty or df2.empty:
            console.print(f"No data found for {symbol}'s hashrate or price.\n")
        else:
            df = df.set_index("t")
            df2 = df2.set_index("t")
            df.index = pd.to_datetime(df.index, unit="s")
            df = df.rename(columns={"v": "hashrate"})
            df2.index = pd.to_datetime(df2.index, unit="s")
            df2 = df2.rename(columns={"v": "price"})
            df = df.merge(df2, left_index=True, right_index=True, how="outer")

    elif r.status_code == 401 or r2.status_code == 401:
        console.print("[red]Invalid API Key[/red]\n")

    else:
        if r.status_code != 200:
            console.print(f"Error getting hashrate: {r.text}")

        if r2.status_code != 200:
            console.print(f"Error getting {symbol} price: {r2.text}")

    return df


@log_start_end(log=logger)
@check_api_key(["API_GLASSNODE_KEY"])
def get_exchange_balances(
    symbol: str,
    exchange: str = "aggregated",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Returns the total amount of coins held on exchange addresses in units and percentage.
    [Source: https://glassnode.com]

    Parameters
    ----------
    symbol : str
        Asset to search active addresses (e.g., BTC)
    exchange : str
        Exchange to check net position change (possible values are: aggregated, binance, bittrex,
        coinex, gate.io, gemini, huobi, kucoin, poloniex, bibox, bigone, bitfinex, hitbtc, kraken,
        okex, bithumb, zb.com, cobinhood, bitmex, bitstamp, coinbase, coincheck, luno), by default "aggregated"
    start_date : Optional[str], optional
        Initial date (format YYYY-MM-DD) by default 2 years ago
    end_date : Optional[str], optional
        Final date (format YYYY-MM-DD) by default 1 year ago

    Returns
    -------
    pd.DataFrame
        total amount of coins in units/percentage and symbol price over time

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> df = openbb.crypto.dd.eb(symbol="BTC")
    """

    if start_date is None:
        start_date = (datetime.now() - timedelta(days=365 * 2)).strftime("%Y-%m-%d")

    if end_date is None:
        end_date = (datetime.now() - timedelta(days=367)).strftime("%Y-%m-%d")

    ts_start_date = str_date_to_timestamp(start_date)
    ts_end_date = str_date_to_timestamp(end_date)

    url = api_url + "distribution/balance_exchanges"
    url2 = api_url + "distribution/balance_exchanges_relative"
    url3 = api_url + "market/price_usd_close"

    parameters = {
        "api_key": get_current_user().credentials.API_GLASSNODE_KEY,
        "a": symbol,
        "i": "24h",
        "e": exchange,
        "s": str(ts_start_date),
        "u": str(ts_end_date),
    }
    df = pd.DataFrame()

    r1 = request(url, params=parameters)  # get balances
    r2 = request(url2, params=parameters)  # get relative (percentage) balances
    r3 = request(
        url3, params=parameters
    )  # get price TODO: grab data from loaded symbol

    if r1.status_code == 200 and r2.status_code == 200 and r3.status_code == 200:
        df1 = pd.DataFrame(json.loads(r1.text))
        df1.set_index("t", inplace=True)
        df1.rename(columns={"v": "stacked"}, inplace=True)

        df2 = pd.DataFrame(json.loads(r2.text))
        df2.set_index("t", inplace=True)
        df2.rename(columns={"v": "percentage"}, inplace=True)

        df3 = pd.DataFrame(json.loads(r3.text))
        df3.set_index("t", inplace=True)
        df3.rename(columns={"v": "price"}, inplace=True)

        df = pd.merge(df1, df2, left_index=True, right_index=True)
        df = pd.merge(df, df3, left_index=True, right_index=True)
        df.index = pd.to_datetime(df.index, unit="s")

        if df.empty or df1.empty or df2.empty or df3.empty:
            console.print(f"No data found for {symbol}'s exchange balance or price.\n")

    elif r1.status_code == 401 or r2.status_code == 401 or r3.status_code == 401:
        console.print("[red]Invalid API Key[/red]\n")
    else:
        if r1.status_code != 200:
            console.print(f"Error getting {symbol}'s exchange balance: {r1.text}")

        if r2.status_code != 200:
            console.print(
                f"Error getting {symbol}'s exchange balance relatives: {r2.text}"
            )

        if r3.status_code != 200:
            console.print(f"Error getting {symbol} price: {r3.text}")

    return df


@log_start_end(log=logger)
@check_api_key(["API_GLASSNODE_KEY"])
def get_exchange_net_position_change(
    symbol: str,
    exchange: str = "binance",
    start_date: str = "2010-01-01",
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Returns 30d change of the supply held in exchange wallets of a certain symbol.
    [Source: https://glassnode.com]

    Parameters
    ----------
    symbol : str
        Asset symbol to search supply (e.g., BTC)
    exchange : str
        Exchange to check net position change (e.g., binance)
    start_date : Optional[str]
        Initial date, format YYYY-MM-DD
    end_date : Optional[str]
        Final date, format YYYY-MM-DD

    Returns
    -------
    pd.DataFrame
        supply change in exchange wallets of a certain symbol over time
    """

    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    ts_start_date = str_date_to_timestamp(start_date)
    ts_end_date = str_date_to_timestamp(end_date)

    url = api_url + "distribution/exchange_net_position_change"

    parameters = {
        "api_key": get_current_user().credentials.API_GLASSNODE_KEY,
        "a": symbol,
        "i": "24h",
        "e": exchange,
        "s": str(ts_start_date),
        "u": str(ts_end_date),
    }

    r = request(url, params=parameters)
    df = pd.DataFrame()

    if r.status_code == 200:
        df = pd.DataFrame(json.loads(r.text))

        if df.empty:
            console.print(f"No data found for {symbol}'s net position change.\n")
        else:
            df["t"] = pd.to_datetime(df["t"], unit="s")
            df = df.set_index("t")
    elif r.status_code == 401:
        console.print("[red]Invalid API Key[/red]\n")
    else:
        console.print(r.text)

    return df
