"""CBOE provider module."""


from openbb_cboe.models.available_indices import CboeAvailableIndicesFetcher
from openbb_cboe.models.european_index_constituents import (
    CboeEuropeanIndexConstituentsFetcher,
)
from openbb_cboe.models.european_index_historical import (
    CboeEuropeanIndexHistoricalFetcher,
)
from openbb_cboe.models.futures_curve import CboeFuturesCurveFetcher
from openbb_cboe.models.index_search import CboeIndexSearchFetcher
from openbb_cboe.models.index_snapshots import CboeIndexSnapshotsFetcher
from openbb_cboe.models.major_indices_historical import (
    CboeMajorIndicesHistoricalFetcher,
)
from openbb_cboe.models.options_chains import CboeOptionsChainsFetcher
from openbb_cboe.models.stock_historical import CboeStockHistoricalFetcher
from openbb_cboe.models.stock_info import CboeStockInfoFetcher
from openbb_cboe.models.stock_search import CboeStockSearchFetcher
from openbb_provider.abstract.provider import Provider

cboe_provider = Provider(
    name="cboe",
    website="https://www.cboe.com/",
    description="""Cboe is the world's go-to derivatives and exchange network,
     delivering cutting-edge trading, clearing and investment solutions to people
     around the world.""",
    required_credentials=None,
    fetcher_dict={
        "StockSearch": CboeStockSearchFetcher,
        "OptionsChains": CboeOptionsChainsFetcher,
        "StockHistorical": CboeStockHistoricalFetcher,
        "StockInfo": CboeStockInfoFetcher,
        "FuturesCurve": CboeFuturesCurveFetcher,
        "AvailableIndices": CboeAvailableIndicesFetcher,
        "EuropeanIndexConstituents": CboeEuropeanIndexConstituentsFetcher,
        "EuropeanIndexHistorical": CboeEuropeanIndexHistoricalFetcher,
        "MajorIndicesHistorical": CboeMajorIndicesHistoricalFetcher,
        "IndexSearch": CboeIndexSearchFetcher,
        "IndexSnapshots": CboeIndexSnapshotsFetcher,
    },
)
