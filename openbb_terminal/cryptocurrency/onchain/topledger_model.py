"""Topledger model"""
__docformat__ = "numpy"

import logging
from typing import Any, Dict, Optional, Tuple

import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

MAPPING: Dict[str, Any] = {
    "tensor": {
        "api_key": "8eSjJnSuOC7uLWkrTQoWADStkNS2ZIy94pH5CsNn",
        "tl_org_slug": "tensor",
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
    },
    "genopets": {
        "api_key": "67F9IFzXma0iusqMAb2VynopTfHqzri2zTeacQnh",
        "tl_org_slug": "genopets",
        "queries": [
            {"id": 1206, "slug": "daily-users"},
            {"id": 1207, "slug": "weekly-users"},
            {"id": 1208, "slug": "monthly-users"},
            {"id": 1209, "slug": "weekly-retention"},
            {"id": 1210, "slug": "monthly-retention"},
            {"id": 1214, "slug": "daily-transactions"},
            {"id": 1215, "slug": "weekly-transactions"},
            {"id": 1216, "slug": "monthly-transactions"},
            {"id": 1221, "slug": "daily-$ki-volume"},
            {"id": 1222, "slug": "weekly-$ki-volume"},
            {"id": 1223, "slug": "monthly-$ki-volume"},
            {"id": 1224, "slug": "daily-$gene-volume"},
            {"id": 1225, "slug": "weekly-$gene-volume"},
            {"id": 1226, "slug": "monthly-$gene-volume"},
            {"id": 1229, "slug": "ghmp-daily-instruction-type-split"},
            {"id": 1230, "slug": "ghmp-weekly-instruction-type-split"},
            {"id": 1231, "slug": "ghmp-monthly-instruction-type-split"},
            {"id": 1234, "slug": "gcmp-daily-instruction-type-split"},
            {"id": 1235, "slug": "gcmp-weekly-instruction-type-split"},
            {"id": 1236, "slug": "gcmp-monthly-instruction-type-split"},
            {"id": 1238, "slug": "gsp-daily-instruction-type-split"},
            {"id": 1239, "slug": "gsp-weekly-instruction-type-split"},
            {"id": 1242, "slug": "harvestki-daily"},
            {"id": 1245, "slug": "withdrawki-daily"},
        ],
    },
    "staratlas": {
        "api_key": "l8Q9sOseZRAoFVqvTExxWJ8W9j4ETySHiDFGIHg3",
        "tl_org_slug": "staratlas",
        "queries": [
            {"id": 1033, "slug": "daily-users"},
            {"id": 1026, "slug": "weekly-users"},
            {"id": 1040, "slug": "monthly-users"},
            {"id": 1048, "slug": "weekly-retention"},
            {"id": 1051, "slug": "monthly-retention"},
            {"id": 1049, "slug": "daily-transactions"},
            {"id": 1034, "slug": "weekly-transactions"},
            {"id": 1043, "slug": "monthly-transactions"},
            {"id": 1056, "slug": "ssp-daily-instruction-type-split"},
            {"id": 1058, "slug": "ssp-weekly-instruction-type-split"},
            {"id": 1037, "slug": "ssp-monthly-instruction-type-split"},
            {"id": 1059, "slug": "daily-process-harvest-atlas-volume"},
            {"id": 1036, "slug": "weekly-process-harvest-atlas-volume"},
            {"id": 1039, "slug": "monthly-process-harvest-atlas-volume"},
            {"id": 1038, "slug": "daily-gas-fee"},
            {"id": 1046, "slug": "weekly-gas-fee"},
            {"id": 1027, "slug": "monthly-gas-fee"},
        ],
    },
    "aurory": {
        "api_key": "LzJODEsQnkySsqbCoRxPqj8KuN5x8SGK3AESatgm",
        "tl_org_slug": "aurory",
        "queries": [
            {"id": 1147, "slug": "daily-users"},
            {"id": 1132, "slug": "weekly-users"},
            {"id": 1127, "slug": "monthly-users"},
            {"id": 1166, "slug": "weekly-retention"},
            {"id": 1135, "slug": "monthly-retention"},
            {"id": 1143, "slug": "daily-transactions"},
            {"id": 1153, "slug": "weekly-transactions"},
            {"id": 1160, "slug": "monthly-transactions"},
            {"id": 1149, "slug": "daily-aury-volume"},
            {"id": 1165, "slug": "weekly-aury-volume"},
            {"id": 1152, "slug": "monthly-aury-volume"},
            {"id": 1151, "slug": "daily-xaury-volume"},
            {"id": 1150, "slug": "weekly-xaury-volume"},
            {"id": 1152, "slug": "monthly-xaury-volume"},
        ],
    },
    "sol_casino": {
        "api_key": "biEGK5IM7ciI3GCOJ0QJVrHWHMYflGsAcfcCixcP",
        "tl_org_slug": "tl",
        "queries": [
            {"id": 1468, "slug": "daily-transactions"},
            {"id": 1471, "slug": "weekly-transactions"},
            {"id": 1473, "slug": "monthly-transactions"},
            {"id": 1481, "slug": "daily-active-wallets"},
            {"id": 1482, "slug": "weekly-active-wallets"},
            {"id": 1483, "slug": "monthly-active-wallets"},
            {"id": 1505, "slug": "daily-volume"},
            {"id": 1485, "slug": "daily-sol-deposits"},
            {"id": 1486, "slug": "daily-usdc-usdt-deposits"},
            {"id": 1488, "slug": "daily-bonk-deposits"},
        ],
    },
    "exchange_art": {
        "api_key": "biEGK5IM7ciI3GCOJ0QJVrHWHMYflGsAcfcCixcP",
        "tl_org_slug": "tl",
        "queries": [
            {"id": 1331, "slug": "daily-transactions"},
            {"id": 1332, "slug": "weekly-transactions"},
            {"id": 1333, "slug": "monthly-transactions"},
            {"id": 1334, "slug": "daily-transaction-fee"},
            {"id": 1335, "slug": "daily-users"},
            {"id": 1336, "slug": "weekly-users"},
            {"id": 1337, "slug": "monthly-users"},
            {"id": 1338, "slug": "daily-transactions-by-programs"},
            {"id": 1339, "slug": "weekly-transactions-by-programs"},
            {"id": 1340, "slug": "monthly-transactions-by-programs"},
            {"id": 1349, "slug": "daily-new-users"},
            {"id": 1358, "slug": "weekly-new-users"},
            {"id": 1359, "slug": "monthly-new-users"},
            {"id": 1367, "slug": "daily-bids-placed"},
            {"id": 1371, "slug": "daily-finearts-listed"},
            {"id": 1418, "slug": "daily-primary-gmv"},
            {"id": 1422, "slug": "weekly-primary-gmv"},
            {"id": 1423, "slug": "monthly-primary-gmv"},
            {"id": 1427, "slug": "daily-secondary-gmv"},
            {"id": 1428, "slug": "weekly-secondary-gmv"},
            {"id": 1429, "slug": "monthly-secondary-gmv"},
        ],
    },
    "xNFT_Backpack": {
        "api_key": "biEGK5IM7ciI3GCOJ0QJVrHWHMYflGsAcfcCixcP",
        "tl_org_slug": "tl",
        "queries": [
            {"id": 2318, "slug": "xnft-installed"},
            {"id": 1738, "slug": "daily-xnft-installed"},
            {"id": 1736, "slug": "daily-xnft-users"},
            {"id": 1760, "slug": "xnft-by-tag"},
            {"id": 1762, "slug": "xnft-by-rating"},
            {"id": 2320, "slug": "top20-users-by-nft-installs"},
            {"id": 1764, "slug": "mad-lad-nft"},
            {"id": 1757, "slug": "users-by-xnft"},
            {"id": 1731, "slug": "cumulative-xnft-installed"},
        ],
    },
    "bonk": {
        "api_key": "biEGK5IM7ciI3GCOJ0QJVrHWHMYflGsAcfcCixcP",
        "tl_org_slug": "tl",
        "queries": [
            {"id": 486, "slug": "bonk-transaction-fee"},
            {"id": 506, "slug": "daily-bonk-burn"},
            {"id": 507, "slug": "top-100-accounts-burning-bonk"},
            {"id": 477, "slug": "daily-active-users"},
            {"id": 488, "slug": "user-split-by-pools"},
            {"id": 479, "slug": "bonk-transactions"},
            {"id": 487, "slug": "transactions-split-by-pools"},
            {"id": 514, "slug": "bonk-volume-usd"},
            {"id": 483, "slug": "bonk-volume"},
            {"id": 509, "slug": "bonk-holders"},
            {"id": 484, "slug": "top-100-bonk-holders"},
            {"id": 485, "slug": "top-wallets-by-transactions"},
            {"id": 492, "slug": "daily-users-split-by-dex"},
        ],
    },
    "light_protocol": {
        "api_key": "De2qJPBJKt19Yh24Z2n6kezIlaEBA4UYkBBjdbXn",
        "tl_org_slug": "luminouslabs",
        "queries": [
            {"id": 1846, "slug": "hourly-transactions"},
            {"id": 1506, "slug": "daily-transactions"},
            {"id": 1690, "slug": "weekly-transactions"},
            {"id": 1691, "slug": "monthly-transaction"},
            {"id": 1692, "slug": "daily-fee"},
            {"id": 1697, "slug": "daily-shielded-and-unshielded-volume"},
            {"id": 1699, "slug": "weekly-shielded-and-unshielded-volume"},
            {"id": 1700, "slug": "monthly-shielded-and-unshielded-volume"},
            {"id": 1701, "slug": "shielded-and-unshielded-transactions-by-wallets"},
        ],
    },
}


@log_start_end(log=logger)
def make_request(org_slug="", query_slug="") -> Tuple[Optional[int], Any]:
    """Helper methods for requests to topledger's query results [Source: Topledger]

    Parameters
    ----------
    org_slug: str
        Organization Slug
    query_slug: str
        Query Slug

    Returns
    -------
    Tuple[Optional[int], Any]
        status code, response from api request
    """
    org = MAPPING[org_slug]
    if not org:
        console.print(f"[red]Organization Slug[{org_slug}] is invalid[/red]\n")
        logger.error("Organization Slug[%s] is invalid", org_slug)
        return None, None

    query_items = [x for x in org["queries"] if x["slug"] == query_slug]
    if len(query_items) == 0:
        console.print(
            f"[red]Query Slug[{query_slug}] is invalid for Organization[{org_slug}][/red]\n"
        )
        logger.error(
            "Query Slug[%s] is invalid for Organization[%s]", query_slug, org_slug
        )
        return None, None

    query = query_items[0]
    query_id = query["id"]
    api_key = org["api_key"]
    tl_org_slug = org["tl_org_slug"]

    # """
    # API Documentation
    # ----------
    # :param string tl_org_slug: Slug of Topledger Organization
    # :param string query_id: the ID of the query to fetch result of
    # :param string api_key: Authentication Key to fetch result
    #
    # API Format: HOST/<tl_org_slug>/api/queries/<query_id>/results.json?api_key=<api_key>
    # """

    url = f"https://analytics.topledger.xyz/{tl_org_slug}/api/queries/{query_id}/results.json?api_key={api_key}"
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
def get_topledger_data(org_slug: str, query_slug: str) -> pd.DataFrame:
    """Returns Topledger's Data for the given Organization's Slug[org_slug] based
    on Query Slug[query_slug] [Source: Topledger]

    Parameters
    ----------
    org_slug: str
        Organization Slug
    query_slug: str
        Query Slug

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
