"""CoinPaprika model"""
__docformat__ = "numpy"

import logging
import textwrap
from datetime import datetime, timedelta
from typing import Optional, Tuple

import pandas as pd
from dateutil import parser

from openbb_terminal.cryptocurrency.coinpaprika_helpers import PaprikaSession
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

# pylint: disable=unsupported-assignment-operation

logger = logging.getLogger(__name__)
# pylint: disable=unsupported-assignment-operation


@log_start_end(log=logger)
def get_coin_twitter_timeline(
    symbol: str = "BTC", sortby: str = "date", ascend: bool = True
) -> pd.DataFrame:
    """Get twitter timeline for given coin id. Not more than last 50 tweets [Source: CoinPaprika]

    Parameters
    ----------
    symbol: str
        Cryptocurrency symbol (e.g. BTC)
    sortby: str
        Key by which to sort data. Every column name is valid
        (see for possible values:
        https://api.coinpaprika.com/docs#tag/Coins/paths/~1coins~1%7Bcoin_id%7D~1twitter/get).
    ascend: bool
        Flag to sort data descending

    Returns
    -------
    pd.DataFrame
        Twitter timeline for given coin.
        Columns: date, user_name, status, retweet_count, like_count
    """
    # get coinpaprika id using crypto symbol
    cp_id = get_coinpaprika_id(symbol)

    session = PaprikaSession()
    res = session.make_request(session.ENDPOINTS["coin_tweeter"].format(cp_id))
    if "error" in res:
        console.print(res)
        return pd.DataFrame()
    if isinstance(res, list) and len(res) == 0:
        return pd.DataFrame()
    df = pd.DataFrame(res)[
        ["date", "user_name", "status", "retweet_count", "like_count"]
    ]

    df = df.applymap(
        lambda x: "\n".join(textwrap.wrap(x, width=80)) if isinstance(x, str) else x
    )
    df["status"] = df["status"].apply(lambda x: x.replace("  ", ""))
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%dT%H:%M:%SZ").dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    df = df.sort_values(by=sortby, ascending=ascend)
    # Remove unicode chars (it breaks pretty tables)
    df["status"] = df["status"].apply(
        lambda text: "".join(i if ord(i) < 128 else "" for i in text)
    )
    return df


@log_start_end(log=logger)
def get_coin_events_by_id(
    symbol: str = "BTC", sortby: str = "date", ascend: bool = False
) -> pd.DataFrame:
    """Get all events related to given coin like conferences, start date of futures trading etc.
    [Source: CoinPaprika]

    Example of response from API:

    .. code-block:: json

    {
        "id": "17398-cme-april-first-trade",
        "date": "2018-04-02T00:00:00Z",
        "date_to": "string",
        "name": "CME: April First Trade",
        "description": "First trade of Bitcoin futures contract for April 2018.",
        "is_conference": false,
        "link": "http://www.cmegroup.com/trading/equity-index/us-index/bitcoin_product_calendar_futures.html",
        "proof_image_link": "https://static.coinpaprika.com/storage/cdn/event_images/16635.jpg"
    }

    Parameters
    ----------
    symbol: str
        Cryptocurrency symbol (e.g. BTC)
    sortby: str
        Key by which to sort data. Every column name is valid
        (see for possible values:
        https://api.coinpaprika.com/docs#tag/Coins/paths/~1coins~1%7Bcoin_id%7D~1events/get).
    ascend: bool
        Flag to sort data ascending

    Returns
    -------
    pd.DataFrame
        Events found for given coin
        Columns: id, date , date_to, name, description, is_conference, link, proof_image_link
    """
    # get coinpaprika id using crypto symbol
    cp_id = get_coinpaprika_id(symbol)

    session = PaprikaSession()
    res = session.make_request(session.ENDPOINTS["coin_events"].format(cp_id))
    if not res or "error" in res:
        return pd.DataFrame()
    data = pd.DataFrame(res)
    data["description"] = data["description"].apply(
        lambda x: "\n".join(textwrap.wrap(x, width=40)) if isinstance(x, str) else x
    )
    data.drop(["id", "proof_image_link"], axis=1, inplace=True)
    data["date"] = pd.to_datetime(
        data["date"], format="%Y-%m-%dT%H:%M:%SZ"
    ).dt.strftime("%Y-%m-%d %H:%M:%S")
    data["date_to"] = pd.to_datetime(
        data["date_to"], format="%Y-%m-%dT%H:%M:%SZ"
    ).dt.strftime("%Y-%m-%d %H:%M:%S")
    data = data.sort_values(by=sortby, ascending=ascend)

    return data


@log_start_end(log=logger)
def get_coin_exchanges_by_id(
    symbol: str = "BTC",
    sortby: str = "adjusted_volume_24h_share",
    ascend: bool = True,
) -> pd.DataFrame:
    """Get all exchanges for given coin id. [Source: CoinPaprika]

    Parameters
    ----------
    symbol: str
        Cryptocurrency symbol (e.g. BTC)
    sortby: str
        Key by which to sort data. Every column name is valid (see for possible values:
        https://api.coinpaprika.com/v1).
    ascend: bool
        Flag to sort data ascending

    Returns
    -------
    pd.DataFrame
        All exchanges for given coin
        Columns: id, name, adjusted_volume_24h_share, fiats
    """
    # get coinpaprika id using crypto symbol
    cp_id = get_coinpaprika_id(symbol)

    session = PaprikaSession()
    res = session.make_request(session.ENDPOINTS["coin_exchanges"].format(cp_id))
    df = pd.DataFrame(res)

    if "fiats" in df.columns.tolist():
        df["fiats"] = (
            df["fiats"].copy().apply(lambda x: len([i["symbol"] for i in x if x]))
        )
    df = df.sort_values(by=sortby, ascending=ascend)
    return df


@log_start_end(log=logger)
def get_coin_markets_by_id(
    symbol: str = "BTC",
    quotes: str = "USD",
    sortby: str = "pct_volume_share",
    ascend: bool = True,
) -> pd.DataFrame:
    """All markets for given coin and currency [Source: CoinPaprika]

    Parameters
    ----------
    symbol: str
        Cryptocurrency symbol (e.g. BTC)
    quotes: str
        Comma separated list of quotes to return.
        Example: quotes=USD,BTC
        Allowed values:
        BTC, ETH, USD, EUR, PLN, KRW, GBP, CAD, JPY, RUB, TRY, NZD, AUD, CHF, UAH, HKD, SGD, NGN,
        PHP, MXN, BRL, THB, CLP, CNY, CZK, DKK, HUF, IDR, ILS, INR, MYR, NOK, PKR, SEK, TWD, ZAR,
        VND, BOB, COP, PEN, ARS, ISK
    sortby: str
        Key by which to sort data. Every column name is valid (see for possible values:
        https://api.coinpaprika.com/v1).
    ascend: bool
        Flag to sort data ascending

    Returns
    -------
    pd.DataFrame
        All markets for given coin and currency
    """
    if sortby in ["volume", "price"]:
        sortby = f"{str(symbol).lower()}_{sortby}"

    # get coinpaprika id using crypto symbol
    cp_id = get_coinpaprika_id(symbol)

    session = PaprikaSession()
    markets = session.make_request(
        session.ENDPOINTS["coin_markets"].format(cp_id), quotes=quotes
    )
    if "error" in markets:
        console.print(markets)
        return pd.DataFrame()

    data = []
    for r in markets:
        dct = {
            "exchange": r.get("exchange_name"),
            "pair": r.get("pair"),
            "trust_score": r.get("trust_score"),
            "pct_volume_share": r.get("adjusted_volume_24h_share"),
        }
        _quotes: dict = r.get("quotes")
        for k, v in _quotes.items():
            dct[f"{k.lower()}_price"] = v.get("price")
            dct[f"{k.lower()}_volume"] = v.get("volume_24h")
        dct["market_url"] = r.get("market_url")
        data.append(dct)

    df = pd.DataFrame(data)
    df = df.sort_values(by=sortby, ascending=ascend)
    return df


@log_start_end(log=logger)
def get_ohlc_historical(
    symbol: str = "eth-ethereum", quotes: str = "USD", days: int = 90
) -> pd.DataFrame:
    """
    Open/High/Low/Close values with volume and market_cap. [Source: CoinPaprika]
    Request example: https://api.coinpaprika.com/v1/coins/btc-bitcoin/ohlcv/historical?start=2019-01-01&end=2019-01-20
    if the last day is current day it can an change with every request until actual close of the day at 23:59:59


    Parameters
    ----------
    symbol: str
        Paprika coin identifier e.g. eth-ethereum
    quotes: str
        returned data quote (available values: usd btc)
    days: int
        time range for chart in days. Maximum 365

    Returns
    -------
    pd.DataFrame
        Open/High/Low/Close values with volume and market_cap.
    """

    if quotes.lower() not in ["usd", "btc"]:
        quotes = "USD"

    if abs(int(days)) > 365:
        days = 365

    end = datetime.now().strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    session = PaprikaSession()
    data = session.make_request(
        session.ENDPOINTS["ohlcv_hist"].format(symbol),
        quotes=quotes,
        start=start,
        end=end,
    )
    if "error" in data:
        # console.print(
        #    "Could not load data. Try use symbol (e.g., btc) instead of coin name (e.g., bitcoin)"
        # )
        return pd.DataFrame()
    return pd.DataFrame(data)


@log_start_end(log=logger)
def get_tickers_info_for_coin(symbol: str = "BTC", quotes: str = "USD") -> pd.DataFrame:
    """Get all most important ticker related information for given coin id [Source: CoinPaprika]

    .. code-block:: json

        {
            "id": "btc-bitcoin",
            "name": "Bitcoin",
            "symbol": "BTC",
            "rank": 1,
            "circulating_supply": 17007062,
            "total_supply": 17007062,
            "max_supply": 21000000,
            "beta_value": 0.735327,
            "first_data_at": "2010-11-14T07:20:41Z",
            "last_updated": "2018-11-14T07:20:41Z",
            "quotes": {
                "USD": {
                    "price": 5162.15941296,
                    "volume_24h": 7304207651.1585,
                    "volume_24h_change_24h": -2.5,
                    "market_cap": 91094433242,
                    "market_cap_change_24h": 1.6,
                    "percent_change_15m": 0,
                    "percent_change_30m": 0,
                    "percent_change_1h": 0,
                    "percent_change_6h": 0,
                    "percent_change_12h": -0.09,
                    "percent_change_24h": 1.59,
                    "percent_change_7d": 0.28,
                    "percent_change_30d": 27.39,
                    "percent_change_1y": -37.99,
                    "ath_price": 20089,
                    "ath_date": "2017-12-17T12:19:00Z",
                    "percent_from_price_ath": -74.3
                }
            }
        }

    Parameters
    ----------
    symbol: str
        Cryptocurrency symbol (e.g. BTC)
    quotes: str
        Comma separated quotes to return e.g quotes = USD, BTC

    Returns
    -------
    pd.DataFrame
        Most important ticker related information
        Columns: Metric, Value
    """
    # get coinpaprika id using crypto symbol
    cp_id = get_coinpaprika_id(symbol)

    session = PaprikaSession()
    tickers = session.make_request(
        session.ENDPOINTS["ticker_info"].format(cp_id), quotes=quotes
    )

    for key, date in tickers.items():
        if "date" in key or "data" in key:
            try:
                tickers[key] = parser.parse(date).strftime("%Y-%m-%d %H:%M:%S")
            except (KeyError, ValueError, TypeError) as e:
                logger.exception(str(e))
                console.print(e)
        if key == "quotes":
            try:
                tickers[key][quotes]["ath_date"] = parser.parse(
                    tickers[key][quotes]["ath_date"]
                ).strftime("%Y-%m-%d %H:%M:%S")
            except (KeyError, ValueError, TypeError) as e:
                logger.exception(str(e))
                console.print(e)

    df = pd.json_normalize(tickers)
    try:
        df.columns = [col.replace("quotes.", "") for col in list(df.columns)]
        df.columns = [col.replace(".", "_").lower() for col in list(df.columns)]
    except KeyError as e:
        logger.exception(str(e))
        console.print(e)
    df = df.T.reset_index()
    df.columns = ["Metric", "Value"]
    return df


@log_start_end(log=logger)
def basic_coin_info(symbol: str = "BTC") -> pd.DataFrame:
    """Basic coin information [Source: CoinPaprika]

    Parameters
    ----------
    symbol: str
        Cryptocurrency symbol (e.g. BTC)

    Returns
    -------
    pd.DataFrame
        Metric, Value
    """
    # get coinpaprika id using crypto symbol
    cp_id = get_coinpaprika_id(symbol)

    coin = get_coin(cp_id)
    tags = coin.get("tags") or []
    keys = [
        "id",
        "name",
        "symbol",
        "rank",
        "type",
        "description",
        "platform",
        "proof_type",
        "contract",
    ]
    results = {key: coin.get(key) for key in keys}
    try:
        tags = ", ".join(t.get("name") for t in tags)
        parent = coin.get("parent") or {}
    except (KeyError, IndexError):
        tags, parent = [], {}

    results["tags"] = tags
    results["parent"] = parent.get("id")
    df = pd.Series(results).reset_index()
    df.columns = ["Metric", "Value"]
    df["Value"] = df["Value"].apply(
        lambda x: "\n".join(textwrap.wrap(x, width=80)) if isinstance(x, str) else x
    )
    df.dropna(subset=["Value"], inplace=True)
    return df


@log_start_end(log=logger)
def get_coin(symbol: str = "eth-ethereum") -> dict:
    """Get coin by id [Source: CoinPaprika]

    Parameters
    ----------
    symbol: str
        id of coin from coinpaprika e.g. Ethereum - > 'eth-ethereum'
    Returns
    -------
    dict
        Coin response
    """

    session = PaprikaSession()
    coin = session.make_request(session.ENDPOINTS["coin"].format(symbol))
    return coin


def get_coinpaprika_id(symbol: str) -> Optional[str]:
    paprika_coins = get_coin_list()
    paprika_coins_dict = dict(zip(paprika_coins.id, paprika_coins.symbol))
    coinpaprika_id, _ = validate_coin(symbol.upper(), paprika_coins_dict)
    return coinpaprika_id


def get_coin_list() -> pd.DataFrame:
    """Get list of all available coins on CoinPaprika  [Source: CoinPaprika]

    Returns
    -------
    pandas.DataFrame
        Available coins on CoinPaprika
        rank, id, name, symbol, type
    """

    session = PaprikaSession()
    coins = session.make_request(session.ENDPOINTS["coins"])
    df = pd.DataFrame(coins)
    df = df[df["is_active"]]
    return df[["rank", "id", "name", "symbol", "type"]]


def validate_coin(symbol: str, coins_dct: dict) -> Tuple[Optional[str], Optional[str]]:
    """
    Helper method that validates if proper coin id or symbol was provided
    [Source: CoinPaprika]

    Parameters
    ----------
    symbol: str
        id or symbol of coin for CoinPaprika
    coins_dct: dict
        dictionary of coins

    Returns
    -------
    Tuple[Optional[str], Optional[str]]
        coin id, coin symbol
    """

    for key, value in coins_dct.items():
        if symbol == value:
            return key, value.lower()
    return None, None
