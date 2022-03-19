# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.economy import alphavantage_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [("apikey", "MOCK_API_KEY")],
    }


@pytest.mark.vcr
def test_get_screener_data(recorder):
    result_df = alphavantage_model.get_sector_data()

    recorder.capture(result_df)
