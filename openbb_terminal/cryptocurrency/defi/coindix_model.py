"""Coindix model"""
__docformat__ = "numpy"

import logging
from typing import Optional

import pandas as pd
import urllib3

from openbb_terminal import rich_config
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    get_user_agent,
    lambda_long_number_format,
    request,
)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

VAULTS_FILTERS = ["name", "chain", "protocol", "apy", "tvl", "link"]
CHAINS = [
    "ethereum",
    "polygon",
    "avalanche",
    "bsc",
    "terra",
    "fantom",
    "moonriver",
    "celo",
    "heco",
    "okex",
    "cronos",
    "arbitrum",
    "eth",
    "harmony",
    "fuse",
    "defichain",
    "solana",
    "optimism",
    "kusama",
    "metis",
    "osmosis",
]
PROTOCOLS = [
    "aave",
    "acryptos",
    "alpaca",
    "anchor",
    "autofarm",
    "balancer",
    "bancor",
    "beefy",
    "belt",
    "compound",
    "convex",
    "cream",
    "curve",
    "defichain",
    "geist",
    "lido",
    "liquity",
    "mirror",
    "pancakeswap",
    "raydium",
    "sushi",
    "tarot",
    "traderjoe",
    "tulip",
    "ubeswap",
    "uniswap",
    "venus",
    "yearn",
    "osmosis",
    "tulip",
]
VAULT_KINDS = [
    "lp",
    "single",
    "noimploss",
    "stable",
]


@log_start_end(log=logger)
def _prepare_params(**kwargs) -> dict:
    """Helper method, which handles preparation of parameters for requests to coindix api.

    Parameters
    ----------
    kwargs: keyword arguments: chain, kind, protocol

    Returns
    -------
    dict:
        Prepared parameters for request
    """

    params = {"sort": "-apy", "tvl": "1m", "kind": "all"}
    mapping = {"chain": CHAINS, "protocol": PROTOCOLS, "kind": VAULT_KINDS}
    for key, value in kwargs.items():
        category = mapping.get(key, [])
        if value in category:
            params.update({key: value})
    return {k: v.lower() for k, v in params.items()}


@log_start_end(log=logger)
def get_defi_vaults(
    chain: Optional[str] = None,
    protocol: Optional[str] = None,
    kind: Optional[str] = None,
    ascend: bool = True,
    sortby: str = "apy",
) -> pd.DataFrame:
    """Get DeFi Vaults Information. DeFi Vaults are pools of funds with an assigned strategy which main goal is to
    maximize returns of its crypto assets. [Source: https://coindix.com/]

    Parameters
    ----------
    chain: str
        Blockchain - one from list [
        'ethereum', 'polygon', 'avalanche', 'bsc', 'terra', 'fantom',
        'moonriver', 'celo', 'heco', 'okex', 'cronos', 'arbitrum', 'eth',
        'harmony', 'fuse', 'defichain', 'solana', 'optimism'
        ]
    protocol: str
        DeFi protocol - one from list: [
        'aave', 'acryptos', 'alpaca', 'anchor', 'autofarm', 'balancer', 'bancor',
        'beefy', 'belt', 'compound', 'convex', 'cream', 'curve', 'defichain', 'geist',
        'lido', 'liquity', 'mirror', 'pancakeswap', 'raydium', 'sushi', 'tarot', 'traderjoe',
        'tulip', 'ubeswap', 'uniswap', 'venus', 'yearn'
        ]
    kind: str
        Kind/type of vault - one from list: ['lp','single','noimploss','stable']

    Returns
    -------
    pd.DataFrame
        Top 100 DeFi Vaults for given chain/protocol sorted by APY.
    """

    headers = {"User-Agent": get_user_agent()}
    params = _prepare_params(chain=chain, protocol=protocol, kind=kind)
    response = request(
        "https://apiv2.coindix.com/search", headers=headers, params=params, verify=False
    )
    if not 200 <= response.status_code < 300:
        raise Exception(f"Coindix api exception: {response.text}")

    try:
        data = response.json()["data"]
        if len(data) == 0:
            return pd.DataFrame()
        df = pd.DataFrame(data)[VAULTS_FILTERS]
    except Exception as e:
        logger.exception(e)
        raise ValueError(f"Invalid Response: {response.text}") from e

    df = df.sort_values(by=sortby, ascending=ascend).fillna("NA")

    if rich_config.USE_COLOR and not get_current_user().preferences.USE_INTERACTIVE_DF:
        df["tvl"] = df["tvl"].apply(lambda x: lambda_long_number_format(x))
        df["apy"] = df["apy"].apply(
            lambda x: f"{str(round(x * 100, 2))} %"
            if isinstance(x, (int, float))
            else x
        )

    df.columns = [x.title() for x in df.columns]
    df.rename(columns={"Apy": "APY (%)", "Tvl": "TVL ($)"}, inplace=True)
    return df
