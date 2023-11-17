"""API integration tests for equity extension."""
from datetime import time

import pytest
import requests
from openbb_provider.utils.helpers import get_querystring

# pylint: disable=too-many-lines,redefined-outer-name


@pytest.fixture(scope="session")
def headers():
    return {}


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "period": "annual", "limit": 12, "provider": "fmp"}),
        (
            {
                "provider": "intrinio",
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
            }
        ),
        (
            {
                "provider": "polygon",
                "include_sources": True,
                "order": "asc",
                "sort": "filing_date",
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
                "filing_date": "2022-10-27",
                "filing_date_lt": "2022-11-01",
                "filing_date_lte": "2022-11-01",
                "filing_date_gt": "2022-10-10",
                "filing_date_gte": "2022-10-10",
                "period_of_report_date": "2022-09-24",
                "period_of_report_date_lt": "2022-11-01",
                "period_of_report_date_lte": "2022-11-01",
                "period_of_report_date_gt": "2022-10-10",
                "period_of_report_date_gte": "2022-10-10",
            }
        ),
        (
            {
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
                "provider": "fmp",
                "cik": "0000320193",
            }
        ),
        (
            {
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
                "provider": "yfinance",
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_balance(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/balance?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "limit": 10})],
)
@pytest.mark.integration
def test_equity_fundamental_balance_growth(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/balance_growth?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"start_date": "2023-11-05", "end_date": "2023-11-10", "provider": "fmp"}),
        ({"start_date": "2023-11-05", "end_date": "2023-11-10", "provider": "nasdaq"}),
    ],
)
@pytest.mark.integration
def test_equity_calendar_dividend(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/calendar/dividend?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"start_date": "2023-11-05", "end_date": "2023-11-10", "provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_equity_calendar_split(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/calendar/split?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"start_date": "2023-11-09", "end_date": "2023-11-10", "provider": "fmp"}),
        ({"start_date": "2023-11-09", "end_date": "2023-11-10", "provider": "nasdaq"}),
    ],
)
@pytest.mark.integration
def test_equity_calendar_earnings(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/calendar/earnings?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "period": "annual", "limit": 12, "provider": "fmp"}),
        (
            {
                "provider": "intrinio",
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
            }
        ),
        (
            {
                "provider": "polygon",
                "include_sources": True,
                "order": "asc",
                "sort": "filing_date",
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
                "filing_date": "2022-10-27",
                "filing_date_lt": "2022-11-01",
                "filing_date_lte": "2022-11-01",
                "filing_date_gt": "2022-10-10",
                "filing_date_gte": "2022-10-10",
                "period_of_report_date": "2022-09-24",
                "period_of_report_date_lt": "2022-11-01",
                "period_of_report_date_lte": "2022-11-01",
                "period_of_report_date_gt": "2022-10-10",
                "period_of_report_date_gte": "2022-10-10",
            }
        ),
        (
            {
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
                "provider": "fmp",
                "cik": "0000320193",
            }
        ),
        (
            {
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
                "provider": "yfinance",
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_cash(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/cash?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "limit": 10})],
)
@pytest.mark.integration
def test_equity_fundamental_cash_growth(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/cash_growth?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL"})],
)
@pytest.mark.integration
def test_equity_fundamental_management_compensation(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/management_compensation?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL"})],
)
@pytest.mark.integration
def test_equity_fundamental_historical_splits(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/historical_splits?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL"})],
)
@pytest.mark.integration
def test_equity_fundamental_dividends(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/dividends?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "limit": 50})],
)
@pytest.mark.integration
def test_equity_fundamental_earnings(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/earnings?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL"})],
)
@pytest.mark.integration
def test_equity_fundamental_employee_count(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/employee_count?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "period": "annual", "limit": 30})],
)
@pytest.mark.integration
def test_equity_estimates_historical(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/estimates/historical?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "period": "annual", "limit": 12, "provider": "fmp"}),
        (
            {
                "provider": "intrinio",
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
            }
        ),
        (
            {
                "provider": "polygon",
                "include_sources": True,
                "order": "asc",
                "sort": "filing_date",
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
                "filing_date": "2022-10-27",
                "filing_date_lt": "2022-11-01",
                "filing_date_lte": "2022-11-01",
                "filing_date_gt": "2022-10-10",
                "filing_date_gte": "2022-10-10",
                "period_of_report_date": "2022-09-24",
                "period_of_report_date_lt": "2022-11-01",
                "period_of_report_date_lte": "2022-11-01",
                "period_of_report_date_gt": "2022-10-10",
                "period_of_report_date_gte": "2022-10-10",
            }
        ),
        (
            {
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
                "provider": "fmp",
                "cik": "0000320193",
            }
        ),
        (
            {
                "symbol": "AAPL",
                "period": "annual",
                "limit": 12,
                "provider": "yfinance",
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_income(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/income?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "limit": 10, "period": "annual"})],
)
@pytest.mark.integration
def test_equity_fundamental_income_growth(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/income_growth?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "symbol": "AAPL",
                "transaction_type": "P-Purchase",
                "limit": 10,
                "provider": "fmp",
            }
        )
    ],
)
@pytest.mark.integration
def test_equity_ownership_insider_trading(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/ownership/insider_trading?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "symbol": "AAPL",
                "include_current_quarter": True,
                "date": "2021-09-30",
                "provider": "fmp",
            }
        )
    ],
)
@pytest.mark.integration
def test_equity_ownership_institutional(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/ownership/institutional?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "symbol": "",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "limit": 100,
                "provider": "intrinio",
            }
        ),
        (
            {
                "start_date": "2023-01-01",
                "end_date": "2023-11-01",
                "status": "priced",
                "provider": "nasdaq",
                "is_spo": False,
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_calendar_ipo(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/calendar/ipo?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "period": "annual", "limit": 100})],
)
@pytest.mark.integration
def test_equity_fundamental_metrics(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/metrics?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL"})],
)
@pytest.mark.integration
def test_equity_fundamental_management(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/management?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL"})],
)
@pytest.mark.integration
def test_equity_fundamental_overview(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/overview?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "date": "2023-01-01", "page": 1})],
)
@pytest.mark.integration
def test_equity_ownership_major_holders(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/ownership/major_holders?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL"})],
)
@pytest.mark.integration
def test_equity_estimates_price_target(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/estimates/price_target?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL"})],
)
@pytest.mark.integration
def test_equity_estimates_consensus(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/estimates/consensus?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "period": "annual", "limit": 12})],
)
@pytest.mark.integration
def test_equity_fundamental_ratios(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/ratios?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "period": "annual", "structure": "flat"})],
)
@pytest.mark.integration
def test_equity_fundamental_revenue_per_geography(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/revenue_per_geography?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "period": "annual", "structure": "flat"})],
)
@pytest.mark.integration
def test_equity_fundamental_revenue_per_segment(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = (
        f"http://0.0.0.0:8000/api/v1/equity/fundamental/revenue_per_segment?{query_str}"
    )
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "type": "1", "page": 1, "limit": 100, "provider": "fmp"}),
        (
            {
                "symbol": "AAPL",
                "type": "10-K",
                "limit": 100,
                "cik": None,
                "use_cache": False,
                "provider": "sec",
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_filings(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/filings?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL"})],
)
@pytest.mark.integration
def test_equity_ownership_share_statistics(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/ownership/share_statistics?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "year": 2023})],
)
@pytest.mark.integration
def test_equity_fundamental_transcript(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/transcript?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL"})],
)
@pytest.mark.integration
def test_equity_compare_peers(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/compare/peers?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "interval": "1d",
                "provider": "yfinance",
            }
        ),
        (
            {
                "adjusted": True,
                "extended_hours": True,
                "month": "2023-01",
                "output_size": "full",
                "provider": "alpha_vantage",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-01-02",
                "interval": "1m",
            }
        ),
        (
            {
                "adjusted": True,
                "extended_hours": False,
                "output_size": "full",
                "month": "2023-01",
                "provider": "alpha_vantage",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "interval": "1d",
            }
        ),
        (
            {
                "provider": "cboe",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-01-02",
                "interval": "1m",
            }
        ),
        (
            {
                "provider": "cboe",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "interval": "1d",
            }
        ),
        (
            {
                "limit": "30",
                "provider": "fmp",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-01-02",
                "interval": "1m",
            }
        ),
        (
            {
                "limit": "30",
                "provider": "fmp",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "interval": "1d",
            }
        ),
        (
            {
                "timezone": "UTC",
                "source": "realtime",
                "start_time": time(5, 30, 0),
                "end_time": time(12, 0, 0),
                "provider": "intrinio",
                "symbol": "AAPL",
                "start_date": "2023-06-01",
                "end_date": "2023-06-03",
                "interval": "1h",
            }
        ),
        (
            {
                "timezone": "UTC",
                "source": "realtime",
                "start_time": time(5, 30, 0),
                "end_time": time(12, 0, 0),
                "provider": "intrinio",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "interval": "1d",
            }
        ),
        (
            {
                "sort": "desc",
                "limit": "49999",
                "adjusted": "True",
                "provider": "polygon",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-01-02",
                "interval": "1m",
            }
        ),
        (
            {
                "sort": "desc",
                "limit": "49999",
                "adjusted": "True",
                "provider": "polygon",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "interval": "1d",
            }
        ),
        (
            {
                "prepost": False,
                "include": True,
                "adjusted": False,
                "back_adjust": False,
                "ignore_tz": True,
                "provider": "yfinance",
                "symbol": "AAPL",
                "start_date": "2023-06-01",
                "end_date": "2023-06-03",
                "interval": "1h",
            }
        ),
        (
            {
                "prepost": False,
                "include": True,
                "adjusted": False,
                "back_adjust": False,
                "ignore_tz": True,
                "provider": "yfinance",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "interval": "1d",
            }
        ),
        (
            {
                "provider": "tiingo",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "interval": "1d",
            }
        ),
        (
            {
                "provider": "tiingo",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "interval": "1M",
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_price_historical(params, headers):
    if params.get("provider") == "alpha_vantage":
        pytest.skip("Alpha Vantage is premium.")
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/price/historical?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "limit": 100, "provider": "fmp"})],
)
@pytest.mark.integration
def test_equity_fundamental_multiples(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/multiples?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"query": "ebit", "limit": 100, "provider": "intrinio"}),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_search_financial_attributes(params, obb):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/search_financial_attributes?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "intrinio",
                "symbol": "AAPL",
                "tag": "ebit",
                "period": "annual",
                "limit": 1000,
                "type": None,
                "start_date": "2013-01-01",
                "end_date": "2023-01-01",
                "sort": "desc",
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_financial_attributes(params, obb):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/financial_attributes?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"query": "AAPl", "is_symbol": True, "provider": "cboe"}),
        ({"query": "Apple", "provider": "sec", "use_cache": False, "is_fund": False}),
        (
            {
                "query": "residential",
                "industry": "REIT",
                "sector": "Real Estate",
                "mktcap_min": None,
                "mktcap_max": None,
                "price_min": None,
                "price_max": None,
                "volume_min": None,
                "volume_max": None,
                "dividend_min": None,
                "dividend_max": None,
                "is_active": True,
                "is_etf": False,
                "beta_min": None,
                "beta_max": None,
                "country": "US",
                "exchange": "nyse",
                "limit": None,
                "provider": "fmp",
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_search(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/search?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "industry": "REIT",
                "sector": "Real Estate",
                "mktcap_min": None,
                "mktcap_max": None,
                "price_min": None,
                "price_max": None,
                "volume_min": None,
                "volume_max": None,
                "dividend_min": None,
                "dividend_max": None,
                "is_active": True,
                "is_etf": False,
                "beta_min": None,
                "beta_max": None,
                "country": "US",
                "exchange": "nyse",
                "limit": None,
                "provider": "fmp",
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_screener(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/screener?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"source": "iex", "provider": "intrinio", "symbol": "AAPL"}),
        ({"symbol": "AAPL", "provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_equity_price_quote(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/price/quote?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "provider": "cboe"})],
)
@pytest.mark.integration
def test_equity_profile(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/profile?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"sort": "desc", "provider": "yfinance"})],
)
@pytest.mark.integration
def test_equity_discovery_gainers(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/discovery/gainers?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"sort": "desc", "provider": "yfinance"})],
)
@pytest.mark.integration
def test_equity_discovery_losers(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/discovery/losers?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"sort": "desc", "provider": "yfinance"})],
)
@pytest.mark.integration
def test_equity_discovery_active(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/discovery/active?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "provider": "fmp"})],
)
@pytest.mark.integration
def test_equity_price_performance(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/price/performance?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"sort": "desc", "provider": "yfinance"})],
)
@pytest.mark.integration
def test_equity_discovery_undervalued_large_caps(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/discovery/undervalued_large_caps?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"sort": "desc"})],
)
@pytest.mark.integration
def test_equity_discovery_undervalued_growth(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/discovery/undervalued_growth?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"sort": "desc"})],
)
@pytest.mark.integration
def test_equity_discovery_aggressive_small_caps(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = (
        f"http://0.0.0.0:8000/api/v1/equity/discovery/aggressive_small_caps?{query_str}"
    )
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"sort": "desc", "provider": "yfinance"})],
)
@pytest.mark.integration
def test_equity_discovery_growth_tech(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/discovery/growth_tech?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"limit": 10, "provider": "nasdaq"})],
)
@pytest.mark.integration
def test_equity_discovery_top_retail(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/discovery/top_retail?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"limit": 5})],
)
@pytest.mark.integration
def test_equity_discovery_upcoming_release_days(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = (
        f"http://0.0.0.0:8000/api/v1/equity/discovery/upcoming_release_days?{query_str}"
    )
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "start_date": None,
                "end_date": None,
                "limit": 10,
                "form_type": None,
                "is_done": None,
                "provider": "fmp",
            }
        ),
        (
            {
                "start_date": "2023-11-06",
                "end_date": "2023-11-07",
                "limit": 50,
                "form_type": "10-Q",
                "is_done": "true",
                "provider": "fmp",
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_discovery_filings(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/discovery/filings?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
        ({"limit": 24, "provider": "sec", "symbol": "AAPL", "skip_reports": 1}),
    ],
)
@pytest.mark.integration
def test_equity_shorts_fails_to_deliver(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/shorts/fails_to_deliver?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL"})],
)
@pytest.mark.integration
def test_equity_shorts_short_volume(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/shorts/short_volume?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL"})],
)
@pytest.mark.integration
def test_equity_shorts_short_interest(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/shorts/short_interest?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "symbol": "CLOV",
                "date": "2023-10-26",
                "provider": "polygon",
                "limit": 1000,
                "timestamp_lte": None,
                "timestamp_gte": None,
                "timestamp_gt": None,
                "timestamp_lt": None,
            }
        ),
        (
            {
                "symbol": "CLOV",
                "provider": "polygon",
                "timestamp_gt": "2023-10-26T15:20:00.000000000-04:00",
                "timestamp_lt": "2023-10-26T15:30:00.000000000-04:00",
                "limit": 5000,
                "timestamp_gte": None,
                "timestamp_lte": None,
                "date": None,
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_price_nbbo(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/price/nbbo?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
        ({"tier": "T1", "is_ats": True, "provider": "finra", "symbol": "AAPL"}),
    ],
)
@pytest.mark.integration
def test_equity_darkpool_otc(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/darkpool/otc?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"provider": "fmp", "market": "EURONEXT"}),
        ({"provider": "polygon"}),
    ],
)
@pytest.mark.integration
def test_equity_market_snapshots(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/market_snapshots?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "limit": 5, "provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_historical_eps(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/historical_eps?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"provider": "tiingo", "symbol": "AAPL"})],
)
@pytest.mark.integration
def test_equity_fundamental_trailing_dividend_yield(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/trailing_dividend_yield?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200
