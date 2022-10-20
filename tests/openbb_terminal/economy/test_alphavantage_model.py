# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.economy import alphavantage_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [("apikey", "MOCK_API_KEY")],
    }


@pytest.mark.vcr
def test_get_sector_data(recorder):
    result_df = alphavantage_model.get_sector_data()
    recorder.capture(result_df)


@pytest.mark.vcr
def test_get_real_gdp(recorder):
    result_df = alphavantage_model.get_real_gdp()
    recorder.capture(result_df)


@pytest.mark.vcr
def test_get_gdp_capita(recorder):
    result_df = alphavantage_model.get_gdp_capita()
    recorder.capture(result_df)


@pytest.mark.vcr
def test_get_inflation(recorder):
    result_df = alphavantage_model.get_inflation()
    recorder.capture(result_df)


@pytest.mark.vcr
def test_get_cpi(recorder):
    result_df = alphavantage_model.get_cpi()
    recorder.capture(result_df)


@pytest.mark.vcr
def test_get_treasury_yield(recorder):
    result_df = alphavantage_model.get_treasury_yield()
    recorder.capture(result_df)


@pytest.mark.vcr
def test_get_unemployment(recorder):
    result_df = alphavantage_model.get_unemployment()
    recorder.capture(result_df)
