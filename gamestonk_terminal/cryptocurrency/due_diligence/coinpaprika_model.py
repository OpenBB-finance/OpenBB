"""CoinPaprika model"""
__docformat__ = "numpy"

from datetime import datetime, timedelta
import textwrap
import pandas as pd
from dateutil import parser
from gamestonk_terminal.cryptocurrency.coinpaprika_helpers import PaprikaSession


def get_coin(coin_id="eth-ethereum"):
    """Get coin by id
    Parameters
    ----------
    coin_id: str
        id of coin from coinpaprika e.g. Ethereum - > 'eth-ethereum'
    Returns
    -------
    dict with response
    """
    session = PaprikaSession()
    coin = session.make_request(session.ENDPOINTS["coin"].format(coin_id))
    return coin


def get_coin_twitter_timeline(coin_id="eth-ethereum"):
    """Get twitter timeline for given coin id. Not more than last 50 tweets

    Parameters
    ----------
    coin_id: str
        id of coin from coinpaprika e.g. Ethereum - > 'eth-ethereum'
    Returns
    -------
    pandas.DataFrame
        date, user_name, status, retweet_count, like_count

    """
    session = PaprikaSession()
    res = session.make_request(session.ENDPOINTS["coin_tweeter"].format(coin_id))
    if "error" in res:
        print(res)
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
    df["date"] = df["date"].apply(lambda x: x.replace("T", "\n"))
    df["date"] = df["date"].apply(lambda x: x.replace("Z", ""))
    return df


def get_coin_events_by_id(coin_id="eth-ethereum"):
    """Get all events related to given coin like conferences, start date of futures trading etc.

    Example of response from API:
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
    coin_id: str
        id of coin from coinpaprika e.g. Ethereum - > 'eth-ethereum'
    Returns
    -------
    pandas.DataFrame
        id, date , date_to, name, description, is_conference, link, proof_image_link

    """
    session = PaprikaSession()
    res = session.make_request(session.ENDPOINTS["coin_events"].format(coin_id))
    if not res:
        return pd.DataFrame()
    data = pd.DataFrame(res)
    data["description"] = data["description"].apply(
        lambda x: "\n".join(textwrap.wrap(x, width=40)) if isinstance(x, str) else x
    )
    data.drop(["id", "proof_image_link"], axis=1, inplace=True)
    for col in ["date", "date_to"]:
        data[col] = data[col].apply(
            lambda x: x.replace("T", "\n") if isinstance(x, str) else x
        )
        data[col] = data[col].apply(
            lambda x: x.replace("Z", "") if isinstance(x, str) else x
        )
    return data


def get_coin_exchanges_by_id(coin_id="eth-ethereum"):
    """Get all exchanges for given coin id.

    Parameters
    ----------
    coin_id: Identifier of Coin from CoinPaprika

    Returns
    -------
    pandas.DataFrame
        id, name, adjusted_volume_24h_share, fiats
    """
    session = PaprikaSession()
    res = session.make_request(session.ENDPOINTS["coin_exchanges"].format(coin_id))
    df = pd.DataFrame(res)
    df["fiats"] = df["fiats"].copy().apply(lambda x: len([i["symbol"] for i in x if x]))
    return df


def get_coin_markets_by_id(coin_id="eth-ethereum", quotes="USD"):
    """

    Parameters
    ----------
    coin_id: Coin Parpika identifier of coin e.g. eth-ethereum
    quotes: Comma separated list of quotes to return.
        Example: quotes=USD,BTC
        Allowed values:
        BTC, ETH, USD, EUR, PLN, KRW, GBP, CAD, JPY, RUB, TRY, NZD, AUD, CHF, UAH, HKD, SGD, NGN, PHP, MXN, BRL,
        THB, CLP, CNY, CZK, DKK, HUF, IDR, ILS, INR, MYR, NOK, PKR, SEK, TWD, ZAR, VND, BOB, COP, PEN, ARS, ISK

    Returns
    -------
    pandas.DataFrame
    """
    session = PaprikaSession()
    markets = session.make_request(
        session.ENDPOINTS["coin_markets"].format(coin_id), quotes=quotes
    )
    if "error" in markets:
        print(markets)
        return pd.DataFrame()

    data = []
    for r in markets:
        dct = {
            "exchange": r.get("exchange_name"),
            "pair": r.get("pair"),
            "trust_score": r.get("trust_score"),
            "pct_volume_share": r.get("adjusted_volume_24h_share"),
        }
        quotes = r.get("quotes")
        for k, v in quotes.items():
            dct[f"{k.lower()}_price"] = v.get("price")
            dct[f"{k.lower()}_volume"] = v.get("volume_24h")
        dct["market_url"] = r.get("market_url")
        data.append(dct)

    return pd.DataFrame(data)


def get_ohlc_historical(coin_id="eth-ethereum", quotes="USD", days=90):
    """
    Open/High/Low/Close values with volume and market_cap.
    Request example: https://api.coinpaprika.com/v1/coins/btc-bitcoin/ohlcv/historical?start=2019-01-01&end=2019-01-20
    if the last day is current day it can an change with every request until actual close of the day at 23:59:59


    Parameters
    ----------
    coin_id: str
        Paprika coin identifier e.g. eth-ethereum
    quotes: str
        returned data quote (available values: usd btc)
    days: int
        time range for chart in days. Maximum 365

    Returns
    -------
    pandas.DataFrame

    """
    if quotes.lower() not in ["usd", "btc"]:
        quotes = "USD"

    if abs(int(days)) > 365:
        days = 365

    end = datetime.now().strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    session = PaprikaSession()
    data = session.make_request(
        session.ENDPOINTS["ohlcv_hist"].format(coin_id),
        quotes=quotes,
        start=start,
        end=end,
    )
    if "error" in data:
        print(data)
        return pd.DataFrame()
    return pd.DataFrame(data)


def get_tickers_info_for_coin(coin_id="btc-bitcoin", quotes="USD"):
    """Get all most important ticker related information for given coin id
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
    coin_id: Id of coin from CoinPaprika
    quotes: Coma separated quotes to return e.g quotes = USD, BTC

    Returns
    -------
    pandas.DataFrame
        Metric, Value
    """
    session = PaprikaSession()
    tickers = session.make_request(
        session.ENDPOINTS["ticker_info"].format(coin_id), quotes=quotes
    )

    for key, date in tickers.items():
        if "date" in key or "data" in key:
            try:
                tickers[key] = parser.parse(date).strftime("%Y-%m-%d %H:%M:%S")
            except (KeyError, ValueError, TypeError) as e:
                print(e)
        if key == "quotes":
            try:
                tickers[key][quotes]["ath_date"] = parser.parse(
                    tickers[key][quotes]["ath_date"]
                ).strftime("%Y-%m-%d %H:%M:%S")
            except (KeyError, ValueError, TypeError) as e:
                print(e)

    df = pd.json_normalize(tickers)
    try:
        df.columns = [col.replace("quotes.", "") for col in list(df.columns)]
        df.columns = [col.replace(".", "_").lower() for col in list(df.columns)]
    except KeyError as e:
        print(e)
    df = df.T.reset_index()
    df.columns = ["Metric", "Value"]
    return df


def validate_coin(coin: str, coins_dct: dict):
    """Helper method that validates if proper coin id or symbol was provided

    Parameters
    ----------
    coin: id or symbol of coin for CoinPaprika
    coins_dct: dictionary of coins

    Returns
    -------
    coin id, coin symbol

    """
    coin_found, symbol = None, None
    if coin in coins_dct:
        coin_found = coin
        symbol = coins_dct.get(coin_found)
    else:
        for key, value in coins_dct.items():
            if coin.upper() == value:
                coin_found = key
                symbol = value

    if not coin_found:
        raise ValueError(f"Could not find coin with given id: {coin}\n")
    print(f"Coin found : {coin_found} with symbol {symbol}\n")
    return coin_found, symbol


def basic_coin_info(coin_id: str):
    coin = get_coin(coin_id)
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
    results = {}
    for key in keys:
        results[key] = coin.get(key)

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
