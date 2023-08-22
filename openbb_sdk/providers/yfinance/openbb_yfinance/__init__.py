"""yfinance (Yahoo!Finance) provider module."""


from openbb_provider.abstract.provider import Provider

from openbb_yfinance.models.crypto_eod import YFinanceCryptoEODFetcher
from openbb_yfinance.models.forex_eod import YFinanceForexEODFetcher
from openbb_yfinance.models.futures_curve import YFinanceFuturesCurveFetcher
from openbb_yfinance.models.futures_eod import YFinanceFuturesEODFetcher
from openbb_yfinance.models.major_indices_eod import YFinanceMajorIndicesEODFetcher
from openbb_yfinance.models.stock_eod import YFinanceStockEODFetcher

yfinance_provider = Provider(
    name="yfinance",
    website="https://finance.yahoo.com/",
    description="""Yahoo! Finance is a web-based platform that offers financial news,
    data, and tools for investors and individuals interested in tracking and analyzing
    financial markets and assets.""",
    required_credentials=None,
    fetcher_dict={
        "CryptoEOD": YFinanceCryptoEODFetcher,
        "ForexEOD": YFinanceForexEODFetcher,
        "MajorIndicesEOD": YFinanceMajorIndicesEODFetcher,
        "StockEOD": YFinanceStockEODFetcher,
        "FuturesEOD": YFinanceFuturesEODFetcher,
        "FuturesCurve": YFinanceFuturesCurveFetcher,
    },
)
