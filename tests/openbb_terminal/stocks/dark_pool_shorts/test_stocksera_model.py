# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.dark_pool_shorts import stocksera_model


@pytest.mark.vcr
def test_get_cost_to_borrow(recorder):
    result_df = stocksera_model.get_cost_to_borrow("TSLA")

    recorder.capture(result_df)
