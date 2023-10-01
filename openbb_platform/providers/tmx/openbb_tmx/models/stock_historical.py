"""TMX Company Filings Model"""

import json
from datetime import (
    date as dateType,
    datetime,
    timedelta,
)
from typing import Any, Dict, List, Literal, Optional, Union

import pandas as pd
import requests
from openbb_provider.abstract.data import Data
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.abstract.query_params import QueryParams
from pydantic import Field, NonNegativeInt, validator
from random_user_agent.user_agent import UserAgent

from openbb_tmx.utils.gql import GQL
from openbb_tmx.utils.helpers import get_random_agent

INTERVALS = Literal["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1d", "1w", "1mo"]



def get_timeseries(
    symbol: str,
    interval: Optional[INTERVALS] = "1d",
    multiplier: Optional[int] = 1,
    start_date: Optional[Union[str, dateType]] = (datetime.today() - timedelta(weeks=2000)).strftime("%Y-%m-%d"),
    end_date: Optional[str] = "",
) -> Dict:

    start_time: Any = ""
    end_time: int
    results = []
    _interval: Any = ""
    freq: str = ""

    INTERVAL_DICT = {
        "1d" : "day",
        "1w" : "week",
        "1mo" : "month",
        "1m": 1,
        "2m": 2,
        "5m": 5,
        "15m": 15,
        "30m": 30,
        "60m": 60,
        "90m": 90
    }

    interval = INTERVAL_DICT[interval]  # type: ignore

    if isinstance(interval, int):
        _interval = interval * multiplier  # type: ignore
        start_time = int(datetime.timestamp(datetime.now()-timedelta(days=41)))
        #end_time=int(datetime.timestamp(datetime.now()-timedelta(days=start_day)+timedelta(weeks=2)))
        freq = ""
        end_date = ""

    if isinstance(interval, str):
        _interval = ""
        freq = interval

    payload = GQL.get_timeseries_payload.copy()
    payload["variables"]["symbol"] = symbol.upper()
    payload["variables"]["start"] = start_date
    payload["variables"]["startDateTime"] = start_time
    payload["variables"]["end"] = end_date
    #payload["variables"]["endDateTime"] = end_time
    payload["variables"]["freq"] = freq
    payload["variables"]["interval"] = _interval

    items = list(payload["variables"].keys())

    for item in items:
        if payload["variables"][item] == "":
            payload["variables"].pop(item)

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
            r_data = r.json()["data"]["timeseries"]
            return r_data
    except Exception as e:
        raise (e)



def get_recent_price_history(
    symbol: str,
    start_date: Optional[Union[str, dateType]] = (datetime.today() - timedelta(days=89)).strftime("%Y-%m-%d"),
    end_date: Optional[str] = "",
    adjusted: bool = True,
    adjustment_type: Optional[str] = "SO",
    unadjusted: bool = False,
) -> Dict:

    payload = GQL.get_company_price_history_payload.copy()
    payload["variables"]["symbol"] = symbol.upper()
    payload["variables"]["start"] = start_date
    payload["variables"]["end"] = end_date
    payload["variables"]["adjusted"] = adjusted
    payload["variables"]["adjustmentType"] = adjustment_type
    payload["variables"]["unadjusted"] = unadjusted


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
            r_data = r.json()["data"]["company_price_history"]
            return r_data
    except Exception as e:
        raise (e)


def get_recent_trades(
    symbol: str,
    limit: int = 51
) -> Dict:

    payload = GQL.get_company_most_recent_trades_payload.copy()
    payload["variables"]["symbol"] = symbol.upper()
    payload["variables"]["limit"] = limit


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
            r_data = r.json()["data"]["trades"]
            return r_data
    except Exception as e:
        raise (e)
