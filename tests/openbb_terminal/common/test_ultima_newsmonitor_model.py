# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.common.ultima_newsmonitor_model import get_news, supported_terms, get_company_info


# @pytest.mark.default_cassette("test_get_news.yaml")
# @pytest.mark.vcr
@pytest.mark.parametrize(
    "term, sources",
    [
        ("", ""),
        ("AAPL", ""),
        ("TSLA", ""),
        ("FCX", ""),
        ("asdf$#", ""),
    ],
)
def test_get_news(term, sources, recorder):
    df = get_news(term=term, sources=sources)
    recorder.capture(df)


# @pytest.mark.default_cassette("test_supported_terms.yaml")
# @pytest.mark.vcr
def test_supported_terms(recorder):
    r = supported_terms()
    recorder.capture(r)


# @pytest.mark.default_cassette("test_get_company_info.yaml")
# @pytest.mark.vcr
@pytest.mark.parametrize("ticker", ["AAPL", "TSLA", "FCX", "asdf$#"], )
def test_get_company_info(ticker, recorder):
    df = get_company_info(ticker=ticker)
    recorder.capture(df)
