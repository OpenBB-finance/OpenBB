"""Pyth Provider Module."""


from openbb_core.provider.abstract.provider import Provider
from openbb_fmp import fmp_provider
from openbb_providers.models.cftc import CommitmentOfTradersAnalysisFetcher
from openbb_providers.models.cftc_contracts import  CommitmentOfTradersReportFetcher
from openbb_providers.models.fmp_marketcap import FMPMarketCapDataFetcher
from openbb_providers.models.seekingalpha import SADividendPicksFetcher, SAStockIdeaFetcher
from openbb_providers.models.cramer import CramerFetcher
from openbb_providers.models.finviz import FinvizCanslimFetcher

cramer_provider = Provider(
    name="cramer_provider",
    website="https://pyth.network/",
    description=(
        "Provider for fetching Jim Cramer recommendations."
    ),
    fetcher_dict={
        'CramerRecommendations' : CramerFetcher,
    }
)

