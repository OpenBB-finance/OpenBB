# pylint: disable=no-member
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
    }


@pytest.mark.vcr
def test_SYMBOLS(recorder):
    ticker = nasdaq_model.load_options("AAPL")
    results_df = ticker.SYMBOLS
    assert not results_df.empty
    recorder.capture(results_df.columns.to_list())


@pytest.mark.vcr
def test_last_price():
    result_df = nasdaq_model.load_options("QQQ")
    assert isinstance(result_df.last_price, float)
    assert result_df.last_price > 0


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_load_options_bad_symbol(mocker):
    mock_response = requests.Response()
    mock_response.status_code = 400
    mocker.patch(
        target="openbb_terminal.helper_funcs.requests.get",
        new=mocker.Mock(return_value=mock_response),
    )
    data = nasdaq_model.load_options("BAD_SYMBOL")
    assert hasattr(data, "underlying_name") is False


@pytest.mark.vcr
def test_load_options(recorder):
    data = nasdaq_model.load_options(symbol="SPY")
    assert isinstance(data.chains, pd.DataFrame)
    assert isinstance(data.last_price, float)
    assert isinstance(data.underlying_price, pd.Series)
    df1 = pd.DataFrame(data.chains)
    data = nasdaq_model.load_options(symbol="SPY", pydantic=True)
    assert isinstance(data.chains, dict)
    assert isinstance(data.underlying_price, dict)
    assert isinstance(data.expirations, list)
    assert isinstance(data.strikes, list)
    df2 = pd.DataFrame(data.chains)
    assert df1.columns.equals(df2.columns)
    df_greeks = data.get_available_greeks(data.expirations[-1])
    recorder.capture(df2.columns.to_list())
    recorder.capture(list(data.underlying_price.keys()))
    recorder.capture(data.underlying_name)
    recorder.capture(data.symbol)
    recorder.capture(df_greeks.columns.to_list())
