# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.comparison_analysis import finviz_compare_view


@pytest.mark.default_cassette("test_screener")
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "tab",
    [True, False],
)
def test_screener(mocker, tab):
    mocker.patch.object(
        target=finviz_compare_view.gtff, attribute="USE_TABULATE_DF", new=tab
    )
    finviz_compare_view.screener(
        similar=["TSLA", "GM"],
        data_type="overview",
        export="",
    )


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_screener_empty(mocker):
    target = "gamestonk_terminal.stocks.comparison_analysis.finviz_compare_model.get_comparison_data"
    mocker.patch(target=target, return_value=pd.DataFrame())

    finviz_compare_view.screener(
        similar=["TSLA", "GM"],
        data_type="overview",
        export="",
    )
