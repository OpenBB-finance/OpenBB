"""DeFi Pulse model"""
__docformat__ = "numpy"

import requests
from bs4 import BeautifulSoup
import pandas as pd


def get_defipulse_index() -> pd.DataFrame:
    """Scrapes data from DeFi Pulse with all DeFi Pulse crypto protocols.
    [Source: https://defipulse.com/]

    Returns
    -------
    pd.DataFrame
        List of DeFi Pulse protocols.
    """

    req = requests.get("https://defipulse.com/")
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
            "x",
            "Rank",
            "Name",
            "Chain",
            "Category",
            "TVL",
            "Change_1D",
        ],
    )
    try:
        df["Rank"] = df["Rank"].apply(lambda x: int(x.replace(".", "")))
    except Exception as e:
        print(e, "\n")

    df.drop("x", axis=1, inplace=True)
    return df
