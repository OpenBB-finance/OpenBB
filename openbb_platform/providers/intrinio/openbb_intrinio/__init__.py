"""Intrinio provider module."""

from openbb_intrinio.models.balance_sheet import IntrinioBalanceSheetFetcher
from openbb_intrinio.models.calendar_ipo import IntrinioCalendarIpoFetcher
from openbb_intrinio.models.cash_flow import IntrinioCashFlowStatementFetcher
from openbb_intrinio.models.company_news import IntrinioCompanyNewsFetcher
from openbb_intrinio.models.currency_pairs import IntrinioCurrencyPairsFetcher
from openbb_intrinio.models.fred_historical import IntrinioFredHistoricalFetcher
from openbb_intrinio.models.global_news import IntrinioGlobalNewsFetcher
from openbb_intrinio.models.income_statement import IntrinioIncomeStatementFetcher
from openbb_intrinio.models.options_chains import IntrinioOptionsChainsFetcher
from openbb_intrinio.models.options_unusual import IntrinioOptionsUnusualFetcher
from openbb_intrinio.models.stock_historical import IntrinioStockHistoricalFetcher
from openbb_intrinio.models.stock_quote import IntrinioStockQuoteFetcher
from openbb_provider.abstract.provider import Provider

intrinio_provider = Provider(
    name="intrinio",
    website="https://intrinio.com/",
    description="""Intrinio is a financial data platform that provides real-time and
    historical financial market data to businesses and developers through an API.""",
    required_credentials=["api_key"],
    fetcher_dict={
        "BalanceSheet": IntrinioBalanceSheetFetcher,
        "CalendarIpo": IntrinioCalendarIpoFetcher,
        "CashFlowStatement": IntrinioCashFlowStatementFetcher,
        "CompanyNews": IntrinioCompanyNewsFetcher,
        "CurrencyPairs": IntrinioCurrencyPairsFetcher,
        "FredHistorical": IntrinioFredHistoricalFetcher,
        "GlobalNews": IntrinioGlobalNewsFetcher,
        "IncomeStatement": IntrinioIncomeStatementFetcher,
        "OptionsChains": IntrinioOptionsChainsFetcher,
        "OptionsUnusual": IntrinioOptionsUnusualFetcher,
        "StockHistorical": IntrinioStockHistoricalFetcher,
        "StockQuote": IntrinioStockQuoteFetcher,
    },
)
