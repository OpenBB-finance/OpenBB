# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.fundamental_analysis import av_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("apikey", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "func, kwargs_dict",
    [
        ("get_overview", {"symbol": "TSLA"}),
        ("get_key_metrics", {"symbol": "TSLA"}),
        ("get_earnings", {"symbol": "TSLA", "quarterly": True}),
    ],
)
def test_invalid_response_status(func, kwargs_dict, mocker):
    # MOCK GET
    attrs = {
        "json.return_value": {"Error Message": "mock error message"},
    }
    mock_response = mocker.Mock(**attrs)

    mocker.patch(
        target="requests.get",
        new=mocker.Mock(return_value=mock_response),
    )

    result_df = getattr(av_model, func)(**kwargs_dict)
    assert result_df.empty


@pytest.mark.vcr
@pytest.mark.parametrize(
    "func, kwargs_dict",
    [
        ("get_overview", {"symbol": "TSLA"}),
        ("get_key_metrics", {"symbol": "TSLA"}),
        ("get_earnings", {"symbol": "TSLA", "quarterly": True}),
        ("get_earnings", {"symbol": "TSLA", "quarterly": False}),
        ("get_income_statements", {"symbol": "TSLA", "limit": 5, "quarterly": True}),
        ("get_income_statements", {"symbol": "TSLA", "limit": 5, "quarterly": False}),
        ("get_balance_sheet", {"symbol": "TSLA", "limit": 5, "quarterly": True}),
        ("get_balance_sheet", {"symbol": "TSLA", "limit": 5, "quarterly": False}),
        ("get_cash_flow", {"symbol": "TSLA", "limit": 5, "quarterly": True}),
        ("get_cash_flow", {"symbol": "TSLA", "limit": 5, "quarterly": False}),
    ],
)
def test_check_output(func, kwargs_dict, recorder):
    result_df = getattr(av_model, func)(**kwargs_dict)
    recorder.capture(result_df)


@pytest.mark.vcr
def test_get_fraud_ratios(recorder):
    result_df = av_model.get_fraud_ratios(symbol="TSLA")

    recorder.capture(result_df)


@pytest.mark.vcr
def test_get_dupont(recorder):
    result_df = av_model.get_dupont(symbol="TSLA")

    recorder.capture(result_df)
