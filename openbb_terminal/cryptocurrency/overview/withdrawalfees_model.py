"""Withdrawal Fees model"""
import logging
import math
from typing import Any, List

import pandas as pd
from bs4 import BeautifulSoup

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_user_agent, request

logger = logging.getLogger(__name__)

POSSIBLE_CRYPTOS = [
    "bitcoin",
    "ethereum",
    "binance-coin",
    "tether",
    "solana",
    "cardano",
    "usd-coin",
    "xrp",
    "polkadot",
    "terra",
    "dogecoin",
    "avalanche",
    "shiba-inu",
    "polygon",
    "crypto-com-coin",
    "binance-usd",
    "wrapped-bitcoin",
    "litecoin",
    "algorand",
    "chainlink",
    "tron",
    "dai",
    "bitcoin-cash",
    "terrausd",
    "uniswap",
    "stellar",
    "axie-infinity",
    "okb",
    "cosmos",
    "lido-staked-ether",
    "vechain",
    "ftx-token",
    "elrond",
    "internet-computer",
    "filecoin",
    "decentraland",
    "ethereum-classic",
    "hedera",
    "the-sandbox",
    "theta-network",
    "fantom",
    "near",
    "magic-internet-money",
    "gala",
    "bittorrent",
    "monero",
    "tezos",
    "klaytn",
    "the-graph",
    "leo-token",
    "iota",
    "helium",
    "flow",
    "eos",
    "radix",
    "loopring",
    "bitcoin-sv",
    "pancakeswap",
    "olympus",
    "enjin-coin",
    "kusama",
    "amp",
    "aave",
    "stacks",
    "ecash",
    "maker",
    "arweave",
    "quant",
    "thorchain",
    "harmony",
    "zcash",
    "neo",
    "bitcoin-cash-abc",
    "basic-attention-token",
    "waves",
    "kadena",
    "theta-fuel",
    "holo",
    "chiliz",
    "kucoin-token",
    "celsius-network",
    "curve-dao-token",
    "dash",
    "marinade-staked-sol",
    "nexo",
    "compound",
    "celo",
    "huobi-token",
    "wonderland",
    "frax",
    "decred",
    "trueusd",
    "ecomi",
    "e-radix",
    "spell-token",
    "mina-protocol",
    "nem",
    "qtum",
    "sushi",
    "synthetix-network-token",
]


@log_start_end(log=logger)
def get_overall_withdrawal_fees(limit: int = 100) -> pd.DataFrame:
    """Scrapes top coins withdrawal fees
    [Source: https://withdrawalfees.com/]

    Parameters
    ----------
    limit: int
        Number of coins to search, by default n=100, one page has 100 coins, so 1 page is scraped.

    Returns
    -------
    pd.DataFrame
        Coin, Lowest, Average, Median, Highest, Exchanges Compared
    """

    COINS_PER_PAGE = 100
    withdrawal_fees_homepage = BeautifulSoup(
        request(
            "https://withdrawalfees.com/",
            headers={"User-Agent": get_user_agent()},
        ).text,
        "lxml",
    )
    table = withdrawal_fees_homepage.find_all("table")
    tickers_html = withdrawal_fees_homepage.find_all("div", {"class": "name"})
    if table is None or tickers_html is None:
        return pd.DataFrame()
    df = pd.read_html(str(table))[0]

    df["Coin"] = [ticker.text for ticker in tickers_html]
    df["Lowest"] = df["Lowest"].apply(
        lambda x: f'{x[:x.index(".")+3]} ({x[x.index(".")+3:]})'
        if "." in x and isinstance(x, str)
        else x
    )

    num_pages = int(math.ceil(limit / COINS_PER_PAGE))
    if num_pages > 1:
        for idx in range(2, num_pages + 1):
            withdrawal_fees_homepage = BeautifulSoup(
                request(
                    f"https://withdrawalfees.com/coins/page/{idx}",
                    headers={"User-Agent": get_user_agent()},
                ).text,
                "lxml",
            )
            table = withdrawal_fees_homepage.find_all("table")
            tickers_html = withdrawal_fees_homepage.find_all("div", {"class": "name"})
            if table is not None and tickers_html is not None:
                new_df = pd.read_html(str(table))[0]
                new_df["Highest"] = new_df["Highest"].apply(
                    lambda x: f'{x[:x.index(".")+3]} ({x[x.index(".")+3:]})'
                    if "." in x
                    else x
                )
                new_df["Coin"] = [ticker.text for ticker in tickers_html]
                df = df.append(new_df)
    df = df.fillna("")
    return df


@log_start_end(log=logger)
def get_overall_exchange_withdrawal_fees() -> pd.DataFrame:
    """Scrapes exchange withdrawal fees
    [Source: https://withdrawalfees.com/]

    Returns
    -------
    pd.DataFrame
        Exchange, Coins, Lowest, Average, Median, Highest
    """
    exchange_withdrawal_fees = BeautifulSoup(
        request(
            "https://withdrawalfees.com/exchanges",
            headers={"User-Agent": get_user_agent()},
        ).text,
        "lxml",
    )
    table = exchange_withdrawal_fees.find_all("table")
    if table is None:
        return pd.DataFrame()
    df = pd.read_html(str(table))[0]
    df = df.fillna("")
    return df


@log_start_end(log=logger)
def get_crypto_withdrawal_fees(
    symbol: str,
) -> List[Any]:
    """Scrapes coin withdrawal fees per exchange
    [Source: https://withdrawalfees.com/]

    Parameters
    ----------
    symbol: str
        Coin to check withdrawal fees. By default bitcoin

    Returns
    -------
    List
        - str: Overall statistics (exchanges, lowest, average and median)
        - pd.DataFrame: Exchange, Withdrawal Fee, Minimum Withdrawal Amount
    """
    crypto_withdrawal_fees = BeautifulSoup(
        request(
            f"https://withdrawalfees.com/coins/{symbol}",
            headers={"User-Agent": get_user_agent()},
        ).text,
        "lxml",
    )
    if crypto_withdrawal_fees is None:
        return ["", pd.DataFrame()]
    table = crypto_withdrawal_fees.find_all("table")
    html_stats = crypto_withdrawal_fees.find("div", {"class": "details"})

    if len(table) == 0 or html_stats is None:
        return ["", pd.DataFrame()]
    df = pd.read_html(str(table))[0]
    df["Withdrawal Fee"] = df["Withdrawal Fee"].apply(
        lambda x: f'{x[:x.index(".")+3]} ({x[x.index(".")+3:]})'
        if "." in x and isinstance(x, str)
        else x
    )
    df["Minimum Withdrawal Amount"] = df["Minimum Withdrawal Amount"].apply(
        lambda x: f'{x[:x.index(".")+3]} ({x[x.index(".")+3:]})'
        if isinstance(x, str) and "." in x
        else x
    )
    df = df.fillna("")

    stats = html_stats.find_all("div", recursive=False)
    exchanges = stats[0].find("div", {"class": "value"}).text
    lowest = stats[1].find("div", {"class": "value"}).text
    average = stats[2].find("div", {"class": "value"}).text
    median = stats[3].find("div", {"class": "value"}).text
    stats_string = (
        f"{symbol} is available on {exchanges} exchanges with alowest fee of "
    )
    stats_string += f"{lowest}, average of {average} and median of {median}"
    return [stats_string, df]
