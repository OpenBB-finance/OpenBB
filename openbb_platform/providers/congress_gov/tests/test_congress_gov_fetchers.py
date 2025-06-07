"""Congress.gov Fetchers tests."""

from datetime import date

import pytest
from openbb_congress_gov.models.congress_bills import CongressBillsFetcher
from openbb_congress_gov.models.congress_bill_summaries import (
    CongressBillSummariesFetcher,
)
from openbb_congress_gov.models.presidential_documents import (
    PresidentialDocumentsFetcher,
)
from openbb_core.app.service.user_service import UserService

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.fixture(scope="module")
def vcr_config():
    """VCR configuration."""
    return {
        "filter_headers": [
            ("User-Agent", None),
            ("api_key", "MOCK_API_KEY"),
        ],
        "filter_query_parameters": [
            ("api_key", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.record_http
def test_congress_bills_fetcher(credentials=test_credentials):
    """Test Congress Bills fetcher."""
    params = {
        "limit": 5,
        "sort": "updateDate+desc",
    }

    fetcher = CongressBillsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_congress_bills_fetcher_with_filters(credentials=test_credentials):
    """Test Congress Bills fetcher with congress and bill type filters."""
    params = {
        "congress": 118,
        "bill_type": "hr",
        "limit": 3,
        "sort": "updateDate+desc",
    }

    fetcher = CongressBillsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_congress_bills_fetcher_with_date_range(credentials=test_credentials):
    """Test Congress Bills fetcher with date range."""
    params = {
        "limit": 5,
        "from_date": date(2024, 1, 1),
        "to_date": date(2024, 6, 30),
        "sort": "updateDate+desc",
    }

    fetcher = CongressBillsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_congress_bill_summaries_fetcher(credentials=test_credentials):
    """Test Congress Bill Summaries fetcher."""
    params = {
        "congress": 118,
        "bill_type": "hr",
        "bill_number": "1",
        "limit": 3,
    }

    fetcher = CongressBillSummariesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_congress_bill_summaries_fetcher_senate(credentials=test_credentials):
    """Test Congress Bill Summaries fetcher for Senate bill."""
    params = {
        "congress": 118,
        "bill_type": "s",
        "bill_number": "1",
        "limit": 2,
    }

    fetcher = CongressBillSummariesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_presidential_documents_fetcher(credentials=test_credentials):
    """Test Presidential Documents fetcher."""
    params = {
        "president": "joe-biden",
        "document_types": "executive_order",
        "per_page": 5,
        "page": 1,
    }

    # Presidential Documents don't need credentials (Federal Register API)
    fetcher = PresidentialDocumentsFetcher()
    result = fetcher.test(params, None)
    assert result is None


@pytest.mark.record_http
def test_presidential_documents_fetcher_multiple_types(
    credentials=test_credentials
):
    """Test Presidential Documents fetcher with multiple document types."""
    params = {
        "president": "joe-biden",
        "document_types": "executive_order,memorandum",
        "per_page": 3,
        "page": 1,
    }

    fetcher = PresidentialDocumentsFetcher()
    result = fetcher.test(params, None)
    assert result is None


@pytest.mark.record_http
def test_presidential_documents_fetcher_trump(credentials=test_credentials):
    """Test Presidential Documents fetcher for Trump administration."""
    params = {
        "president": "donald-trump",
        "document_types": "executive_order",
        "per_page": 3,
        "page": 1,
    }

    fetcher = PresidentialDocumentsFetcher()
    result = fetcher.test(params, None)
    assert result is None


@pytest.mark.record_http
def test_presidential_documents_fetcher_obama(credentials=test_credentials):
    """Test Presidential Documents fetcher for Obama administration."""
    params = {
        "president": "barack-obama",
        "document_types": "proclamation",
        "per_page": 3,
        "page": 1,
    }

    fetcher = PresidentialDocumentsFetcher()
    result = fetcher.test(params, None)
    assert result is None


@pytest.mark.record_http
def test_congress_bills_fetcher_pagination(credentials=test_credentials):
    """Test Congress Bills fetcher with pagination."""
    params = {
        "limit": 10,
        "offset": 5,
        "sort": "updateDate+desc",
    }

    fetcher = CongressBillsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_congress_bills_fetcher_asc_sort(credentials=test_credentials):
    """Test Congress Bills fetcher with ascending sort."""
    params = {
        "limit": 5,
        "sort": "updateDate+asc",
    }

    fetcher = CongressBillsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None 