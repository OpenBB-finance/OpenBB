# IMPORTATION STANDARD
import dataclasses

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.core.models.preferences_model import PreferencesModel
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.etf.screener import screener_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "preset,num_to_show,sortby,ascend",
    [
        ("etf_config.ini", 5, "Assets", True),
        ("etf_config.ini", 10, "Expense", False),
        ("etf_config.ini", 7, "Volume", True),
    ],
)
def test_view_screener(preset, num_to_show, sortby, ascend, mocker):
    current_user = get_current_user()
    preference = PreferencesModel(USE_TABULATE_DF=False)
    user_model = dataclasses.replace(current_user, preference=preference)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.get_current_user",
        return_value=user_model,
    )
    screener_view.view_screener(
        preset, num_to_show=num_to_show, sortby=sortby, ascend=ascend, export=""
    )
