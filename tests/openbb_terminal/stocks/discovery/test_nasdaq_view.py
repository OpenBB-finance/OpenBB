# IMPORTATION STANDARD
import dataclasses

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.core.models.preferences_model import PreferencesModel
from openbb_terminal.core.session.current_user import get_current_user
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
    current_user = get_current_user()
    preference = PreferencesModel(USE_TABULATE_DF=use_tab)
    user_model = dataclasses.replace(current_user, preference=preference)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.get_current_user",
        return_value=user_model,
    )

    nasdaq_view.display_top_retail(limit=3, export="")


@pytest.mark.default_cassette("test_display_dividend_calendar")
@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_dividend_calendar(mocker):
    current_user = get_current_user()
    preference = PreferencesModel(USE_TABULATE_DF=False)
    user_model = dataclasses.replace(current_user, preference=preference)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.get_current_user",
        return_value=user_model,
    )

    nasdaq_view.display_dividend_calendar(date="2022-01-11", limit=2)
