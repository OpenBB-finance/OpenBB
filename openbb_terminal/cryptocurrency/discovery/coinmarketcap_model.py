"""CoinMarketCap model"""
__docformat__ = "numpy"

import logging

import pandas as pd
from coinmarketcapapi import CoinMarketCapAPI, CoinMarketCapAPIError

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

FILTERS = ["Symbol", "CMC_Rank", "LastPrice", "DayPctChange", "MarketCap"]

sort_map = {
    "Symbol": "Symbol",
    "CMC_Rank": "CMC_Rank",
    "LastPrice": "Last Price",
    "DayPctChange": "1 Day Pct Change",
    "MarketCap": "Market Cap ($B)",
}


@log_start_end(log=logger)
@check_api_key(["API_CMC_KEY"])
def get_cmc_top_n(sortby: str = "CMC_Rank", ascend: bool = True) -> pd.DataFrame:
    """Shows top n coins. [Source: CoinMarketCap]

    Parameters
    ----------
    sortby: str
        Key to sort data. The table can be sorted by every of its columns. Refer to
        Coin Market Cap:s API documentation, see:
        https://coinmarketcap.com/api/documentation/v1/#operation/getV1CryptocurrencyListingsLatest
    ascend: bool
        Whether to sort ascending or descending

    Returns
    -------
    pd.DataFrame
        Top coin on CoinMarketCap

    """
    df = pd.DataFrame()

    try:
        cmc = CoinMarketCapAPI(get_current_user().credentials.API_CMC_KEY)
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
    except CoinMarketCapAPIError as e:
        if "API Key" in str(e):
            console.print("[red]Invalid API Key[/red]\n")
        else:
            console.print(e)

    df = df.sort_values(by=sort_map[sortby], ascending=ascend)
    return df
