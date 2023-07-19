"""Polygon provider module."""

# IMPORT STANDARD

# IMPORT INTERNAL
from openbb_provider.abstract.provider import Provider, ProviderNameType

from openbb_polygon.balance_sheet import PolygonBalanceSheetFetcher
from openbb_polygon.cash_flow import PolygonCashFlowStatementFetcher
from openbb_polygon.crypto_eod import PolygonCryptoEODFetcher
from openbb_polygon.crypto_price import PolygonCryptoPriceFetcher
from openbb_polygon.forex_eod import PolygonForexEODFetcher
from openbb_polygon.forex_price import PolygonForexPriceFetcher
from openbb_polygon.income_statement import PolygonIncomeStatementFetcher
from openbb_polygon.major_indices_eod import PolygonMajorIndicesEODFetcher
from openbb_polygon.major_indices_price import PolygonMajorIndicesPriceFetcher
from openbb_polygon.stock_eod import PolygonStockEODFetcher
from openbb_polygon.stock_news import PolygonStockNewsFetcher
from openbb_polygon.stock_price import PolygonStockPriceFetcher

# IMPORT THIRD-PARTY

# mypy: disable-error-code="list-item"
polygon_provider = Provider(
    name=ProviderNameType("polygon"),
    description="Provider for Polygon.",
    fetcher_list=[
        PolygonStockEODFetcher,
        PolygonStockNewsFetcher,
        PolygonBalanceSheetFetcher,
        PolygonIncomeStatementFetcher,
        PolygonCashFlowStatementFetcher,
        PolygonStockPriceFetcher,
        PolygonCryptoPriceFetcher,
        PolygonCryptoEODFetcher,
        PolygonMajorIndicesEODFetcher,
        PolygonMajorIndicesPriceFetcher,
        PolygonForexEODFetcher,
        PolygonForexPriceFetcher,
    ],
    credentials=True,
)
