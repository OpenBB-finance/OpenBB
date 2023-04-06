# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.dark_pool_shorts import quandl_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("x-api-token", "MOCK_API_TOKEN")],
    }


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "raw",
    [True, False],
)
@pytest.mark.parametrize(
    "nyse",
    [True, False],
)
def test_short_interest(nyse, raw):
    quandl_view.short_interest(
        symbol="PM",
        nyse=nyse,
        limit=2,
        raw=raw,
        export="",
        sheet_name=None,
    )
