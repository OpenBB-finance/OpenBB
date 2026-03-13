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
from openbb_yfinance.models.equity_profile import YFinanceEquityProfileFetcher
from openbb_yfinance.models.equity_quote import YFinanceEquityQuoteFetcher
from openbb_yfinance.models.equity_screener import YFinanceEquityScreenerFetcher
from openbb_yfinance.models.etf_info import YFinanceEtfInfoFetcher
from openbb_yfinance.models.futures_curve import YFinanceFuturesCurveFetcher
from openbb_yfinance.models.futures_historical import YFinanceFuturesHistoricalFetcher
from openbb_yfinance.models.gainers import YFGainersFetcher
from openbb_yfinance.models.growth_tech_equities import YFGrowthTechEquitiesFetcher
from openbb_yfinance.models.historical_dividends import (
    YFinanceHistoricalDividendsFetcher,
)
from openbb_yfinance.models.income_statement import YFinanceIncomeStatementFetcher
from openbb_yfinance.models.index_historical import (
    YFinanceIndexHistoricalFetcher,
)
from openbb_yfinance.models.key_executives import YFinanceKeyExecutivesFetcher
from openbb_yfinance.models.key_metrics import YFinanceKeyMetricsFetcher
from openbb_yfinance.models.losers import YFLosersFetcher
from openbb_yfinance.models.options_chains import YFinanceOptionsChainsFetcher
from openbb_yfinance.models.price_target_consensus import (
    YFinancePriceTargetConsensusFetcher,
)
from openbb_yfinance.models.share_statistics import YFinanceShareStatisticsFetcher
from openbb_yfinance.models.undervalued_growth_equities import (
    YFUndervaluedGrowthEquitiesFetcher,
)
from openbb_yfinance.models.undervalued_large_caps import YFUndervaluedLargeCapsFetcher

yfinance_provider = Provider(
    name="yfinance",
    website="https://finance.yahoo.com",
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
        "EquityInfo": YFinanceEquityProfileFetcher,
        "EquityLosers": YFLosersFetcher,
        "EquityQuote": YFinanceEquityQuoteFetcher,
        "EquityScreener": YFinanceEquityScreenerFetcher,
        "EquityUndervaluedGrowth": YFUndervaluedGrowthEquitiesFetcher,
        "EquityUndervaluedLargeCaps": YFUndervaluedLargeCapsFetcher,
        "EtfHistorical": YFinanceEquityHistoricalFetcher,
        "EtfInfo": YFinanceEtfInfoFetcher,
        "FuturesCurve": YFinanceFuturesCurveFetcher,
        "FuturesHistorical": YFinanceFuturesHistoricalFetcher,
        "GrowthTechEquities": YFGrowthTechEquitiesFetcher,
        "HistoricalDividends": YFinanceHistoricalDividendsFetcher,
        "IncomeStatement": YFinanceIncomeStatementFetcher,
        "IndexHistorical": YFinanceIndexHistoricalFetcher,
        "KeyExecutives": YFinanceKeyExecutivesFetcher,
        "KeyMetrics": YFinanceKeyMetricsFetcher,
        "OptionsChains": YFinanceOptionsChainsFetcher,
        "PriceTargetConsensus": YFinancePriceTargetConsensusFetcher,
        "ShareStatistics": YFinanceShareStatisticsFetcher,
    },
    repr_name="Yahoo Finance",
)
