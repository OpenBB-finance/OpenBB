"""Barchart Model"""
__docformat__ = "numpy"

import pandas as pd
import requests
from bs4 import BeautifulSoup
from gamestonk_terminal.helper_funcs import get_user_agent


def get_options_info(ticker: str) -> pd.DataFrame:
    """Scrape barchart for options info

    Parameters
    ----------
    ticker: str
        Stock ticker

    Returns
    -------
    df: pd.DataFrame
        Dataframe of information
    """
    page = f"https://www.barchart.com/stocks/quotes/{ticker}/overview"

    r = requests.get(page, headers={"User-Agent": get_user_agent()})
    soup = BeautifulSoup(r.text, "html.parser")
    tags = soup.find(
        "div",
        attrs={
            "class": "barchart-content-block symbol-fundamentals bc-cot-table-wrapper"
        },
    )
    data = tags.find_all("li")
    labels = []
    values = []
    for row in data:
        labels.append(row.find_all("span")[0].getText())
        values.append(row.find_all("span")[1].getText())

    df = pd.DataFrame(data=[labels, values]).T

    return df
