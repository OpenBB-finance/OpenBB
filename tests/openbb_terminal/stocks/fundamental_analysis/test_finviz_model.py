# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import finviz.main_func
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.fundamental_analysis import finviz_model


@pytest.mark.vcr
def test_get_data(mocker):
    # REMOVE FINVIZ STOCK_PAGE CACHE
    mocker.patch.object(target=finviz.main_func, attribute="STOCK_PAGE", new={})
    result_df = finviz_model.get_data(symbol="AAPL")

    assert isinstance(result_df, pd.DataFrame)
    assert result_df.empty is False


@pytest.mark.record_http
def test_get_analyst_data(mocker):
    # REMOVE FINVIZ STOCK_PAGE CACHE
    mocker.patch.object(target=finviz.main_func, attribute="STOCK_PAGE", new={})
    result_df = finviz_model.get_analyst_data(symbol="AAPL")

    assert isinstance(result_df, pd.DataFrame)
    assert not result_df.empty


@pytest.mark.record_http
def test_get_analyst_price_targets_workaround(mocker):
    # REMOVE FINVIZ STOCK_PAGE CACHE
    mocker.patch.object(target=finviz.main_func, attribute="STOCK_PAGE", new={})
    result = finviz_model.get_analyst_price_targets_workaround(ticker="AAPL")

    # assert it is a List[Dict]
    assert isinstance(result, list)
    assert isinstance(result[0], dict)


@pytest.mark.record_http
def test_get_news(mocker):
    # REMOVE FINVIZ STOCK_PAGE CACHE
    mocker.patch.object(target=finviz.main_func, attribute="STOCK_PAGE", new={})
    result = finviz_model.get_news(symbol="AAPL")

    assert isinstance(result, list)
