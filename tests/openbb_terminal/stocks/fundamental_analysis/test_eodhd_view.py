"""Test the EODHD view."""

import pytest

from openbb_terminal.stocks.fundamental_analysis import eodhd_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": [
            ("api_token", "MOCK_API_KEY"),
        ],
    }


# Only works with a premium key
@pytest.mark.record_http
@pytest.mark.parametrize(
    "symbol, statement, kwargs",
    [
        ("PM", "Income_Statement", {}),
    ],
)
def test_display_fundamentals_fail(symbol, statement, kwargs):
    eodhd_view.display_fundamentals(symbol=symbol, statement=statement, **kwargs)
