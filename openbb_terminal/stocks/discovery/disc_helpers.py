import pandas as pd
import requests

from openbb_terminal.helper_funcs import get_user_agent


def get_df(url: str, header: int = None) -> pd.DataFrame:
    headers = {"User-Agent": get_user_agent()}
    html = requests.get(url, headers=headers).text
    dfs = pd.read_html(html, header=header)
    return dfs
