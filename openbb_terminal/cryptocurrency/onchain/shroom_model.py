"""Shroom model"""
import logging
from typing import List

import pandas as pd
import requests
import json
import time

from openbb_terminal.decorators import log_start_end
from openbb_terminal import config_terminal as cfg

logger = logging.getLogger(__name__)


TTL_MINUTES = 15

# return up to 100,000 results per GET request on the query id
PAGE_SIZE = 100000

# return results of page 1
PAGE_NUMBER = 1


def create_query(query: str):
    r = requests.post(
        "https://node-api.flipsidecrypto.com/queries",
        data=json.dumps({"sql": query, "ttlMinutes": TTL_MINUTES}),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "x-api-key": cfg.API_SHROOM_KEY,
        },
    )
    if r.status_code != 200:
        raise Exception(
            f"Error creating query, got response: {r.text} with status code: {str(r.status_code)}"
        )

    return json.loads(r.text)


def get_query_results(token):
    r = requests.get(
        "https://node-api.flipsidecrypto.com/queries/{token}?pageNumber={page_number}&pageSize={page_size}".format(
            token=token, page_number=PAGE_NUMBER, page_size=PAGE_SIZE
        ),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "x-api-key": cfg.API_SHROOM_KEY,
        },
    )
    if r.status_code != 200:
        raise Exception(
            f"Error creating query, got response: {r.text} with status code: {str(r.status_code)}"
        )

    data = json.loads(r.text)
    if data["status"] == "running":
        time.sleep(10)
        return get_query_results(token)

    return data


@log_start_end(log=logger)
def get_daily_transactions(symbols: List[str]) -> pd.DataFrame:
    """Get daily transactions for certain symbols in ethereum blockchain
    [Source: https://sdk.flipsidecrypto.xyz/shroomdk]

    Parameters
    ----------
    symbols : List[str]
        List of symbols to get transactions for

    Returns
    -------
    pd.DataFrame
        DataFrame with transactions for each symbol
    """

    sql = f"""
    select
    date_trunc('day', block_timestamp) as timeframe,
    sum(case when symbol = 'DAI' then amount_usd end) as DAI,
    sum(case when symbol = 'USDT' then amount_usd end) as USDT ,
    sum(case when symbol = 'BUSD' then amount_usd end) as BUSD,
    sum(case when symbol = 'USDC' then amount_usd end) as USDC
    from  ethereum.udm_events
    where 
    block_timestamp >= '2020-06-01'
    -- and amount0_usd > '0'
    group by 1
    order by 1 desc
    """

    query = create_query(sql)
    token = query.get("token")
    data = get_query_results(token)

    df = pd.DataFrame(
        data["results"], columns=["timeframe", "DAI", "USDT", "BUSD", "USDC"]
    )
    df["timeframe"] = pd.to_datetime(df["timeframe"])
    df.set_index("timeframe", inplace=True)

    return df.iloc[::-1]
