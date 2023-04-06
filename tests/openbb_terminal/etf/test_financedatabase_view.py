# IMPORTATION STANDARD


# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.core.session.current_user import (
    PreferencesModel,
    copy_user,
)
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
    preferences = PreferencesModel(USE_TABULATE_DF=False)
    mock_current_user = copy_user(preferences=preferences)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
    )
    financedatabase_view.display_etf_by_name(name, limit=5, export="")


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "description",
    ["oil", "banks"],
)
def test_display_etf_by_description(description, mocker):
    preferences = PreferencesModel(USE_TABULATE_DF=False)
    mock_current_user = copy_user(preferences=preferences)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
    )
    financedatabase_view.display_etf_by_description(description, limit=5, export="")


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "category",
    [
        "Bonds",
        "Materials",
    ],
)
def test_display_etf_by_category(category, mocker):
    preferences = PreferencesModel(USE_TABULATE_DF=False)
    mock_current_user = copy_user(preferences=preferences)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
    )
    financedatabase_view.display_etf_by_category(category, limit=5, export="")
