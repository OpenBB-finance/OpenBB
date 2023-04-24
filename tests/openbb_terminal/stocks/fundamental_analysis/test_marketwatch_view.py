# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.fundamental_analysis import marketwatch_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [("token", "MOCK_TOKEN")],
    }


@pytest.mark.record_http
def test_display_sean_seah_warnings():
    marketwatch_view.display_sean_seah_warnings("TSLA")
    assert True
