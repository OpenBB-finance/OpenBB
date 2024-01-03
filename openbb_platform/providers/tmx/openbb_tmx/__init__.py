"""TMX Provider Module."""

from openbb_core.provider.abstract.provider import Provider
from openbb_tmx.models.available_indices import TmxAvailableIndicesFetcher
from openbb_tmx.models.bond_prices import TmxBondPricesFetcher
from openbb_tmx.models.calendar_earnings import TmxCalendarEarningsFetcher
from openbb_tmx.models.company_filings import TmxCompanyFilingsFetcher
from openbb_tmx.models.company_news import TmxCompanyNewsFetcher
from openbb_tmx.models.equity_historical import TmxEquityHistoricalFetcher
from openbb_tmx.models.equity_profile import TmxEquityProfileFetcher
from openbb_tmx.models.equity_quote import TmxEquityQuoteFetcher
from openbb_tmx.models.equity_search import TmxEquitySearchFetcher
from openbb_tmx.models.etf_countries import TmxEtfCountriesFetcher
from openbb_tmx.models.etf_holdings import TmxEtfHoldingsFetcher
from openbb_tmx.models.etf_info import TmxEtfInfoFetcher
from openbb_tmx.models.etf_search import TmxEtfSearchFetcher
from openbb_tmx.models.etf_sectors import TmxEtfSectorsFetcher
from openbb_tmx.models.gainers import TmxGainersFetcher
from openbb_tmx.models.historical_dividends import TmxHistoricalDividendsFetcher
from openbb_tmx.models.index_constituents import TmxIndexConstituentsFetcher
from openbb_tmx.models.index_sectors import TmxIndexSectorsFetcher
from openbb_tmx.models.index_snapshots import TmxIndexSnapshotsFetcher
from openbb_tmx.models.insider_trading import TmxInsiderTradingFetcher
from openbb_tmx.models.options_chains import TmxOptionsChainsFetcher
from openbb_tmx.models.price_target_consensus import TmxPriceTargetConsensusFetcher
from openbb_tmx.models.treasury_prices import TmxTreasuryPricesFetcher

tmx_provider = Provider(
    name="tmx",
    website="https://www.tmx.com/",
    description="""Unofficial TMX Data Provider Extension
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
    fetcher_dict={
        "AvailableIndices": TmxAvailableIndicesFetcher,
        "BondPrices": TmxBondPricesFetcher,
        "CalendarEarnings": TmxCalendarEarningsFetcher,
        "CompanyFilings": TmxCompanyFilingsFetcher,
        "CompanyNews": TmxCompanyNewsFetcher,
        "EquityHistorical": TmxEquityHistoricalFetcher,
        "EquityInfo": TmxEquityProfileFetcher,
        "EquityQuote": TmxEquityQuoteFetcher,
        "EquitySearch": TmxEquitySearchFetcher,
        "EtfSearch": TmxEtfSearchFetcher,
        "EtfHoldings": TmxEtfHoldingsFetcher,
        "EtfSectors": TmxEtfSectorsFetcher,
        "EtfCountries": TmxEtfCountriesFetcher,
        "EtfInfo": TmxEtfInfoFetcher,
        "EquityGainers": TmxGainersFetcher,
        "HistoricalDividends": TmxHistoricalDividendsFetcher,
        "IndexConstituents": TmxIndexConstituentsFetcher,
        "IndexSectors": TmxIndexSectorsFetcher,
        "IndexSnapshots": TmxIndexSnapshotsFetcher,
        "InsiderTrading": TmxInsiderTradingFetcher,
        "OptionsChains": TmxOptionsChainsFetcher,
        "PriceTargetConsensus": TmxPriceTargetConsensusFetcher,
        "TreasuryPrices": TmxTreasuryPricesFetcher,
    },
)
