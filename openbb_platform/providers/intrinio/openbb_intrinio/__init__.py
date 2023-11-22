"""Intrinio provider module."""

from openbb_core.provider.abstract.provider import Provider
from openbb_intrinio.models.balance_sheet import IntrinioBalanceSheetFetcher
from openbb_intrinio.models.calendar_ipo import IntrinioCalendarIpoFetcher
from openbb_intrinio.models.cash_flow import IntrinioCashFlowStatementFetcher
from openbb_intrinio.models.company_news import IntrinioCompanyNewsFetcher
from openbb_intrinio.models.currency_pairs import IntrinioCurrencyPairsFetcher
from openbb_intrinio.models.equity_historical import IntrinioEquityHistoricalFetcher
from openbb_intrinio.models.equity_quote import IntrinioEquityQuoteFetcher
from openbb_intrinio.models.financial_attributes import (
    IntrinioFinancialAttributesFetcher,
)
from openbb_intrinio.models.fred_indices import IntrinioFredIndicesFetcher
from openbb_intrinio.models.income_statement import IntrinioIncomeStatementFetcher
from openbb_intrinio.models.options_chains import IntrinioOptionsChainsFetcher
from openbb_intrinio.models.options_unusual import IntrinioOptionsUnusualFetcher
from openbb_intrinio.models.search_financial_attributes import (
    IntrinioSearchFinancialAttributesFetcher,
)
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
        "CompanyNews": IntrinioCompanyNewsFetcher,
        "CurrencyPairs": IntrinioCurrencyPairsFetcher,
        "EquityHistorical": IntrinioEquityHistoricalFetcher,
        "EquityQuote": IntrinioEquityQuoteFetcher,
        "FinancialAttributes": IntrinioFinancialAttributesFetcher,
        "FredIndices": IntrinioFredIndicesFetcher,
        "WorldNews": IntrinioWorldNewsFetcher,
        "IncomeStatement": IntrinioIncomeStatementFetcher,
        "OptionsChains": IntrinioOptionsChainsFetcher,
        "OptionsUnusual": IntrinioOptionsUnusualFetcher,
        "SearchFinancialAttributes": IntrinioSearchFinancialAttributesFetcher,
    },
)
