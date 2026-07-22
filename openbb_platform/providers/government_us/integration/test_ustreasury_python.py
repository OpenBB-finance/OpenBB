"""Integration tests for the ustreasury Python interface (obb.ustreasury)."""

import pytest
from openbb_core.app.model.obbject import OBBject


@pytest.fixture(scope="session")
def obb(pytestconfig):
    """Fixture to setup obb."""
    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb

        return openbb.obb


def _clean(params: dict) -> dict:
    """Drop None values so omitted params fall back to their defaults."""
    return {k: v for k, v in params.items() if v is not None}


@pytest.mark.parametrize(
    "params",
    [
        {"provider": "us_treasury"},
        {
            "provider": "us_treasury",
            "start_date": "2025-01-01",
            "end_date": "2025-06-30",
        },
    ],
)
@pytest.mark.integration
def test_ustreasury_debt_to_penny(params, obb):
    """Total public debt outstanding per business day."""
    result = obb.ustreasury.debt_to_penny(**_clean(params))
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        {"provider": "us_treasury"},
        {
            "provider": "us_treasury",
            "table": "deposits_withdrawals_operating_cash",
            "start_date": "2025-06-01",
            "end_date": "2025-06-30",
        },
    ],
)
@pytest.mark.integration
def test_ustreasury_daily_statement(params, obb):
    """Daily Treasury Statement tables."""
    result = obb.ustreasury.daily_statement(**_clean(params))
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        {"provider": "us_treasury"},
        {"provider": "us_treasury", "security_type": "bill"},
    ],
)
@pytest.mark.integration
def test_ustreasury_upcoming_auctions(params, obb):
    """Securities scheduled for announcement or auction."""
    result = obb.ustreasury.upcoming_auctions(**_clean(params))
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        {
            "provider": "us_treasury",
            "start_date": "2025-01-01",
            "end_date": "2025-03-31",
        },
        {
            "provider": "us_treasury",
            "security_type": "bond",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
        },
    ],
)
@pytest.mark.integration
def test_ustreasury_auction_results(params, obb):
    """Auction announcements and results."""
    result = obb.ustreasury.auction_results(**_clean(params))
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        {"provider": "us_treasury"},
        {
            "provider": "us_treasury",
            "start_date": "2025-01-01",
            "end_date": "2025-03-31",
        },
    ],
)
@pytest.mark.integration
def test_ustreasury_weekly_bill_offerings(params, obb):
    """Weekly bill auction results from the Treasury Bulletin."""
    result = obb.ustreasury.weekly_bill_offerings(**_clean(params))
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
