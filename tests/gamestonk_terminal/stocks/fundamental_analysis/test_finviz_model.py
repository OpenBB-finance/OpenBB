# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.fundamental_analysis import finviz_model


@pytest.mark.vcr
def test_get_data(recorder):
    result_df = finviz_model.get_data(ticker="PM")

    recorder.capture(result_df)
