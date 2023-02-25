# IMPORTATION STANDARD
import dataclasses

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.core.models.preferences_model import PreferencesModel
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.etf import financedatabase_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "name",
    ["oil", "banks"],
)
def test_display_etf_by_name(name, mocker):
    current_user = get_current_user()
    preference = PreferencesModel(USE_TABULATE_DF=False)
    user_model = dataclasses.replace(current_user, preference=preference)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.get_current_user",
        return_value=user_model,
    )
    financedatabase_view.display_etf_by_name(name, limit=5, export="")


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "description",
    ["oil", "banks"],
)
def test_display_etf_by_description(description, mocker):
    current_user = get_current_user()
    preference = PreferencesModel(USE_TABULATE_DF=False)
    user_model = dataclasses.replace(current_user, preference=preference)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.get_current_user",
        return_value=user_model,
    )
    financedatabase_view.display_etf_by_description(description, limit=5, export="")


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "category",
    [
        "Bank Loan",
        "Bear Market",
    ],
)
def test_display_etf_by_category(category, mocker):
    current_user = get_current_user()
    preference = PreferencesModel(USE_TABULATE_DF=False)
    user_model = dataclasses.replace(current_user, preference=preference)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.get_current_user",
        return_value=user_model,
    )
    financedatabase_view.display_etf_by_category(category, limit=5, export="")
