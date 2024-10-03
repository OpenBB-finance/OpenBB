"""DeFiLlama provider module."""

from openbb_core.provider.abstract.provider import Provider
from openbb_defillama.models.tvl_chains import DeFiLlamaTvlChainsFetcher

defillama_provider = Provider(
    name="defillama",
    website="https://defillama.com",
    description="DeFiLlama is the largest TVL aggregator for DeFi (Decentralized Finance).",
    credentials=None,
    fetcher_dict={
        "TvlChains": DeFiLlamaTvlChainsFetcher,
    },
    repr_name="DeFiLlama",
)
