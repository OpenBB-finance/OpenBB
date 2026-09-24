"""Integration tests for the ustreasury REST API."""

import pytest
import requests
from openbb_core.provider.utils.helpers import get_querystring

BASE = "http://127.0.0.1:8000/api/v1/ustreasury"


def _get(endpoint: str, params: dict, headers: dict) -> requests.Response:
    """GET an endpoint with None-stripped query params."""
    query = get_querystring({k: v for k, v in params.items() if v is not None}, [])
    return requests.get(f"{BASE}/{endpoint}?{query}", headers=headers, timeout=60)


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
def test_ustreasury_debt_to_penny(params, headers):
    """GET /debt_to_penny."""
    assert _get("debt_to_penny", params, headers).status_code == 200


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
def test_ustreasury_daily_statement(params, headers):
    """GET /daily_statement."""
    assert _get("daily_statement", params, headers).status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {"provider": "us_treasury"},
        {"provider": "us_treasury", "security_type": "bill"},
    ],
)
@pytest.mark.integration
def test_ustreasury_upcoming_auctions(params, headers):
    """GET /upcoming_auctions."""
    assert _get("upcoming_auctions", params, headers).status_code == 200


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
def test_ustreasury_auction_results(params, headers):
    """GET /auction_results."""
    assert _get("auction_results", params, headers).status_code == 200


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
def test_ustreasury_weekly_bill_offerings(params, headers):
    """GET /weekly_bill_offerings."""
    assert _get("weekly_bill_offerings", params, headers).status_code == 200
