"""Test the EODHD model."""

import pytest

from openbb_terminal.stocks.fundamental_analysis import eodhd_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": [
            ("api_token", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.record_http
def test_get_financials():
    """Test get_financials."""
    eodhd_model.get_financials(symbol="TSLA", statement="balance")
