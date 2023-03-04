# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.core.session.current_user import (
    PreferencesModel,
    copy_user,
)
from openbb_terminal.stocks.fundamental_analysis import fmp_view


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
def test_valinvest_score():
    fmp_view.valinvest_score(symbol="PM", years=10)


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_filings():
    fmp_view.display_filings()


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "func, kwargs_dict",
    [
        (
            "display_profile",
            {"symbol": "PM"},
        ),
        (
            "display_enterprise",
            {"symbol": "PM", "limit": 5, "quarterly": False},
        ),
        (
            "display_discounted_cash_flow",
            {"symbol": "PM", "limit": 5, "quarterly": False},
        ),
        (
            "display_income_statement",
            {"symbol": "PM", "limit": 5, "quarterly": False},
        ),
        (
            "display_balance_sheet",
            {"symbol": "PM", "limit": 5, "quarterly": False},
        ),
        (
            "display_cash_flow",
            {"symbol": "PM", "limit": 5, "quarterly": False},
        ),
        (
            "display_key_metrics",
            {"symbol": "PM", "limit": 5, "quarterly": False},
        ),
        (
            "display_financial_ratios",
            {"symbol": "PM", "limit": 5, "quarterly": False},
        ),
        (
            "display_financial_statement_growth",
            {"symbol": "PM", "limit": 5, "quarterly": False},
        ),
    ],
)
@pytest.mark.parametrize(
    "use_tab",
    [True, False],
)
def test_check_output(func, kwargs_dict, mocker, use_tab):
    preferences = PreferencesModel(
        USE_TABULATE_DF=use_tab,
        ENABLE_CHECK_API=False,
    )
    mock_current_user = copy_user(preferences=preferences)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
    )

    getattr(fmp_view, func)(**kwargs_dict)


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_rating():
    fmp_view.rating(symbol="TSLA", limit=5, export=None)
