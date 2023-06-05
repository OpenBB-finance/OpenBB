"""Token Terminal Model"""
import logging
from typing import Dict, List

import pandas as pd
from tokenterminal import TokenTerminal

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)

token_terminal = TokenTerminal(
    key=get_current_user().credentials.API_TOKEN_TERMINAL_KEY
)


# Fetch all data for projects'
try:
    PROJECTS_DATA = token_terminal.get_all_projects()

    # This is to catch the invalid header and raise Exception to load the autocomplete tickers
    if PROJECTS_DATA["message"] == "Invalid authorization header":
        raise Exception
except Exception:
    PROJECTS_DATA = [
        "0x",
        "1inch",
        "88mph",
        "aave",
        "abracadabra-money",
        "alchemist",
        "alchemix-finance",
        "algorand",
        "alpha-finance",
        "arweave",
        "autofarm",
        "avalanche",
        "axie-infinity",
        "balancer",
        "bancor",
        "barnbridge",
        "basket-dao",
        "benqi",
        "binance-smart-chain",
        "bitcoin",
        "cap",
        "cardano",
        "centrifuge",
        "clipper",
        "compound",
        "convex-finance",
        "cosmos",
        "cryptex",
        "curve",
        "decentral-games",
        "decred",
        "dforce",
        "dhedge",
        "dodo",
        "dogecoin",
        "dydx",
        "ellipsis-finance",
        "elrond",
        "enzyme-finance",
        "erasure-protocol",
        "ethereum",
        "ethereum-name-service",
        "euler",
        "fantom",
        "fei-protocol",
        "filecoin",
        "futureswap",
        "gmx",
        "goldfinch",
        "harvest-finance",
        "helium",
        "hurricaneswap",
        "idle-finance",
        "index-cooperative",
        "instadapp",
        "integral-protocol",
        "karura",
        "keeperdao",
        "keep-network",
        "kusama",
        "kyber",
        "lido-finance",
        "liquity",
        "litecoin",
        "livepeer",
        "looksrare",
        "loopring",
        "maiar",
        "makerdao",
        "maple-finance",
        "mcdex",
        "metamask",
        "mstable",
        "near-protocol",
        "nexus-mutual",
        "nftx",
        "notional-finance",
        "opensea",
        "optimism",
        "osmosis",
        "pancakeswap",
        "pangolin",
        "perpetual-protocol",
        "piedao",
        "pocket-network",
        "polkadot",
        "polygon",
        "polymarket",
        "pooltogether",
        "powerpool",
        "quickswap",
        "rarible",
        "rari-capital",
        "reflexer",
        "ren",
        "ribbon-finance",
        "rocket-pool",
        "saddle-finance",
        "set-protocol",
        "solana",
        "solend",
        "spookyswap",
        "stake-dao",
        "stellar",
        "sushiswap",
        "synthetix",
        "terra",
        "tezos",
        "the-graph",
        "thorchain",
        "tokemak",
        "tokenlon",
        "tornado-cash",
        "trader-joe",
        "uma",
        "uniswap",
        "unit-protocol",
        "venus",
        "vesper-finance",
        "volmex",
        "wakaswap",
        "yearn-finance",
        "yield-guild-games",
        "yield-yak",
        "zcash",
        "zora",
    ]

METRICS = [
    "twitter_followers",
    "gmv_annualized",
    "market_cap",
    "take_rate",
    "revenue",
    "revenue_protocol",
    "tvl",
    "pe",
    "pe_circulating",
    "ps",
    "ps_circulating",
]


@log_start_end(log=logger)
def get_possible_metrics() -> List[str]:
    """This function returns the available metrics.

    Returns
    -------
    List[str]
        A list with the available metrics values.
    """
    return METRICS


@log_start_end(log=logger)
def get_project_ids() -> List[str]:
    """This function returns the available project ids.

    Returns
    -------
    List[str]
        A list with the all the project IDs
    """

    # check if its a dict - which would be a successful api call -
    # might need to add error checking here later if they messed up the API key though.
    if isinstance(PROJECTS_DATA, dict):
        return [project["project_id"] for project in PROJECTS_DATA]
    return PROJECTS_DATA


@log_start_end(log=logger)
def get_fundamental_metric_from_project(
    metric: str,
    project: str,
) -> pd.Series:
    """Get fundamental metrics from a single project [Source: Token Terminal]

    Parameters
    ----------
    metric : str
        The metric of interest. See `get_possible_metrics()` for available metrics.
    project : str
        The project of interest. See `get_possible_projects()` for available categories.

    Returns
    -------
    pandas.Series:
        Date, Metric value
    """
    project_metrics = token_terminal.get_historical_metrics(project)

    metric_date = list()
    metric_value = list()
    for proj in project_metrics:
        if metric in proj:
            val = proj[metric]
            if isinstance(val, (float, int)):
                metric_value.append(val)
                metric_date.append(proj["datetime"])
        else:
            return pd.Series(dtype="float64")

    if metric_value:
        return pd.Series(index=pd.to_datetime(metric_date), data=metric_value)[::-1]

    return pd.Series(dtype="float64")


@log_start_end(log=logger)
def get_description(
    project: str,
) -> Dict:
    """Get description from a single project [Source: Token Terminal]

    Parameters
    ----------
    project : str
        The project of interest. See `get_possible_projects()` for available categories.

    Returns
    -------
    Dict[str, Any]
        Description of the project with fields: 'how', 'who', 'what', 'funding',
        'competition', 'business_model', 'github_contributors'
    """
    for p in PROJECTS_DATA:
        if p["project_id"] == project:
            return p["description"]

    return Dict()
