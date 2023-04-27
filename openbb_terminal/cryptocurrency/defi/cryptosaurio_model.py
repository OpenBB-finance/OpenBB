"""Cryptosaurio model"""
__docformat__ = "numpy"

import logging
from typing import Tuple

import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

api_url = "https://barney.cryptosaurio.com"


@log_start_end(log=logger)
def get_anchor_data(address: str = "") -> Tuple[pd.DataFrame, pd.DataFrame, str]:
    """Returns anchor protocol earnings data of a certain terra address
    [Source: https://cryptosaurio.com/]

    Parameters
    ----------
    address : str
        Terra address. Valid terra addresses start with 'terra'

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame, str]
        - pd.DataFrame: Earnings over time in UST
        - pd.DataFrame: History of transactions
        - str:              Overall statistics
    """

    if not address.startswith("terra"):
        console.print(
            "Select a valid address. Valid terra addresses start with 'terra'"
        )
        return pd.DataFrame(), pd.DataFrame(), ""

    response = request(f"{api_url}/get-anchor-protocol-data-v2/{address}")
    if response.status_code != 200:
        console.print(f"Status code: {response.status_code}. Reason: {response.reason}")
        return pd.DataFrame(), pd.DataFrame(), ""

    data = response.json()
    df = pd.DataFrame(reversed(data["historicalData"]))
    df["time"] = pd.to_datetime(df["time"])
    df["yield"] = df["yield"].astype("float64")
    df_deposits = pd.DataFrame(data["deposits"], columns=["out", "fee", "time"])
    df_deposits["out"] = df_deposits["out"].astype("float64")
    df_deposits["fee"] = df_deposits["fee"].astype("float64")
    df_deposits["time"] = pd.to_datetime(df_deposits["time"])
    df_deposits["Type"] = df_deposits.apply(
        lambda row: "Deposit" if row.out > 0 else "Withdrawal", axis=1
    )
    df_deposits.columns = ["Amount [UST]", "Fee [UST]", "Date", "Type"]
    df_deposits = df_deposits[["Type", "Amount [UST]", "Fee [UST]", "Date"]]

    stats_str = f"""Current anchor APY is {data['currentRate']}%
Deposit amount in Anchor Earn of address {address} is {data["totalYield"]["ustHoldings"]} UST.
You already earned [bold]{df.iloc[-1, 1]}[/bold] UST in Anchor Earn.
Your deposit is generating approximately:
- {data["estimatedYield"]["perHour"]} UST hourly
- {data["estimatedYield"]["perDay"]} UST daily
- {data["estimatedYield"]["perWeek"]} UST weekly
- {data["estimatedYield"]["perMonth"]} UST monthly
- {data["estimatedYield"]["perYear"]} UST yearly"""

    return df, df_deposits, stats_str
