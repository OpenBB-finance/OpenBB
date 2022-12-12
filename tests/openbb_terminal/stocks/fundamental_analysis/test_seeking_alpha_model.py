# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.fundamental_analysis import seeking_alpha_model


@pytest.fixture(scope="module")
# might not be necessary
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr
def test_get_seekingalpha_id(recorder):
    seeking_id = seeking_alpha_model.get_seekingalpha_id(ticker="JNJ")

    recorder.capture(seeking_id)


@pytest.mark.vcr
def test_check_get_estimates_eps(recorder):
    df = seeking_alpha_model.get_estimates_eps(ticker="JNJ")
    recorder.capture(df)


@pytest.mark.vcr
def test_check_get_estimates_rev(recorder):
    df = seeking_alpha_model.get_estimates_eps(ticker="JNJ")
    recorder.capture(df)
