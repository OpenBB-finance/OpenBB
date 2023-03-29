# IMPORTATION STANDARD


# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.core.session.current_user import (
    PreferencesModel,
    copy_user,
)
from openbb_terminal.etf.discovery import wsj_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "sort_type",
    [
        "gainers",
        "decliners",
        "active",
    ],
)
def test_show_top_mover(sort_type, mocker):
    preferences = PreferencesModel(USE_TABULATE_DF=False)
    mock_current_user = copy_user(preferences=preferences)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
    )
    wsj_view.show_top_mover(sort_type, limit=5, export="")
