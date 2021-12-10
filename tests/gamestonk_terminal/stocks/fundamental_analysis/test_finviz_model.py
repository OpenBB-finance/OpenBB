# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import finviz.main_func
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.fundamental_analysis import finviz_model


@pytest.mark.vcr
def test_get_data(mocker, recorder):
    # REMOVE FINVIZ STOCK_PAGE CACHE
    mocker.patch.object(target=finviz.main_func, attribute="STOCK_PAGE", new={})
    result_df = finviz_model.get_data(ticker="PM")

    recorder.capture(result_df)
