import pandas as pd
import requests
import json
from bs4 import BeautifulSoup

from gamestonk_terminal.helper_funcs import get_user_agent

DAYS = [30, 90, 365]

def get_altcoin_index(days: int):
    """Scrapes top coins withdrawal fees
     [Source: https://blockchaincenter.net]

     Parameters
     ----------
     days: int

     Returns
     -------
     pandas.DataFrame:
         Date, Value (Altcoin Index)
     """
    if days not in DAYS:
        return pd.DataFrame()
    soup = BeautifulSoup(
        requests.get(
            "https://www.blockchaincenter.net/altcoin-season-index/",
            headers={"User-Agent": get_user_agent()},
        ).content,
        'html.parser',
    )
    script = soup.select_one(f'script:-soup-contains("chartdata[{days}]")')

    string = script.contents[0].strip()
    initiator = string.index(f'chartdata[{days}] = ') + len(f"chartdata[{days}] = ")
    terminator = string.index(';')
    dict_data = json.loads(string[initiator:terminator])
    df = pd.DataFrame(zip(dict_data["labels"]["all"], dict_data["values"]["all"]), columns=("Date", "Value"))
    df['Date'] = pd.to_datetime(df['Date'])
    df['Value'] = df['Value'].astype(int)
    df = df.set_index("Date")
    return df
