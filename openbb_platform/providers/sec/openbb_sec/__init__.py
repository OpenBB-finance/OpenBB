"""SEC provider module."""
from openbb_provider.abstract.provider import Provider
from openbb_sec.models.stock_ftd import SecStockFtdFetcher
from openbb_sec.models.stock_search import SecStockSearchFetcher

sec_provider = Provider(
    name="sec",
    website="https://sec.gov",
    description="SEC is the public listings regulatory body for the United States.",
    required_credentials=None,
    fetcher_dict={
        "StockFTD": SecStockFtdFetcher,
        "StockSearch": SecStockSearchFetcher,
    },
)
