"""intrinio provider module."""


from openbb_intrinio.models.balance_sheet import IntrinioBalanceSheetFetcher
from openbb_intrinio.models.calendar_ipo import IntrinioCalendarIpoFetcher
from openbb_intrinio.models.cash_flow import IntrinioCashFlowStatementFetcher
from openbb_intrinio.models.forex_pairs import IntrinioForexPairsFetcher
from openbb_intrinio.models.fred_historical import IntrinioFredHistoricalFetcher
from openbb_intrinio.models.global_news import IntrinioGlobalNewsFetcher
from openbb_intrinio.models.income_statement import IntrinioIncomeStatementFetcher
from openbb_intrinio.models.options_chains import IntrinioOptionsChainsFetcher
from openbb_intrinio.models.stock_historical import IntrinioStockHistoricalFetcher
from openbb_intrinio.models.stock_news import IntrinioStockNewsFetcher
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
        "CashFlowStatement": IntrinioCashFlowStatementFetcher,
        "ForexPairs": IntrinioForexPairsFetcher,
        "FredHistorical": IntrinioFredHistoricalFetcher,
        "GlobalNews": IntrinioGlobalNewsFetcher,
        "IncomeStatement": IntrinioIncomeStatementFetcher,
        "CalendarIpo": IntrinioCalendarIpoFetcher,
        "OptionsChains": IntrinioOptionsChainsFetcher,
        "StockHistorical": IntrinioStockHistoricalFetcher,
        "StockNews": IntrinioStockNewsFetcher,
        "StockQuote": IntrinioStockQuoteFetcher,
    },
)
