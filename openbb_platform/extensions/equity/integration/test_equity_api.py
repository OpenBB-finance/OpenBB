"""API integration tests for equity extension."""

import base64

import pytest
import requests
from extensions.tests.conftest import parametrize
from openbb_core.env import Env
from openbb_core.provider.utils.helpers import get_querystring

# pylint: disable=too-many-lines,redefined-outer-name


@pytest.fixture(scope="session")
def headers():
    """Get the headers for the API request."""
    userpass = f"{Env().API_USERNAME}:{Env().API_PASSWORD}"
    userpass_bytes = userpass.encode("ascii")
    base64_bytes = base64.b64encode(userpass_bytes)

    return {"Authorization": f"Basic {base64_bytes.decode('ascii')}"}


@parametrize(
    "params",
    [
        ({"symbol": "AAPL", "period": "annual", "limit": 12, "provider": "fmp"}),
        (
            {
                "provider": "intrinio",
                "symbol": "AAPL",
                "period": "annual",
                "fiscal_year": None,
                "limit": 2,
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
    """Test the equity fundamental balance endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/balance?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"symbol": "AAPL", "limit": 10, "provider": "fmp", "period": "annual"})],
)
@pytest.mark.integration
def test_equity_fundamental_balance_growth(params, headers):
    """Test the equity fundamental balance growth endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/balance_growth?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"start_date": "2023-11-05", "end_date": "2023-11-10", "provider": "fmp"}),
        ({"start_date": "2023-11-05", "end_date": "2023-11-10", "provider": "nasdaq"}),
    ],
)
@pytest.mark.integration
def test_equity_calendar_dividend(params, headers):
    """Test the equity calendar dividend endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/calendar/dividend?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"start_date": "2023-11-05", "end_date": "2023-11-10", "provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_equity_calendar_splits(params, headers):
    """Test the equity calendar splits endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/calendar/splits?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"start_date": "2023-11-09", "end_date": "2023-11-10", "provider": "fmp"}),
        ({"start_date": "2023-11-09", "end_date": "2023-11-10", "provider": "nasdaq"}),
        ({"start_date": "2023-11-09", "end_date": "2023-11-10", "provider": "tmx"}),
        (
            {
                "start_date": None,
                "end_date": None,
                "provider": "seeking_alpha",
                "country": "us",
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_calendar_earnings(params, headers):
    """Test the equity calendar earnings endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/calendar/earnings?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        (
            {
                "provider": "intrinio",
                "symbol": "AAPL",
                "period": "ttm",
                "fiscal_year": 2015,
                "limit": 4,
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
    """Test the equity fundamental cash endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/cash?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"symbol": "AAPL", "limit": 10, "provider": "fmp", "period": "annual"})],
)
@pytest.mark.integration
def test_equity_fundamental_cash_growth(params, headers):
    """Test the equity fundamental cash growth endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/cash_growth?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        (
            {
                "symbol": "AAPL",
                "year": 2022,
                "provider": "fmp",
            }
        ),
        (
            {
                "symbol": "AAPL",
                "provider": "fmp",
                "year": None,
            }
        ),
        (
            {
                "symbol": "AAPL,MSFT",
                "provider": "fmp",
                "year": None,
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_management_compensation(params, headers):
    """Test the equity fundamental management compensation endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/management_compensation?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"symbol": "AAPL", "provider": "fmp"})],
)
@pytest.mark.integration
def test_equity_fundamental_historical_splits(params, headers):
    """Test the equity fundamental historical splits endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/historical_splits?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        (
            {
                "symbol": "AAPL",
                "start_date": "2021-01-01",
                "end_date": "2023-06-06",
                "limit": 100,
                "provider": "intrinio",
            }
        ),
        ({"symbol": "RY", "provider": "tmx"}),
        (
            {
                "symbol": "AAPL",
                "start_date": "2021-01-01",
                "end_date": "2023-06-06",
                "provider": "fmp",
            }
        ),
        (
            {
                "symbol": "AAPL",
                "limit": 3,
                "provider": "intrinio",
            }
        ),
        (
            {
                "symbol": "AAPL",
                "provider": "fmp",
            }
        ),
        (
            {
                "symbol": "AAPL",
                "start_date": "2021-01-01",
                "end_date": "2023-06-06",
                "provider": "nasdaq",
            }
        ),
        (
            {
                "symbol": "AAPL",
                "provider": "yfinance",
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_dividends(params, headers):
    """Test the equity fundamental dividends endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/dividends?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"symbol": "AAPL", "provider": "fmp"})],
)
@pytest.mark.integration
def test_equity_fundamental_employee_count(params, headers):
    """Test the equity fundamental employee count endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/employee_count?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"symbol": "AAPL,MSFT", "period": "annual", "limit": 30})],
)
@pytest.mark.integration
def test_equity_estimates_historical(params, headers):
    """Test the equity estimates historical endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/estimates/historical?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        (
            {
                "symbol": "AAPL,MSFT",
                "fiscal_period": "fy",
                "fiscal_year": None,
                "calendar_year": None,
                "calendar_period": None,
                "provider": "intrinio",
            }
        ),
        (
            {
                "symbol": "AAPL,BAM:CA",
                "period": "annual",
                "provider": "seeking_alpha",
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_estimates_forward_sales(params, headers):
    """Test the equity estimates forward sales endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/estimates/forward_sales?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        (
            {
                "symbol": "AAPL,MSFT",
                "fiscal_period": "fy",
                "fiscal_year": None,
                "calendar_year": None,
                "calendar_period": None,
                "provider": "intrinio",
            }
        ),
        (
            {
                "symbol": "AAPL,MSFT",
                "fiscal_period": "annual",
                "limit": None,
                "include_historical": False,
                "provider": "fmp",
            }
        ),
        (
            {
                "symbol": "AAPL,BAM:CA",
                "period": "annual",
                "provider": "seeking_alpha",
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_estimates_forward_eps(params, headers):
    """Test the equity estimates forward EPS endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/estimates/forward_eps?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"symbol": "AAPL", "period": "annual", "limit": 12, "provider": "fmp"}),
        (
            {
                "provider": "intrinio",
                "symbol": "AAPL",
                "period": "ytd",
                "fiscal_year": 2020,
                "limit": 4,
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
    """Test the equity fundamental income endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/income?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"symbol": "AAPL", "limit": 10, "period": "annual", "provider": "fmp"})],
)
@pytest.mark.integration
def test_equity_fundamental_income_growth(params, headers):
    """Test the equity fundamental income growth endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/income_growth?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        (
            {
                "symbol": "RY",
                "provider": "tmx",
                "limit": 0,
            }
        ),
        (
            {
                "provider": "fmp",
                "symbol": "AAPL",
                "limit": 10,
                "transaction_type": None,
            }
        ),
        (
            {
                "provider": "intrinio",
                "symbol": "AAPL",
                "limit": 10,
                "start_date": "2021-01-01",
                "end_date": "2023-06-06",
                "ownership_type": None,
                "sort_by": "updated_on",
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_ownership_insider_trading(params, headers):
    """Test the equity ownership insider trading endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/ownership/insider_trading?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        (
            {
                "symbol": "AAPL",
                "include_current_quarter": True,
                "date": "2021-09-30",
                "provider": "fmp",
            }
        ),
        # Disabled due to unreliable Intrinio endpoint
        # (
        #     {
        #         "provider": "intrinio",
        #         "symbol": "AAPL",
        #         "limit": 100,
        #     }
        # ),
    ],
)
@pytest.mark.integration
def test_equity_ownership_institutional(params, headers):
    """Test the equity ownership institutional endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/ownership/institutional?{query_str}"
    result = requests.get(url, headers=headers, timeout=20)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        (
            {
                "symbol": None,
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
    """Test the equity calendar IPO endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/calendar/ipo?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        (
            {
                "provider": "fmp",
                "symbol": "AAPL",
                "period": "annual",
                "limit": 100,
                "with_ttm": False,
            }
        ),
        ({"provider": "intrinio", "symbol": "AAPL", "limit": 100}),
        ({"provider": "yfinance", "symbol": "AAPL"}),
        ({"provider": "finviz", "symbol": "AAPL,GOOG"}),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_metrics(params, headers):
    """Test the equity fundamental metrics endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/metrics?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"symbol": "AAPL", "provider": "fmp"}),
        ({"symbol": "AAPL", "provider": "yfinance"}),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_management(params, headers):
    """Test the equity fundamental management endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/management?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"symbol": "AAPL", "date": "2023-01-01", "page": 1, "provider": "fmp"})],
)
@pytest.mark.integration
def test_equity_ownership_major_holders(params, headers):
    """Test the equity ownership major holders endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/ownership/major_holders?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"symbol": "AAPL", "limit": 10, "provider": "fmp", "with_grade": True}),
        ({"symbol": "AAPL", "provider": "finviz"}),
        (
            {
                "symbol": "AAPL",
                "limit": 10,
                "provider": "benzinga",
                # optional provider params
                "fields": None,
                "date": None,
                "start_date": None,
                "end_date": None,
                "importance": None,
                "updated": None,
                "action": None,
                "analyst_ids": None,
                "firm_ids": None,
                "page": 0,
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_estimates_price_target(params, headers):
    """Test the equity estimates price target endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/estimates/price_target?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        (
            {
                "limit": 10,
                "provider": "benzinga",
                # optional provider params
                "fields": None,
                "analyst_ids": None,
                "firm_ids": None,
                "firm_name": "Barclays",
                "analyst_name": None,
                "page": 0,
            }
        ),
        (
            {
                "limit": 3,
                "provider": "benzinga",
                # optional provider params
                "fields": None,
                "analyst_ids": None,
                "firm_ids": None,
                "firm_name": "Barclays,Credit Suisse",
                "analyst_name": None,
                "page": 1,
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_estimates_analyst_search(params, headers):
    """Test the equity estimates analyst search endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/estimates/analyst_search?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"symbol": "AAPL", "provider": "fmp"}),
        ({"symbol": "AAPL,AMZN,RELIANCE.NS", "provider": "yfinance"}),
        ({"symbol": "TD:US", "provider": "tmx"}),
        (
            {
                "symbol": "AAPL,MSFT",
                "industry_group_number": None,
                "provider": "intrinio",
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_estimates_consensus(params, headers):
    """Test the equity estimates consensus endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/estimates/consensus?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"symbol": "AAPL", "period": "annual", "limit": 12, "provider": "fmp"}),
        (
            {
                "symbol": "AAPL",
                "period": "ttm",
                "fiscal_year": 2019,
                "limit": 4,
                "provider": "intrinio",
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_ratios(params, headers):
    """Test the equity fundamental ratios endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/ratios?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"symbol": "AAPL", "period": "annual", "provider": "fmp"})],
)
@pytest.mark.integration
def test_equity_fundamental_revenue_per_geography(params, headers):
    """Test the equity fundamental revenue per geography endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/revenue_per_geography?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"symbol": "AAPL", "period": "annual", "provider": "fmp"})],
)
@pytest.mark.integration
def test_equity_fundamental_revenue_per_segment(params, headers):
    """Test the equity fundamental revenue per segment endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = (
        f"http://0.0.0.0:8000/api/v1/equity/fundamental/revenue_per_segment?{query_str}"
    )
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"symbol": "AAPL", "form_type": "1", "limit": 100, "provider": "fmp"}),
        (
            {
                "provider": "intrinio",
                "symbol": "AAPL",
                "start_date": "2021-01-01",
                "end_date": "2023-11-01",
                "form_type": None,
                "limit": 100,
                "thea_enabled": None,
            }
        ),
        (
            {
                "symbol": "AAPL",
                "limit": 3,
                "form_type": "8-K",
                "start_date": None,
                "end_date": None,
                "cik": None,
                "provider": "sec",
                "use_cache": False,
            }
        ),
        (
            {
                "cik": "0001067983",
                "limit": 3,
                "form_type": "10-Q",
                "symbol": None,
                "start_date": None,
                "end_date": None,
                "provider": "sec",
                "use_cache": False,
            }
        ),
        (
            {
                "provider": "tmx",
                "symbol": "IBM:US",
                "start_date": "2023-09-30",
                "end_date": "2023-12-31",
                "limit": None,
                "form_type": None,
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_filings(params, headers):
    """Test the equity fundamental filings endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/filings?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"symbol": "AAPL", "provider": "fmp"}),
        ({"symbol": "AAPL", "provider": "intrinio"}),
        ({"symbol": "AAPL", "provider": "yfinance"}),
    ],
)
@pytest.mark.integration
def test_equity_ownership_share_statistics(params, headers):
    """Test the equity ownership share statistics endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/ownership/share_statistics?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"symbol": "AAPL", "year": 2023})],
)
@pytest.mark.integration
def test_equity_fundamental_transcript(params, headers):
    """Test the equity fundamental transcript endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/transcript?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"symbol": "AAPL"})],
)
@pytest.mark.integration
def test_equity_compare_peers(params, headers):
    """Test the equity compare peers endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/compare/peers?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"group": "country", "metric": "overview", "provider": "finviz"})],
)
@pytest.mark.integration
def test_equity_compare_groups(params, headers):
    """Test the equity compare groups endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/compare/groups?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        (
            {
                "adjustment": "unadjusted",
                "extended_hours": True,
                "provider": "alpha_vantage",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "interval": "15m",
            }
        ),
        (
            {
                "provider": "cboe",
                "symbol": "AAPL",
                "start_date": None,
                "end_date": None,
                "interval": "1m",
                "use_cache": False,
            }
        ),
        (
            {
                "provider": "cboe",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "interval": "1d",
                "use_cache": False,
            }
        ),
        (
            {
                "provider": "fmp",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "interval": "1d",
            }
        ),
        (
            {
                "interval": "1h",
                "provider": "fmp",
                "symbol": "AAPL,MSFT",
                "start_date": None,
                "end_date": None,
            }
        ),
        (
            {
                "timezone": "UTC",
                "source": "realtime",
                "start_time": None,
                "end_time": None,
                "provider": "intrinio",
                "symbol": "AAPL",
                "start_date": "2023-06-01",
                "end_date": "2023-06-03",
                "interval": "1h",
            }
        ),
        (
            {
                "timezone": None,
                "source": "delayed",
                "start_time": None,
                "end_time": None,
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
                "adjustment": "unadjusted",
                "provider": "polygon",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-01-03",
                "interval": "1m",
                "extended_hours": False,
            }
        ),
        (
            {
                "sort": "desc",
                "limit": "49999",
                "adjustment": "splits_only",
                "provider": "polygon",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "interval": "1d",
                "extended_hours": False,
            }
        ),
        (
            {
                "extended_hours": False,
                "include_actions": False,
                "adjustment": "splits_only",
                "provider": "yfinance",
                "symbol": "AAPL",
                "start_date": None,
                "end_date": None,
                "interval": "1h",
            }
        ),
        (
            {
                "extended_hours": False,
                "include_actions": True,
                "adjustment": "splits_only",
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
        (
            {
                "provider": "tradier",
                "symbol": "AAPL,MSFT",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "interval": "1M",
                "extended_hours": False,
            }
        ),
        (
            {
                "provider": "tradier",
                "symbol": "AAPL,MSFT",
                "start_date": None,
                "end_date": None,
                "interval": "15m",
                "extended_hours": False,
            }
        ),
        (
            {
                "provider": "tmx",
                "symbol": "AAPL:US",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "interval": "1d",
                "adjustment": "splits_only",
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_price_historical(params, headers):
    """Test the equity price historical endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/price/historical?{query_str}"
    result = requests.get(url, headers=headers, timeout=40)
    result = requests.get(url, headers=headers, timeout=40)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"symbol": "AAPL", "provider": "fmp"})],
)
@pytest.mark.integration
def test_equity_fundamental_multiples(params, headers):
    """Test the equity fundamental multiples endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/multiples?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"query": "ebit", "limit": 100, "provider": "intrinio"}),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_search_attributes(params, headers):
    """Test the equity fundamental search attributes endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/search_attributes?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        (
            {
                "provider": "intrinio",
                "symbol": "AAPL",
                "tag": "ebit",
                "frequency": "yearly",
                "limit": 1000,
                "tag_type": None,
                "start_date": "2013-01-01",
                "end_date": "2023-01-01",
                "sort": "desc",
            }
        ),
        (
            {
                "provider": "intrinio",
                "symbol": "AAPL",
                "tag": "ebit,ebitda,marketcap",
                "frequency": "yearly",
                "limit": 1000,
                "tag_type": None,
                "start_date": "2013-01-01",
                "end_date": "2023-01-01",
                "sort": "desc",
            }
        ),
        (
            {
                "provider": "intrinio",
                "symbol": "AAPL",
                "tag": ["ebit", "ebitda", "marketcap"],
                "frequency": "yearly",
                "limit": 1000,
                "tag_type": None,
                "start_date": "2013-01-01",
                "end_date": "2023-01-01",
                "sort": "desc",
            }
        ),
        (
            {
                "provider": "intrinio",
                "symbol": "AAPL,MSFT",
                "tag": "ebit,ebitda,marketcap",
                "frequency": "yearly",
                "limit": 1000,
                "tag_type": None,
                "start_date": "2013-01-01",
                "end_date": "2023-01-01",
                "sort": "desc",
            }
        ),
        (
            {
                "provider": "intrinio",
                "symbol": ["AAPL", "MSFT"],
                "tag": ["ebit", "ebitda", "marketcap"],
                "frequency": "yearly",
                "limit": 1000,
                "tag_type": None,
                "start_date": "2013-01-01",
                "end_date": "2023-01-01",
                "sort": "desc",
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_historical_attributes(params, headers):
    """Test the equity fundamental historical attributes endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/historical_attributes?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        (
            {
                "provider": "intrinio",
                "symbol": "AAPL",
                "tag": "ceo",
            }
        ),
        (
            {
                "provider": "intrinio",
                "symbol": "AAPL",
                "tag": "ebitda",
            }
        ),
        (
            {
                "provider": "intrinio",
                "symbol": "AAPL",
                "tag": "ceo,ebitda",
            }
        ),
        (
            {
                "provider": "intrinio",
                "symbol": "AAPL",
                "tag": ["ceo", "ebitda"],
            }
        ),
        (
            {
                "provider": "intrinio",
                "symbol": "AAPL,MSFT",
                "tag": ["ceo", "ebitda"],
            }
        ),
        (
            {
                "provider": "intrinio",
                "symbol": ["AAPL", "MSFT"],
                "tag": ["ceo", "ebitda"],
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_latest_attributes(params, headers):
    """Test the equity fundamental latest attributes endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/latest_attributes?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"query": "AAPl", "is_symbol": True, "provider": "cboe", "use_cache": False}),
        ({"query": "Apple", "provider": "sec", "use_cache": False, "is_fund": False}),
        ({"query": "", "provider": "nasdaq", "is_etf": True}),
        ({"query": "gold", "provider": "tmx", "use_cache": False}),
        ({"query": "gold", "provider": "tradier", "is_symbol": False}),
        (
            {
                "query": "gold",
                "provider": "intrinio",
                "active": True,
                "limit": 100,
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_search(params, headers):
    """Test the equity search endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/search?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        (
            {
                "industry": "REIT",
                "sector": "real_estate",
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
        (
            {
                "sector": "consumer_staples,consumer_discretionary",
                "exchange": "all",
                "exsubcategory": "all",
                "region": "all",
                "country": "all",
                "mktcap": "large",
                "recommendation": "all",
                "limit": None,
                "provider": "nasdaq",
            }
        ),
        (
            {
                "metric": "overview",
                "signal": None,
                "preset": None,
                "filters_dict": None,
                "sector": "consumer_defensive",
                "industry": "grocery_stores",
                "index": "all",
                "exchange": "all",
                "mktcap": "all",
                "recommendation": "all",
                "limit": None,
                "provider": "finviz",
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_screener(params, headers):
    """Test the equity screener endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/screener?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"source": "iex", "provider": "intrinio", "symbol": "AAPL"}),
        ({"symbol": "AAPL", "provider": "fmp"}),
        ({"symbol": "AAPL", "provider": "cboe", "use_cache": False}),
        ({"symbol": "AAPL", "provider": "yfinance"}),
        ({"symbol": "AAPL:US", "provider": "tmx"}),
        ({"symbol": "AAPL,MSFT", "provider": "tradier"}),
    ],
)
@pytest.mark.integration
def test_equity_price_quote(params, headers):
    """Test the equity price quote endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/price/quote?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"symbol": "MSFT", "provider": "intrinio"}),
        ({"symbol": "AAPL,MSFT", "provider": "intrinio"}),
        ({"symbol": "AAPL,MSFT", "provider": "finviz"}),
        ({"symbol": "AAPL,MSFT", "provider": "yfinance"}),
        ({"provider": "tmx", "symbol": "AAPL:US"}),
        ({"symbol": "AAPL,MSFT", "provider": "fmp"}),
    ],
)
@pytest.mark.integration
def test_equity_profile(params, headers):
    """Test the equity profile endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/profile?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"sort": "desc", "provider": "yfinance"}),
        ({"provider": "tmx", "category": "52w_high"}),
    ],
)
@pytest.mark.integration
def test_equity_discovery_gainers(params, headers):
    """Test the equity discovery gainers endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/discovery/gainers?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"sort": "desc", "provider": "yfinance"})],
)
@pytest.mark.integration
def test_equity_discovery_losers(params, headers):
    """Test the equity discovery losers endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/discovery/losers?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"sort": "desc", "provider": "yfinance"})],
)
@pytest.mark.integration
def test_equity_discovery_active(params, headers):
    """Test the equity discovery active endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/discovery/active?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"symbol": "AAPL", "provider": "fmp"}),
        ({"symbol": "AAPL,MSFT", "provider": "finviz"}),
    ],
)
@pytest.mark.integration
def test_equity_price_performance(params, headers):
    """Test the equity price performance endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/price/performance?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"sort": "desc", "provider": "yfinance"})],
)
@pytest.mark.integration
def test_equity_discovery_undervalued_large_caps(params, headers):
    """Test the equity discovery undervalued large caps endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/discovery/undervalued_large_caps?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"sort": "desc", "provider": "yfinance"})],
)
@pytest.mark.integration
def test_equity_discovery_undervalued_growth(params, headers):
    """Test the equity discovery undervalued growth endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/discovery/undervalued_growth?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"sort": "desc", "provider": "yfinance"})],
)
@pytest.mark.integration
def test_equity_discovery_aggressive_small_caps(params, headers):
    """Test the equity discovery aggressive small caps endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = (
        f"http://0.0.0.0:8000/api/v1/equity/discovery/aggressive_small_caps?{query_str}"
    )
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"sort": "desc", "provider": "yfinance"})],
)
@pytest.mark.integration
def test_equity_discovery_growth_tech(params, headers):
    """Test the equity discovery growth tech endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/discovery/growth_tech?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"limit": 10, "provider": "nasdaq"})],
)
@pytest.mark.integration
def test_equity_discovery_top_retail(params, headers):
    """Test the equity discovery top retail endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/discovery/top_retail?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
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
    """Test the equity discovery filings endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/discovery/filings?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
        (
            {
                "limit": 24,
                "provider": "sec",
                "symbol": "AAPL",
                "skip_reports": 1,
                "use_cache": False,
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_shorts_fails_to_deliver(params, headers):
    """Test the equity shorts fails to deliver endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/shorts/fails_to_deliver?{query_str}"
    result = requests.get(url, headers=headers, timeout=20)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"symbol": "AAPL", "provider": "stockgrid"})],
)
@pytest.mark.integration
def test_equity_shorts_short_volume(params, headers):
    """Test the equity shorts short volume endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/shorts/short_volume?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"symbol": "AAPL", "provider": "finra"})],
)
@pytest.mark.integration
def test_equity_shorts_short_interest(params, headers):
    """Test the equity shorts short interest endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/shorts/short_interest?{query_str}"
    result = requests.get(url, headers=headers, timeout=60)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        (
            {
                "symbol": "CLOV",
                "provider": "polygon",  # premium endpoint
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
    """Test the equity price NBBO endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/price/nbbo?{query_str}"
    result = requests.get(url, headers=headers, timeout=40)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
        ({"tier": "T1", "is_ats": True, "provider": "finra", "symbol": "AAPL"}),
    ],
)
@pytest.mark.integration
def test_equity_darkpool_otc(params, headers):
    """Test the equity darkpool otc endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/darkpool/otc?{query_str}"

    try:
        result = requests.get(url, headers=headers, timeout=30)
    except requests.exceptions.Timeout:
        pytest.skip("Timeout: `equity/darkpool/otc` took too long to respond.")

    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"provider": "fmp", "market": "euronext"}),
        ({"provider": "polygon"}),
        ({"provider": "intrinio", "date": "2022-06-30"}),
    ],
)
@pytest.mark.integration
def test_equity_market_snapshots(params, headers):
    """Test the equity market snapshots endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/market_snapshots?{query_str}"
    result = requests.get(url, headers=headers, timeout=20)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"symbol": "AAPL", "limit": 5, "provider": "fmp"}),
        (
            {
                "symbol": "AAPL",
                "period": "quarter",
                "limit": 5,
                "provider": "alpha_vantage",
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_historical_eps(params, headers):
    """Test the equity fundamental historical eps endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/historical_eps?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"provider": "tiingo", "symbol": "AAPL", "limit": 10})],
)
@pytest.mark.integration
def test_equity_fundamental_trailing_dividend_yield(params, headers):
    """Test the equity fundamental trailing dividend yield endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/fundamental/trailing_dividend_yield?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        (
            {
                "symbol": "AAPL",
                "statement_type": "income",
                "period": "quarter",
                "limit": 5,
                "fiscal_year": None,
                "provider": "intrinio",
            }
        ),
        (
            {
                "symbol": "AAPL",
                "statement_type": "cash",
                "period": "annual",
                "limit": 1,
                "fiscal_year": 2015,
                "provider": "intrinio",
            }
        ),
        (
            {
                "symbol": "AAPL",
                "statement_type": "balance",
                "period": "annual",
                "fiscal_year": None,
                "limit": 10,
                "provider": "intrinio",
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_fundamental_reported_financials(params, headers):
    """Test the equity fundamental reported financials endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = (
        f"http://0.0.0.0:8000/api/v1/equity/fundamental/reported_financials?{query_str}"
    )
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        (
            {
                "symbol": "NVDA",
                "date": None,
                "limit": 1,
                "provider": "sec",
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_ownership_form_13f(params, headers):
    """Test the equity ownership form 13f endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/ownership/form_13f?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        (
            {
                "symbol": "NVDA,MSFT",
                "provider": "intrinio",
            }
        ),
        (
            {
                "symbol": None,
                "provider": "intrinio",
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_estimates_forward_pe(params, headers):
    """Test the equity estimates forward_pe endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/estimates/forward_pe?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        (
            {
                "symbol": "AAPL,MSFT",
                "fiscal_period": "quarter",
                "provider": "intrinio",
            }
        ),
        (
            {
                "symbol": "AAPL,MSFT",
                "fiscal_period": "annual",
                "limit": None,
                "include_historical": False,
                "provider": "fmp",
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_estimates_forward_ebitda(params, headers):
    """Test the equity estimates forward_ebitda endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/estimates/forward_ebitda?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        (
            {
                "provider": "sec",
                "symbol": "NVDA,AAPL,AMZN,MSFT,GOOG,SMCI",
                "fact": "RevenueFromContractWithCustomerExcludingAssessedTax",
                "year": 2024,
                "fiscal_period": None,
                "instantaneous": False,
                "use_cache": False,
            }
        ),
        (
            {
                "provider": "sec",
                "symbol": None,
                "fact": None,
                "year": None,
                "fiscal_period": None,
                "instantaneous": False,
                "use_cache": False,
            }
        ),
    ],
)
@pytest.mark.integration
def test_equity_compare_company_facts(params, headers):
    """Test the equity compare company_facts endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/compare/company_facts?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        (
            {
                "symbol": "AAPL,MSFT",
                "start_date": None,
                "end_date": None,
                "provider": "fmp",
            }
        )
    ],
)
@pytest.mark.integration
def test_equity_historical_market_cap(params, headers):
    """Test the equity historical market cap endpoint."""
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/equity/historical_market_cap?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200
