"""Polygon provider module."""
from openbb_core.provider.abstract.provider import Provider
from openbb_polygon.models.balance_sheet import PolygonBalanceSheetFetcher
from openbb_polygon.models.cash_flow import PolygonCashFlowStatementFetcher
from openbb_polygon.models.company_news import PolygonCompanyNewsFetcher
from openbb_polygon.models.crypto_historical import PolygonCryptoHistoricalFetcher
from openbb_polygon.models.currency_historical import PolygonCurrencyHistoricalFetcher
from openbb_polygon.models.currency_pairs import PolygonCurrencyPairsFetcher
from openbb_polygon.models.equity_historical import PolygonEquityHistoricalFetcher
from openbb_polygon.models.equity_nbbo import PolygonEquityNBBOFetcher
from openbb_polygon.models.income_statement import PolygonIncomeStatementFetcher
from openbb_polygon.models.market_indices import (
    PolygonMarketIndicesFetcher,
)
from openbb_polygon.models.market_snapshots import PolygonMarketSnapshotsFetcher

polygon_provider = Provider(
    name="polygon",
    website="https://polygon.io/",
    description="""The Polygon.io Stocks API provides REST endpoints that let you query
     the latest market data from all US stock exchanges. You can also find data on
     company financials, stock market holidays, corporate actions, and more.""",
    credentials=["api_key"],
    fetcher_dict={
        "BalanceSheet": PolygonBalanceSheetFetcher,
        "CashFlowStatement": PolygonCashFlowStatementFetcher,
        "CompanyNews": PolygonCompanyNewsFetcher,
        "CryptoHistorical": PolygonCryptoHistoricalFetcher,
        "CurrencyHistorical": PolygonCurrencyHistoricalFetcher,
        "CurrencyPairs": PolygonCurrencyPairsFetcher,
        "EquityHistorical": PolygonEquityHistoricalFetcher,
        "EquityNBBO": PolygonEquityNBBOFetcher,
        "IncomeStatement": PolygonIncomeStatementFetcher,
        "MarketIndices": PolygonMarketIndicesFetcher,
        "MarketSnapshots": PolygonMarketSnapshotsFetcher,
    },
)
