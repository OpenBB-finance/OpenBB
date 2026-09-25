"""US Treasury fetcher tests."""

import datetime

import pytest
from openbb_core.app.service.user_service import UserService

from openbb_government_us.treasury.models.auction_results import (
    TreasuryAuctionResultsFetcher,
)
from openbb_government_us.treasury.models.bill_offerings import (
    TreasuryBillOfferingsFetcher,
)
from openbb_government_us.treasury.models.daily_treasury_statement import (
    DailyTreasuryStatementFetcher,
)
from openbb_government_us.treasury.models.debt_to_penny import DebtToPennyFetcher
from openbb_government_us.treasury.models.treasury_auctions import (
    UsTreasuryAuctionsFetcher,
)
from openbb_government_us.treasury.models.treasury_bulletin import (
    TreasuryBulletinFetcher,
)
from openbb_government_us.treasury.models.treasury_prices import (
    UsTreasuryPricesFetcher,
)
from openbb_government_us.treasury.models.upcoming_auctions import (
    UpcomingTreasuryAuctionsFetcher,
)

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.fixture(scope="module")
def vcr_config():
    """VCR config."""
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            None,
        ],
    }


class TestUsTreasuryFetchers:
    """Tests for the US Treasury provider fetchers."""

    @pytest.mark.record_http
    def test_treasury_auctions_fetcher(self, credentials=test_credentials):
        """Test UsTreasuryAuctionsFetcher."""
        params = {
            "start_date": datetime.date(2023, 9, 1),
            "end_date": datetime.date(2023, 11, 16),
        }

        fetcher = UsTreasuryAuctionsFetcher()
        result = fetcher.test(params, credentials)
        assert result is None

    @pytest.mark.record_http
    def test_treasury_prices_fetcher(self, credentials=test_credentials):
        """Test UsTreasuryPricesFetcher."""
        params = {"date": datetime.date(2024, 6, 25)}

        fetcher = UsTreasuryPricesFetcher()
        result = fetcher.test(params, credentials)
        assert result is None

    @pytest.mark.record_http
    def test_debt_to_penny_fetcher(self, credentials=test_credentials):
        """Test DebtToPennyFetcher."""
        params = {
            "start_date": datetime.date(2025, 1, 1),
            "end_date": datetime.date(2025, 3, 31),
        }

        fetcher = DebtToPennyFetcher()
        result = fetcher.test(params, credentials)
        assert result is None

    @pytest.mark.record_http
    def test_daily_treasury_statement_fetcher(self, credentials=test_credentials):
        """Test DailyTreasuryStatementFetcher."""
        params = {
            "table": "operating_cash_balance",
            "start_date": datetime.date(2025, 7, 7),
            "end_date": datetime.date(2025, 7, 11),
        }

        fetcher = DailyTreasuryStatementFetcher()
        result = fetcher.test(params, credentials)
        assert result is None

    @pytest.mark.record_http
    def test_upcoming_treasury_auctions_fetcher(self, credentials=test_credentials):
        """Test UpcomingTreasuryAuctionsFetcher."""
        params = {}

        fetcher = UpcomingTreasuryAuctionsFetcher()
        result = fetcher.test(params, credentials)
        assert result is None

    @pytest.mark.record_http
    def test_treasury_auction_results_fetcher(self, credentials=test_credentials):
        """Test TreasuryAuctionResultsFetcher."""
        params = {
            "security_type": "bill",
            "start_date": datetime.date(2026, 1, 1),
            "end_date": datetime.date(2026, 1, 31),
        }

        fetcher = TreasuryAuctionResultsFetcher()
        result = fetcher.test(params, credentials)
        assert result is None

    @pytest.mark.record_http
    def test_treasury_bulletin_fetcher(self, credentials=test_credentials):
        """Test TreasuryBulletinFetcher."""
        params = {
            "table": "ofs2",
            "start_date": datetime.date(2026, 1, 1),
        }

        fetcher = TreasuryBulletinFetcher()
        result = fetcher.test(params, credentials)
        assert result is None

    @pytest.mark.record_http
    def test_treasury_bill_offerings_fetcher(self, credentials=test_credentials):
        """Test TreasuryBillOfferingsFetcher."""
        params = {
            "start_date": datetime.date(2026, 3, 1),
            "end_date": datetime.date(2026, 3, 31),
        }

        fetcher = TreasuryBillOfferingsFetcher()
        result = fetcher.test(params, credentials)
        assert result is None
