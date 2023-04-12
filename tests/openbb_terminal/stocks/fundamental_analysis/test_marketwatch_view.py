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


@pytest.mark.record_http
@pytest.mark.parametrize(
    "symbol, limit, year, form_group",
    [
        ("TSLA", 5, 2020, "annual"),
    ],
)
def test_sec_filings(symbol, limit, year, form_group):
    marketwatch_view.sec_filings(
        symbol=symbol, limit=limit, year=year, form_group=form_group
    )
    assert True
