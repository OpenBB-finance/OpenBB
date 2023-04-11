# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.fundamental_analysis import yahoo_finance_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("period1", "1598220000"),
            ("period2", "1635980400"),
        ],
    }


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "func",
    [
        "display_shareholders",
        "display_dividends",
        "display_splits",
        "display_mktcap",
    ],
)
@pytest.mark.vcr
@pytest.mark.record_stdout
def test_call_func(func):
    getattr(yahoo_finance_view, func)(symbol="PM")


@pytest.mark.vcr
def test_display_info():
    yahoo_finance_view.display_info(symbol="TSLA")


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "func, mocked_func",
    [
        ("display_dividends", "get_dividends"),
        ("display_splits", "get_splits"),
    ],
)
def test_call_func_empty_df(func, mocker, mocked_func):
    mocker.patch(
        "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_model."
        + mocked_func,
        return_value=pd.DataFrame(),
    )
    getattr(yahoo_finance_view, func)(symbol="PM")


@pytest.mark.record_http
@pytest.mark.record_verify_screen
@pytest.mark.parametrize(
    "symbol, kwargs",
    [
        ("TSLA", {}),
    ],
)
def test_display_shareholders(symbol, kwargs):
    yahoo_finance_view.display_shareholders(symbol=symbol, **kwargs)


@pytest.mark.record_http
@pytest.mark.record_verify_screen
@pytest.mark.parametrize(
    "symbol, kwargs",
    [
        ("TSLA", {"limit": 1}),
    ],
)
def test_display_dividends(symbol, kwargs):
    yahoo_finance_view.display_dividends(symbol=symbol, **kwargs)


@pytest.mark.record_http
@pytest.mark.parametrize(
    "symbol, kwargs",
    [
        ("TSLA", {}),
    ],
)
def test_display_splits(symbol, kwargs):
    yahoo_finance_view.display_splits(symbol=symbol, **kwargs)


@pytest.mark.record_http
@pytest.mark.record_verify_screen
@pytest.mark.parametrize(
    "symbol, start_date, end_date, kwargs",
    [
        ("TSLA", "2021-01-01", "2021-02-01", {}),
    ],
)
def test_display_mktcap(symbol, start_date, end_date, kwargs):
    yahoo_finance_view.display_mktcap(
        symbol=symbol, start_date=start_date, end_date=end_date, **kwargs
    )


@pytest.mark.record_http
@pytest.mark.parametrize(
    "symbol, statement, kwargs",
    [
        ("TSLA", "cash-flow", {}),
        ("TSLA", "financials", {}),
        ("TSLA", "financials", {"plot": ["total_revenue"]}),
    ],
)
def test_display_fundamentals(symbol, statement, kwargs):
    yahoo_finance_view.display_fundamentals(
        symbol=symbol, statement=statement, **kwargs
    )


@pytest.mark.record_http
@pytest.mark.record_verify_screen
@pytest.mark.parametrize(
    "symbol, limit, kwargs",
    [
        ("TSLA", 10, {}),
    ],
)
def test_display_earnings(symbol, limit, kwargs):
    yahoo_finance_view.display_earnings(symbol=symbol, limit=limit, **kwargs)
