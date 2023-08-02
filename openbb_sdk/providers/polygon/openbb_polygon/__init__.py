"""Polygon provider module."""
from openbb_provider.abstract.provider import Provider

from openbb_polygon.models.balance_sheet import PolygonBalanceSheetFetcher
from openbb_polygon.models.cash_flow import PolygonCashFlowStatementFetcher
from openbb_polygon.models.crypto_eod import PolygonCryptoEODFetcher
from openbb_polygon.models.forex_eod import PolygonForexEODFetcher
from openbb_polygon.models.forex_pairs import PolygonForexPairsFetcher
from openbb_polygon.models.income_statement import PolygonIncomeStatementFetcher
from openbb_polygon.models.major_indices_eod import PolygonMajorIndicesEODFetcher
from openbb_polygon.models.stock_eod import PolygonStockEODFetcher
from openbb_polygon.models.stock_news import PolygonStockNewsFetcher

polygon_provider = Provider(
    name="polygon",
    website="https://polygon.io/",
    description="""The Polygon.io Stocks API provides REST endpoints that let you query
     the latest market data from all US stock exchanges. You can also find data on
     company financials, stock market holidays, corporate actions, and more.""",
    required_credentials=["api_key"],
    fetcher_dict={
        "StockEOD": PolygonStockEODFetcher,
        "StockNews": PolygonStockNewsFetcher,
        "BalanceSheet": PolygonBalanceSheetFetcher,
        "IncomeStatement": PolygonIncomeStatementFetcher,
        "CashFlowStatement": PolygonCashFlowStatementFetcher,
        "CryptoEOD": PolygonCryptoEODFetcher,
        "MajorIndicesEOD": PolygonMajorIndicesEODFetcher,
        "ForexEOD": PolygonForexEODFetcher,
        "ForexPairs": PolygonForexPairsFetcher,
    },
)
