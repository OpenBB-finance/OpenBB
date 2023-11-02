import datetime

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_fred.models.ameribor_rates import FREDAMERIBORFetcher
from openbb_fred.models.cp import FREDCommercialPaperFetcher
from openbb_fred.models.cpi import FREDCPIFetcher
from openbb_fred.models.dwpcr_rates import FREDDiscountWindowPrimaryCreditRateFetcher
from openbb_fred.models.ecb_interest_rates import (
    FREDEuropeanCentralBankInterestRatesFetcher,
)
from openbb_fred.models.estr_rates import FREDESTRFetcher
from openbb_fred.models.fed_projections import FREDPROJECTIONFetcher
from openbb_fred.models.fed_rates import FREDFEDFetcher
from openbb_fred.models.ffrmc import FREDSelectedTreasuryConstantMaturityFetcher
from openbb_fred.models.hqm import FREDHighQualityMarketCorporateBondFetcher
from openbb_fred.models.ice_bofa import FREDICEBofAFetcher
from openbb_fred.models.iorb_rates import FREDIORBFetcher
from openbb_fred.models.moody import FREDMoodyCorporateBondIndexFetcher
from openbb_fred.models.sofr_rates import FREDSOFRFetcher
from openbb_fred.models.sonia_rates import FREDSONIAFetcher
from openbb_fred.models.spot import FREDSpotRateFetcher
from openbb_fred.models.tbffr import FREDSelectedTreasuryBillFetcher
from openbb_fred.models.tmc import FREDTreasuryConstantMaturityFetcher
from openbb_fred.models.us_yield_curve import FREDYieldCurveFetcher

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


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


@pytest.mark.record_http
def test_fred_discount_window_primary_credit_rate_fetcher(credentials=test_credentials):
    params = {
        "start_date": datetime.date(2023, 1, 1),
        "end_date": datetime.date(2023, 6, 6),
    }

    fetcher = FREDDiscountWindowPrimaryCreditRateFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fred_european_central_bank_interest_rates_fetcher(
    credentials=test_credentials,
):
    params = {
        "start_date": datetime.date(2023, 1, 1),
        "end_date": datetime.date(2023, 6, 6),
    }

    fetcher = FREDEuropeanCentralBankInterestRatesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fredice_bof_a_fetcher(credentials=test_credentials):
    params = {
        "start_date": datetime.date(2023, 1, 1),
        "end_date": datetime.date(2023, 6, 6),
    }

    fetcher = FREDICEBofAFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fred_moody_corporate_bond_index_fetcher(credentials=test_credentials):
    params = {
        "start_date": datetime.date(2023, 1, 1),
        "end_date": datetime.date(2023, 6, 6),
    }

    fetcher = FREDMoodyCorporateBondIndexFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fred_commercial_paper_fetcher(credentials=test_credentials):
    params = {
        "start_date": datetime.date(2023, 1, 1),
        "end_date": datetime.date(2023, 6, 6),
    }

    fetcher = FREDCommercialPaperFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fred_spot_rate_fetcher(credentials=test_credentials):
    params = {
        "start_date": datetime.date(2023, 1, 1),
        "end_date": datetime.date(2023, 6, 6),
    }

    fetcher = FREDSpotRateFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fred_high_quality_market_corporate_bond_fetcher(credentials=test_credentials):
    params = {"date": datetime.date(2023, 1, 1)}

    fetcher = FREDHighQualityMarketCorporateBondFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fred_treasury_constant_maturity_fetcher(credentials=test_credentials):
    params = {
        "start_date": datetime.date(2023, 1, 1),
        "end_date": datetime.date(2023, 6, 6),
    }

    fetcher = FREDTreasuryConstantMaturityFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fred_selected_treasury_constant_maturity_fetcher(credentials=test_credentials):
    params = {
        "start_date": datetime.date(2023, 1, 1),
        "end_date": datetime.date(2023, 6, 6),
    }

    fetcher = FREDSelectedTreasuryConstantMaturityFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fred_selected_treasury_bill_fetcher(credentials=test_credentials):
    params = {
        "start_date": datetime.date(2023, 1, 1),
        "end_date": datetime.date(2023, 6, 6),
    }

    fetcher = FREDSelectedTreasuryBillFetcher()
    result = fetcher.test(params, credentials)
    assert result is None
