# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.discovery import fmp_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("apikey", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.vcr
@pytest.mark.parametrize(
    "func, kwargs_dict",
    [
        (
            "get_filings",
            {},
        ),
    ],
)
@pytest.mark.record_stdout
def test_valid_df(func, kwargs_dict):
    result_df = getattr(fmp_model, func)(**kwargs_dict)
    assert isinstance(result_df, pd.DataFrame)
