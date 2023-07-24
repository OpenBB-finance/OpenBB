"""Polygon provider module."""


# IMPORT INTERNAL
from openbb_provider.abstract.provider import Provider

from openbb_polygon.models.balance_sheet import PolygonBalanceSheetFetcher
from openbb_polygon.models.cash_flow import PolygonCashFlowStatementFetcher
from openbb_polygon.models.crypto_eod import PolygonCryptoEODFetcher
from openbb_polygon.models.crypto_price import PolygonCryptoPriceFetcher
from openbb_polygon.models.forex_eod import PolygonForexEODFetcher
from openbb_polygon.models.forex_price import PolygonForexPriceFetcher
from openbb_polygon.models.income_statement import PolygonIncomeStatementFetcher
from openbb_polygon.models.major_indices_eod import PolygonMajorIndicesEODFetcher
from openbb_polygon.models.major_indices_price import PolygonMajorIndicesPriceFetcher
from openbb_polygon.models.stock_eod import PolygonStockEODFetcher
from openbb_polygon.models.stock_news import PolygonStockNewsFetcher
from openbb_polygon.models.stock_price import PolygonStockPriceFetcher

# IMPORT THIRD-PARTY

# mypy: disable-error-code="list-item"
polygon_provider = Provider(
    name="polygon",
    description="Provider for Polygon.",
    required_credentials=["api_key"],
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
)
