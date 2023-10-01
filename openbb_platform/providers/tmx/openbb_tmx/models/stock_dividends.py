"""TMX Stock Dividends Model"""

import json

import pandas as pd
import requests

from openbb_tmx.utils.gql import GQL
from openbb_tmx.utils.helpers import get_random_agent


def get_dividends(symbol: str, batch: int = 200, page: int = 1):
    payload = GQL.get_dividend_history_payload.copy()
    payload["variables"]["symbol"] = symbol.upper()
    payload["variables"]["batch"] = batch
    payload["variables"]["page"] = page

    url = "https://app-money.tmx.com/graphql"
    r = requests.post(
        url,
        data=json.dumps(payload),
        headers={
            "authority": "app-money.tmx.com",
            "referer": f"https://money.tmx.com/en/quote/{symbol.upper()}",
            "locale": "en",
            "Content-Type": "application/json",
            "User-Agent": get_random_agent(),
            "Accept": "*/*",
        },
        timeout=10,
    )
    try:
        if r.status_code == 403:
            raise RuntimeError(f"HTTP error - > {r.text}")
        else:
            r_data = r.json()["data"]["dividends"]
            if r_data["hasNextPage"] is False:
                return pd.DataFrame.from_records(r_data["dividends"])
            return r_data
    except Exception as e:
        raise (e)
