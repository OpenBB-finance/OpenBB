# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.due_diligence import fmp_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": [
            ("apikey", "MOCK_API_KEY"),
        ]
    }


@pytest.mark.vcr
def test_get_rating(default_csv_path):
    result_df = fmp_model.get_rating(ticker="TSLA")

    # result_df.to_csv(default_csv_path, index=True)
    expected_df = pd.read_csv(default_csv_path, index_col="date")

    pd.testing.assert_frame_equal(result_df, expected_df)
