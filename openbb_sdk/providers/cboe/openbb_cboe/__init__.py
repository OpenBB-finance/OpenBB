"""cboe provider module."""
from openbb_provider.abstract.provider import Provider

from openbb_cboe.models.company_search import CboeCompanySearchFetcher
from openbb_cboe.models.options_chains import CboeOptionsChainsFetcher
from openbb_cboe.models.stock_eod import CboeStockEODFetcher
from openbb_cboe.models.stock_info import CboeStockInfoFetcher

cboe_provider = Provider(
    name="cboe",
    website="https://www.cboe.com/",
    description="""Provider for CBOE.""",
    required_credentials=None,
    fetcher_dict={
        "CompanySearch": CboeCompanySearchFetcher,
        "OptionsChains": CboeOptionsChainsFetcher,
        "StockEOD": CboeStockEODFetcher,
        "StockInfo": CboeStockInfoFetcher,
    },
)
