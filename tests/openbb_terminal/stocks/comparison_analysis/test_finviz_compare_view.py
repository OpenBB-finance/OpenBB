# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.comparison_analysis import finviz_compare_view
from openbb_terminal import helper_funcs


@pytest.mark.default_cassette("test_screener")
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "tab",
    [True, False],
)
def test_screener(mocker, tab):
    mocker.patch.object(target=helper_funcs.obbff, attribute="USE_TABULATE_DF", new=tab)
    finviz_compare_view.screener(
        similar=["TSLA", "GM"],
        data_type="overview",
        export="",
    )


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_screener_empty(mocker):
    target = "openbb_terminal.stocks.comparison_analysis.finviz_compare_model.get_comparison_data"
    mocker.patch(target=target, return_value=pd.DataFrame())

    finviz_compare_view.screener(
        similar=["TSLA", "GM"],
        data_type="overview",
        export="",
    )
