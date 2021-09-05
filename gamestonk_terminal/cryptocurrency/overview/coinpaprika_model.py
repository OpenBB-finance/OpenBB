"""CoinPaprika model"""
__docformat__ = "numpy"

from datetime import datetime
import textwrap
import pandas as pd
from dateutil import parser
from gamestonk_terminal.cryptocurrency.coinpaprika_helpers import PaprikaSession


def get_global_market() -> pd.DataFrame:
    """Return data frame with most important global crypto statistics like:
    market_cap_usd, volume_24h_usd, bitcoin_dominance_percentage, cryptocurrencies_number,
    market_cap_ath_value, market_cap_ath_date, volume_24h_ath_value, volume_24h_ath_date,
    market_cap_change_24h, volume_24h_change_24h, last_updated.   [Source: CoinPaprika]

    Returns
    -------
    pandas.DataFrame
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
                global_markets[key] = parser.parse(date).strftime("%Y-%m-%d %H:%M:%S")
            except (KeyError, ValueError, TypeError) as e:
                print(e)
    df = pd.Series(global_markets).to_frame().reset_index()
    df.columns = ["Metric", "Value"]
    return df


def get_list_of_coins() -> pd.DataFrame:
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


def _get_coins_info_helper(quotes: str = "USD") -> pd.DataFrame:
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
    quotes: Comma separated quotes to return e.g quotes=USD,BTC

    Returns
    -------
    pandas.DataFrame
        id, name, symbol, rank, circulating_supply, total_supply, max_supply, beta_value, first_data_at,
        last_updated, price, volume_24h, volume_24h_change_24h, market_cap, market_cap_change_24h,
        percent_change_15m, percent_change_30m, percent_change_1h, percent_change_6h, percent_change_12h,
       percent_change_24h, percent_change_7d, percent_change_30d, percent_change_1y,
       ath_price, ath_date, percent_from_price_ath
    """

    session = PaprikaSession()
    tickers = session.make_request(session.ENDPOINTS["tickers"], quotes=quotes)
    data = pd.json_normalize(tickers)
    try:
        # data.columns = [col.replace(f"quotes.{quotes}.", f"{quotes.lower()}_") for col in data.columns.tolist()]
        data.columns = [
            col.replace(f"quotes.{quotes}.", "") for col in data.columns.tolist()
        ]
        data.columns = [col.replace("percent", "pct") for col in list(data.columns)]
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


def get_coins_info(quotes: str = "USD") -> pd.DataFrame:  # > format big numbers fix
    """Returns basic coin information for all coins from CoinPaprika API [Source: CoinPaprika]

    Parameters
    ----------
    quotes: str
        Comma separated quotes to return e.g quotes=USD,BTC

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


def get_coins_market_info(quotes: str = "USD") -> pd.DataFrame:
    """Returns basic coin information for all coins from CoinPaprika API [Source: CoinPaprika]

    Parameters
    ----------
    quotes: str
        Comma separated quotes to return e.g quotes=USD,BTC

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
        "ath_price",
        "pct_from_ath",
    ]
    return _get_coins_info_helper(quotes=quotes)[cols].sort_values(by="rank")


def get_list_of_exchanges(quotes: str = "USD") -> pd.DataFrame:
    """
    List exchanges from CoinPaprika API [Source: CoinPaprika]

    Parameters
    ----------
    quotes: str
        Comma separated quotes to return e.g quotes=USD,BTC

    Returns
    -------
    pandas.DataFrame
        rank, name, currencies, markets, fiats, confidence_score, reported_volume_24h,
        reported_volume_7d ,reported_volume_30d, sessions_per_month,
    """

    session = PaprikaSession()
    exchanges = session.make_request(session.ENDPOINTS["exchanges"], quotes=quotes)
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


def get_exchanges_market(
    exchange_id: str = "binance", quotes: str = "USD"
) -> pd.DataFrame:
    """List markets by exchange ID [Source: CoinPaprika]

    Parameters
    ----------
    exchange_id: str
        identifier of exchange e.g for Binance Exchange -> binance
    quotes: str
        Comma separated quotes to return e.g quotes=USD,BTC

    Returns
    -------
    pandas.DataFrame
        pair, base_currency_name, quote_currency_name, market_url,
        category, reported_volume_24h_share, trust_score,
    """

    session = PaprikaSession()
    data = session.make_request(
        session.ENDPOINTS["exchange_markets"].format(exchange_id), quotes=quotes
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


def get_all_contract_platforms() -> pd.DataFrame:
    """List all smart contract platforms like ethereum, solana, cosmos, polkadot, kusama ... [Source: CoinPaprika]

    Returns
    -------
    pandas.DataFrame
        index, platform_id
    """

    session = PaprikaSession()
    contract_platforms = session.make_request(session.ENDPOINTS["contract_platforms"])
    df = pd.DataFrame(contract_platforms).reset_index()
    df.columns = ["index", "platform_id"]
    df["index"] = df["index"] + 1
    return df


def get_contract_platform(platform_id: str = "eth-ethereum") -> pd.DataFrame:
    """Gets all contract addresses for given platform [Source: CoinPaprika]
    Parameters
    ----------
    platform_id: str
        Blockchain platform like eth-ethereum

    Returns
    -------
    pandas.DataFrame
         id, type, active, address
    """

    session = PaprikaSession()
    contract_platforms = session.make_request(
        session.ENDPOINTS["contract_platform_addresses"].format(platform_id)
    )

    return pd.DataFrame(contract_platforms)[["id", "type", "active", "address"]]
