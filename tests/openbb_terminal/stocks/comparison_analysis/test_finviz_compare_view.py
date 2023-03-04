# IMPORTATION STANDARD


# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.core.session.current_user import (
    copy_user,
    PreferencesModel,
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
    current_user = get_current_user()
    preferences = PreferencesModel(
        USE_TABULATE_DF=tab,
    )
    user_model = dataclasses.replace(current_user, preferences=preferences)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.get_current_user",
        return_value=user_model,
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
