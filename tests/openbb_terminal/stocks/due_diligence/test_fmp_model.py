# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.due_diligence import fmp_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": [
            ("apikey", "MOCK_API_KEY"),
        ]
    }


@pytest.mark.vcr
def test_get_rating(recorder):
    result_df = fmp_model.get_rating(ticker="TSLA")

    recorder.capture(result_df)
