"""Yahoo Finance provider module."""


from openbb_core.provider.abstract.provider import Provider
from openbb_yfinance.models.active import YFActiveFetcher
from openbb_yfinance.models.aggressive_small_caps import YFAggressiveSmallCapsFetcher
from openbb_yfinance.models.available_indices import YFinanceAvailableIndicesFetcher
from openbb_yfinance.models.balance_sheet import YFinanceBalanceSheetFetcher
from openbb_yfinance.models.cash_flow import YFinanceCashFlowStatementFetcher
from openbb_yfinance.models.company_news import YFinanceCompanyNewsFetcher
from openbb_yfinance.models.crypto_historical import YFinanceCryptoHistoricalFetcher
from openbb_yfinance.models.currency_historical import YFinanceCurrencyHistoricalFetcher
from openbb_yfinance.models.equity_historical import YFinanceEquityHistoricalFetcher
from openbb_yfinance.models.etf_historical import YFinanceEtfHistoricalFetcher
from openbb_yfinance.models.futures_curve import YFinanceFuturesCurveFetcher
from openbb_yfinance.models.futures_historical import YFinanceFuturesHistoricalFetcher
from openbb_yfinance.models.gainers import YFGainersFetcher
from openbb_yfinance.models.growth_tech_equities import YFGrowthTechEquitiesFetcher
from openbb_yfinance.models.income_statement import YFinanceIncomeStatementFetcher
from openbb_yfinance.models.losers import YFLosersFetcher
from openbb_yfinance.models.market_indices import (
    YFinanceMarketIndicesFetcher,
)
from openbb_yfinance.models.undervalued_growth_equities import (
    YFUndervaluedGrowthEquitiesFetcher,
)
from openbb_yfinance.models.undervalued_large_caps import YFUndervaluedLargeCapsFetcher

yfinance_provider = Provider(
    name="yfinance",
    website="https://finance.yahoo.com/",
    description="""Yahoo! Finance is a web-based platform that offers financial news,
    data, and tools for investors and individuals interested in tracking and analyzing
    financial markets and assets.""",
    fetcher_dict={
        "AvailableIndices": YFinanceAvailableIndicesFetcher,
        "BalanceSheet": YFinanceBalanceSheetFetcher,
        "CashFlowStatement": YFinanceCashFlowStatementFetcher,
        "CompanyNews": YFinanceCompanyNewsFetcher,
        "CryptoHistorical": YFinanceCryptoHistoricalFetcher,
        "CurrencyHistorical": YFinanceCurrencyHistoricalFetcher,
        "EquityActive": YFActiveFetcher,
        "EquityAggressiveSmallCaps": YFAggressiveSmallCapsFetcher,
        "EquityGainers": YFGainersFetcher,
        "EquityHistorical": YFinanceEquityHistoricalFetcher,
        "EquityLosers": YFLosersFetcher,
        "EquityUndervaluedGrowth": YFUndervaluedGrowthEquitiesFetcher,
        "EquityUndervaluedLargeCaps": YFUndervaluedLargeCapsFetcher,
        "EtfHistorical": YFinanceEtfHistoricalFetcher,
        "FuturesCurve": YFinanceFuturesCurveFetcher,
        "FuturesHistorical": YFinanceFuturesHistoricalFetcher,
        "GrowthTechEquities": YFGrowthTechEquitiesFetcher,
        "IncomeStatement": YFinanceIncomeStatementFetcher,
        "MarketIndices": YFinanceMarketIndicesFetcher,
    },
)
