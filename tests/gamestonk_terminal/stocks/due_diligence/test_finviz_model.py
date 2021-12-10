# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import finviz.main_func
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.due_diligence import finviz_model


@pytest.mark.vcr
def test_get_news(mocker, recorder):
    # REMOVE FINVIZ STOCK_PAGE CACHE
    mocker.patch.object(target=finviz.main_func, attribute="STOCK_PAGE", new={})
    result_dict = finviz_model.get_news(ticker="TSLA")

    recorder.capture(result_dict)


@pytest.mark.vcr
def test_get_analyst_data(mocker, recorder):
    # REMOVE FINVIZ STOCK_PAGE CACHE
    mocker.patch.object(target=finviz.main_func, attribute="STOCK_PAGE", new={})
    result_df = finviz_model.get_analyst_data(ticker="TSLA")

    recorder.capture(result_df)
