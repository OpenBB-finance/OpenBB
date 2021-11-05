"""BitQuery model"""
__docformat__ = "numpy"

import datetime
import requests
import pandas as pd
from gamestonk_terminal import config_terminal as cfg

BQ_URL = "https://graphql.bitquery.io"
CURRENCIES = ["ETH", "USD", "BTC"]


def query_graph(url: str, query: str) -> dict:
    """Helper methods for querying graphql api. [Source: https://bitquery.io/pricing]

    Parameters
    ----------
    url: str
        Endpoint url
    query: str
        Graphql query

    Returns
    -------
    dict:
        Dictionary with response data
    """
    headers = {"x-api-key": cfg.API_BITQUERY_KEY}
    request = requests.post(url, json={"query": query}, headers=headers)
    print(request.text)
    if request.status_code == 200:
        response = request.json()
        if "error" in response:
            print(f"Something went wrong: {response['error']}")
            return {}
        return response["data"]
    if request.status_code == 403:
        print("Please visit https://bitquery.io/pricing and generate you free api key")
    else:
        print("Something went wrong: ", request.text)
    return {}


def get_dex_trades_by_protocol() -> pd.DataFrame:
    """Get trades on Decentralized Exchanges aggregated by DEX [Source: https://graphql.bitquery.io/]

    Returns
    -------
    pd.DataFrame
        Trades on Decentralized Exchanges aggregated by DEX
    """

    query = """
            {
          ethereum {
            dexTrades(options: {limit: 100, desc: "count"}) {
              protocol
              count
              tradeAmount(in: USD)
            }
          }
        }
        """

    data = query_graph(BQ_URL, query)
    if not data:
        return pd.DataFrame()

    return pd.DataFrame(data["ethereum"]["dexTrades"])


def get_dex_trades_monthly(trade_amount_currency: str = "USD") -> pd.DataFrame:
    """Get list of trades on Decentralized Exchanges monthly aggregated. [Source: https://graphql.bitquery.io/]

    Parameters
    ----------
    trade_amount_currency: str
        Currency of displayed trade amount. Default: USD

    Returns
    -------
    pd.DataFrame
        Trades on Decentralized Exchanges monthly aggregated
    """

    if trade_amount_currency not in CURRENCIES:
        trade_amount_currency = "USD"

    query = (
        """
            {
          ethereum {
            dexTrades(options: {limit: 1000, desc: ["count","protocol", "date.year","date.month"]}) {
              protocol
              count
              tradeAmount(in: %s)
              date {
                year
                month
                }
            }
          }
        }
        """
        % trade_amount_currency
    )

    data = query_graph(BQ_URL, query)
    if not data:
        return pd.DataFrame()

    return pd.json_normalize(data["ethereum"]["dexTrades"])


def get_daily_dex_volume_for_given_pair(
    limit: int = 90,
    token_address: str = "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984",
    vs: str = "usdt",
) -> pd.DataFrame:
    """Get daily volume for given pair [Source: https://graphql.bitquery.io/]

    Parameters
    -------
    limit:  int
        Last n days to query data
    token_address: str
        ERC20 token address
    vs: str
        Quoted currency. One from [usdt, usdc, dai, wbtc, eth]

    Returns
    -------
    pd.DataFrame
         Daily volume for given pair
    """

    dt = (datetime.date.today() - datetime.timedelta(limit)).strftime("%Y-%m-%d")
    vs_currency_map = {
        "eth": "ETH",
        "usdt": "0xdac17f958d2ee523a2206206994597c13d831ec7",
        "usdc": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "dai": "0x6b175474e89094c44da98b954eedeac495271d0f",
        "wbtc": "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599",
    }

    currency = vs_currency_map.get(vs.lower(), "ETH")

    query = """
        {
          ethereum(network: ethereum) {
            dexTrades(
              options: {limit: %s, asc: "timeInterval.day"}
              date: {since: "%s"}
              exchangeName: {is: "Uniswap"}
              baseCurrency: {is: "%s"}
              quoteCurrency: {is: "%s"}
            ) {
              timeInterval {
                day(count: 1)
              }
              baseCurrency {
                symbol
              }
              quoteCurrency {
                symbol
              }
              trades: count
              tradeAmount(in: USD)
              quotePrice
              maximum_price: quotePrice(calculate: maximum)
              minimum_price: quotePrice(calculate: minimum)
              open_price: minimum(of: block, get: quote_price)
              close_price: maximum(of: block, get: quote_price)
            }
          }
        }

        """ % (
        limit,
        dt,
        token_address,
        currency,
    )

    data = query_graph(BQ_URL, query)
    if not data:
        return pd.DataFrame()

    df = pd.json_normalize(data["ethereum"]["dexTrades"])
    df.columns = [
        "trades",
        "amount",
        "price",
        "high",
        "low",
        "open",
        "close",
        "date",
        "base",
        "quote",
    ]
    return df[
        ["date", "base", "quote", "open", "high", "low", "close", "amount", "trades"]
    ].sort_values(by="date", ascending=False)


def get_token_volume_on_dexes(
    token_address: str = "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984",
    trade_amount_currency: str = "USD",
) -> pd.DataFrame:
    """Get token volume on different Decentralized Exchanges. [Source: https://graphql.bitquery.io/]

    Parameters
    ----------
    token_address: str
        ERC20 token address.
    trade_amount_currency: str
        Currency to display trade amount in.

    Returns
    -------
    pd.DataFrame
        Token volume on Decentralized Exchanges
    """

    if trade_amount_currency not in CURRENCIES:
        trade_amount_currency = "USD"

    query = """
        {
           ethereum {
            dexTrades(
              baseCurrency: {is:"%s"}
            ) {
                  baseCurrency{
        symbol
      }
              exchange {
              name
              fullName
              }
              count
              tradeAmount(in:%s)

            }
            }
            }

        """ % (
        token_address,
        trade_amount_currency,
    )

    data = query_graph(BQ_URL, query)
    if not data:
        return pd.DataFrame()

    df = pd.json_normalize(data["ethereum"]["dexTrades"])[
        ["exchange.fullName", "baseCurrency.symbol", "tradeAmount", "count"]
    ]
    df.columns = ["exchange", "coin", "amount", "trades"]
    return df[~df["exchange"].str.startswith("<")].sort_values(
        by="amount", ascending=False
    )


def get_ethereum_unique_senders(interval: str = "day") -> pd.DataFrame:
    """Get number of unique ethereum addresses which made a transaction in given time interval.

    Parameters
    ----------
    interval: str
        Time interval in which count unique ethereum addresses which made transaction. day, month or week.

    Returns
    -------
    pd.DataFrame
        Unique ethereum addresses which made a transaction

    """

    intervals = ["day", "month", "week"]
    if interval not in intervals:
        interval = "day"

    dt = (datetime.date.today() - datetime.timedelta(90)).strftime("%Y-%m-%d")

    query = """
     {
          ethereum(network: ethereum) {
            transactions(options: {desc: "date.date"}, date: {since: "%s"}) {
              uniqueSenders: count(uniq: senders)
              date {
                date:startOfInterval(unit: %s)
              }
                avgGasPrice: gasPrice(calculate: average)
                  medGasPrice: gasPrice(calculate: median)
                  maxGasPrice: gasPrice(calculate: maximum)
                  transactions: count
            }
          }
        }

        """ % (
        dt,
        interval,
    )

    data = query_graph(BQ_URL, query)
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data["ethereum"]["transactions"])
    df["date"] = df["date"].apply(lambda x: x["date"])
    return df
