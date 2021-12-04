# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import numpy as np
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.due_diligence import finviz_model


@pytest.mark.vcr
def test_get_news(default_csv_path):
    result_dict = finviz_model.get_news(ticker="TSLA")
    result_df = pd.DataFrame(result_dict)

    # result_df.to_csv(default_csv_path, index=True)
    expected_df = pd.read_csv(default_csv_path)

    np.array_equal(result_df.values, expected_df.values)


@pytest.mark.vcr
def test_get_analyst_data(default_csv_path):
    result_df = finviz_model.get_analyst_data(ticker="TSLA")

    # result_df.to_csv(default_csv_path, index=True)
    expected_df = pd.read_csv(default_csv_path, index_col="date")

    pd.testing.assert_frame_equal(result_df, expected_df)
