# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.comparison_analysis import finbrain_model


@pytest.mark.vcr
def test_get_sentiments(recorder):
    result_df = finbrain_model.get_sentiments(tickers=["TSLA"])

    recorder.capture(result_df)
