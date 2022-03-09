# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import finviz.main_func
import pytest
import pandas as pd

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.fundamental_analysis import finviz_model


@pytest.mark.vcr
def test_get_data(mocker):
    # REMOVE FINVIZ STOCK_PAGE CACHE
    mocker.patch.object(target=finviz.main_func, attribute="STOCK_PAGE", new={})
    result_df = finviz_model.get_data(ticker="AAPL")

    assert isinstance(result_df, pd.DataFrame)
    assert result_df.empty is False
