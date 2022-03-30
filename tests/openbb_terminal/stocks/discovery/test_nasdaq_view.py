# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.discovery import nasdaq_view
from openbb_terminal import helper_funcs


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [("api_key", "MOCK_API"), ("date", "MOCK_DATE")],
    }


@pytest.mark.default_cassette("test_display_top_retail")
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize("use_tab", [True, False])
def test_display_top_retail(mocker, use_tab):
    mocker.patch.object(
        target=helper_funcs.obbff, attribute="USE_TABULATE_DF", new=use_tab
    )

    nasdaq_view.display_top_retail(n_days=3, export="")


@pytest.mark.default_cassette("test_display_dividend_calendar")
@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_dividend_calendar(mocker):
    mocker.patch.object(
        target=helper_funcs.obbff, attribute="USE_TABULATE_DF", new=False
    )

    nasdaq_view.display_dividend_calendar(date="2022-01-11", limit=2)
