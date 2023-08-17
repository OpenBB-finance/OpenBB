# IMPORTATION STANDARD


# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.core.session.current_user import (
    PreferencesModel,
    copy_user,
)
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
    "raw",
    [True, False],
)
def test_display_raw(mocker, raw):
    # MOCK CHARTS
    preferences = PreferencesModel(USE_TABULATE_DF=raw)
    mock_current_user = copy_user(preferences=preferences)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
    )

    # MOCK PLOT_CHART
    mocker.patch(target="openbb_terminal.stocks.options.chartexchange_view.plot_chart")

    chartexchange_view.display_raw(
        export="", symbol="GME", expiry="2021-02-05", call=True, price=90, raw=raw
    )
