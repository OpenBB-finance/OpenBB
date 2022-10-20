# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest
import pandas as pd

# IMPORTATION INTERNAL
from openbb_terminal.stocks.dark_pool_shorts import stocksera_view


@pytest.mark.vcr
def test_plot_cost_to_borrow():
    df = pd.DataFrame()
    stocksera_view.plot_cost_to_borrow("TSLA", df)


@pytest.mark.vcr
def test_cost_to_borrow():
    stocksera_view.cost_to_borrow("TSLA")
