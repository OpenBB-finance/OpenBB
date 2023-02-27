# IMPORTATION STANDARD
import dataclasses

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.core.models.preferences_model import PreferencesModel
from openbb_terminal.core.session.current_user import get_current_user
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
    current_user = get_current_user()
    preference = PreferencesModel(USE_TABULATE_DF=False)
    user_model = dataclasses.replace(current_user, preference=preference)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.get_current_user",
        return_value=user_model,
    )
    wsj_view.show_top_mover(sort_type, limit=5, export="")
