"""DeFiLlama provider module."""

from openbb_core.provider.abstract.provider import Provider
from openbb_defillama.models.coins_change import DeFiLlamaCoinsChangeFetcher
from openbb_defillama.models.coins_chart import DeFiLlamaCoinsChartFetcher
from openbb_defillama.models.coins_current import DeFiLlamaCoinsCurrentFetcher
from openbb_defillama.models.coins_first import DeFiLlamaCoinsFirstFetcher
from openbb_defillama.models.fees_overview import DeFiLlamaFeesOverviewFetcher
from openbb_defillama.models.fees_summary import DeFiLlamaFeesSummaryFetcher
from openbb_defillama.models.revenue_overview import DeFiLlamaRevenueOverviewFetcher
from openbb_defillama.models.revenue_summary import DeFiLlamaRevenueSummaryFetcher
from openbb_defillama.models.tvl_chains import DeFiLlamaTvlChainsFetcher
from openbb_defillama.models.tvl_current import DeFiLlamaTvlCurrentFetcher
from openbb_defillama.models.tvl_historical import DeFiLlamaTvlHistoricalFetcher
from openbb_defillama.models.volumes_overview import DeFiLlamaVolumesOverviewFetcher
from openbb_defillama.models.volumes_summary import DeFiLlamaVolumesSummaryFetcher
from openbb_defillama.models.yields_historical import DeFiLlamaYieldsHistoricalFetcher
from openbb_defillama.models.yields_pools import DeFiLlamaYieldsPoolsFetcher

from openbb_platform.providers.defillama.openbb_defillama.models.coins_block_timestamp import (
    DeFiLlamaCoinsBlockTimestampFetcher,
)

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
        "RevenueOverview": DeFiLlamaRevenueOverviewFetcher,
        "RevenueSummary": DeFiLlamaRevenueSummaryFetcher,
        "VolumesOverview": DeFiLlamaVolumesOverviewFetcher,
        "VolumesSummary": DeFiLlamaVolumesSummaryFetcher,
        "BlockTimestamp": DeFiLlamaCoinsBlockTimestampFetcher,
        "CoinsCurrent": DeFiLlamaCoinsCurrentFetcher,
        "CoinsFirst": DeFiLlamaCoinsFirstFetcher,
        "CoinsChange": DeFiLlamaCoinsChangeFetcher,
        "CoinsChart": DeFiLlamaCoinsChartFetcher,
    },
    repr_name="DeFiLlama",
)
