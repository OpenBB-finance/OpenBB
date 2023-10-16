import pytest
from openbb_core.app.service.user_service import UserService
from openbb_fred.models.ameribor_rates import FREDAMERIBORFetcher
from openbb_fred.models.cpi import FREDCPIFetcher
from openbb_fred.models.estr_rates import FREDESTRFetcher
from openbb_fred.models.fed_projections import FREDPROJECTIONFetcher
from openbb_fred.models.fed_rates import FREDFEDFetcher
from openbb_fred.models.iorb_rates import FREDIORBFetcher
from openbb_fred.models.sofr_rates import FREDSOFRFetcher
from openbb_fred.models.sonia_rates import FREDSONIAFetcher
from openbb_fred.models.us_yield_curve import FREDYieldCurveFetcher

test_credentials = UserService().default_user_settings.credentials.model_dump()


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("api_key", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.record_http
@pytest.mark.skip(reason="FRED has deeply nested return types which are not supported.")
def test_fredcpi_fetcher(credentials=test_credentials):
    params = {"countries": ["portugal", "spain"]}

    fetcher = FREDCPIFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
@pytest.mark.skip(reason="FRED has deeply nested return types which are not supported.")
def test_fred_yield_curve_fetcher(credentials=test_credentials):
    params = {}

    fetcher = FREDYieldCurveFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
@pytest.mark.skip(reason="FRED has deeply nested return types which are not supported.")
def test_fredsofr_fetcher(credentials=test_credentials):
    params = {}

    fetcher = FREDSOFRFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
@pytest.mark.skip(reason="FRED has deeply nested return types which are not supported.")
def test_fredestr_fetcher(credentials=test_credentials):
    params = {}

    fetcher = FREDESTRFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
@pytest.mark.skip(reason="FRED has deeply nested return types which are not supported.")
def test_fredsonia_fetcher(credentials=test_credentials):
    params = {}

    fetcher = FREDSONIAFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
@pytest.mark.skip(reason="FRED has deeply nested return types which are not supported.")
def test_fredameribor_fetcher(credentials=test_credentials):
    params = {}

    fetcher = FREDAMERIBORFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
@pytest.mark.skip(reason="FRED has deeply nested return types which are not supported.")
def test_fredfed_fetcher(credentials=test_credentials):
    params = {}

    fetcher = FREDFEDFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
@pytest.mark.skip(reason="FRED has deeply nested return types which are not supported.")
def test_fredprojection_fetcher(credentials=test_credentials):
    params = {}

    fetcher = FREDPROJECTIONFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
@pytest.mark.skip(reason="FRED has deeply nested return types which are not supported.")
def test_frediorb_fetcher(credentials=test_credentials):
    params = {}

    fetcher = FREDIORBFetcher()
    result = fetcher.test(params, credentials)
    assert result is None
