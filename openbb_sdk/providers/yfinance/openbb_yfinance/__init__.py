"""yfinance (Yahoo!Finance) provider module."""


from openbb_provider.abstract.provider import Provider
from openbb_yfinance.models.available_indices import YFinanceAvailableIndicesFetcher
from openbb_yfinance.models.balance_sheet import YFinanceBalanceSheetFetcher
from openbb_yfinance.models.cash_flow import YFinanceCashFlowStatementFetcher
from openbb_yfinance.models.crypto_historical import YFinanceCryptoHistoricalFetcher
from openbb_yfinance.models.forex_historical import YFinanceForexHistoricalFetcher
from openbb_yfinance.models.futures_curve import YFinanceFuturesCurveFetcher
from openbb_yfinance.models.futures_historical import YFinanceFuturesHistoricalFetcher
from openbb_yfinance.models.income_statement import YFinanceIncomeStatementFetcher
from openbb_yfinance.models.major_indices_historical import (
    YFinanceMajorIndicesHistoricalFetcher,
)
from openbb_yfinance.models.stock_historical import YFinanceStockHistoricalFetcher
from openbb_yfinance.models.stock_news import YFinanceStockNewsFetcher

yfinance_provider = Provider(
    name="yfinance",
    website="https://finance.yahoo.com/",
    description="""Yahoo! Finance is a web-based platform that offers financial news,
    data, and tools for investors and individuals interested in tracking and analyzing
    financial markets and assets.""",
    fetcher_dict={
        "CryptoHistorical": YFinanceCryptoHistoricalFetcher,
        "ForexHistorical": YFinanceForexHistoricalFetcher,
        "MajorIndicesHistorical": YFinanceMajorIndicesHistoricalFetcher,
        "StockHistorical": YFinanceStockHistoricalFetcher,
        "FuturesHistorical": YFinanceFuturesHistoricalFetcher,
        "FuturesCurve": YFinanceFuturesCurveFetcher,
        "StockNews": YFinanceStockNewsFetcher,
        "BalanceSheet": YFinanceBalanceSheetFetcher,
        "CashFlowStatement": YFinanceCashFlowStatementFetcher,
        "IncomeStatement": YFinanceIncomeStatementFetcher,
        "AvailableIndices": YFinanceAvailableIndicesFetcher,
    },
)
