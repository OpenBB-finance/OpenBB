# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.fundamental_analysis.financial_modeling_prep import (
    fmp_view,
)
from gamestonk_terminal import helper_funcs


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
    fmp_view.valinvest_score(ticker="PM")


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "func, kwargs_dict",
    [
        (
            "display_profile",
            {"ticker": "PM"},
        ),
        (
            "display_quote",
            {"ticker": "PM"},
        ),
        (
            "display_enterprise",
            {"ticker": "PM", "number": 5, "quarterly": False},
        ),
        (
            "display_discounted_cash_flow",
            {"ticker": "PM", "number": 5, "quarterly": False},
        ),
        (
            "display_income_statement",
            {"ticker": "PM", "number": 5, "quarterly": False},
        ),
        (
            "display_balance_sheet",
            {"ticker": "PM", "number": 5, "quarterly": False},
        ),
        (
            "display_cash_flow",
            {"ticker": "PM", "number": 5, "quarterly": False},
        ),
        (
            "display_key_metrics",
            {"ticker": "PM", "number": 5, "quarterly": False},
        ),
        (
            "display_financial_ratios",
            {"ticker": "PM", "number": 5, "quarterly": False},
        ),
        (
            "display_financial_statement_growth",
            {"ticker": "PM", "number": 5, "quarterly": False},
        ),
    ],
)
@pytest.mark.parametrize(
    "use_tab",
    [True, False],
)
def test_check_output(func, kwargs_dict, monkeypatch, use_tab):
    monkeypatch.setattr(helper_funcs.gtff, "USE_TABULATE_DF", use_tab)
    getattr(fmp_view, func)(**kwargs_dict)
