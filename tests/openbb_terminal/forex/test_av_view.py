# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.forex import av_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": [
            ("apikey", "MOCK_API_KEY"),
        ]
    }


@pytest.mark.vcr
@pytest.mark.parametrize(
    "from_symbol, to_symbol",
    [
        ("EUR", "USD"),
        ("USD", "JPY"),
        ("GBP", "EUR"),
        ("CHF", "USD"),
    ],
)
def test_display_quote(from_symbol, to_symbol):
    av_view.display_quote(from_symbol=from_symbol, to_symbol=to_symbol)
