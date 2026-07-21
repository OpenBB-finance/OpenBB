"""SEC provider module."""

from importlib.util import find_spec

from openbb_core.provider.abstract.provider import Provider

from openbb_sec.models.adviser_profile import (
    SecAdviserDocumentsFetcher,
    SecAdviserProfileFetcher,
)
from openbb_sec.models.adviser_search import (
    SecAdviserFirmsFetcher,
    SecAdviserIndividualsFetcher,
)
from openbb_sec.models.balance_sheet import SecBalanceSheetFetcher
from openbb_sec.models.balance_sheet_growth import SecBalanceSheetGrowthFetcher
from openbb_sec.models.cash_flow import SecCashFlowStatementFetcher
from openbb_sec.models.cash_flow_growth import SecCashFlowStatementGrowthFetcher
from openbb_sec.models.cik_map import SecCikMapFetcher
from openbb_sec.models.company_filings import SecCompanyFilingsFetcher
from openbb_sec.models.compare_company_facts import SecCompareCompanyFactsFetcher
from openbb_sec.models.equity_ftd import SecEquityFtdFetcher
from openbb_sec.models.equity_search import SecEquitySearchFetcher
from openbb_sec.models.form_13FHR import SecForm13FHRFetcher
from openbb_sec.models.full_text_search import SecFullTextSearchFetcher
from openbb_sec.models.htm_file import SecHtmFileFetcher
from openbb_sec.models.income_statement import SecIncomeStatementFetcher
from openbb_sec.models.income_statement_growth import SecIncomeStatementGrowthFetcher
from openbb_sec.models.insider_trading import SecInsiderTradingFetcher
from openbb_sec.models.institutions_search import SecInstitutionsSearchFetcher
from openbb_sec.models.latest_financial_reports import SecLatestFinancialReportsFetcher
from openbb_sec.models.management_discussion_analysis import (
    SecManagementDiscussionAnalysisFetcher,
)
from openbb_sec.models.nport_disclosure import SecNportDisclosureFetcher
from openbb_sec.models.nport_fund_metrics import SecNportFundMetricsFetcher
from openbb_sec.models.rss_litigation import SecRssLitigationFetcher
from openbb_sec.models.schema_files import SecSchemaFilesFetcher
from openbb_sec.models.sec_as_filed_statements import SecAsFiledStatementsFetcher
from openbb_sec.models.sec_beneficial_ownership import SecBeneficialOwnershipFetcher
from openbb_sec.models.sec_company_overview import SecCompanyOverviewFetcher
from openbb_sec.models.sec_disclosures import SecDisclosuresFetcher
from openbb_sec.models.sec_executive_compensation import (
    SecExecutiveCompensationFetcher,
)
from openbb_sec.models.sec_exhibit import SecExhibitFetcher
from openbb_sec.models.sec_filing import SecFilingFetcher
from openbb_sec.models.sec_legal_proceedings import SecLegalProceedingsFetcher
from openbb_sec.models.sec_management_ownership import SecManagementOwnershipFetcher
from openbb_sec.models.sec_pay_versus_performance import (
    SecPayVersusPerformanceFetcher,
)
from openbb_sec.models.sec_risk_factors import SecRiskFactorsFetcher
from openbb_sec.models.sec_segment_revenue import SecSegmentRevenueFetcher
from openbb_sec.models.sic_search import SecSicSearchFetcher
from openbb_sec.models.symbol_map import SecSymbolMapFetcher

EQUITY_INSTALLED = find_spec("openbb_equity") is not None
ETF_INSTALLED = find_spec("openbb_etf") is not None


def _equity_key(standard: str, alias: str) -> str:
    """Use ``standard`` when ``openbb-equity`` is installed, else the SEC ``alias``."""
    return standard if EQUITY_INSTALLED else alias


def _etf_key(standard: str, alias: str) -> str:
    """Use ``standard`` when ``openbb-etf`` is installed, else the SEC ``alias``."""
    return standard if ETF_INSTALLED else alias


sec_provider = Provider(
    name="sec",
    website="https://www.sec.gov/data",
    description="SEC is the public listings regulatory body for the United States.",
    credentials=None,
    fetcher_dict={
        _equity_key("BalanceSheet", "SecBalanceSheet"): SecBalanceSheetFetcher,
        _equity_key("BalanceSheetGrowth", "SecBalanceSheetGrowth"): (
            SecBalanceSheetGrowthFetcher
        ),
        _equity_key("CashFlowStatement", "SecCashFlowStatement"): (
            SecCashFlowStatementFetcher
        ),
        _equity_key("CashFlowStatementGrowth", "SecCashFlowStatementGrowth"): (
            SecCashFlowStatementGrowthFetcher
        ),
        "CikMap": SecCikMapFetcher,
        _equity_key("CompanyFilings", "SecCompanyFilings"): SecCompanyFilingsFetcher,
        _equity_key("CompareCompanyFacts", "SecCompareCompanyFacts"): (
            SecCompareCompanyFactsFetcher
        ),
        _equity_key("EquityFTD", "SecEquityFtd"): SecEquityFtdFetcher,
        _equity_key("EquitySearch", "SecEquitySearch"): SecEquitySearchFetcher,
        "Filings": SecCompanyFilingsFetcher,
        _equity_key("Form13FHR", "SecForm13FHR"): SecForm13FHRFetcher,
        "SecFullTextSearch": SecFullTextSearchFetcher,
        "SecHtmFile": SecHtmFileFetcher,
        _equity_key("IncomeStatement", "SecIncomeStatement"): SecIncomeStatementFetcher,
        _equity_key("IncomeStatementGrowth", "SecIncomeStatementGrowth"): (
            SecIncomeStatementGrowthFetcher
        ),
        _equity_key("InsiderTrading", "SecInsiderTrading"): SecInsiderTradingFetcher,
        "InstitutionsSearch": SecInstitutionsSearchFetcher,
        "SecAdviserFirms": SecAdviserFirmsFetcher,
        "SecAdviserIndividuals": SecAdviserIndividualsFetcher,
        "SecAdviserProfile": SecAdviserProfileFetcher,
        "SecAdviserDocuments": SecAdviserDocumentsFetcher,
        _equity_key("LatestFinancialReports", "SecLatestFinancialReports"): (
            SecLatestFinancialReportsFetcher
        ),
        _equity_key(
            "ManagementDiscussionAnalysis", "SecManagementDiscussionAnalysis"
        ): (SecManagementDiscussionAnalysisFetcher),
        _etf_key("NportDisclosure", "SecNportDisclosure"): SecNportDisclosureFetcher,
        "SecNportFundMetrics": SecNportFundMetricsFetcher,
        "RssLitigation": SecRssLitigationFetcher,
        "SchemaFiles": SecSchemaFilesFetcher,
        "SecAsFiledStatements": SecAsFiledStatementsFetcher,
        "SecBeneficialOwnership": SecBeneficialOwnershipFetcher,
        "SecCompanyOverview": SecCompanyOverviewFetcher,
        "SecDisclosures": SecDisclosuresFetcher,
        "SecExecutiveCompensation": SecExecutiveCompensationFetcher,
        "SecExhibit": SecExhibitFetcher,
        "SecFiling": SecFilingFetcher,
        "SecLegalProceedings": SecLegalProceedingsFetcher,
        "SecManagementOwnership": SecManagementOwnershipFetcher,
        "SecPayVersusPerformance": SecPayVersusPerformanceFetcher,
        "SecRiskFactors": SecRiskFactorsFetcher,
        "SecSegmentRevenue": SecSegmentRevenueFetcher,
        "SicSearch": SecSicSearchFetcher,
        "SymbolMap": SecSymbolMapFetcher,
    },
    repr_name="Securities and Exchange Commission (SEC)",
)
