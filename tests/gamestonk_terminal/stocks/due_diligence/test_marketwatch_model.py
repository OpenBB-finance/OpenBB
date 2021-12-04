# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
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
def test_get_rating_over_time(default_csv_path):
    result_df = marketwatch_model.get_sec_filings(ticker="TSLA")

    # result_df.to_csv(default_csv_path, index=True)
    expected_df = pd.read_csv(
        default_csv_path, index_col="Filing Date", na_filter=False
    )

    pd.testing.assert_frame_equal(result_df, expected_df)
