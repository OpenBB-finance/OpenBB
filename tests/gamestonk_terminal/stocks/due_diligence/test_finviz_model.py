# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.due_diligence import finviz_model


@pytest.mark.vcr
def test_get_news(recorder):
    result_dict = finviz_model.get_news(ticker="TSLA")

    recorder.capture(result_dict)


@pytest.mark.vcr
def test_get_analyst_data(recorder):
    result_df = finviz_model.get_analyst_data(ticker="TSLA")

    recorder.capture(result_df)
