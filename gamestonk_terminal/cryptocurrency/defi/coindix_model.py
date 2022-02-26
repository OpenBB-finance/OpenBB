"""Coindix model"""
__docformat__ = "numpy"

import logging
from typing import Optional

import pandas as pd
import requests

from gamestonk_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)

VAULTS_FILTERS = ["name", "chain", "protocol", "apy", "tvl", "risk", "link"]
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
]
VAULT_KINDS = [
    "lp",
    "single",
    "noimploss",
    "stable",
]


def _lambda_risk_mapper(risk_level: int) -> str:
    """Helper methods
    Parameters
    ----------
    risk_level: int
        number from range 0-4 represents risk factor for given vault
    Returns
    -------
    string:
        text representation of risk
    """

    mappings = {0: "Non Eligible", 1: "Least", 2: "Low", 3: "Medium", 4: "High"}
    return mappings.get(risk_level, "Non Eligible")


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

    params = _prepare_params(chain=chain, protocol=protocol, kind=kind)
    response = requests.get("https://apiv2.coindix.com/search", params=params)
    if not 200 <= response.status_code < 300:
        raise Exception(f"Coindix api exception: {response.text}")

    try:
        data = response.json()["data"]
        if len(data) == 0:
            return pd.DataFrame()
        df = pd.DataFrame(data)[VAULTS_FILTERS].fillna("NA")
        df["risk"] = df["risk"].apply(lambda x: _lambda_risk_mapper(x))
        return df
    except Exception as e:
        logger.exception(e)
        raise ValueError(f"Invalid Response: {response.text}") from e
