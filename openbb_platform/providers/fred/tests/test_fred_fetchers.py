"""Test FRED fetchers."""

import datetime

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_fred.models.ameribor import FredAmeriborFetcher
from openbb_fred.models.balance_of_payments import FredBalanceOfPaymentsFetcher
from openbb_fred.models.bond_indices import FredBondIndicesFetcher
from openbb_fred.models.commercial_paper import FREDCommercialPaperFetcher
from openbb_fred.models.consumer_price_index import FREDConsumerPriceIndexFetcher
from openbb_fred.models.dwpcr_rates import FREDDiscountWindowPrimaryCreditRateFetcher
from openbb_fred.models.ecb_interest_rates import (
    FREDEuropeanCentralBankInterestRatesFetcher,
)
from openbb_fred.models.euro_short_term_rate import FredEuroShortTermRateFetcher
from openbb_fred.models.fed_projections import FREDPROJECTIONFetcher
from openbb_fred.models.federal_funds_rate import FredFederalFundsRateFetcher
from openbb_fred.models.ffrmc import FREDSelectedTreasuryConstantMaturityFetcher
from openbb_fred.models.high_quality_market import (
    FredHighQualityMarketCorporateBondFetcher,
)
from openbb_fred.models.ice_bofa import FREDICEBofAFetcher
from openbb_fred.models.iorb_rates import FREDIORBFetcher
from openbb_fred.models.moody import FREDMoodyCorporateBondIndexFetcher
from openbb_fred.models.mortgage_indices import FredMortgageIndicesFetcher
from openbb_fred.models.overnight_bank_funding_rate import (
    FredOvernightBankFundingRateFetcher,
)
from openbb_fred.models.regional import FredRegionalDataFetcher
from openbb_fred.models.retail_prices import FredRetailPricesFetcher
from openbb_fred.models.search import (
    FredSearchFetcher,
)
from openbb_fred.models.series import FredSeriesFetcher
from openbb_fred.models.sofr import FREDSOFRFetcher
from openbb_fred.models.sonia_rates import FREDSONIAFetcher
from openbb_fred.models.spot import FREDSpotRateFetcher
from openbb_fred.models.tbffr import FREDSelectedTreasuryBillFetcher
from openbb_fred.models.tmc import FREDTreasuryConstantMaturityFetcher
from openbb_fred.models.us_yield_curve import (
    FREDYieldCurveFetcher as FREDUSYieldCurveFetcher,
)
from openbb_fred.models.yield_curve import FREDYieldCurveFetcher

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.fixture(scope="module")
def vcr_config():
    """VCR config."""
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("api_key", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.record_http
def test_fredcpi_fetcher(credentials=test_credentials):
    """Test FREDConsumerPriceIndexFetcher."""
    params = {"country": "portugal,spain"}

    fetcher = FREDConsumerPriceIndexFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fred_us_yield_curve_fetcher(credentials=test_credentials):
    """Test FREDUSYieldCurveFetcher."""
    params = {"date": datetime.date(2023, 12, 1)}

    fetcher = FREDUSYieldCurveFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fred_sofr_fetcher(credentials=test_credentials):
    """Test FREDSOFRFetcher."""
    params = {
        "start_date": datetime.date(2024, 6, 1),
        "end_date": datetime.date(2024, 6, 6),
    }

    fetcher = FREDSOFRFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fred_euro_short_term_rate_fetcher(credentials=test_credentials):
    """Test FREDEuroShortTermRateFetcher."""
    params = {
        "start_date": datetime.date(2024, 6, 1),
        "end_date": datetime.date(2024, 6, 6),
    }

    fetcher = FredEuroShortTermRateFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fredsonia_fetcher(credentials=test_credentials):
    """Test FREDSONIAFetcher."""
    params = {}

    fetcher = FREDSONIAFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fred_ameribor_fetcher(credentials=test_credentials):
    """Test FredAmeriborFetcher."""
    params = {
        "start_date": datetime.date(2023, 1, 1),
        "end_date": datetime.date(2023, 6, 6),
        "maturity": "overnight",
    }

    fetcher = FredAmeriborFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fred_federal_funds_rate_fetcher(credentials=test_credentials):
    """Test FRED Federal Funds Rate Fetcher."""
    params = {
        "start_date": datetime.date(2023, 1, 1),
        "end_date": datetime.date(2023, 6, 6),
        "effr_only": True,
    }

    fetcher = FredFederalFundsRateFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fredprojection_fetcher(credentials=test_credentials):
    """Test FREDPROJECTIONFetcher."""
    params = {}

    fetcher = FREDPROJECTIONFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_frediorb_fetcher(credentials=test_credentials):
    """Test FREDIORBFetcher."""
    params = {}

    fetcher = FREDIORBFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fred_discount_window_primary_credit_rate_fetcher(credentials=test_credentials):
    """Test FREDDiscountWindowPrimaryCreditRateFetcher."""
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
    """Test FREDEuropeanCentralBankInterestRatesFetcher."""
    params = {
        "start_date": datetime.date(2023, 1, 1),
        "end_date": datetime.date(2023, 6, 6),
    }

    fetcher = FREDEuropeanCentralBankInterestRatesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fredice_bof_a_fetcher(credentials=test_credentials):
    """Test FREDICEBofAFetcher."""
    params = {
        "start_date": datetime.date(2023, 1, 1),
        "end_date": datetime.date(2023, 6, 6),
    }

    fetcher = FREDICEBofAFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fred_moody_corporate_bond_index_fetcher(credentials=test_credentials):
    """Test FREDMoodyCorporateBondIndexFetcher."""
    params = {
        "start_date": datetime.date(2023, 1, 1),
        "end_date": datetime.date(2023, 6, 6),
    }

    fetcher = FREDMoodyCorporateBondIndexFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fred_commercial_paper_fetcher(credentials=test_credentials):
    """Test FREDCommercialPaperFetcher."""
    params = {
        "start_date": datetime.date(2024, 1, 1),
        "end_date": datetime.date(2024, 2, 1),
        "category": "asset_backed",
        "maturity": "30d",
    }

    fetcher = FREDCommercialPaperFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fred_spot_rate_fetcher(credentials=test_credentials):
    """Test FREDSpotRateFetcher."""
    params = {
        "start_date": datetime.date(2023, 1, 1),
        "end_date": datetime.date(2023, 6, 6),
    }

    fetcher = FREDSpotRateFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fred_high_quality_market_corporate_bond_fetcher(credentials=test_credentials):
    """Test FredHighQualityMarketCorporateBondFetcher."""
    params = {"date": "2023-01-01"}

    fetcher = FredHighQualityMarketCorporateBondFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fred_treasury_constant_maturity_fetcher(credentials=test_credentials):
    """Test FREDTreasuryConstantMaturityFetcher."""
    params = {
        "start_date": datetime.date(2023, 1, 1),
        "end_date": datetime.date(2023, 6, 6),
    }

    fetcher = FREDTreasuryConstantMaturityFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fred_selected_treasury_constant_maturity_fetcher(credentials=test_credentials):
    """Test FREDSelectedTreasuryConstantMaturityFetcher."""
    params = {
        "start_date": datetime.date(2023, 1, 1),
        "end_date": datetime.date(2023, 6, 6),
    }

    fetcher = FREDSelectedTreasuryConstantMaturityFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fred_selected_treasury_bill_fetcher(credentials=test_credentials):
    """Test FREDSelectedTreasuryBillFetcher."""
    params = {
        "start_date": datetime.date(2023, 1, 1),
        "end_date": datetime.date(2023, 6, 6),
    }

    fetcher = FREDSelectedTreasuryBillFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fred_search_fetcher(credentials=test_credentials):
    """Test FredSearchFetcher."""
    params = {"query": "Consumer Price Index"}

    fetcher = FredSearchFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fred_series_fetcher(credentials=test_credentials):
    """Test FredSeriesFetcher."""
    params = {"symbol": "SP500", "filter_variable": "frequency", "filter_value": "w"}

    fetcher = FredSeriesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fred_regional_fetcher(credentials=test_credentials):
    """Test FredRegionalFetcher."""
    params = {
        "symbol": "942",
        "is_series_group": True,
        "start_date": datetime.date(1975, 1, 1),
        "frequency": "q",
        "units": "Index 1980:Q1=100",
        "region_type": "state",
        "season": "NSA",
    }

    fetcher = FredRegionalDataFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fred_balance_of_payments_fetcher(credentials=test_credentials):
    """Test FredBalanceOfPaymentsFetcher."""
    params = {
        "country": "united_states",
        "start_date": datetime.date(2020, 1, 1),
        "end_date": datetime.date(2024, 3, 31),
    }

    fetcher = FredBalanceOfPaymentsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fred_yield_curve_fetcher(credentials=test_credentials):
    """Test FREDYieldCurveFetcher."""
    params = {"date": "2024-05-14,2023-05-14,2022-03-16,2021-05-14,2020-05-14"}

    fetcher = FREDYieldCurveFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fred_retail_prices_fetcher(credentials=test_credentials):
    """Test FREDRetailPricesFetcher."""
    params = {"item": "eggs", "start_date": datetime.date(2024, 1, 1)}

    fetcher = FredRetailPricesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fred_bond_indices_fetcher(credentials=test_credentials):
    """Test FredBondIndicesFetcher."""
    params = {
        "category": "us",
        "index": "corporate",
        "start_date": datetime.date(2024, 6, 1),
        "end_date": datetime.date(2024, 6, 4),
    }

    fetcher = FredBondIndicesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fred_bond_mortgage_fetcher(credentials=test_credentials):
    """Test FredMortgageIndicesFetcher."""
    params = {
        "index": "jumbo_30y",
        "start_date": datetime.date(2024, 6, 1),
        "end_date": datetime.date(2024, 6, 4),
    }

    fetcher = FredMortgageIndicesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fred_overnight_bank_funding_rate_fetcher(credentials=test_credentials):
    """Test FRED Overnight Bank Funding Rate Fetcher."""
    params = {
        "start_date": datetime.date(2024, 6, 1),
        "end_date": datetime.date(2024, 6, 6),
    }

    fetcher = FredOvernightBankFundingRateFetcher()
    result = fetcher.test(params, credentials)
    assert result is None
