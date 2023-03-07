# IMPORTATION STANDARD


# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.core.session.current_user import (
    PreferencesModel,
    copy_user,
)
from openbb_terminal.stocks.discovery import nasdaq_view


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
    preferences = PreferencesModel(
        USE_TABULATE_DF=use_tab,
        ENABLE_CHECK_API=False,
    )
    mock_current_user = copy_user(preferences=preferences)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
    )

    nasdaq_view.display_top_retail(limit=3, export="")


@pytest.mark.default_cassette("test_display_dividend_calendar")
@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_dividend_calendar(mocker):
    preferences = PreferencesModel(USE_TABULATE_DF=False)
    mock_current_user = copy_user(preferences=preferences)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
    )

    nasdaq_view.display_dividend_calendar(date="2022-01-11", limit=2)
