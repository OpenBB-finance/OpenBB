"""yfinance (Yahoo!Finance) provider module."""


from openbb_provider.abstract.provider import Provider

from openbb_yfinance.models.crypto_eod import YFinanceCryptoHistoricalFetcher
from openbb_yfinance.models.forex_eod import YFinanceForexHistoricalFetcher
from openbb_yfinance.models.futures_curve import YFinanceFuturesCurveFetcher
from openbb_yfinance.models.futures_eod import YFinanceFuturesHistoricalFetcher
from openbb_yfinance.models.major_indices_eod import YFinanceMajorIndicesHistoricalFetcher
from openbb_yfinance.models.stock_eod import YFinanceStockHistoricalFetcher

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
        "FutureHistoricalD": YFinanceFuturHistoricalODFetcher,
        "FuturHistoricalurve": YFinanceFHistoricalresCurveFetcher,
    },HistoricalHistorical
)HistoricalHistorical
HistoricalHistorical
