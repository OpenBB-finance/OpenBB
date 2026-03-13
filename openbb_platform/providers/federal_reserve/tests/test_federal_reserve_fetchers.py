"""Tests for the Federal Reserve fetchers."""

from datetime import date

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_federal_reserve.models.central_bank_holdings import (
    FederalReserveCentralBankHoldingsFetcher,
)
from openbb_federal_reserve.models.federal_funds_rate import (
    FederalReserveFederalFundsRateFetcher,
)
from openbb_federal_reserve.models.fomc_documents import (
    FederalReserveFomcDocumentsFetcher,
)
from openbb_federal_reserve.models.inflation_expectations import (
    FederalReserveInflationExpectationsFetcher,
)
from openbb_federal_reserve.models.money_measures import (
    FederalReserveMoneyMeasuresFetcher,
)
from openbb_federal_reserve.models.overnight_bank_funding_rate import (
    FederalReserveOvernightBankFundingRateFetcher,
)
from openbb_federal_reserve.models.primary_dealer_fails import (
    FederalReservePrimaryDealerFailsFetcher,
)
from openbb_federal_reserve.models.primary_dealer_positioning import (
    FederalReservePrimaryDealerPositioningFetcher,
)
from openbb_federal_reserve.models.sofr import FederalReserveSOFRFetcher
from openbb_federal_reserve.models.svensson_yield_curve import (
    FederalReserveSvenssonFetcher,
)
from openbb_federal_reserve.models.total_factor_productivity import (
    FederalReserveTfpFetcher,
)
from openbb_federal_reserve.models.treasury_rates import (
    FederalReserveTreasuryRatesFetcher,
)
from openbb_federal_reserve.models.yield_curve import FederalReserveYieldCurveFetcher

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.fixture(scope="module")
def vcr_config():
    """VCR config."""
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [],
    }


@pytest.mark.record_http
def test_federal_reserve_treasury_rates_fetcher(credentials=test_credentials):
    """Test the Federal Reserve Treasury Rates fetcher."""
    params = {"start_date": date(2023, 1, 1), "end_date": date(2023, 5, 10)}

    fetcher = FederalReserveTreasuryRatesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_federal_reserve_money_measures_fetcher(credentials=test_credentials):
    """Test the Federal Reserve Money Measures fetcher."""
    params = {"start_date": date(2023, 1, 1), "end_date": date(2023, 5, 10)}

    fetcher = FederalReserveMoneyMeasuresFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_federal_reserve_federal_funds_rate_fetcher(credentials=test_credentials):
    """Test the Federal Reserve Federal Funds Rate fetcher."""
    params = {"start_date": date(2023, 1, 1), "end_date": date(2023, 6, 6)}

    fetcher = FederalReserveFederalFundsRateFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_federal_reserve_yield_curve_fetcher(credentials=test_credentials):
    """Test the Federal Reserve yield curve fetcher."""
    params = {"date": "2024-05-13,2020-05-09"}

    fetcher = FederalReserveYieldCurveFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_federal_reserve_svensson_fetcher(credentials=test_credentials):
    """Test the Federal Reserve Svensson fetcher."""
    params = {}

    fetcher = FederalReserveSvenssonFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_federal_reserve_central_bank_holdings_fetcher(credentials=test_credentials):
    """Test the Federal Reserve Central Bank Holdings Fetcher."""
    params = {"date": date(2019, 1, 2), "holding_type": "agency_debts"}

    fetcher = FederalReserveCentralBankHoldingsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_federal_reserve_sofr_fetcher(credentials=test_credentials):
    """Test the Federal Reserve SOFR Fetcher."""
    params = {"start_date": date(2024, 6, 1), "end_date": date(2024, 6, 6)}

    fetcher = FederalReserveSOFRFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_federal_reserve_overnight_bank_funding_rate_fetcher(
    credentials=test_credentials,
):
    """Test the Federal Reserve Overnight Bank Funding Rate Fetcher."""
    params = {"start_date": date(2024, 6, 1), "end_date": date(2024, 6, 6)}

    fetcher = FederalReserveOvernightBankFundingRateFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_federal_reserve_primary_dealer_positioning_fetcher(
    credentials=test_credentials,
):
    """Test the Federal Reserve Primary Dealer Positioning Fetcher."""
    params = {
        "category": "cmbs",
        "start_date": date(2024, 6, 1),
        "end_date": date(2024, 6, 30),
    }

    fetcher = FederalReservePrimaryDealerPositioningFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_federal_reserve_primary_dealer_fails_fetcher(
    credentials=test_credentials,
):
    """Test the Federal Reserve Primary Dealer Fails Fetcher."""
    params = {}

    fetcher = FederalReservePrimaryDealerFailsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_federal_reserve_fomc_documents_fetcher(
    credentials=test_credentials,
):
    """Test the Federal Reserve FOMC Documents Fetcher."""
    params = {}

    fetcher = FederalReserveFomcDocumentsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_federal_reserve_total_factor_productivity_fetcher(
    credentials=test_credentials,
):
    """Test the Federal Reserve Total Factor Productivity Fetcher."""
    params = {}

    fetcher = FederalReserveTfpFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_federal_reserve_inflation_expectations_fetcher(
    credentials=test_credentials,
):
    """Test the Federal Reserve Inflation Expectations Fetcher."""
    params = {}

    fetcher = FederalReserveInflationExpectationsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None
