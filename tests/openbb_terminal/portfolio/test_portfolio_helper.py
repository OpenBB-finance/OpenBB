# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.portfolio import portfolio_helper


def test_clean_name(recorder):
    result = portfolio_helper.clean_name("beta_hello")
    recorder.capture(result)


@pytest.mark.vcr
def test_is_ticker():
    result = portfolio_helper.is_ticker("aapl")
    assert result
