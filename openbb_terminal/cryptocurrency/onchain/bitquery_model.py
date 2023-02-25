"""BitQuery model"""
__docformat__ = "numpy"

import datetime
import json
import logging
import os
from typing import Optional

import numpy as np
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.cryptocurrency.dataframe_helpers import prettify_column_names
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


class BitQueryApiKeyException(Exception):
    """Bit Query Api Key Exception object"""

    @log_start_end(log=logger)
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    @log_start_end(log=logger)
    def __str__(self) -> str:
        return f"BitQueryApiKeyException: {self.message}"


class BitQueryTimeoutException(Exception):
    """BitQuery Timeout Exception class"""


BQ_URL = "https://graphql.bitquery.io"
CURRENCIES = ["ETH", "USD", "BTC", "USDT"]
LT_FILTERS = ["exchange", "trades", "tradeAmount"]
LT_KIND = ["dex", "time"]
INTERVALS = ["day", "month", "week"]
DVCP_FILTERS = [
    "date",
    "exchange",
    "base",
    "quote",
    "open",
    "high",
    "low",
    "close",
    "tradeAmount",
    "trades",
]
UEAT_FILTERS = [
    "date",
    "uniqueSenders",
    "transactions",
    "averageGasPrice",
    "mediumGasPrice",
    "maximumGasPrice",
]
TTCP_FILTERS = ["base", "quoted", "trades", "tradeAmount"]
BAAS_FILTERS = [
    "date",
    "baseCurrency",
    "quoteCurrency",
    "dailySpread",
    "averageBidPrice",
    "averageAskPrice",
]
DECENTRALIZED_EXCHANGES = [
    "1inch",
    "AfroDex",
    "AirSwap",
    "Amplbitcratic",
    "Balancer",
    "BestSwap",
    "Bitox",
    "CellSwap",
    "Cellswap",
    "Cofix",
    "Coinchangex",
    "Curve",
    "DDEX",
    "DUBIex",
    "DecentrEx",
    "DeversiFi",
    "Dodo",
    "ETHERCExchange",
    "EtherBlockchain",
    "EtherDelta",
    "Ethernext",
    "Ethfinex",
    "FEGex",
    "FFFSwap",
    "Fordex",
    "GUDecks",
    "GUDeks",
    "HiSwap",
    "IDEX",
    "LedgerDex",
    "Matcha",
    "Miniswap",
    "Mooniswap",
    "Oasis",
    "OpenRelay",
    "S.Finance",
    "SakeSwap",
    "SeedDex",
    "SingularX",
    "StarBitEx",
    "SushiSwap",
    "SwapX",
    "SwitchDex",
    "TacoSwap",
    "TokenJar",
    "TokenStore",
    "TokenTrove",
    "Tokenlon",
    "TradexOne",
    "Uniswap",
    "ZeusSwap",
    "dYdX",
    "dex.blue",
]
DECENTRALIZED_EXCHANGES_MAP = {e.lower(): e for e in DECENTRALIZED_EXCHANGES}
NETWORKS = ["bsc", "ethereum", "matic"]


@log_start_end(log=logger)
def _extract_dex_trades(data: dict) -> pd.DataFrame:
    """Helper method that extracts from bitquery api response data from nested dictionary:
    response = {'ethereum' : {'dexTrades' : <data>}}. If 'dexTrades' is None, raises Exception.

    Parameters
    ----------
    data: dict
        response data from bitquery api.

    Returns
    -------
    pd.DataFrame
        normalized pandas data frame with data
    """

    dex_trades = data["ethereum"]["dexTrades"]
    if not dex_trades:
        raise ValueError("No data was returned in request response\n")
    return pd.json_normalize(dex_trades)


@log_start_end(log=logger)
@check_api_key(["API_BITQUERY_KEY"])
def query_graph(url: str, query: str) -> dict:
    """Helper methods for querying graphql api. [Source: https://bitquery.io/]

    Parameters
    ----------
    url: str
        Endpoint url
    query: str
        Graphql query

    Returns
    -------
    dict
        Dictionary with response data
    """

    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=5))
    headers = {"x-api-key": get_current_user().credentials.API_BITQUERY_KEY}
    timeout = 30

    try:
        response = session.post(
            url, json={"query": query}, headers=headers, timeout=timeout
        )
    except requests.Timeout as e:
        logger.exception("BitQuery timeout")
        raise BitQueryTimeoutException(
            f"BitQuery API didn't respond within {timeout} seconds."
        ) from e

    if response.status_code == 500:
        raise HTTPError(f"Internal sever error {response.reason}")

    if not 200 <= response.status_code < 300:
        raise BitQueryApiKeyException(
            f"Invalid Authentication: {response.status_code}. "
            f"Please visit https://bitquery.io/pricing and generate you free api key"
        )
    try:
        data = response.json()
        if "error" in data:
            raise ValueError(f"Invalid Response: {data['error']}")
    except Exception as e:
        logger.exception("Invalid Response: %s", str(e))
        raise ValueError(f"Invalid Response: {response.text}") from e
    return data["data"]


@log_start_end(log=logger)
def get_erc20_tokens() -> pd.DataFrame:
    """Helper method that loads ~1500 most traded erc20 token.
    [Source: json file]

    Returns
    -------
    pd.DataFrame
        ERC20 tokens with address, symbol and name
    """
    file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "data", "erc20_coins.json"
    )
    with open(file_path) as f:
        data = json.load(f)
    df = pd.json_normalize(data)
    df.columns = ["count", "address", "symbol", "name"]
    df = df[~df["symbol"].isin(["", None, np.NaN])]
    return df[["name", "symbol", "address", "count"]]


@log_start_end(log=logger)
def find_token_address(symbol: str) -> Optional[str]:
    """Helper methods that search for ERC20 coin base on provided symbol or token address.
    If erc20 token address is provided, then checks if it's proper address and returns it back.
    In other case mapping data is loaded from file, and lookup for belonging token address.

    Parameters
    ----------
    symbol: str
        ERC20 token symbol e.g. UNI, SUSHI, ETH, WBTC or token address e.g.
        0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48

    Returns
    -------
    str or None
        ERC20 token address, or None if nothing found.
    """

    if symbol.startswith("0x") and len(symbol) >= 38:
        return symbol

    if symbol == "ETH":
        return symbol

    token = "WBTC" if symbol == "BTC" else symbol
    tokens_map: pd.DataFrame = get_erc20_tokens()

    found_token = tokens_map.loc[tokens_map["symbol"] == token]
    if found_token.empty:
        return None
    if len(found_token) > 1:
        return found_token.sort_values(by="count", ascending=False).iloc[0]["address"]
    return found_token.iloc[0]["address"]


@log_start_end(log=logger)
def get_dex_trades_by_exchange(
    trade_amount_currency: str = "USD",
    limit: int = 90,
    sortby: str = "tradeAmount",
    ascend: bool = True,
) -> pd.DataFrame:
    """Get trades on Decentralized Exchanges aggregated by DEX [Source: https://graphql.bitquery.io/]

    Parameters
    ----------
    trade_amount_currency: str
        Currency of displayed trade amount. Default: USD
    limit:  int
        Last n days to query data. Maximum 365 (bigger numbers can cause timeouts
        on server side)
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending

    Returns
    -------
    pd.DataFrame
        Trades on Decentralized Exchanges aggregated by DEX
    """

    dt = (datetime.date.today() - datetime.timedelta(min(limit, 365))).strftime(
        "%Y-%m-%d"
    )

    if trade_amount_currency not in CURRENCIES:
        trade_amount_currency = "USD"

    query = f"""
        {{
        ethereum {{
        dexTrades(options: {{limit: 40, desc: ["count"]}}
            date: {{since: "{dt}"}}
        ) {{
            exchange {{
            name
        }}
            count
            tradeAmount(in: {trade_amount_currency})
        }}
        }}
    }}
    """

    try:
        data = query_graph(BQ_URL, query)
    except BitQueryApiKeyException:
        logger.exception("Invalid API Key")
        console.print("[red]Invalid API Key[/red]\n")
        return pd.DataFrame()

    if not data:
        return pd.DataFrame()

    df = _extract_dex_trades(data)
    df.columns = ["trades", "tradeAmount", "exchange"]
    df = df[~df["exchange"].isin([None, np.NaN, ""])]
    df = df[["exchange", "trades", "tradeAmount"]].sort_values(
        by="tradeAmount", ascending=True
    )
    df = df.sort_values(by=sortby, ascending=ascend)
    df.columns = prettify_column_names(df.columns)
    return df


@log_start_end(log=logger)
def get_dex_trades_monthly(
    trade_amount_currency: str = "USD", limit: int = 90, ascend: bool = True
) -> pd.DataFrame:
    """Get list of trades on Decentralized Exchanges monthly aggregated.
    [Source: https://graphql.bitquery.io/]

    Parameters
    ----------
    trade_amount_currency: str
        Currency of displayed trade amount. Default: USD
    limit:  int
        Last n days to query data. Maximum 365 (bigger numbers can cause timeouts
        on server side)
    ascend: bool
        Flag to sort data ascending

    Returns
    -------
    pd.DataFrame
        Trades on Decentralized Exchanges monthly aggregated
    """

    if trade_amount_currency not in CURRENCIES:
        trade_amount_currency = "USD"

    dt = (datetime.date.today() - datetime.timedelta(min(limit, 365))).strftime(
        "%Y-%m-%d"
    )

    query = f"""
    {{
        ethereum {{
        dexTrades(
            options: {{desc: ["date.year", "date.month", "count"]}}
            date: {{since: "{dt}"}}
        ) {{
            count
            date {{
            month
            year
            }}
            tradeAmount(in: {trade_amount_currency})
        }}
        }}
    }}
    """
    try:
        data = query_graph(BQ_URL, query)
    except BitQueryApiKeyException:
        logger.exception("Invalid API Key")
        console.print("[red]Invalid API Key[/red]\n")
        return pd.DataFrame()
    if not data:
        return pd.DataFrame()

    df = _extract_dex_trades(data)
    df["date"] = df.apply(
        lambda x: datetime.date(int(x["date.year"]), int(x["date.month"]), 1), axis=1
    )
    df.rename(columns={"count": "trades"}, inplace=True)
    df = df[["date", "trades", "tradeAmount"]]
    df = df.sort_values(by="date", ascending=ascend)
    df.columns = prettify_column_names(df.columns)
    return df


@log_start_end(log=logger)
def get_daily_dex_volume_for_given_pair(
    limit: int = 100,
    symbol: str = "UNI",
    to_symbol: str = "USDT",
    sortby: str = "date",
    ascend: bool = True,
) -> pd.DataFrame:
    """Get daily volume for given pair [Source: https://graphql.bitquery.io/]

    Parameters
    ----------
    limit:  int
        Last n days to query data
    symbol: str
        ERC20 token symbol
    to_symbol: str
        Quote currency.
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending

    Returns
    -------
    pd.DataFrame
        Daily volume for given pair
    """

    dt = (datetime.date.today() - datetime.timedelta(min(limit, 365))).strftime(
        "%Y-%m-%d"
    )

    base, quote = find_token_address(symbol), find_token_address(to_symbol)
    if not base or not quote:
        raise ValueError("Provided coin or quote currency doesn't exist\n")

    query = f"""
        {{
        ethereum(network: ethereum) {{
        dexTrades(
            options: {{desc: ["timeInterval.day", "trades"]}}
            baseCurrency: {{is: "{base}"}}
            quoteCurrency: {{is: "{quote}"}}
            date: {{since: "{dt}" }}
        ) {{
            timeInterval {{
            day(count: 1)
            }}
            baseCurrency {{
            symbol
            }}
            quoteCurrency {{
            symbol
            }}
            exchange {{
            fullName
            }}
            trades: count
            tradeAmount(in: USD)
            quotePrice
            maximum_price: quotePrice(calculate: maximum)
            minimum_price: quotePrice(calculate: minimum)
            open_price: minimum(of: block, get: quote_price)
            close_price: maximum(of: block, get: quote_price)
        }}
        }}
    }}
    """

    try:
        data = query_graph(BQ_URL, query)
    except BitQueryApiKeyException:
        logger.exception("Invalid API Key")
        console.print("[red]Invalid API Key[/red]\n")
        return pd.DataFrame()

    if not data:
        return pd.DataFrame()

    df = _extract_dex_trades(data)
    df.columns = [
        "trades",
        "tradeAmount",
        "price",
        "high",
        "low",
        "open",
        "close",
        "date",
        "base",
        "quote",
        "exchange",
    ]
    df = df[
        [
            "date",
            "exchange",
            "base",
            "quote",
            "open",
            "high",
            "low",
            "close",
            "tradeAmount",
            "trades",
        ]
    ]
    df = df.sort_values(by=sortby, ascending=ascend)
    df.columns = prettify_column_names(df.columns)
    return df


@log_start_end(log=logger)
def get_token_volume_on_dexes(
    symbol: str = "UNI",
    trade_amount_currency: str = "USD",
    sortby: str = "tradeAmount",
    ascend: bool = True,
) -> pd.DataFrame:
    """Get token volume on different Decentralized Exchanges. [Source: https://graphql.bitquery.io/]

    Parameters
    ----------
    symbol: str
        ERC20 token symbol.
    trade_amount_currency: str
        Currency to display trade amount in.
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending

    Returns
    -------
    pd.DataFrame
        Token volume on Decentralized Exchanges
    """

    if trade_amount_currency not in CURRENCIES:
        trade_amount_currency = "USD"

    token_address = find_token_address(symbol)
    if token_address is None:
        raise ValueError(f"Couldn't find token with symbol {symbol}\n")
    query = f"""
    {{
        ethereum {{
        dexTrades(
            baseCurrency: {{is:"{token_address}"}}
        ) {{
                baseCurrency{{
    symbol
    }}
            exchange {{
            name
            fullName
            }}
            count
            tradeAmount(in: {trade_amount_currency})

        }}
        }}
        }}

    """
    try:
        data = query_graph(BQ_URL, query)
    except BitQueryApiKeyException:
        logger.exception("Invalid API Key")
        console.print("[red]Invalid API Key[/red]\n")
        return pd.DataFrame()

    if not data:
        return pd.DataFrame()

    df = _extract_dex_trades(data)[["exchange.fullName", "tradeAmount", "count"]]
    df.columns = LT_FILTERS
    df = df[~df["exchange"].str.startswith("<")]
    df = df.sort_values(by=sortby, ascending=ascend)
    df.columns = prettify_column_names(df.columns)
    return df


@log_start_end(log=logger)
def get_ethereum_unique_senders(
    interval: str = "day",
    limit: int = 90,
    sortby: str = "tradeAmount",
    ascend: bool = True,
) -> pd.DataFrame:
    """Get number of unique ethereum addresses which made a transaction in given time interval.

    Parameters
    ----------
    interval: str
        Time interval in which count unique ethereum addresses which made transaction. day,
        month or week.
    limit: int
        Number of records for data query.
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending

    Returns
    -------
    pd.DataFrame
        Unique ethereum addresses which made a transaction
    """

    intervals = {
        "day": 1,
        "month": 30,
        "week": 7,
    }

    if interval not in intervals:
        interval = "day"

    days = min(limit * intervals[interval], 90)

    dt = (datetime.date.today() - datetime.timedelta(days)).strftime("%Y-%m-%d")

    query = f"""
    {{
        ethereum(network: ethereum) {{
            transactions(options: {{desc: "date.date"}}, date: {{since: "{dt}"}}) {{
                uniqueSenders: count(uniq: senders)
                date {{
                    date:startOfInterval(unit: {interval})
                }}
                averageGasPrice: gasPrice(calculate: average)
                mediumGasPrice: gasPrice(calculate: median)
                maximumGasPrice: gasPrice(calculate: maximum)
                transactions: count
            }}
        }}
    }}
    """

    try:
        data = query_graph(BQ_URL, query)
    except BitQueryApiKeyException:
        logger.exception("Invalid API Key")
        console.print("[red]Invalid API Key[/red]\n")
        return pd.DataFrame()
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data["ethereum"]["transactions"])
    df["date"] = df["date"].apply(lambda x: x["date"])
    df = df[UEAT_FILTERS]
    df = df.sort_values(by=sortby, ascending=ascend)
    df.columns = prettify_column_names(df.columns)
    return df


@log_start_end(log=logger)
def get_most_traded_pairs(
    network: str = "ethereum",
    exchange: str = "Uniswap",
    limit: int = 90,
    sortby: str = "tradeAmount",
    ascend: bool = True,
) -> pd.DataFrame:
    """Get most traded crypto pairs on given decentralized exchange in chosen time period.
    [Source: https://graphql.bitquery.io/]

    Parameters
    ----------
    network: str
        EVM network. One from list: bsc (binance smart chain), ethereum or matic
    exchange: st
        Decentralized exchange name
    limit: int
        Number of days taken into calculation account.
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending

    Returns
    -------
    pd.DataFrame
        Most traded crypto pairs on given decentralized exchange in chosen time period.
    """

    dt = (datetime.date.today() - datetime.timedelta(limit)).strftime("%Y-%m-%d")
    exchange = DECENTRALIZED_EXCHANGES_MAP.get(exchange, "Uniswap")
    query = f"""
    {{
        ethereum(network: {network}){{
            dexTrades(options: {{limit: 100, desc: "tradeAmount"}},
            exchangeName: {{is: "{exchange}"}}
            date: {{since: "{dt}"}}) {{
                buyCurrency {{
                    symbol
                }}
                sellCurrency{{
                    symbol
                }}
                trades: count
                tradeAmount(in: USD)
            }}
        }}
    }}
    """
    try:
        data = query_graph(BQ_URL, query)
    except BitQueryApiKeyException:
        logger.exception("Invalid API Key")
        console.print("[red]Invalid API Key[/red]\n")
        return pd.DataFrame()
    if not data:
        return pd.DataFrame()

    df = _extract_dex_trades(data)
    df.columns = ["trades", "tradeAmount", "base", "quoted"]
    df = df[TTCP_FILTERS]
    df = df.sort_values(by=sortby, ascending=ascend)
    df.columns = prettify_column_names(df.columns)
    return df


@log_start_end(log=logger)
def get_spread_for_crypto_pair(
    symbol: str = "WETH",
    to_symbol: str = "USDT",
    limit: int = 10,
    sortby: str = "date",
    ascend: bool = True,
) -> pd.DataFrame:
    """Get an average bid and ask prices, average spread for given crypto pair for chosen time period.
        [Source: https://graphql.bitquery.io/]

    Parameters
    ----------
    symbol: str
        ERC20 token symbol
    to_symbol: str
        Quoted currency.
    limit:  int
        Last n days to query data
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending

    Returns
    -------
    pd.DataFrame
        Average bid and ask prices, spread for given crypto pair for chosen time period
    """

    dt = (datetime.date.today() - datetime.timedelta(limit)).strftime("%Y-%m-%d")
    base, quote = find_token_address(symbol), find_token_address(to_symbol)

    if not base or not quote:
        raise ValueError("Provided coin or quote currency doesn't exist\n")

    query = f"""
    {{
        ethereum(network: ethereum){{
            dexTrades(
                date: {{since:"{dt}"}}
                baseCurrency: {{is: "{base}"}},
                quoteCurrency: {{is: "{quote}"}}) {{
                    date {{date}}
                    baseCurrency {{symbol}}
                    baseAmount
                    quoteCurrency {{
                        symbol
                    }}
                    quoteAmount
                    trades: count
                    quotePrice
                    side
                }}
        }}
    }}
    """
    try:
        data = query_graph(BQ_URL, query)
    except BitQueryApiKeyException:
        logger.exception("Invalid API Key")
        console.print("[red]Invalid API Key[/red]\n")
        return pd.DataFrame()
    if not data:
        return pd.DataFrame()

    df = _extract_dex_trades(data)
    columns = ["quotePrice", "date.date", "baseCurrency.symbol", "quoteCurrency.symbol"]
    bids = df.query("side == 'SELL'")[columns]
    asks = df.query("side == 'BUY'")[columns]

    bids.columns = ["averageBidPrice", "date", "baseCurrency", "quoteCurrency"]
    asks.columns = ["averageAskPrice", "date", "baseCurrency", "quoteCurrency"]

    daily_spread = pd.merge(asks, bids, on=["date", "baseCurrency", "quoteCurrency"])
    daily_spread["dailySpread"] = abs(
        daily_spread["averageBidPrice"] - daily_spread["averageAskPrice"]
    )
    df = daily_spread[
        [
            "date",
            "baseCurrency",
            "quoteCurrency",
            "dailySpread",
            "averageBidPrice",
            "averageAskPrice",
        ]
    ]
    df = df.sort_values(by=sortby, ascending=ascend)
    df.columns = prettify_column_names(df.columns)
    return df


POSSIBLE_CRYPTOS = list(get_erc20_tokens()["symbol"].unique())
