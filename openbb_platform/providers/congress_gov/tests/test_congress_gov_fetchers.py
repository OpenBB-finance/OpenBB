"""Congress.gov Fetchers tests."""

from datetime import datetime

import pytest
from openbb_congress_gov.models.bill_info import CongressBillInfoFetcher
from openbb_congress_gov.models.bill_text import CongressBillTextFetcher
from openbb_congress_gov.models.congress_bills import CongressBillsFetcher
from openbb_congress_gov.utils.helpers import year_to_congress
from openbb_core.app.service.user_service import UserService

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)
test_credentials = (
    test_credentials
    if test_credentials and test_credentials.get("congress_gov_api_key")
    else {"congress_gov_api_key": "MOCK_API_KEY"}
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


def test_year_to_congress():
    """Test year to congress conversion."""
    current_year = datetime.now().year
    assert year_to_congress(current_year) >= 119
    assert year_to_congress(2000) == 106
    assert year_to_congress(1993) == 103
    with pytest.raises(ValueError):
        year_to_congress(1930)


@pytest.mark.record_http
def test_congress_bills_fetcher(credentials=test_credentials):
    """Test Congress Bills fetcher."""
    params = {
        "limit": 1,
    }

    fetcher = CongressBillsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_congress_bill_info_fetcher(credentials=test_credentials):
    """Test Congress Bill Info fetcher."""
    params = {
        "bill_url": "119/s/1947",
    }

    fetcher = CongressBillInfoFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_congress_bill_text_fetcher(credentials=test_credentials):
    """Test Congress Bill Text fetcher."""
    params = {
        "urls": ["https://www.congress.gov/119/bills/s1947/BILLS-119s1947is.pdf"],
    }

    fetcher = CongressBillTextFetcher()
    result = fetcher.test(params, credentials)
    assert result is None
