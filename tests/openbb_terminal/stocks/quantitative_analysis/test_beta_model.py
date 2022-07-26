# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.quantitative_analysis.beta_model import beta_model


@pytest.mark.vcr
def test_beta_model(recorder):
    stock = pd.DataFrame.from_dict({"close": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]})
    ref = pd.DataFrame.from_dict({"close": [2, 3, 5, 7, 7, 9, 20, -2, -5, 0]})

    result_tuple = beta_model(
        stock_ticker="TSLA", ref_ticker="XLK", stock=stock, ref=ref
    )
    recorder.capture(result_tuple)
