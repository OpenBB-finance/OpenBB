"""Token Terminal Model"""
import logging
from typing import List

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
except Exception as e:
    logger.error(e)
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

TIMELINES = ["24h", "7d", "30d", "90d", "180d", "365d"]

CATEGORIES = [
    "Asset Management",
    "Blockchain",
    "DeFi",
    "Exchange",
    "Gaming",
    "Insurance",
    "Interoperability",
    "Lending",
    "NFT",
    "Other",
    "Prediction Market",
    "Stablecoin",
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
def get_possible_timelines() -> List[str]:
    """This function returns the available timelines.

    Returns
    -------
    List[str]
        A list with the available timelines values.
    """
    return TIMELINES


@log_start_end(log=logger)
def get_possible_categories() -> List[str]:
    """This function returns the available categories.

    Returns
    -------
    List[str]
        A list with the available categories values.
    """
    return CATEGORIES


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
def get_fundamental_metrics(
    metric: str,
    category: str = "",
    timeline: str = "24h",
    ascend: bool = False,
) -> pd.Series:
    """Get fundamental metrics [Source: Token Terminal]

    Parameters
    ----------
    metric : str
        The metric of interest. See `get_possible_metrics()` for available metrics.
    category : str
        The category of interest. See `get_possible_categories()` for available categories.
        The default value is an empty string which means that all categories are considered.
    timeline : str
        The category of interest. See `get_possible_timelines()` for available timelines.
    ascend : bool
        Direction of the sort. If True, the data is sorted in ascending order.

    Returns
    -------
    pd.Series
        Project, Metric value
    """
    metric_values = {}
    for project in PROJECTS_DATA:
        if category and (
            (
                "," in project["category_tags"]
                and category in project["category_tags"].split(",")
            )
            or project["category_tags"] == category
        ):
            # check that is in metrics with a timeline
            if metric in [
                "revenue",
                "revenue_protocol",
                "tvl",
                "pe",
                "pe_circulating",
                "ps",
                "ps_circulating",
            ]:
                val = project[metric + "_" + timeline]
            else:
                val = project[metric]
            if isinstance(val, (float, int)):
                if project["symbol"]:
                    metric_values[f"{project['name']} ({project['symbol']})"] = float(
                        val
                    )
                else:
                    metric_values[f"{project['name']}"] = float(val)

        else:
            # check that is in metrics with a timeline
            if metric in [
                "revenue",
                "revenue_protocol",
                "tvl",
                "pe",
                "pe_circulating",
                "ps",
                "ps_circulating",
            ]:
                val = project[metric + "_" + timeline]
            else:
                val = project[metric]
            if isinstance(val, (float, int)):
                if project["symbol"]:
                    metric_values[f"{project['name']} ({project['symbol']})"] = float(
                        val
                    )
                else:
                    metric_values[f"{project['name']}"] = float(val)

    metric_values = dict(
        sorted(metric_values.items(), key=lambda item: item[1], reverse=not ascend)
    )

    return pd.Series(metric_values)
