# IMPORTATION STANDARD
import dataclasses

# IMPORTATION THIRDPARTY
import pytest

from openbb_terminal import helper_funcs

# IMPORTATION INTERNAL
from openbb_terminal.core.models.preferences_model import PreferencesModel
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.stocks.options import chartexchange_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.default_cassette("test_display_raw")
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "tab",
    [True, False],
)
def test_display_raw(mocker, tab):
    # MOCK CHARTS
    current_user = get_current_user()
    preference = PreferencesModel(USE_TABULATE_DF=tab)
    user_model = dataclasses.replace(current_user, preference=preference)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.get_current_user",
        return_value=user_model,
    )

    # MOCK VISUALIZE_OUTPUT
    mocker.patch(
        target="openbb_terminal.stocks.options.chartexchange_view.theme.visualize_output"
    )

    # MOCK PLOT_CHART
    mocker.patch(target="openbb_terminal.stocks.options.chartexchange_view.plot_chart")

    chartexchange_view.display_raw(
        export="",
        symbol="GME",
        expiry="2021-02-05",
        call=True,
        price=90,
    )
