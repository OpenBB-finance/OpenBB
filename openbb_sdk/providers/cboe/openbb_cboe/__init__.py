"""CBOE provider module."""


from openbb_provider.abstract.provider import Provider

from openbb_cboe.models.options_chains import CboeOptionsChainsFetcher
from openbb_cboe.models.stock_eod import CboeStockEODFetcher
from openbb_cboe.models.stock_info import CboeStockInfoFetcher
from openbb_cboe.models.stock_search import CboeStockSearchFetcher

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
        "StockEOD": CboeStockEODFetcher,
        "StockInfo": CboeStockInfoFetcher,
    },
)
