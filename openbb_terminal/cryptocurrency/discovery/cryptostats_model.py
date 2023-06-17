"""CryptoStats model"""
__docformat__ = "numpy"

import logging

import pandas as pd

from openbb_terminal.cryptocurrency.defi.llama_model import (
    get_chains,
    get_defi_protocols,
)
from openbb_terminal.cryptocurrency.discovery.pycoingecko_model import get_coins
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import request

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_fees(marketcap: bool, tvl: bool, date) -> pd.DataFrame:
    """Show cryptos with most fees. [Source: CryptoStats]

    Parameters
    ----------
    marketcap: bool
        Whether to show marketcap or not
    tvl: bool
        Whether to show tvl or not
    date: datetime
        Date to get data from (YYYY-MM-DD)

    Returns
    -------
    pd.DataFrame
        Top coins with most fees
    """
    df = pd.DataFrame()
    if not isinstance(date, str):
        date = date.strftime("%Y-%m-%d")
    response = request(
        f"https://api.cryptostats.community/api/v1/fees/oneDayTotalFees/{date}"
    )
    if response.status_code != 200:
        raise Exception(f"Status code: {response.status_code}. Reason: {response.text}")
    res = response.json()
    data = res["data"]
    df = pd.DataFrame(columns=["Symbol", "Name", "Category", "One Day Fees"])

    for i, item in enumerate(data):
        metadata = item["metadata"]
        results = item["results"]
        symbol = metadata.get("tokenTicker", "")
        name = metadata.get("name", "")
        category = metadata.get("category", "")
        fees = results.get("oneDayTotalFees", "")
        df.loc[i] = [symbol, name, category, fees]

    df = df.groupby(["Symbol", "Name", "Category"]).sum().reset_index()
    df = df.sort_values("One Day Fees", ascending=False)

    if marketcap:
        coins = get_coins()
        coins["symbol"] = coins["symbol"].str.upper()
        coins = coins[["symbol", "market_cap", "market_cap_rank"]]
        coins = coins.rename(
            columns={
                "symbol": "Symbol",
                "market_cap": "Market Cap",
                "market_cap_rank": "MC Rank",
            }
        )
        df = df.merge(coins, left_on="Symbol", right_on="Symbol", how="left")
    if tvl:
        protocols = get_defi_protocols(1000)
        protocols = protocols[["Symbol", "TVL ($)"]]
        protocols = protocols.rename(columns={"TVL ($)": "TVL"})
        protocols = protocols.groupby(["Symbol"]).sum().reset_index()

        df = df.merge(protocols, left_on="Symbol", right_on="Symbol", how="left")
        chains = get_chains()
        chains = chains[["tokenSymbol", "tvl"]]
        chains = chains.rename(columns={"tokenSymbol": "Symbol", "tvl": "TVL"})

        df = df.fillna(0)

        for index, row in df.iterrows():
            chain_tvl = chains[chains["Symbol"] == row["Symbol"]]
            if not chain_tvl.empty:
                df.loc[index, "TVL"] = chain_tvl["TVL"].iloc[0]

    return df
