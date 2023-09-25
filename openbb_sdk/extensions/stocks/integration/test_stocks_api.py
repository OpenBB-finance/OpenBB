import pytest
import requests
from openbb_provider.utils.helpers import get_querystring


def get_token():
    return requests.post(
        "http://0.0.0.0:8000/api/v1/account/token",
        data={"username": "openbb", "password": "openbb"},
    )


@pytest.fixture(scope="session")
def headers():
    access_token = get_token().json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "",
                "symbol": "",
                "period": "",
                "limit": "",
                "type": "",
                "year": "",
                "company_name": "",
                "company_name_search": "",
                "sic": "",
                "filing_date": "",
                "filing_date_lt": "",
                "filing_date_lte": "",
                "filing_date_gt": "",
                "filing_date_gte": "",
                "period_of_report_date": "",
                "period_of_report_date_lt": "",
                "period_of_report_date_lte": "",
                "period_of_report_date_gt": "",
                "period_of_report_date_gte": "",
                "include_sources": "",
                "order": "",
                "sort": "",
            }
        )
    ],
)
def test_stocks_fa_balance(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/balance?{query_str}"
    result = requests.get(url, headers=headers)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"provider": "", "symbol": "", "limit": ""})],
)
def test_stocks_fa_balance_growth(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/balance_growth?{query_str}"
    result = requests.get(url, headers=headers)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"provider": "", "start_date": "", "end_date": ""})],
)
def test_stocks_fa_cal(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/cal?{query_str}"
    result = requests.get(url, headers=headers)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "",
                "symbol": "",
                "period": "",
                "limit": "",
                "type": "",
                "year": "",
                "company_name": "",
                "company_name_search": "",
                "sic": "",
                "filing_date": "",
                "filing_date_lt": "",
                "filing_date_lte": "",
                "filing_date_gt": "",
                "filing_date_gte": "",
                "period_of_report_date": "",
                "period_of_report_date_lt": "",
                "period_of_report_date_lte": "",
                "period_of_report_date_gt": "",
                "period_of_report_date_gte": "",
                "include_sources": "",
                "order": "",
                "sort": "",
            }
        )
    ],
)
def test_stocks_fa_cash(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/cash?{query_str}"
    result = requests.get(url, headers=headers)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"provider": "", "symbol": "", "limit": ""})],
)
def test_stocks_fa_cash_growth(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/cash_growth?{query_str}"
    result = requests.get(url, headers=headers)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"provider": "", "symbol": ""})],
)
def test_stocks_fa_comp(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/comp?{query_str}"
    result = requests.get(url, headers=headers)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"provider": "", "start_date": "", "end_date": ""})],
)
def test_stocks_fa_comsplit(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/comsplit?{query_str}"
    result = requests.get(url, headers=headers)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"provider": "", "symbol": ""})],
)
def test_stocks_fa_divs(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/divs?{query_str}"
    result = requests.get(url, headers=headers)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"provider": "", "symbol": "", "limit": ""})],
)
def test_stocks_fa_earning(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/earning?{query_str}"
    result = requests.get(url, headers=headers)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"provider": "", "symbol": ""})],
)
def test_stocks_fa_emp(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/emp?{query_str}"
    result = requests.get(url, headers=headers)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"provider": "", "symbol": "", "period": "", "limit": ""})],
)
def test_stocks_fa_est(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/est?{query_str}"
    result = requests.get(url, headers=headers)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "",
                "symbol": "",
                "period": "",
                "limit": "",
                "type": "",
                "year": "",
                "company_name": "",
                "company_name_search": "",
                "sic": "",
                "filing_date": "",
                "filing_date_lt": "",
                "filing_date_lte": "",
                "filing_date_gt": "",
                "filing_date_gte": "",
                "period_of_report_date": "",
                "period_of_report_date_lt": "",
                "period_of_report_date_lte": "",
                "period_of_report_date_gt": "",
                "period_of_report_date_gte": "",
                "include_sources": "",
                "order": "",
                "sort": "",
            }
        )
    ],
)
def test_stocks_fa_income(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/income?{query_str}"
    result = requests.get(url, headers=headers)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"provider": "", "symbol": "", "limit": "", "period": ""})],
)
def test_stocks_fa_income_growth(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/income_growth?{query_str}"
    result = requests.get(url, headers=headers)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "",
                "symbol": "",
                "transactionType": "",
                "reportingCik": "",
                "companyCik": "",
                "page": "",
            }
        )
    ],
)
def test_stocks_fa_ins(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/ins?{query_str}"
    result = requests.get(url, headers=headers)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"provider": "", "symbol": "", "include_current_quarter": "", "date": ""})],
)
def test_stocks_fa_ins_own(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/ins_own?{query_str}"
    result = requests.get(url, headers=headers)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"provider": "", "symbol": "", "period": "", "limit": ""})],
)
def test_stocks_fa_metrics(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/metrics?{query_str}"
    result = requests.get(url, headers=headers)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"provider": "", "symbol": ""})],
)
def test_stocks_fa_mgmt(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/mgmt?{query_str}"
    result = requests.get(url, headers=headers)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"provider": "", "symbol": ""})],
)
def test_stocks_fa_overview(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/overview?{query_str}"
    result = requests.get(url, headers=headers)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"provider": "", "symbol": "", "date": "", "page": ""})],
)
def test_stocks_fa_own(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/own?{query_str}"
    result = requests.get(url, headers=headers)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"provider": "", "symbol": ""})],
)
def test_stocks_fa_pt(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/pt?{query_str}"
    result = requests.get(url, headers=headers)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"provider": "", "symbol": "", "with_grade": ""})],
)
def test_stocks_fa_pta(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/pta?{query_str}"
    result = requests.get(url, headers=headers)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"provider": "", "symbol": "", "period": "", "limit": ""})],
)
def test_stocks_fa_ratios(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/ratios?{query_str}"
    result = requests.get(url, headers=headers)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"provider": "", "symbol": "", "period": "", "structure": ""})],
)
def test_stocks_fa_revgeo(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/revgeo?{query_str}"
    result = requests.get(url, headers=headers)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"provider": "", "symbol": "", "period": "", "structure": ""})],
)
def test_stocks_fa_revseg(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/revseg?{query_str}"
    result = requests.get(url, headers=headers)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"provider": "", "symbol": "", "type": "", "page": "", "limit": ""})],
)
def test_stocks_fa_sec(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/sec?{query_str}"
    result = requests.get(url, headers=headers)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"provider": "", "symbol": ""})],
)
def test_stocks_fa_shrs(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/shrs?{query_str}"
    result = requests.get(url, headers=headers)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"provider": "", "symbol": ""})],
)
def test_stocks_fa_split(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/split?{query_str}"
    result = requests.get(url, headers=headers)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"provider": "", "symbol": "", "year": "", "quarter": ""})],
)
def test_stocks_fa_transcript(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/fa/transcript?{query_str}"
    result = requests.get(url, headers=headers)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"provider": "", "symbol": ""})],
)
def test_stocks_ca_peers(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/ca/peers?{query_str}"
    result = requests.get(url, headers=headers)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"provider": "", "symbol": "", "date": ""})],
)
def test_stocks_options_chains(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/options/chains?{query_str}"
    result = requests.get(url, headers=headers)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "fmp",
                "symbol": "AAPL",
                "start_date": "",
                "end_date": "",
                "period": "",
                "interval": "",
                "adjusted": "",
                "extended_hours": "",
                "month": "",
                "outputsize": "",
                "timeseries": "",
                "timezone": "",
                "source": "",
                "start_time": "",
                "end_time": "",
                "interval_size": "",
                "multiplier": "",
                "timespan": "",
                "sort": "",
                "limit": "",
                "prepost": "",
                "actions": "",
                "auto_adjust": "",
                "back_adjust": "",
                "progress": "",
                "ignore_tz": "",
                "rounding": "",
                "repair": "",
                "keepna": "",
                "group_by": "",
            }
        )
    ],
)
def test_stocks_load(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/load?{query_str}"

    print(url)

    result = requests.get(url, headers=headers)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "",
                "symbols": "",
                "limit": "",
                "display": "",
                "date": "",
                "start_date": "",
                "end_date": "",
                "updated_since": "",
                "published_since": "",
                "sort": "",
                "order": "",
                "isin": "",
                "cusip": "",
                "channels": "",
                "topics": "",
                "authors": "",
                "content_types": "",
                "published_utc": "",
            }
        )
    ],
)
def test_stocks_news(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/news?{query_str}"
    result = requests.get(url, headers=headers)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"provider": "", "symbol": "", "limit": ""})],
)
def test_stocks_multiples(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/multiples?{query_str}"
    result = requests.get(url, headers=headers)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"provider": "", "query": "", "ticker": ""})],
)
def test_stocks_search(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/search?{query_str}"
    result = requests.get(url, headers=headers)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"provider": "", "symbol": "", "source": ""})],
)
def test_stocks_quote(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/quote?{query_str}"
    result = requests.get(url, headers=headers)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"provider": "", "symbol": ""})],
)
def test_stocks_info(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/stocks/info?{query_str}"
    result = requests.get(url, headers=headers)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200
