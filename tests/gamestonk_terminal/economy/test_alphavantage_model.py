# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest
import requests

# IMPORTATION INTERNAL
from gamestonk_terminal.economy import alphavantage_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [("apikey", "MOCK_API_KEY")],
    }


@pytest.mark.vcr
def test_get_screener_data(recorder):
    result_df = alphavantage_model.get_sector_data()

    recorder.capture(result_df)


@pytest.mark.vcr
def test_get_real_gdp(recorder):
    result_df = alphavantage_model.get_real_gdp(interval="a")

    recorder.capture(result_df)


@pytest.mark.vcr(record_mode="none")
def test_get_real_gdp_no_response(mocker):
    # MOCK GET
    mock_response = requests.Response()
    mock_response.status_code = 400
    mocker.patch(target="requests.get", new=mocker.Mock(return_value=mock_response))

    result_df = alphavantage_model.get_real_gdp(interval="a")

    assert isinstance(result_df, pd.DataFrame)
    assert result_df.empty


@pytest.mark.vcr
def test_get_gdp_capita(recorder):
    result_df = alphavantage_model.get_gdp_capita()

    recorder.capture(result_df)


@pytest.mark.vcr(record_mode="none")
def test_get_gdp_capita_no_response(mocker):
    # MOCK GET
    mock_response = requests.Response()
    mock_response.status_code = 400
    mocker.patch(target="requests.get", new=mocker.Mock(return_value=mock_response))

    result_df = alphavantage_model.get_gdp_capita()

    assert isinstance(result_df, pd.DataFrame)
    assert result_df.empty


@pytest.mark.vcr
def test_get_inflation(recorder):
    result_df = alphavantage_model.get_inflation()

    recorder.capture(result_df)


@pytest.mark.vcr(record_mode="none")
def test_get_inflation_no_response(mocker):
    # MOCK GET
    mock_response = requests.Response()
    mock_response.status_code = 400
    mocker.patch(target="requests.get", new=mocker.Mock(return_value=mock_response))

    result_df = alphavantage_model.get_inflation()

    assert isinstance(result_df, pd.DataFrame)
    assert result_df.empty


@pytest.mark.vcr
def test_get_cpi(recorder):
    result_df = alphavantage_model.get_cpi(interval="m")

    recorder.capture(result_df)


@pytest.mark.vcr(record_mode="none")
def test_get_cpi_no_response(mocker):
    # MOCK GET
    mock_response = requests.Response()
    mock_response.status_code = 400
    mocker.patch(target="requests.get", new=mocker.Mock(return_value=mock_response))

    result_df = alphavantage_model.get_cpi(interval="m")

    assert isinstance(result_df, pd.DataFrame)
    assert result_df.empty


@pytest.mark.vcr
def test_get_treasury_yield(recorder):
    result_df = alphavantage_model.get_treasury_yield(interval="m", maturity="3m")

    recorder.capture(result_df)


@pytest.mark.vcr
def test_get_treasury_yield_response(mocker):
    # MOCK GET
    mock_response = requests.Response()
    mock_response.status_code = 400
    mocker.patch(target="requests.get", new=mocker.Mock(return_value=mock_response))

    result_df = alphavantage_model.get_treasury_yield(interval="m", maturity="3m")

    assert isinstance(result_df, pd.DataFrame)
    assert result_df.empty


@pytest.mark.vcr
def test_get_unemployment(recorder):
    result_df = alphavantage_model.get_unemployment()

    recorder.capture(result_df)


@pytest.mark.vcr
def test_get_unemployment_response(mocker):
    # MOCK GET
    mock_response = requests.Response()
    mock_response.status_code = 400
    mocker.patch(target="requests.get", new=mocker.Mock(return_value=mock_response))

    result_df = alphavantage_model.get_unemployment()

    assert isinstance(result_df, pd.DataFrame)
    assert result_df.empty
