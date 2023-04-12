# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest
from pandas import DataFrame, Series

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
        target="openbb_terminal.helper_funcs.requests.get",
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


@pytest.mark.record_http
def test_get_overview(record):
    result_df = av_model.get_overview(symbol="TSLA")
    record.add_verify(result_df)

    assert isinstance(result_df, DataFrame)
    assert not result_df.empty


@pytest.mark.record_http
def test_get_key_metrics(record):
    result_df = av_model.get_key_metrics(symbol="TSLA")
    record.add_verify(result_df)

    assert isinstance(result_df, DataFrame)
    assert not result_df.empty


@pytest.mark.record_http
@pytest.mark.parametrize(
    "symbol, kwargs",
    [
        ("TSLA", {}),
        ("TSLA", {"quarterly": True}),
        ("TSLA", {"ratios": True}),
    ],
)
def test_get_income_statements(record, symbol, kwargs):
    result_df = av_model.get_income_statements(symbol=symbol, **kwargs)
    record.add_verify(result_df)

    assert isinstance(result_df, DataFrame)


@pytest.mark.record_http
@pytest.mark.parametrize(
    "symbol, kwargs",
    [
        ("TSLA", {}),
    ],
)
def test_get_balance_sheet(record, symbol, kwargs):
    result_df = av_model.get_balance_sheet(symbol=symbol, **kwargs)
    record.add_verify(result_df)

    assert isinstance(result_df, DataFrame)
    assert not result_df.empty


@pytest.mark.record_http
@pytest.mark.parametrize(
    "symbol, kwargs",
    [
        ("TSLA", {}),
    ],
)
def test_get_cash_flow(record, symbol, kwargs):
    result_df = av_model.get_cash_flow(symbol=symbol, **kwargs)
    record.add_verify(result_df)

    assert isinstance(result_df, DataFrame)
    assert not result_df.empty


@pytest.mark.record_http
@pytest.mark.parametrize(
    "symbol, quarterly",
    [
        ("TSLA", False),
    ],
)
def test_get_earnings(record, symbol, quarterly):
    result_df = av_model.get_earnings(symbol=symbol, quarterly=quarterly)
    record.add_verify(result_df)

    assert isinstance(result_df, DataFrame)


def test_df_values():
    df = DataFrame(
        {
            "a": [1, 2, 3, 4, 5],
            "b": [6, 7, 8, 9, 10],
            "c": [11, 12, 13, 14, 15],
        }
    )
    assert av_model.df_values(df, "a") == [1, 2, 3, 4, 5]
    assert av_model.df_values(df, "b", index=1) == [7, 8]
    assert av_model.df_values(df, "c", index=2, length=3) == [13, 14, 15]


@pytest.mark.parametrize("name", ["Mscore", "Zscore"])
def test_replace_df(name):
    series = Series([1, 2, 3, 4, 5])
    av_model.replace_df(name=name, row=series)


@pytest.mark.parametrize(
    "value, result",
    [
        (1, "[red]1.00[/red]"),
        (-2, "[yellow]-2.00[/yellow]"),
        (-3, "[green]-3.00[/green]"),
        ("nan", "N/A"),
    ],
)
def test_color_mscore(value, result):
    response = av_model.color_mscore(value)
    assert isinstance(result, str)
    assert response == result


@pytest.mark.parametrize(
    "value, result",
    [
        (1, "[green]1.00[/green]"),
        (-2, "[red]-2.00[/red]"),
        ("nan", "N/A"),
    ],
)
def test_color_zscore_mckee(value, result):
    response = av_model.color_zscore_mckee(value)
    assert isinstance(result, str)
    assert response == result


@pytest.mark.parametrize(
    "json_response",
    [
        {
            "Information": "Thank you for using Alpha Vantage!\
            This is a premium endpoint. You may subscribe to "
            "any of the premium plans at https://www.alphavantage.co/premium/\
            to instantly unlock all premium endpoints"
        },
        {},
    ],
)
def test_check_premium_key(json_response):
    result = av_model.check_premium_key(json_response)
    assert isinstance(result, bool)
