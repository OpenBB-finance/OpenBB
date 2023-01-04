# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.portfolio import portfolio_helper


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("period1", "1598220000"),
            ("period2", "1635980400"),
        ],
    }


def test_clean_name(recorder):
    result = portfolio_helper.clean_name("beta_hello")
    recorder.capture(result)


@pytest.mark.vcr
def test_is_ticker():
    result = portfolio_helper.is_ticker("aapl")
    assert result
