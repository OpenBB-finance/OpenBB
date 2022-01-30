"""CoinMarketCap model"""
__docformat__ = "numpy"

import pandas as pd
from coinmarketcapapi import CoinMarketCapAPI
import gamestonk_terminal.config_terminal as cfg

FILTERS = ["Symbol", "CMC_Rank", "LastPrice", "DayPctChange", "MarketCap"]


def get_cmc_top_n() -> pd.DataFrame:
    """Shows top n coins. [Source: CoinMarketCap]

    Returns
    -------
    pd.DataFrame
        Top coin on CoinMarketCap

    """

    cmc = CoinMarketCapAPI(cfg.API_CMC_KEY)
    ratings = cmc.cryptocurrency_listings_latest().data

    symbol, rank, price, pchange1d, mkt_cap = [], [], [], [], []
    for coin in ratings:
        symbol.append(coin["symbol"])
        rank.append(coin["cmc_rank"])
        price.append(coin["quote"]["USD"]["price"])
        pchange1d.append(coin["quote"]["USD"]["percent_change_24h"])
        mkt_cap.append(coin["quote"]["USD"]["market_cap"] / (10**9))

    df = pd.DataFrame(data=[symbol, rank, price, pchange1d, mkt_cap]).transpose()
    df.columns = [
        "Symbol",
        "CMC_Rank",
        "Last Price",
        "1 Day Pct Change",
        "Market Cap ($B)",
    ]

    return df
