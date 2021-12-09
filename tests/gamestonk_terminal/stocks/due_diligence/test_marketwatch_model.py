# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.due_diligence import marketwatch_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [("token", "MOCK_TOKEN")],
    }


@pytest.mark.vcr
def test_get_rating_over_time(recorder):
    result_df = marketwatch_model.get_sec_filings(ticker="TSLA")
    recorder.capture(result_df)
