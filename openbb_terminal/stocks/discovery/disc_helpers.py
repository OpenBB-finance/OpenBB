import re
from typing import Optional

import pandas as pd

from openbb_terminal.helper_funcs import get_user_agent, request


def get_df(url: str, header: Optional[int] = None) -> pd.DataFrame:
    headers = {"User-Agent": get_user_agent()}
    html = request(url, headers=headers).text
    # use regex to replace radio button html entries
    html_clean = re.sub(r"(<span class=\"Fz\(0\)\">).*?(</span>)", "", html)
    dfs = pd.read_html(html_clean, header=header)
    return dfs
