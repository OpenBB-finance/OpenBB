# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.discovery import shortinterest_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr()
@pytest.mark.record_stdout
def test_low_float():
    shortinterest_view.low_float(limit=2, export="")


@pytest.mark.vcr()
@pytest.mark.record_stdout
def test_hot_penny_stocks():
    shortinterest_view.hot_penny_stocks(limit=2, export="")
