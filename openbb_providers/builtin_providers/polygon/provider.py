"""Polygon provider module."""

# IMPORT STANDARD

from builtin_providers.polygon.balance_sheet import PolygonBalanceSheetFetcher
from builtin_providers.polygon.cash_flow import PolygonCashFlowStatementFetcher
from builtin_providers.polygon.crypto_eod import PolygonCryptoEODFetcher
from builtin_providers.polygon.crypto_price import PolygonCryptoPriceFetcher
from builtin_providers.polygon.forex_eod import PolygonForexEODFetcher
from builtin_providers.polygon.forex_price import PolygonForexPriceFetcher
from builtin_providers.polygon.income_statement import PolygonIncomeStatementFetcher
from builtin_providers.polygon.major_indices_eod import PolygonMajorIndicesEODFetcher
from builtin_providers.polygon.major_indices_price import (
    PolygonMajorIndicesPriceFetcher,
)
from builtin_providers.polygon.stock_eod import PolygonStockEODFetcher
from builtin_providers.polygon.stock_news import PolygonStockNewsFetcher
from builtin_providers.polygon.stock_price import PolygonStockPriceFetcher

# IMPORT INTERNAL
from openbb_provider.provider.abstract.provider import Provider

# IMPORT THIRD-PARTY

# mypy: disable-error-code="list-item"
# ignoring because I dont know how to type the string properly
polygon_provider = Provider(
    name="polygon",  # type: ignore
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
)
