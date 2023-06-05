# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.fundamental_analysis import fmp_model


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
def test_get_score():
    result = fmp_model.get_score(symbol="PM", years=10)
    if result:
        assert isinstance(result, dict)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "func, kwargs_dict",
    [
        (
            "get_profile",
            {"symbol": "PM"},
        ),
        (
            "get_enterprise",
            {"symbol": "PM", "quarterly": False},
        ),
        (
            "get_dcf",
            {"symbol": "PM", "limit": 5, "quarterly": False},
        ),
        (
            "get_income",
            {"symbol": "PM", "limit": 5, "quarterly": False},
        ),
        (
            "get_balance",
            {"symbol": "PM", "limit": 5, "quarterly": False},
        ),
        (
            "get_cash",
            {"symbol": "PM", "limit": 5, "quarterly": False},
        ),
        (
            "get_key_metrics",
            {"symbol": "PM", "limit": 5, "quarterly": False},
        ),
        (
            "get_key_ratios",
            {"symbol": "PM", "limit": 5, "quarterly": False},
        ),
        (
            "get_financial_growth",
            {"symbol": "PM", "limit": 5, "quarterly": False},
        ),
    ],
)
@pytest.mark.record_stdout
def test_valid_df(func, kwargs_dict):
    result_df = getattr(fmp_model, func)(**kwargs_dict)
    assert isinstance(result_df, pd.DataFrame)


@pytest.mark.vcr
def test_get_rating(recorder):
    result_df = fmp_model.get_rating(symbol="TSLA")

    recorder.capture(result_df)


@pytest.mark.record_http
def test_get_profile():
    result = fmp_model.get_profile(symbol="PM")
    assert isinstance(result, pd.DataFrame)
    assert not result.empty


@pytest.mark.record_http
@pytest.mark.parametrize(
    "symbol, start_date, end_date, quarterly",
    [
        ("PM", "2020-01-01", "2020-12-31", False),
    ],
)
def test_get_enterprise(record, symbol, start_date, end_date, quarterly):
    result = fmp_model.get_enterprise(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        quarterly=quarterly,
    )
    record.add_verify(result)
    assert isinstance(result, pd.DataFrame)
    assert not result.empty


@pytest.mark.record_http
@pytest.mark.parametrize(
    "symbol, limit, quarterly",
    [
        ("PM", 5, False),
    ],
)
def test_get_dcf(symbol, limit, quarterly):
    result = fmp_model.get_dcf(
        symbol=symbol,
        limit=limit,
        quarterly=quarterly,
    )
    assert isinstance(result, pd.DataFrame)
    assert not result.empty


@pytest.mark.record_http
@pytest.mark.parametrize(
    "symbol, limit, quarterly, ratios",
    [("PM", 5, False, False), ("TSLA", 5, False, True)],
)
def test_get_income(symbol, limit, quarterly, ratios):
    result = fmp_model.get_income(
        symbol=symbol,
        limit=limit,
        quarterly=quarterly,
        ratios=ratios,
    )
    assert isinstance(result, pd.DataFrame)
    assert not result.empty


@pytest.mark.record_http
@pytest.mark.parametrize(
    "symbol, limit, quarterly, ratios",
    [
        ("PM", 5, False, False),
    ],
)
def test_get_balance(symbol, limit, quarterly, ratios):
    result = fmp_model.get_balance(
        symbol=symbol,
        limit=limit,
        quarterly=quarterly,
        ratios=ratios,
    )
    assert isinstance(result, pd.DataFrame)
    assert not result.empty


@pytest.mark.record_http
@pytest.mark.parametrize(
    "symbol, limit, quarterly, ratios",
    [
        ("PM", 5, False, False),
    ],
)
def test_get_cash(symbol, limit, quarterly, ratios):
    result = fmp_model.get_cash(
        symbol=symbol,
        limit=limit,
        quarterly=quarterly,
        ratios=ratios,
    )
    assert isinstance(result, pd.DataFrame)
    assert not result.empty


@pytest.mark.record_http
@pytest.mark.parametrize(
    "symbol, limit, quarterly",
    [
        ("PM", 5, False),
    ],
)
def test_get_key_metrics(symbol, limit, quarterly):
    result = fmp_model.get_key_metrics(
        symbol=symbol,
        limit=limit,
        quarterly=quarterly,
    )
    assert isinstance(result, pd.DataFrame)
    assert not result.empty


@pytest.mark.record_http
@pytest.mark.parametrize(
    "symbol, limit, quarterly",
    [
        ("PM", 5, False),
    ],
)
def test_key_ratios(symbol, limit, quarterly):
    result = fmp_model.get_key_ratios(
        symbol=symbol,
        limit=limit,
        quarterly=quarterly,
    )
    assert isinstance(result, pd.DataFrame)
    assert not result.empty


@pytest.mark.record_http
@pytest.mark.parametrize(
    "symbol, limit, quarterly",
    [
        ("PM", 5, False),
    ],
)
def test_get_financial_growth(symbol, limit, quarterly):
    result = fmp_model.get_financial_growth(
        symbol=symbol,
        limit=limit,
        quarterly=quarterly,
    )
    assert isinstance(result, pd.DataFrame)
    assert not result.empty


@pytest.mark.record_http
def test_get_price_targets():
    result = fmp_model.get_price_targets(symbol="TSLA")
    assert isinstance(result, pd.DataFrame)
