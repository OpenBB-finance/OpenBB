"""DeFiLlama provider module."""

from openbb_core.provider.abstract.provider import Provider
from openbb_defillama.models.tvl_chains import DeFiLlamaTvlChainsFetcher
from openbb_defillama.models.tvl_current import DeFiLlamaTvlCurrentFetcher
from openbb_defillama.models.tvl_historical import DeFiLlamaTvlHistoricalFetcher
from openbb_defillama.models.yields_pools import DeFiLlamaYieldsPoolsFetcher
from openbb_defillama.models.yields_historical import DeFiLlamaYieldsHistoricalFetcher
from openbb_defillama.models.fees_overview import DeFiLlamaFeesOverviewFetcher
from openbb_defillama.models.fees_summary import DeFiLlamaFeesSummaryFetcher

defillama_provider = Provider(
    name="defillama",
    website="https://defillama.com",
    description="DeFiLlama is the largest TVL aggregator for DeFi (Decentralized Finance).",
    credentials=None,
    fetcher_dict={
        "TvlChains": DeFiLlamaTvlChainsFetcher,
        "TvlCurrent": DeFiLlamaTvlCurrentFetcher,
        "TvlHistorical": DeFiLlamaTvlHistoricalFetcher,
        "YieldsPools": DeFiLlamaYieldsPoolsFetcher,
        "YieldsHistorical": DeFiLlamaYieldsHistoricalFetcher,
        "FeesOverview": DeFiLlamaFeesOverviewFetcher,
        "FeesSummary": DeFiLlamaFeesSummaryFetcher,
    },
    repr_name="DeFiLlama",
)
