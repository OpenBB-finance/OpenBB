# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.discovery import yahoofinance_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("period1", "1598220000"),
            ("period2", "1635980400"),
        ],
    }


@pytest.mark.vcr
@pytest.mark.parametrize(
    "func",
    [
        "get_gainers",
        "get_losers",
        "get_ugs",
        "get_gtech",
        "get_active",
        "get_ulc",
        "get_asc",
    ],
)
def test_call_func(func, recorder):
    result_df = getattr(yahoofinance_model, func)()

    recorder.capture(result_df)
