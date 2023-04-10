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
@pytest.mark.parametrize(
    "symbol, statement, ratios",
    [
        ("TSLA", "balance", False),
        ("TSLA", "income", False),
        ("TSLA", "cash", False),
        ("TSLA", "balance", True),
        ("TSLA", "income", True),
        ("TSLA", "cash", True),
    ],
)
def test_get_financials(symbol, statement, ratios):
    """Test get_financials."""
    eodhd_model.get_financials(symbol=symbol, statement=statement, ratios=ratios)
