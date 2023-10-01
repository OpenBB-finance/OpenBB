"""TMX Stock Analysts Model"""

import json

import requests

from openbb_tmx.utils.gql import GQL
from openbb_tmx.utils.helpers import get_random_agent


def get_company_analysts(symbol: str):
    payload = GQL.get_company_analysts_payload.copy()
    payload["variables"]["symbol"] = symbol.upper()
    payload["variables"]["datatype"] = "equity"

    data = {}
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
            r_data = r.json()["data"]["analysts"]
            data.update(
                {
                    "symbol": symbol.upper(),
                    "total_analysts": r_data["totalAnalysts"],
                    "consensus": r_data["consensusAnalysts"]["consensus"],
                    "buy_ratings": r_data["consensusAnalysts"]["buy"],
                    "sell_ratings": r_data["consensusAnalysts"]["sell"],
                    "hold_ratings": r_data["consensusAnalysts"]["hold"],
                    "price_target": r_data["priceTarget"]["priceTarget"],
                    "price_target_high": r_data["priceTarget"]["highPriceTarget"],
                    "price_target_low": r_data["priceTarget"]["lowPriceTarget"],
                    "price_target_upside": r_data["priceTarget"]["priceTargetUpside"],
                }
            )
            return data
    except Exception as e:
        raise (e)
