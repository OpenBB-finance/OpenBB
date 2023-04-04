# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.common.ultima_newsmonitor_model import (
    get_company_info,
    get_news,
    supported_terms,
)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "term",
    [
        (""),
        ("AAPL"),
        ("TSLA"),
        ("FCX"),
        ("asdf$#"),
    ],
)
def test_get_news(term, recorder):
    df = get_news(term=term)
    recorder.capture(df)


# @pytest.mark.default_cassette("test_supported_terms.yaml")
# @pytest.mark.vcr
def test_supported_terms(recorder):
    r = supported_terms()
    recorder.capture(r)


# @pytest.mark.default_cassette("test_get_company_info.yaml")
# @pytest.mark.vcr
@pytest.mark.parametrize(
    "ticker",
    ["AAPL", "TSLA", "FCX", "asdf$#"],
)
def test_get_company_info(ticker, recorder):
    df = get_company_info(ticker=ticker)
    recorder.capture(df)
