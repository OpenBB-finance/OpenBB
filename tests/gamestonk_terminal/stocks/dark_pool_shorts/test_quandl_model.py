# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.dark_pool_shorts import quandl_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("x-api-token", "MOCK_API_TOKEN")],
    }


@pytest.mark.vcr
@pytest.mark.parametrize(
    "nyse",
    [True, False],
)
def test_get_short_interest(nyse, recorder):
    result_df = quandl_model.get_short_interest(
        ticker="PM",
        nyse=nyse,
    )

    recorder.capture(result_df)
