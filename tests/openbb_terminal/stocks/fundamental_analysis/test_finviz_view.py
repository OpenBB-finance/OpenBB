# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import finviz.main_func
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.fundamental_analysis import finviz_view
from openbb_terminal import helper_funcs


@pytest.mark.vcr
@pytest.mark.parametrize(
    "use_tab",
    [True, False],
)
def test_display_screen_data(mocker, use_tab):
    # REMOVE FINVIZ STOCK_PAGE CACHE
    mocker.patch.object(target=finviz.main_func, attribute="STOCK_PAGE", new={})
    mocker.patch.object(
        target=helper_funcs.obbff, attribute="USE_TABULATE_DF", new=use_tab
    )
    finviz_view.display_screen_data(ticker="AAPL", export="")
