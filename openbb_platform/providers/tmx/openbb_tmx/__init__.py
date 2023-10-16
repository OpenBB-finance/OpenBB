"""TMX provider module."""

from openbb_provider.abstract.provider import Provider
from openbb_tmx.models.available_indices import TmxAvailableIndicesFetcher
from openbb_tmx.models.company_filings import TmxCompanyFilingsFetcher
from openbb_tmx.models.earnings_calendar import TmxEarningsCalendarFetcher
from openbb_tmx.models.etf_countries import TmxEtfCountriesFetcher
from openbb_tmx.models.etf_holdings import TmxEtfHoldingsFetcher
from openbb_tmx.models.etf_info import TmxEtfInfoFetcher
from openbb_tmx.models.etf_search import TmxEtfSearchFetcher
from openbb_tmx.models.etf_sectors import TmxEtfSectorsFetcher
from openbb_tmx.models.historical_dividends import TmxHistoricalDividendsFetcher
from openbb_tmx.models.index_constituents import TmxIndexConstituentsFetcher
from openbb_tmx.models.index_info import TmxIndexInfoFetcher
from openbb_tmx.models.price_target_consensus import TmxPriceTargetConsensusFetcher
from openbb_tmx.models.stock_info import TmxStockInfoFetcher
from openbb_tmx.models.stock_insider_activity import TmxStockInsiderActivityFetcher
from openbb_tmx.models.stock_news import TmxStockNewsFetcher
from openbb_tmx.models.stock_search import TmxStockSearchFetcher

tmx_provider = Provider(
    name="tmx",
    website="https://www.tmx.com/",
    description="""
        TMX Group Companies
         - Toronto Stock Exchange
         - TSX Venture Exchange
         - TSX Trust
         - Montréal Exchange
         - TSX Alpha Exchange
         - Shorcan
         - CDCC
         - CDS
         - TMX Datalinx
         - Trayport
    """,
    required_credentials=None,
    fetcher_dict={
        "AvailableIndices": TmxAvailableIndicesFetcher,
        "CompanyFilings": TmxCompanyFilingsFetcher,
        "EarningsCalendar": TmxEarningsCalendarFetcher,
        "EtfSearch": TmxEtfSearchFetcher,
        "EtfHoldings": TmxEtfHoldingsFetcher,
        "EtfSectors": TmxEtfSectorsFetcher,
        "EtfCountries": TmxEtfCountriesFetcher,
        "EtfInfo": TmxEtfInfoFetcher,
        "HistoricalDividends": TmxHistoricalDividendsFetcher,
        "IndexConstituents": TmxIndexConstituentsFetcher,
        "IndexInfo": TmxIndexInfoFetcher,
        "PriceTargetConsensus": TmxPriceTargetConsensusFetcher,
        "StockInfo": TmxStockInfoFetcher,
        "StockInsiderTrading": TmxStockInsiderActivityFetcher,
        "StockNews": TmxStockNewsFetcher,
        "StockSearch": TmxStockSearchFetcher,
    },
)
