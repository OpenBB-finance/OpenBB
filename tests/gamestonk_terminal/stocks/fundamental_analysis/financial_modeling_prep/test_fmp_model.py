# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest
import numpy as np
import pandas as pd

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.fundamental_analysis.financial_modeling_prep import (
    fmp_model,
)


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("apikey", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.vcr
def test_get_score():
    result = fmp_model.get_score(ticker="PM")
    assert isinstance(result, np.number)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "func, kwargs_dict",
    [
        (
            "get_profile",
            {"ticker": "PM"},
        ),
        (
            "get_quote",
            {"ticker": "PM"},
        ),
        (
            "get_enterprise",
            {"ticker": "PM", "number": 5, "quarterly": False},
        ),
        (
            "get_dcf",
            {"ticker": "PM", "number": 5, "quarterly": False},
        ),
        (
            "get_income",
            {"ticker": "PM", "number": 5, "quarterly": False},
        ),
        (
            "get_balance",
            {"ticker": "PM", "number": 5, "quarterly": False},
        ),
        (
            "get_cash",
            {"ticker": "PM", "number": 5, "quarterly": False},
        ),
        (
            "get_key_metrics",
            {"ticker": "PM", "number": 5, "quarterly": False},
        ),
        (
            "get_key_ratios",
            {"ticker": "PM", "number": 5, "quarterly": False},
        ),
        (
            "get_financial_growth",
            {"ticker": "PM", "number": 5, "quarterly": False},
        ),
    ],
)
def test_valid_df(func, kwargs_dict):
    result_df = getattr(fmp_model, func)(**kwargs_dict)
    assert isinstance(result_df, pd.DataFrame)
    assert not result_df.empty
