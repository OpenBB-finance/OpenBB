"""Intrinio Provider Modules."""

from openbb_core.provider.abstract.provider import Provider
from openbb_intrinio.models.balance_sheet import IntrinioBalanceSheetFetcher
from openbb_intrinio.models.calendar_ipo import IntrinioCalendarIpoFetcher
from openbb_intrinio.models.cash_flow import IntrinioCashFlowStatementFetcher
from openbb_intrinio.models.company_filings import IntrinioCompanyFilingsFetcher
from openbb_intrinio.models.company_news import IntrinioCompanyNewsFetcher
from openbb_intrinio.models.currency_pairs import IntrinioCurrencyPairsFetcher
from openbb_intrinio.models.equity_historical import IntrinioEquityHistoricalFetcher
from openbb_intrinio.models.equity_info import IntrinioEquityInfoFetcher
from openbb_intrinio.models.equity_quote import IntrinioEquityQuoteFetcher
from openbb_intrinio.models.equity_search import IntrinioEquitySearchFetcher
from openbb_intrinio.models.financial_ratios import IntrinioFinancialRatiosFetcher
from openbb_intrinio.models.fred_series import IntrinioFredSeriesFetcher
from openbb_intrinio.models.historical_attributes import (
    IntrinioHistoricalAttributesFetcher,
)
from openbb_intrinio.models.historical_dividends import (
    IntrinioHistoricalDividendsFetcher,
)
from openbb_intrinio.models.income_statement import IntrinioIncomeStatementFetcher
from openbb_intrinio.models.index_historical import IntrinioIndexHistoricalFetcher
from openbb_intrinio.models.insider_trading import IntrinioInsiderTradingFetcher
from openbb_intrinio.models.institutional_ownership import (
    IntrinioInstitutionalOwnershipFetcher,
)
from openbb_intrinio.models.key_metrics import IntrinioKeyMetricsFetcher
from openbb_intrinio.models.latest_attributes import IntrinioLatestAttributesFetcher
from openbb_intrinio.models.market_indices import IntrinioMarketIndicesFetcher
from openbb_intrinio.models.options_chains import IntrinioOptionsChainsFetcher
from openbb_intrinio.models.options_unusual import IntrinioOptionsUnusualFetcher
from openbb_intrinio.models.reported_financials import IntrinioReportedFinancialsFetcher
from openbb_intrinio.models.search_attributes import (
    IntrinioSearchAttributesFetcher,
)
from openbb_intrinio.models.share_statistics import IntrinioShareStatisticsFetcher
from openbb_intrinio.models.world_news import IntrinioWorldNewsFetcher

intrinio_provider = Provider(
    name="intrinio",
    website="https://intrinio.com/",
    description="""Intrinio is a financial data platform that provides real-time and
    historical financial market data to businesses and developers through an API.""",
    credentials=["api_key"],
    fetcher_dict={
        "BalanceSheet": IntrinioBalanceSheetFetcher,
        "CalendarIpo": IntrinioCalendarIpoFetcher,
        "CashFlowStatement": IntrinioCashFlowStatementFetcher,
        "CompanyFilings": IntrinioCompanyFilingsFetcher,
        "CompanyNews": IntrinioCompanyNewsFetcher,
        "CurrencyPairs": IntrinioCurrencyPairsFetcher,
        "EquityHistorical": IntrinioEquityHistoricalFetcher,
        "EquityInfo": IntrinioEquityInfoFetcher,
        "EquityQuote": IntrinioEquityQuoteFetcher,
        "EquitySearch": IntrinioEquitySearchFetcher,
        "FinancialRatios": IntrinioFinancialRatiosFetcher,
        "FredSeries": IntrinioFredSeriesFetcher,
        "HistoricalAttributes": IntrinioHistoricalAttributesFetcher,
        "HistoricalDividends": IntrinioHistoricalDividendsFetcher,
        "IncomeStatement": IntrinioIncomeStatementFetcher,
        "IndexHistorical": IntrinioIndexHistoricalFetcher,
        "InsiderTrading": IntrinioInsiderTradingFetcher,
        "InstitutionalOwnership": IntrinioInstitutionalOwnershipFetcher,
        "KeyMetrics": IntrinioKeyMetricsFetcher,
        "LatestAttributes": IntrinioLatestAttributesFetcher,
        "MarketIndices": IntrinioMarketIndicesFetcher,
        "OptionsChains": IntrinioOptionsChainsFetcher,
        "OptionsUnusual": IntrinioOptionsUnusualFetcher,
        "ReportedFinancials": IntrinioReportedFinancialsFetcher,
        "SearchAttributes": IntrinioSearchAttributesFetcher,
        "ShareStatistics": IntrinioShareStatisticsFetcher,
        "WorldNews": IntrinioWorldNewsFetcher,
    },
)
