# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.discovery import yahoofinance_view


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
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "func",
    [
        "display_gainers",
        "display_losers",
        "display_ugs",
        "display_gtech",
        "display_active",
        "display_ulc",
        "display_asc",
    ],
)
def test_call_func(func):
    getattr(yahoofinance_view, func)(num_stocks=2, export="")


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "func, mocked_func",
    [
        ("display_gainers", "get_gainers"),
        ("display_losers", "get_losers"),
        ("display_ugs", "get_ugs"),
        ("display_gtech", "get_gtech"),
        ("display_active", "get_active"),
        ("display_ulc", "get_ulc"),
        ("display_asc", "get_asc"),
    ],
)
def test_func_empty_df(func, mocked_func, mocker):
    view = "openbb_terminal.stocks.discovery.yahoofinance_view.yahoofinance_model."
    mocker.patch(
        view + mocked_func,
        return_value=pd.DataFrame(),
    )

    getattr(yahoofinance_view, func)(num_stocks=2, export="")
