# IMPORTATION STANDARD


# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.core.session.current_user import (
    PreferencesModel,
    copy_user,
)
from openbb_terminal.stocks.fundamental_analysis import av_view


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
            {"symbol": "TSLA"},
        ),
        (
            "display_key",
            {"symbol": "TSLA"},
        ),
        (
            "display_income_statement",
            {"symbol": "TSLA", "limit": 5, "quarterly": True},
        ),
        (
            "display_income_statement",
            {"symbol": "TSLA", "limit": 5, "quarterly": False},
        ),
        (
            "display_balance_sheet",
            {"symbol": "TSLA", "limit": 5, "quarterly": True},
        ),
        (
            "display_balance_sheet",
            {"symbol": "TSLA", "limit": 5, "quarterly": False},
        ),
        (
            "display_cash_flow",
            {"symbol": "TSLA", "limit": 5, "quarterly": True},
        ),
        (
            "display_cash_flow",
            {"symbol": "TSLA", "limit": 5, "quarterly": False},
        ),
        (
            "display_earnings",
            {"symbol": "TSLA", "limit": 5, "quarterly": True},
        ),
        (
            "display_earnings",
            {"symbol": "TSLA", "limit": 5, "quarterly": False},
        ),
    ],
)
@pytest.mark.parametrize(
    "use_tab",
    [True, False],
)
def test_check_output(func, kwargs_dict, mocker, use_tab):
    preferences = PreferencesModel(USE_TABULATE_DF=use_tab)
    mock_current_user = copy_user(preferences=preferences)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
    )
    getattr(av_view, func)(**kwargs_dict)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "func, mocked_func, kwargs_dict",
    [
        (
            "display_overview",
            "get_overview",
            {"symbol": "TSLA"},
        ),
        (
            "display_key",
            "get_key_metrics",
            {"symbol": "TSLA"},
        ),
        (
            "display_earnings",
            "get_earnings",
            {"symbol": "TSLA", "limit": 5, "quarterly": False},
        ),
    ],
)
def test_check_empty_df(func, kwargs_dict, mocked_func, mocker):
    mocker.patch(
        "openbb_terminal.stocks.fundamental_analysis.av_view.av_model." + mocked_func,
        return_value=pd.DataFrame(),
    )
    getattr(av_view, func)(**kwargs_dict)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "df",
    [
        (pd.DataFrame()),
    ],
)
def test_display_fraud(mocker, df):
    mocker.patch(
        "openbb_terminal.stocks.fundamental_analysis.av_view.av_model.get_fraud_ratios",
        return_value=(df),
    )
    av_view.display_fraud(symbol="TSLA")


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "df",
    [
        (pd.DataFrame()),
    ],
)
def test_dupont(mocker, df):
    mocker.patch(
        "openbb_terminal.stocks.fundamental_analysis.av_view.av_model.get_dupont",
        return_value=(df),
    )
    av_view.display_dupont(symbol="TSLA")
