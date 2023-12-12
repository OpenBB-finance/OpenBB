from datetime import date

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_federal_reserve.models.fed_rates import FederalReserveFEDFetcher
from openbb_federal_reserve.models.money_measures import (
    FederalReserveMoneyMeasuresFetcher,
)
from openbb_federal_reserve.models.treasury_rates import (
    FederalReserveTreasuryRatesFetcher,
)

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.mark.record_http
def test_federal_reserve_treasury_rates_fetcher(credentials=test_credentials):
    params = {"start_date": date(2023, 1, 1), "end_date": date(2023, 5, 10)}

    fetcher = FederalReserveTreasuryRatesFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_federal_reserve_money_measures_fetcher(credentials=test_credentials):
    params = {"start_date": date(2023, 1, 1), "end_date": date(2023, 5, 10)}

    fetcher = FederalReserveMoneyMeasuresFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_federal_reserve_fed_fetcher(credentials=test_credentials):
    params = {"start_date": date(2023, 1, 1), "end_date": date(2023, 6, 6)}

    fetcher = FederalReserveFEDFetcher()
    result = fetcher.test(params, credentials)
    assert result is None
