"""DeFi Pulse model"""
__docformat__ = "numpy"

import logging

import pandas as pd
import requests
from bs4 import BeautifulSoup

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_defipulse_index(sortby: str = "TVL_$", ascend: bool = False) -> pd.DataFrame:
    """Scrapes data from DeFi Pulse with all DeFi Pulse crypto protocols.
    [Source: https://defipulse.com/]

    Returns
    -------
    pd.DataFrame
        List of DeFi Pulse protocols.
    """

    req = requests.get("https://www.defipulse.com/")
    result = req.content.decode("utf8")
    soup = BeautifulSoup(result, features="lxml")
    table = soup.find("tbody").find_all("tr")

    list_of_records = []
    for row in table:
        row_elements = []
        for element in row.find_all("td"):
            text = element.text
            row_elements.append(text)
        list_of_records.append(row_elements)

    df = pd.DataFrame(
        list_of_records,
        columns=[
            "Rank",
            "Name",
            "Chain",
            "Sector",
            "30D_Users",
            "TVL_$",
            "1_Day_%",
        ],
    )

    df["Rank"] = df.index
    df["30D_Users"] = df["30D_Users"].str.replace(",", "").astype(int)
    for i, row in df.iterrows():
        value = row["TVL_$"]
        residue = len(value.partition(".")[2]) - 1
        value = value.replace("$", "")
        value = value.replace("M", "000000")
        value = value.replace("B", "000000000")
        value = value[0:-residue]
        value = value.replace(".", "")
        df.at[i, "TVL_$"] = int(value)

        percent = row["1_Day_%"]
        percent = percent.replace("%", "")
        percent = percent.replace("+", "")
        df.at[i, "1_Day_%"] = float(percent)
    df = df.sort_values(by=sortby, ascending=ascend)
    df.rename(
        columns={"30D_Users": "30D Users", "TVL_$": "TVL $", "1_Day_%": "1 Day %"},
        inplace=True,
    )
    return df
