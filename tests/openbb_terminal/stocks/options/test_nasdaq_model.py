# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest
import requests

# IMPORTATION INTERNAL
from openbb_terminal.stocks.options import nasdaq_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("before", "MOCK_BEFORE"),
            ("after", "MOCK_AFTER"),
        ],
    }


@pytest.mark.vcr
def test_last_price(recorder):
    result_df = nasdaq_model.load_options("QQQ")
    assert isinstance(result_df.last_price, float)
    recorder.capture(result_df.last_price)


@pytest.mark.vcr
def test_chains(recorder):
    result_df = nasdaq_model.load_options("SPY")
    assert isinstance(result_df.chains, pd.DataFrame)
    recorder.capture(result_df.chains)


@pytest.mark.vcr
def test_expirations(recorder):
    result_df = nasdaq_model.load_options("AAPL")
    assert isinstance(result_df.expirations, list)
    recorder.capture(result_df.expirations)


@pytest.mark.vcr
def test_strikes(recorder):
    result_df = nasdaq_model.load_options("TSLA")
    assert isinstance(result_df.strikes, list)
    recorder.capture(result_df.strikes)


@pytest.mark.vcr
def test_underlying_name(recorder):
    result_df = nasdaq_model.load_options("QQQ")
    assert isinstance(result_df.underlying_name, str)
    recorder.capture(result_df.underlying_name)


@pytest.mark.vcr
def test_underlying_price(recorder):
    result_df = nasdaq_model.load_options("MSFT")
    assert result_df.underlying_price.dtype == object
    recorder.capture(result_df.underlying_price)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_load_options_bad_symbol(mocker):
    mock_response = requests.Response()
    mock_response.status_code = 400
    mocker.patch(
        target="openbb_terminal.helper_funcs.requests.get",
        new=mocker.Mock(return_value=mock_response),
    )
    result_df = nasdaq_model.load_options("BAD_SYMBOL")
    assert result_df.chains.empty


@pytest.mark.vcr
def test_get_available_greeks(recorder):
    df = nasdaq_model.load_options("TSLA")
    results_df = df.get_available_greeks(df.expirations[-1])
    assert isinstance(results_df, pd.DataFrame)
    recorder.capture(results_df)


@pytest.mark.vcr
def test_load_options(recorder):
    data = nasdaq_model.load_options(symbol="OXY")
    assert isinstance(data.chains, pd.DataFrame)
    assert isinstance(data.last_price, float)
    assert isinstance(data.underlying_price, pd.Series)
    df1 = data.chains
    data = nasdaq_model.load_options(symbol="OXY", pydantic=True)
    assert isinstance(data.chains, dict)
    assert isinstance(data.underlying_price, dict)
    assert isinstance(data.expirations, list)
    assert isinstance(data.strikes, list)
    df2 = pd.DataFrame(data.chains)
    assert df1.equals(df2)
    recorder.capture(data.chains)
    recorder.capture(data.underlying_price)
    recorder.capture(data.last_price)
