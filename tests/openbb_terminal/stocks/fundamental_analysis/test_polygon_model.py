# IMPORTATION THIRDPARTY
import pytest
from pandas import DataFrame

# IMPORTATION INTERNAL
from openbb_terminal.stocks.fundamental_analysis import polygon_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("apiKey", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.vcr
@pytest.mark.parametrize(
    "func, kwargs_dict",
    [
        (
            "get_financials",
            {"symbol": "AAPL", "statement": "balance", "quarterly": True},
        ),
        (
            "get_financials",
            {"symbol": "AAPL", "statement": "balance", "quarterly": False},
        ),
        (
            "get_financials",
            {"symbol": "AAPL", "statement": "income", "quarterly": True},
        ),
        (
            "get_financials",
            {"symbol": "AAPL", "statement": "income", "quarterly": False},
        ),
    ],
)
def test_check_output(func, kwargs_dict, recorder):
    result_df = getattr(polygon_model, func)(**kwargs_dict)
    recorder.capture(result_df)


@pytest.mark.vcr
def test_check_bad_ticker(recorder):
    result_df = polygon_model.get_financials("THIS_IS_NOT_A_TICKER", "income", False)
    recorder.capture(result_df)
    assert result_df.empty is True


@pytest.mark.record_http
@pytest.mark.parametrize(
    "symbol, statement, quarterly, ratios",
    [
        ("AAPL", "balance", True, False),
        ("AAPL", "balance", False, False),
        ("AAPL", "income", False, False),
        ("AAPL", "cash", False, False),
    ],
)
def test_get_financials(symbol, statement, quarterly, ratios):
    result = polygon_model.get_financials(symbol, statement, quarterly, ratios)
    assert isinstance(result, DataFrame)


@pytest.mark.record_http
def test_get_financials_no_statement():
    result = polygon_model.get_financials("AAPL", "bad_statement")
    assert result.empty is True
