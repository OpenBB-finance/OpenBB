# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.fundamental_analysis import fmp_view
from openbb_terminal import helper_funcs


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
    fmp_view.valinvest_score(symbol="PM")


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
            "display_quote",
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
def test_check_output(func, kwargs_dict, monkeypatch, use_tab):
    monkeypatch.setattr(helper_funcs.obbff, "USE_TABULATE_DF", use_tab)
    getattr(fmp_view, func)(**kwargs_dict)
