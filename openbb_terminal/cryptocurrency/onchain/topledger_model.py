"""Topledger model"""
__docformat__ = "numpy"

import logging
from typing import Any, Optional, Tuple

import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

MAPPING = {
    "tensor": {
        "api_key": "8eSjJnSuOC7uLWkrTQoWADStkNS2ZIy94pH5CsNn",
        "queries": [
            {"id": 846, "slug": "daily-transactions"},
            {"id": 847, "slug": "weekly-transactions"},
            {"id": 848, "slug": "monthly-transactions"},
            {"id": 849, "slug": "daily-users"},
            {"id": 852, "slug": "monthly-users"},
            {"id": 851, "slug": "weekly-users"},
            {"id": 1092, "slug": "daily-gmv-sol"},
            {"id": 1104, "slug": "weekly-gmv"},
            {"id": 1105, "slug": "monthly-gmv"},
            {"id": 1110, "slug": "daily-tvl"},
            {"id": 1111, "slug": "weekly-tvl"},
            {"id": 1112, "slug": "monthly-tvl"},
            {"id": 1115, "slug": "top-traders-by-gmv"},
        ],
    }
}


@log_start_end(log=logger)
def make_request(org_slug=None, query_slug=None) -> Tuple[Optional[int], Any]:
    org = MAPPING[org_slug]
    if not org:
        return None, None

    api_key = org["api_key"]
    query_items = [x for x in org["queries"] if x["slug"] == query_slug]
    if len(query_items) == 0:
        return None, None

    query = query_items[0]
    query_id = query["id"]

    url = f"https://analytics.topledger.xyz/{org_slug}/api/queries/{query_id}/results.json?api_key={api_key}"
    try:
        response = request(url)
    except Exception:
        return None, None

    result = {}

    if response.status_code == 200:
        result = response.json()
    elif response.status_code == 401:
        console.print("[red]Invalid API Key[/red]\n")
        logger.error("Invalid Authentication: %s", response.text)
    elif response.status_code == 401:
        console.print("[red]API Key not authorized[/red]\n")
        logger.error("Insufficient Authorization: %s", response.text)
    elif response.status_code == 429:
        console.print("[red]Exceeded number of calls per minute[/red]\n")
        logger.error("Calls limit exceeded: %s", response.text)
    else:
        console.print(response.json()["message"])
        logger.error("Error in request: %s", response.text)

    return response.status_code, result


@log_start_end(log=logger)
def get_topledger_data(org_slug: str = None, query_slug: str = None) -> pd.DataFrame:
    """Returns Topledger Data for org_slug for given query_slug [Source: https://api.blockchain.info/]

    Returns
    -------
    pd.DataFrame
        Topledger Data
    """

    if not org_slug:
        console.print("[red]Org is blank[/red]\n")
        logger.error("Org is blank")
        return pd.DataFrame()

    if not query_slug:
        console.print("[red]Query is blank[/red]\n")
        logger.error("Query is blank")
        return pd.DataFrame()

    status_code, response = make_request(org_slug, query_slug)
    if status_code != 200:
        return pd.DataFrame()

    data = pd.json_normalize(response["query_result"]["data"]["rows"])
    return pd.DataFrame(data)
