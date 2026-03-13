"""Intrinio Provider Modules."""

from openbb_core.provider.abstract.provider import Provider
from openbb_intrinio.models.balance_sheet import IntrinioBalanceSheetFetcher
from openbb_intrinio.models.calendar_ipo import IntrinioCalendarIpoFetcher
from openbb_intrinio.models.cash_flow import IntrinioCashFlowStatementFetcher
from openbb_intrinio.models.company_filings import IntrinioCompanyFilingsFetcher
from openbb_intrinio.models.company_news import IntrinioCompanyNewsFetcher
from openbb_intrinio.models.currency_pairs import IntrinioCurrencyPairsFetcher
from openbb_intrinio.models.equity_historical import IntrinioEquityHistoricalFetcher
from openbb_intrinio.models.equity_info import IntrinioEquityInfoFetcher
from openbb_intrinio.models.equity_quote import IntrinioEquityQuoteFetcher
from openbb_intrinio.models.equity_search import IntrinioEquitySearchFetcher
from openbb_intrinio.models.etf_holdings import IntrinioEtfHoldingsFetcher
from openbb_intrinio.models.etf_info import IntrinioEtfInfoFetcher
from openbb_intrinio.models.etf_price_performance import (
    IntrinioEtfPricePerformanceFetcher,
)
from openbb_intrinio.models.etf_search import IntrinioEtfSearchFetcher
from openbb_intrinio.models.financial_ratios import IntrinioFinancialRatiosFetcher
from openbb_intrinio.models.forward_ebitda_estimates import (
    IntrinioForwardEbitdaEstimatesFetcher,
)
from openbb_intrinio.models.forward_eps_estimates import (
    IntrinioForwardEpsEstimatesFetcher,
)
from openbb_intrinio.models.forward_pe_estimates import (
    IntrinioForwardPeEstimatesFetcher,
)
from openbb_intrinio.models.forward_sales_estimates import (
    IntrinioForwardSalesEstimatesFetcher,
)
from openbb_intrinio.models.fred_series import IntrinioFredSeriesFetcher
from openbb_intrinio.models.historical_attributes import (
    IntrinioHistoricalAttributesFetcher,
)
from openbb_intrinio.models.historical_dividends import (
    IntrinioHistoricalDividendsFetcher,
)
from openbb_intrinio.models.historical_market_cap import (
    IntrinioHistoricalMarketCapFetcher,
)
from openbb_intrinio.models.income_statement import IntrinioIncomeStatementFetcher
from openbb_intrinio.models.index_historical import IntrinioIndexHistoricalFetcher
from openbb_intrinio.models.insider_trading import IntrinioInsiderTradingFetcher

# from openbb_intrinio.models.institutional_ownership import (
#     IntrinioInstitutionalOwnershipFetcher,
# )
from openbb_intrinio.models.key_metrics import IntrinioKeyMetricsFetcher
from openbb_intrinio.models.latest_attributes import IntrinioLatestAttributesFetcher
from openbb_intrinio.models.market_snapshots import IntrinioMarketSnapshotsFetcher
from openbb_intrinio.models.options_chains import IntrinioOptionsChainsFetcher
from openbb_intrinio.models.options_snapshots import IntrinioOptionsSnapshotsFetcher
from openbb_intrinio.models.options_unusual import IntrinioOptionsUnusualFetcher
from openbb_intrinio.models.price_target_consensus import (
    IntrinioPriceTargetConsensusFetcher,
)
from openbb_intrinio.models.reported_financials import IntrinioReportedFinancialsFetcher
from openbb_intrinio.models.search_attributes import (
    IntrinioSearchAttributesFetcher,
)
from openbb_intrinio.models.share_statistics import IntrinioShareStatisticsFetcher
from openbb_intrinio.models.world_news import IntrinioWorldNewsFetcher

intrinio_provider = Provider(
    name="intrinio",
    website="https://intrinio.com",
    description="""Intrinio is a financial data platform that provides real-time and
historical financial market data to businesses and developers through an API.""",
    credentials=["api_key"],
    fetcher_dict={
        "BalanceSheet": IntrinioBalanceSheetFetcher,
        "CalendarIpo": IntrinioCalendarIpoFetcher,
        "CashFlowStatement": IntrinioCashFlowStatementFetcher,
        "CompanyFilings": IntrinioCompanyFilingsFetcher,
        "CompanyNews": IntrinioCompanyNewsFetcher,
        "CurrencyPairs": IntrinioCurrencyPairsFetcher,
        "EquityHistorical": IntrinioEquityHistoricalFetcher,
        "EquityInfo": IntrinioEquityInfoFetcher,
        "EquityQuote": IntrinioEquityQuoteFetcher,
        "EquitySearch": IntrinioEquitySearchFetcher,
        "EtfHistorical": IntrinioEquityHistoricalFetcher,
        "EtfHoldings": IntrinioEtfHoldingsFetcher,
        "EtfInfo": IntrinioEtfInfoFetcher,
        "EtfPricePerformance": IntrinioEtfPricePerformanceFetcher,
        "EtfSearch": IntrinioEtfSearchFetcher,
        "FinancialRatios": IntrinioFinancialRatiosFetcher,
        "ForwardEbitdaEstimates": IntrinioForwardEbitdaEstimatesFetcher,
        "ForwardEpsEstimates": IntrinioForwardEpsEstimatesFetcher,
        "ForwardPeEstimates": IntrinioForwardPeEstimatesFetcher,
        "ForwardSalesEstimates": IntrinioForwardSalesEstimatesFetcher,
        "FredSeries": IntrinioFredSeriesFetcher,
        "HistoricalAttributes": IntrinioHistoricalAttributesFetcher,
        "HistoricalDividends": IntrinioHistoricalDividendsFetcher,
        "HistoricalMarketCap": IntrinioHistoricalMarketCapFetcher,
        "IncomeStatement": IntrinioIncomeStatementFetcher,
        "IndexHistorical": IntrinioIndexHistoricalFetcher,
        "InsiderTrading": IntrinioInsiderTradingFetcher,
        # "InstitutionalOwnership": IntrinioInstitutionalOwnershipFetcher, # Disabled due to unreliable Intrinio endpoint
        "KeyMetrics": IntrinioKeyMetricsFetcher,
        "LatestAttributes": IntrinioLatestAttributesFetcher,
        "MarketSnapshots": IntrinioMarketSnapshotsFetcher,
        "OptionsChains": IntrinioOptionsChainsFetcher,
        "OptionsSnapshots": IntrinioOptionsSnapshotsFetcher,
        "OptionsUnusual": IntrinioOptionsUnusualFetcher,
        "PriceTargetConsensus": IntrinioPriceTargetConsensusFetcher,
        "ReportedFinancials": IntrinioReportedFinancialsFetcher,
        "SearchAttributes": IntrinioSearchAttributesFetcher,
        "ShareStatistics": IntrinioShareStatisticsFetcher,
        "WorldNews": IntrinioWorldNewsFetcher,
    },
    repr_name="Intrinio",
    deprecated_credentials={"API_INTRINIO_KEY": "intrinio_api_key"},
    instructions="Go to: https://intrinio.com/starter-plan\n\n![Intrinio](https://user-images.githubusercontent.com/85772166/219207556-fcfee614-59f1-46ae-bff4-c63dd2f6991d.png)\n\nAn API key will be issued with a subscription. Find the token value within the account dashboard.",  # noqa: E501  pylint: disable=line-too-long
)
