"""CoinPaprika model"""
__docformat__ = "numpy"

import logging
import textwrap
from datetime import datetime

import pandas as pd
from dateutil import parser

from openbb_terminal.cryptocurrency.coinpaprika_helpers import PaprikaSession
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

MARKETS_FILTERS = [
    "rank",
    "name",
    "symbol",
    "price",
    "volume_24h",
    "mcap_change_24h",
    "pct_change_1h",
    "pct_change_24h",
    "ath_price",
    "pct_from_ath",
]

EXMARKETS_FILTERS = [
    "pair",
    "base_currency_name",
    "quote_currency_name",
    "category",
    "reported_volume_24h_share",
    "trust_score",
    "market_url",
]

INFO_FILTERS = [
    "rank",
    "name",
    "symbol",
    "price",
    "volume_24h",
    "circulating_supply",
    "total_supply",
    "max_supply",
    "ath_price",
    "market_cap",
    "beta_value",
]

EXCHANGES_FILTERS = [
    "rank",
    "name",
    "currencies",
    "markets",
    "fiats",
    "confidence",
    "volume_24h",
    "volume_7d",
    "volume_30d",
    "sessions_per_month",
]


CONTRACTS_FILTERS = ["id", "type", "active"]


@log_start_end(log=logger)
def get_global_info() -> pd.DataFrame:
    """Return data frame with most important global crypto statistics like:
    market_cap_usd, volume_24h_usd, bitcoin_dominance_percentage, cryptocurrencies_number,
    market_cap_ath_value, market_cap_ath_date, volume_24h_ath_value, volume_24h_ath_date,
    market_cap_change_24h, volume_24h_change_24h, last_updated.   [Source: CoinPaprika]

    Returns
    -------
    pd.DataFrame
        Most important global crypto statistics
        Metric, Value
    """

    session = PaprikaSession()
    global_markets = session.make_request(session.ENDPOINTS["global"])
    global_markets["last_updated"] = datetime.fromtimestamp(
        global_markets["last_updated"]
    )

    for key, date in global_markets.items():
        if "date" in key:
            try:
                new_date = date if isinstance(date, datetime) else parser.parse(date)
                global_markets[key] = new_date.strftime("%Y-%m-%d %H:%M:%S")
            except (KeyError, ValueError, TypeError) as e:
                logger.exception(str(e))
                console.print(e)
    df = pd.Series(global_markets).to_frame().reset_index()
    df.columns = ["Metric", "Value"]
    return df


@log_start_end(log=logger)
def _get_coins_info_helper(symbols: str = "USD") -> pd.DataFrame:
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

    [Source: CoinPaprika]

    Parameters
    ----------
    symbols: Comma separated quotes to return e.g quotes=USD,BTC

    Returns
    -------
    pd.DataFrame
        id, name, symbol, rank, circulating_supply, total_supply, max_supply, beta_value, first_data_at,
        last_updated, price, volume_24h, volume_24h_change_24h, market_cap, market_cap_change_24h,
        percent_change_15m, percent_change_30m, percent_change_1h, percent_change_6h, percent_change_12h,
        percent_change_24h, percent_change_7d, percent_change_30d, percent_change_1y,
        ath_price, ath_date, percent_from_price_ath
    """

    session = PaprikaSession()
    tickers = session.make_request(session.ENDPOINTS["tickers"], quotes=symbols)
    data = pd.json_normalize(tickers)
    try:
        data.columns = [
            col.replace(f"quotes.{symbols}.", "") for col in data.columns.tolist()
        ]
        data.columns = [col.replace("percent", "pct") for col in list(data.columns)]
    except KeyError as e:
        logger.exception(str(e))
        console.print(e)
    data.rename(
        columns={
            "market_cap_change_24h": "mcap_change_24h",
            "pct_from_price_ath": "pct_from_ath",
        },
        inplace=True,
    )
    return data


@log_start_end(log=logger)
def get_coins_info(
    symbols: str = "USD", sortby: str = "rank", ascend: bool = True
) -> pd.DataFrame:  # > format big numbers fix
    """Returns basic coin information for all coins from CoinPaprika API [Source: CoinPaprika]

    Parameters
    ----------
    symbols: str
        Comma separated quotes to return e.g quotes=USD,BTC
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data descending

    Returns
    -------
    pd.DataFrame
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
    df = _get_coins_info_helper(symbols)[cols]
    df = df.sort_values(by=sortby, ascending=ascend)
    return df


@log_start_end(log=logger)
def get_coins_market_info(
    symbols: str = "USD", sortby: str = "rank", ascend: bool = True
) -> pd.DataFrame:
    """Returns basic coin information for all coins from CoinPaprika API [Source: CoinPaprika]

    Parameters
    ----------
    symbols: str
        Comma separated quotes to return e.g quotes=USD,BTC
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascend

    Returns
    -------
    pd.DataFrame
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
        "ath_price",
        "pct_from_ath",
    ]
    df = _get_coins_info_helper(symbols=symbols)[cols].sort_values(by="rank")
    if sortby == "rank":
        df = df.sort_values(by=sortby, ascending=not ascend)
    else:
        df = df.sort_values(by=sortby, ascending=ascend)
    return df


@log_start_end(log=logger)
def get_list_of_exchanges(
    symbols: str = "USD", sortby: str = "rank", ascend: bool = True
) -> pd.DataFrame:
    """
    List exchanges from CoinPaprika API [Source: CoinPaprika]

    Parameters
    ----------
    symbols: str
        Comma separated quotes to return e.g quotes=USD,BTC
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascend

    Returns
    -------
    pd.DataFrame
        rank, name, currencies, markets, fiats, confidence_score, reported_volume_24h,
        reported_volume_7d ,reported_volume_30d, sessions_per_month,
    """

    session = PaprikaSession()
    exchanges = session.make_request(session.ENDPOINTS["exchanges"], quotes=symbols)
    df = pd.json_normalize(exchanges)
    try:
        df.columns = [
            col.replace(f"quotes.{symbols}.", "") for col in df.columns.tolist()
        ]
    except KeyError as e:
        logger.exception(str(e))
        console.print(e)
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
    df["fiats"] = df["fiats"].apply(lambda x: len([i["symbol"] for i in x if x]))
    df = df[cols]
    df = df.applymap(
        lambda x: "\n".join(textwrap.wrap(x, width=28)) if isinstance(x, str) else x
    )
    df = df.rename(
        columns={"adjusted_rank": "Rank", "confidence_score": "confidence"},
    )
    df.columns = [x.replace("reported_", "") for x in df.columns]
    if sortby.lower() == "rank":
        df = df.sort_values(by="Rank", ascending=not ascend)
    else:
        df = df.sort_values(by=sortby, ascending=ascend)
    return df


@log_start_end(log=logger)
def get_exchanges_market(
    exchange_id: str = "binance",
    symbols: str = "USD",
    sortby: str = "pair",
    ascend: bool = True,
) -> pd.DataFrame:
    """List markets by exchange ID [Source: CoinPaprika]

    Parameters
    ----------
    exchange_id: str
        identifier of exchange e.g for Binance Exchange -> binance
    symbols: str
        Comma separated quotes to return e.g quotes=USD,BTC
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending

    Returns
    -------
    pd.DataFrame
        pair, base_currency_name, quote_currency_name, market_url,
        category, reported_volume_24h_share, trust_score,
    """

    session = PaprikaSession()
    data = session.make_request(
        session.ENDPOINTS["exchange_markets"].format(exchange_id), quotes=symbols
    )
    if "error" in data:
        console.print(data)
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
    df = df[cols]
    df = df.sort_values(by=sortby, ascending=ascend)
    return df


@log_start_end(log=logger)
def get_all_contract_platforms() -> pd.DataFrame:
    """List all smart contract platforms like ethereum, solana, cosmos, polkadot, kusama ... [Source: CoinPaprika]

    Returns
    -------
    pd.DataFrame
        index, platform_id
    """

    session = PaprikaSession()
    contract_platforms = session.make_request(session.ENDPOINTS["contract_platforms"])
    df = pd.DataFrame(contract_platforms).reset_index()
    df.columns = ["index", "platform_id"]

    # pylint: disable=unsupported-assignment-operation
    df["index"] = df["index"] + 1

    return df


@log_start_end(log=logger)
def get_contract_platform(
    platform_id: str = "eth-ethereum", sortby: str = "active", ascend: bool = True
) -> pd.DataFrame:
    """Gets all contract addresses for given platform [Source: CoinPaprika]
    Parameters
    ----------
    platform_id: str
        Blockchain platform like eth-ethereum
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascend

    Returns
    -------
    pd.DataFrame
        id, type, active
    """

    session = PaprikaSession()
    contract_platforms = session.make_request(
        session.ENDPOINTS["contract_platform_addresses"].format(platform_id)
    )

    df = pd.DataFrame(contract_platforms)[["id", "type", "active"]]
    df = df.sort_values(by=sortby, ascending=ascend)
    return df
