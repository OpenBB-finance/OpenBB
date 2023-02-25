# IMPORTATION STANDARD
import dataclasses

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.core.models.preferences_model import PreferencesModel
from openbb_terminal.core.session.current_user import get_current_user

# IMPORTATION INTERNAL
from openbb_terminal.stocks.options import fdscanner_view

# pylint: disable=E1101


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.default_cassette("test_display_options")
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "toggle",
    [True, False],
)
def test_display_options(mocker, toggle):
    # MOCK CHARTS
    current_user = get_current_user()
    preference = PreferencesModel(USE_TABULATE_DF=toggle)
    user_model = dataclasses.replace(current_user, preference=preference)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.get_current_user",
        return_value=user_model,
    )

    # MOCK EXPORT_DATA
    mocker.patch(
        target="openbb_terminal.stocks.options.fdscanner_view.export_data",
    )

    fdscanner_view.display_options(
        limit=5,
        sortby=["Vol"],
        export="csv",
        sheet_name=None,
        ascend=True,
        calls_only=toggle,
        puts_only=not toggle,
    )

    fdscanner_view.export_data.assert_called_once()
