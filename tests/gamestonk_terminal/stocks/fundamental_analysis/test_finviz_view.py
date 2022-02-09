# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import finviz.main_func
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.fundamental_analysis import finviz_view
from gamestonk_terminal import helper_funcs


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "use_tab",
    [True, False],
)
def test_display_screen_data(mocker, use_tab):
    # REMOVE FINVIZ STOCK_PAGE CACHE
    mocker.patch.object(target=finviz.main_func, attribute="STOCK_PAGE", new={})
    mocker.patch.object(
        target=helper_funcs.gtff, attribute="USE_TABULATE_DF", new=use_tab
    )
    finviz_view.display_screen_data(ticker="TSLA", export="")
