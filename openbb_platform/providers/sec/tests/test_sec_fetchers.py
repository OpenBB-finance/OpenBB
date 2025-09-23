"""Tests for the SEC fetchers."""

from datetime import date

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_sec.models.cik_map import SecCikMapFetcher
from openbb_sec.models.company_filings import SecCompanyFilingsFetcher
from openbb_sec.models.compare_company_facts import SecCompareCompanyFactsFetcher
from openbb_sec.models.equity_ftd import SecEquityFtdFetcher
from openbb_sec.models.equity_search import SecEquitySearchFetcher
from openbb_sec.models.form_13FHR import SecForm13FHRFetcher
from openbb_sec.models.htm_file import SecHtmFileFetcher
from openbb_sec.models.insider_trading import SecInsiderTradingFetcher
from openbb_sec.models.institutions_search import SecInstitutionsSearchFetcher
from openbb_sec.models.latest_financial_reports import SecLatestFinancialReportsFetcher
from openbb_sec.models.management_discussion_analysis import (
    SecManagementDiscussionAnalysisFetcher,
)
from openbb_sec.models.nport_disclosure import SecNportDisclosureFetcher
from openbb_sec.models.rss_litigation import SecRssLitigationFetcher
from openbb_sec.models.schema_files import SecSchemaFilesFetcher
from openbb_sec.models.sec_filing import SecFilingFetcher
from openbb_sec.models.sic_search import SecSicSearchFetcher
from openbb_sec.models.symbol_map import SecSymbolMapFetcher

test_credentials = UserService().default_user_settings.credentials.dict()


@pytest.fixture(scope="module")
def vcr_config():
    """VCR configuration."""
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            None,
        ],
    }


@pytest.mark.record_http
def test_sec_symbol_map_fetcher(credentials=test_credentials):
    """Test the SEC Symbol Map fetcher."""
    params = {"query": "0000909832", "use_cache": False}

    fetcher = SecSymbolMapFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_sec_schema_files_fetcher(credentials=test_credentials):
    """Test the SEC Schema Files fetcher."""
    params = {"query": "2022"}

    fetcher = SecSchemaFilesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_sec_nport_disclosure_fetcher(credentials=test_credentials):
    """Test the SEC NPORT Disclosure fetcher."""
    params = {"symbol": "DIA", "year": 2025, "quarter": 1, "use_cache": False}

    fetcher = SecNportDisclosureFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_sec_sic_search_fetcher(credentials=test_credentials):
    """Test the SEC SIC Search fetcher."""
    params = {"query": "oil", "use_cache": False}

    fetcher = SecSicSearchFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_sec_equity_ftd_fetcher(credentials=test_credentials):
    """Test the SEC Equity FTD fetcher."""
    params = {"symbol": "AAPL", "limit": 1, "use_cache": False}

    fetcher = SecEquityFtdFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_sec_equity_search_fetcher(credentials=test_credentials):
    """Test the SEC Equity Search fetcher."""
    params = {"query": "trust", "use_cache": False}

    fetcher = SecEquitySearchFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_sec_company_filings_fetcher(credentials=test_credentials):
    """Test the SEC Company Filings fetcher."""
    params = {"symbol": "AAPL", "type": "10-K", "use_cache": False}

    fetcher = SecCompanyFilingsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_sec_institutions_search_fetcher(credentials=test_credentials):
    """Test the SEC Institutions Search fetcher."""
    params = {"query": "Investment Trust", "use_cache": False}

    fetcher = SecInstitutionsSearchFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_sec_rss_litigation_fetcher(credentials=test_credentials):
    """Test the SEC RSS Litigation fetcher."""
    params = {}

    fetcher = SecRssLitigationFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_sec_cik_map_fetcher(credentials=test_credentials):
    """Test the SEC CIK map fetcher."""
    params = {"symbol": "OXY", "use_cache": False}

    fetcher = SecCikMapFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_sec_form_13FHR_fetcher(credentials=test_credentials):
    """Test the SEC Form 13FHR fetcher."""
    params = {"symbol": "NVDA", "use_cache": False}

    fetcher = SecForm13FHRFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_sec_compare_company_facts_fetcher(credentials=test_credentials):
    """Test the SEC Compare Company Facts fetcher."""
    params = {
        "symbol": None,
        "fact": "PaymentsForRepurchaseOfCommonStock",
        "year": 2023,
        "fiscal_period": None,
        "instantaneous": False,
        "use_cache": False,
    }

    fetcher = SecCompareCompanyFactsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_sec_latest_financial_reports_fetcher(credentials=test_credentials):
    """Test the SEC Latest Financial Reports fetcher."""
    params = {
        "date": date(2024, 11, 5),
        "report_type": "10-K",
    }

    fetcher = SecLatestFinancialReportsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_sec_insider_trading_fetcher(credentials=test_credentials):
    """Test the SEC Insider Trading fetcher."""
    params = {
        "symbol": "AAPL",
        "start_date": date(2024, 6, 30),
        "end_date": date(2024, 9, 30),
        "use_cache": False,
    }

    fetcher = SecInsiderTradingFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_sec_management_discussion_analysis_fetcher(credentials=test_credentials):
    """Test the SEC Management Discussion Analysis fetcher."""
    params = {
        "symbol": "AAPL",
        "calendar_year": 2024,
        "calendar_period": "Q2",
        "wrap_length": 120,
        "include_tables": False,
        "use_cache": False,
        "raw_html": False,
    }

    fetcher = SecManagementDiscussionAnalysisFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_sec_filing_fetcher(credentials=test_credentials):
    """Test the SEC Filing fetcher."""
    params = {
        "url": "https://www.sec.gov/Archives/edgar/data/21344/000155278124000634/",
        "use_cache": False,
    }

    fetcher = SecFilingFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_sec_htm_file_fetcher(credentials=test_credentials):
    """Test the SEC HTM File fetcher."""
    params = {
        "url": "https://www.sec.gov/Archives/edgar/data/1990353/000110465925015513/tm256977d7_ex99-1.htm",
        "use_cache": False,
    }

    fetcher = SecHtmFileFetcher()
    result = fetcher.test(params, credentials)
    assert result is None
