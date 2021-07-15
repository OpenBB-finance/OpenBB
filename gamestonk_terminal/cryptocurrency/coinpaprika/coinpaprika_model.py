from datetime import datetime, timedelta
import textwrap
import requests
import pandas as pd
from dateutil import parser
from requests.adapters import HTTPAdapter

ENDPOINTS = {
    "global": "/global",
    "coin": "/coins/{}",
    "coins": "/coins",
    "coin_tweeter": "/coins/{}/twitter",
    "coin_events": "/coins/{}/events",
    "coin_exchanges": "/coins/{}/exchanges",
    "coin_markets": "/coins/{}/markets",
    "ohlcv": "/coins/{}/ohlcv/latest",
    "ohlcv_hist": "/coins/{}/ohlcv/historical",
    "people": "/people/{}",
    "tickers": "/tickers",
    "ticker_info": "/tickers/{}",
    "exchanges": "/exchanges",
    "exchange_info": "/exchanges/{}",
    "exchange_markets": "/exchanges/{}/markets",
    "contract_platforms": "/contracts",
    "contract_platform_addresses": "/contracts/{}",
    "search": "/search",
}

PAPRIKA_BASE_URL = "https://api.coinpaprika.com/v1"

# Mount a session with adapter. It's solution for time to time timeouts
session = requests.Session()
session.mount(PAPRIKA_BASE_URL, HTTPAdapter(max_retries=5))


def make_request(endpoint, payload=None, **kwargs):
    """Helper method that handles request for coinpaprika api.
    It prepares URL for given endpoint and payload if it's part of requests

    Parameters
    ----------
    endpoint: str,
        it's an endpoint that we want to query. e.g. to get twitter data for given coin we need to use:
       https://api.coinpaprika.com/v1/coins/{}/twitter
    payload: dict
        the body of your request. Contains the data send to the CoinPaprika API when making an API request
    kwargs:
        additional parameters that will be added to payload
    Returns
    -------
    dict with response data

    """
    url = f"{PAPRIKA_BASE_URL}{endpoint}"
    if payload is None:
        payload = {}
    if kwargs:
        payload.update(kwargs)
    return session.get(url, params=payload).json()


def get_global_market():
    """Return data frame with most important global crypto statistics like:
    market_cap_usd, volume_24h_usd, bitcoin_dominance_percentage, cryptocurrencies_number,
    market_cap_ath_value, market_cap_ath_date, volume_24h_ath_value, volume_24h_ath_date,
    market_cap_change_24h, volume_24h_change_24h, last_updated,

    Returns
    -------
    pandas.DataFrame
        Metric, Value
    """
    global_markets = make_request(ENDPOINTS["global"])
    global_markets["last_updated"] = datetime.fromtimestamp(
        global_markets["last_updated"]
    )

    for key, date in global_markets.items():
        if "date" in key:
            try:
                global_markets[key] = parser.parse(date).strftime("%Y-%m-%d %H:%M:%S")
            except (KeyError, ValueError, TypeError):
                ...
    df = pd.Series(global_markets).to_frame().reset_index()
    df.columns = ["Metric", "Value"]
    return df


def get_list_of_coins():
    """Get list of all available coins on CoinPaprika

    Returns
    -------
    pandas.DataFrame
        rank, id, name, symbol, type
    """
    coins = make_request(ENDPOINTS["coins"])
    df = pd.DataFrame(coins)
    df = df[df["is_active"]]
    return df[["rank", "id", "name", "symbol", "type"]]


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
    coin = make_request(ENDPOINTS["coin"].format(coin_id))
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
    res = make_request(ENDPOINTS["coin_tweeter"].format(coin_id))
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
    """
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
    res = make_request(ENDPOINTS["coin_events"].format(coin_id))
    if not res:
        return pd.DataFrame()
    data = pd.DataFrame(res)
    data["description"] = data["description"].apply(
        lambda x: "\n".join(textwrap.wrap(x, width=40)) if isinstance(x, str) else x
    )
    data.drop(["id", "proof_image_link"], axis=1, inplace=True)
    for col in ["date", "date_to"]:
        data[col] = data[col].apply(lambda x: x.replace("T", "\n"))
        data[col] = data[col].apply(lambda x: x.replace("Z", ""))
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
    res = make_request(ENDPOINTS["coin_exchanges"].format(coin_id))
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

    markets = make_request(ENDPOINTS["coin_markets"].format(coin_id), quotes=quotes)
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

    data = make_request(
        ENDPOINTS["ohlcv_hist"].format(coin_id), quotes=quotes, start=start, end=end
    )
    if "error" in data:
        print(data)
        return pd.DataFrame()
    return pd.DataFrame(data)


def _get_coins_info_helper(quotes="USD"):
    """Helper method that call /tickers endpoint which returns for all coins quoted in provided currency/crypto

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
        "quotes" : {
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
    quotes: Coma separated quotes to return e.g quotes=USD,BTC

    Returns
    -------
    pandas.DataFrame
        id, name, symbol, rank, circulating_supply, total_supply, max_supply, beta_value, first_data_at,
        last_updated, price, volume_24h, volume_24h_change_24h, market_cap, market_cap_change_24h,
        percent_change_15m, percent_change_30m, percent_change_1h, percent_change_6h, percent_change_12h,
       percent_change_24h, percent_change_7d, percent_change_30d, percent_change_1y,
       ath_price, ath_date, percent_from_price_ath
    """
    tickers = make_request(ENDPOINTS["tickers"], quotes=quotes)
    data = pd.json_normalize(tickers)
    try:
        # data.columns = [col.replace(f"quotes.{quotes}.", f"{quotes.lower()}_") for col in data.columns.tolist()]
        data.columns = [
            col.replace(f"quotes.{quotes}.", "") for col in data.columns.tolist()
        ]
        data.columns = [col.replace("percent", "pct") for col in data.columns.tolist()]
    except KeyError as e:
        print(e)
    data.rename(
        columns={
            "market_cap_change_24h": "mcap_change_24h",
            "pct_from_price_ath": "pct_from_ath",
        },
        inplace=True,
    )
    return data


def get_coins_info(quotes="USD"):  # > format big numbers fix
    """Returns basic coin information for all coins from CoinPaprika API
    Parameters
    ----------
    quotes: Coma separated quotes to return e.g quotes=USD,BTC

    Returns
    -------
    pandas.DataFrame
        rank, name, symbol, price, volume_24h, circulating_supply, total_supply,
        max_supply, market_cap, beta_value, ath_price,
    """
    cols = [
        "rank",
        "name",
        "symbol",
        "price",
        "volume_24h",
        "circulating_supply",
        "total_supply",
        "max_supply",
        "market_cap",
        "beta_value",
        "ath_price",
    ]
    return _get_coins_info_helper(quotes)[cols].sort_values(by="rank")


def get_coins_market_info(quotes="USD"):
    """Returns basic coin information for all coins from CoinPaprika API
    Parameters
    ----------
    quotes: Coma separated quotes to return e.g quotes=USD,BTC

    Returns
    -------
    pandas.DataFrame
        rank, name, symbol, price, volume_24h, mcap_change_24h,
        pct_change_1h, pct_change_24h, ath_price, pct_from_ath,
    """
    cols = [
        "rank",
        "name",
        "symbol",
        "price",
        "volume_24h",
        "mcap_change_24h",
        "pct_change_1h",
        "pct_change_24h",
        # "pct_change_7d",
        # "pct_change_30d",
        "ath_price",
        "pct_from_ath",
    ]
    return _get_coins_info_helper(quotes=quotes)[cols].sort_values(by="rank")


def get_list_of_exchanges(quotes="USD"):
    """
    List exchanges from CoinPaprika API
    Parameters
    ----------
    quotes: Coma separated quotes to return e.g quotes=USD,BTC

    Returns
    -------
    pandas.DataFrame
        rank, name, currencies, markets, fiats, confidence_score, reported_volume_24h,
        reported_volume_7d ,reported_volume_30d, sessions_per_month,
    """
    exchanges = make_request(ENDPOINTS["exchanges"], quotes=quotes)
    df = pd.json_normalize(exchanges)
    try:
        df.columns = [
            col.replace(f"quotes.{quotes}.", "") for col in df.columns.tolist()
        ]
    except KeyError as e:
        print(e)
    df = df[df["active"]]
    cols = [
        "adjusted_rank",
        "id",
        "name",
        "currencies",
        "markets",
        "fiats",
        "confidence_score",
        "reported_volume_24h",
        "reported_volume_7d",
        "reported_volume_30d",
        "sessions_per_month",
    ]
    df.loc[:, "fiats"] = df["fiats"].apply(lambda x: len([i["symbol"] for i in x if x]))
    df = df[cols]
    df = df.applymap(
        lambda x: "\n".join(textwrap.wrap(x, width=28)) if isinstance(x, str) else x
    )
    df.rename(
        columns={"adjusted_rank": "rank", "confidence_score": "confidence"},
        inplace=True,
    )
    df.columns = [x.replace("reported_", "") for x in df.columns]
    return df.sort_values(by="rank")


def get_exchanges_market(exchange_id="binance", quotes="USD"):
    """List markets by exchange ID
    Parameters
    ----------
    exchange_id: identifier of exchange e.g for Binance Exchange -> binance
    quotes: Coma separated quotes to return e.g quotes=USD,BTC

    Returns
    -------
    pandas.DataFrame
        pair, base_currency_name, quote_currency_name, market_url,
        category, reported_volume_24h_share, trust_score,
    """
    data = make_request(
        ENDPOINTS["exchange_markets"].format(exchange_id), quotes=quotes
    )
    if "error" in data:
        print(data)
        return pd.DataFrame()
    cols = [
        "exchange_id",
        "pair",
        "base_currency_name",
        "quote_currency_name",
        "category",
        "reported_volume_24h_share",
        "trust_score",
        "market_url",
    ]
    df = pd.DataFrame(data)
    df["exchange_id"] = exchange_id
    return df[cols]


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
    tickers = make_request(ENDPOINTS["ticker_info"].format(coin_id), quotes=quotes)

    for key, date in tickers.items():
        if "date" in key or "data" in key:
            try:
                tickers[key] = parser.parse(date).strftime("%Y-%m-%d %H:%M:%S")
            except (KeyError, ValueError, TypeError):
                ...
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


def search(q, c=None, modifier=None):
    """Search CoinPaprika
    Parameters
    ----------
    q:  phrase for search
    c:  one or more categories (comma separated) to search.
        Available options: currencies|exchanges|icos|people|tags
        Default: currencies,exchanges,icos,people,tags
    modifier: set modifier for search results. Available options: symbol_search -
        search only by symbol (works for currencies only)

    Returns
    -------
    pandas.DataFrame
        Metric, Value
    """
    if c is None:
        c = "currencies,exchanges,icos,people,tags"
    data = make_request(ENDPOINTS["search"], q=q, c=c, modifier=modifier, limit=100)
    results = []
    for item in data:
        category = data[item]
        for r in category:
            results.append(
                {
                    "id": r.get("id"),
                    "name": r.get("name"),
                    "category": item,
                }
            )
    return pd.DataFrame(results)


def get_all_contract_platforms():
    """List all smart contract platforms like ethereum, solana, cosmos, polkadot, kusama ...

    Returns
    -------
    pandas.DataFrame
        index, platform_id
    """

    contract_platforms = make_request(ENDPOINTS["contract_platforms"])
    df = pd.DataFrame(contract_platforms).reset_index()
    df.columns = ["index", "platform_id"]
    df["index"] = df["index"] + 1
    return df


def get_contract_platform(platform_id="eth-ethereum"):
    """Gets all contract addresses for given platform
    Parameters
    ----------
    platform_id: Blockchain platform like eth-ethereum

    Returns
    -------
    pandas.DataFrame
         id, type, active, address
    """
    contract_platforms = make_request(
        ENDPOINTS["contract_platform_addresses"].format(platform_id)
    )

    return pd.DataFrame(contract_platforms)[["id", "type", "active", "address"]]


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
    print(f"Coin found : {coin_found} with symbol {symbol}")
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
