"""API integration tests for stocks extension."""
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
def test_stocks_fa_balance(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/balance?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "limit": 10})],
)
@pytest.mark.integration
def test_stocks_fa_balance_growth(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/balance_growth?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"start_date": "2023-01-01", "end_date": "2023-06-06"})],
)
@pytest.mark.integration
def test_stocks_fa_cal(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/cal?{query_str}"
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
def test_stocks_fa_cash(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/cash?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "limit": 10})],
)
@pytest.mark.integration
def test_stocks_fa_cash_growth(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/cash_growth?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL"})],
)
@pytest.mark.integration
def test_stocks_fa_comp(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/comp?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"start_date": "2023-01-01", "end_date": "2023-06-06"})],
)
@pytest.mark.integration
def test_stocks_fa_comsplit(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/comsplit?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL"})],
)
@pytest.mark.integration
def test_stocks_fa_divs(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/divs?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "limit": 50})],
)
@pytest.mark.integration
def test_stocks_fa_earning(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/earning?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL"})],
)
@pytest.mark.integration
def test_stocks_fa_emp(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/emp?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "period": "annual", "limit": 30})],
)
@pytest.mark.integration
def test_stocks_fa_est(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/est?{query_str}"
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
def test_stocks_fa_income(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/income?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "limit": 10, "period": "annual"})],
)
@pytest.mark.integration
def test_stocks_fa_income_growth(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/income_growth?{query_str}"
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
def test_stocks_fa_ins(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/ins?{query_str}"
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
def test_stocks_fa_ins_own(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/ins_own?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "period": "annual", "limit": 100})],
)
@pytest.mark.integration
def test_stocks_fa_metrics(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/metrics?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL"})],
)
@pytest.mark.integration
def test_stocks_fa_mgmt(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/mgmt?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL"})],
)
@pytest.mark.integration
def test_stocks_fa_overview(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/overview?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "date": "2023-01-01", "page": 1})],
)
@pytest.mark.integration
def test_stocks_fa_own(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/own?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL"})],
)
@pytest.mark.integration
def test_stocks_fa_pt(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/pt?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL"}), ({"with_grade": True, "provider": "fmp", "symbol": "AAPL"})],
)
@pytest.mark.integration
def test_stocks_fa_pta(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/pta?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "period": "annual", "limit": 12})],
)
@pytest.mark.integration
def test_stocks_fa_ratios(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/ratios?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "period": "annual", "structure": "flat"})],
)
@pytest.mark.integration
def test_stocks_fa_revgeo(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/revgeo?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "period": "annual", "structure": "flat"})],
)
@pytest.mark.integration
def test_stocks_fa_revseg(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/revseg?{query_str}"
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
def test_stocks_fa_filings(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/filings?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL"})],
)
@pytest.mark.integration
def test_stocks_fa_shrs(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/shrs?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL"})],
)
@pytest.mark.integration
def test_stocks_fa_split(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/split?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "year": 2023})],
)
@pytest.mark.integration
def test_stocks_fa_transcript(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/transcript?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL"})],
)
@pytest.mark.integration
def test_stocks_ca_peers(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/ca/peers?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "provider": "cboe"}),
        ({"date": "2023-01-25", "provider": "intrinio", "symbol": "AAPL"}),
        ({"provider": "cboe", "symbol": "AAPL"}),
    ],
)
@pytest.mark.integration
def test_stocks_options_chains(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/options/chains?{query_str}"
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
    ],
)
@pytest.mark.integration
def test_stocks_load(params, headers):
    if params.get("provider") == "alpha_vantage":
        pytest.skip("Alpha Vantage is premium.")
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/load?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"symbols": "AAPL", "limit": 20, "provider": "benzinga"}),
        (
            {
                "display": "full",
                "date": "2023-01-01",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "updated_since": 1,
                "published_since": 1,
                "sort": "created",
                "order": "desc",
                "isin": "US0378331005",
                "cusip": "037833100",
                "channels": "General",
                "topics": "AAPL",
                "authors": "Benzinga Insights",
                "content_types": "headline",
                "provider": "benzinga",
                "symbols": "AAPL,MSFT",
                "limit": 20,
            }
        ),
        (
            {
                "published_utc": "2023-01-01",
                "order": "desc",
                "provider": "polygon",
                "symbols": "AAPL",
                "limit": 20,
            }
        ),
        (
            {
                "provider": "fmp",
                "symbols": "AAPL",
                "limit": 20,
                "page": 1,
            }
        ),
        (
            {
                "provider": "yfinance",
                "symbols": "AAPL",
                "limit": 20,
            }
        ),
        (
            {
                "provider": "intrinio",
                "symbols": "AAPL",
                "limit": 20,
            }
        ),
    ],
)
@pytest.mark.integration
def test_stocks_news(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/news?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "limit": 100})],
)
@pytest.mark.integration
def test_stocks_multiples(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/multiples?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"query": "AAPl", "is_symbol": True, "provider": "cboe"}),
        ({"query": "Apple", "provider": "sec", "use_cache": False, "is_fund": False}),
    ],
)
@pytest.mark.integration
def test_stocks_search(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/search?{query_str}"
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
def test_stocks_quote(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/quote?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "provider": "cboe"})],
)
@pytest.mark.integration
def test_stocks_info(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/info?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"sort": "desc", "provider": "yfinance"})],
)
@pytest.mark.integration
def test_stocks_disc_gainers(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/disc/gainers?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"sort": "desc", "provider": "yfinance"})],
)
@pytest.mark.integration
def test_stocks_disc_losers(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/disc/losers?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"sort": "desc", "provider": "yfinance"})],
)
@pytest.mark.integration
def test_stocks_disc_active(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/disc/active?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "provider": "sec"}),
        ({"limit": 24, "provider": "sec", "symbol": "AAPL", "skip_reports": 1}),
    ],
)
@pytest.mark.integration
def test_stocks_ftd(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/ftd?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"symbol": "AAPL", "provider": "fmp"})],
)
@pytest.mark.integration
def test_stocks_price_performance(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/price_performance?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "symbol": "UBER",
                "start_date": "2018-01-01",
                "end_date": "2023-06-06",
                "limit": 300,
                "provider": "intrinio",
            }
        ),
    ],
)
@pytest.mark.integration
def test_stocks_calendar_ipo(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/calendar_ipo?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"sort": "desc", "provider": "yfinance"})],
)
@pytest.mark.integration
def test_stocks_disc_undervalued_large_caps(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/disc/undervalued_large_caps?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"sort": "desc", "provider": "yfinance"})],
)
@pytest.mark.integration
def test_stocks_disc_undervalued_growth_equities(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/disc/undervalued_growth_equities?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"sort": "desc", "provider": "yfinance"})],
)
@pytest.mark.integration
def test_stocks_disc_aggressive_small_caps(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/disc/aggressive_small_caps?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"sort": "desc", "provider": "yfinance"})],
)
@pytest.mark.integration
def test_stocks_disc_growth_tech_equities(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/disc/growth_tech_equities?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"limit": 10, "provider": "qunadl"})],
)
@pytest.mark.integration
def test_stocks_disc_top_retail(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/disc/top_retail?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"limit": 5, "start_date": "2023-01-01"})],
)
@pytest.mark.integration
def test_stocks_disc_upcoming_release_days(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/disc/upcoming_release_days?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200
