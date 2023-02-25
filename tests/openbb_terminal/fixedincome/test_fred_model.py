import pandas as pd
import pytest

from openbb_terminal.fixedincome import fred_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("api_key", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.vcr
@pytest.mark.parametrize("inflation", [True, False])
def test_yield_curve(recorder, inflation):
    data = fred_model.get_yield_curve(date="2023-02-08", inflation_adjusted=inflation)

    assert isinstance(data, pd.DataFrame)
    recorder.capture(data)
