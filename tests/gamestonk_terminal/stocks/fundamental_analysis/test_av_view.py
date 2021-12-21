# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import numpy as np
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.fundamental_analysis import av_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("apikey", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "func, kwargs_dict",
    [
        (
            "display_overview",
            {"ticker": "TSLA"},
        ),
        (
            "display_key",
            {"ticker": "TSLA"},
        ),
        (
            "display_income_statement",
            {"ticker": "TSLA", "limit": 5, "quarterly": True},
        ),
        (
            "display_income_statement",
            {"ticker": "TSLA", "limit": 5, "quarterly": False},
        ),
        (
            "display_balance_sheet",
            {"ticker": "TSLA", "limit": 5, "quarterly": True},
        ),
        (
            "display_balance_sheet",
            {"ticker": "TSLA", "limit": 5, "quarterly": False},
        ),
        (
            "display_cash_flow",
            {"ticker": "TSLA", "limit": 5, "quarterly": True},
        ),
        (
            "display_cash_flow",
            {"ticker": "TSLA", "limit": 5, "quarterly": False},
        ),
        (
            "display_earnings",
            {"ticker": "TSLA", "limit": 5, "quarterly": True},
        ),
        (
            "display_earnings",
            {"ticker": "TSLA", "limit": 5, "quarterly": False},
        ),
    ],
)
@pytest.mark.parametrize(
    "use_tab",
    [True, False],
)
def test_check_output(func, kwargs_dict, monkeypatch, use_tab):
    monkeypatch.setattr(av_view.gtff, "USE_TABULATE_DF", use_tab)
    getattr(av_view, func)(**kwargs_dict)


@pytest.mark.skip
@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "func, mocked_func, kwargs_dict",
    [
        (
            "display_overview",
            "get_overview",
            {"ticker": "TSLA"},
        ),
        (
            "display_key",
            "get_key_metrics",
            {"ticker": "TSLA"},
        ),
        (
            "display_earnings",
            "get_earnings",
            {"ticker": "TSLA", "limit": 5, "quarterly": False},
        ),
    ],
)
def test_check_empty_df(func, kwargs_dict, mocked_func, mocker):
    mocker.patch(
        "gamestonk_terminal.stocks.fundamental_analysis.av_view.av_model."
        + mocked_func,
        return_value=pd.DataFrame(),
    )
    getattr(av_view, func)(**kwargs_dict)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "ratios, zscore",
    [
        (
            {
                "DSRI": np.nan,
                "GMI": np.nan,
                "AQI": np.nan,
                "SGI": np.nan,
                "DEPI": np.nan,
                "SGAI": np.nan,
                "LVGI": np.nan,
                "TATA": np.nan,
                "MSCORE": np.nan,
            },
            np.nan,
        ),
        ({"MSCORE": -1}, 0.1),
        ({"AQI": 1, "MSCORE": -2}, 0.1),
        ({"MSCORE": -3}, 1),
    ],
)
def test_display_fraud(mocker, ratios, zscore):
    mocker.patch(
        "gamestonk_terminal.stocks.fundamental_analysis.av_view.av_model.get_fraud_ratios",
        return_value=(ratios, zscore),
    )
    av_view.display_fraud(ticker="TSLA")
