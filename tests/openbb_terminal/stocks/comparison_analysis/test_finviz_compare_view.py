# IMPORTATION STANDARD


# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.core.session.current_user import (
    PreferencesModel,
    copy_user,
)
from openbb_terminal.stocks.comparison_analysis import finviz_compare_view


@pytest.mark.skip(
    reason="Column 'Market Cap' of output has exponential notation format in Windows contrary to Ubuntu."
)
@pytest.mark.default_cassette("test_screener")
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "tab",
    [True, False],
)
def test_screener(mocker, tab):
    preferences = PreferencesModel(USE_TABULATE_DF=tab)
    mock_current_user = copy_user(preferences=preferences)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
    )

    finviz_compare_view.screener(
        similar=["TSLA", "GM"],
        data_type="overview",
        export="",
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_screener_empty(mocker):
    target = "openbb_terminal.stocks.comparison_analysis.finviz_compare_model.get_comparison_data"
    mocker.patch(target=target, return_value=pd.DataFrame())

    finviz_compare_view.screener(
        similar=["TSLA", "GM"],
        data_type="overview",
        export="",
    )
