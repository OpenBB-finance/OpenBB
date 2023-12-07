import base64

import pytest
import requests
from extensions.tests.conftest import parametrize
from openbb_core.env import Env
from openbb_core.provider.utils.helpers import get_querystring

# pylint: disable=redefined-outer-name


@pytest.fixture(scope="session")
def headers():
    userpass = f"{Env().API_USERNAME}:{Env().API_PASSWORD}"
    userpass_bytes = userpass.encode("ascii")
    base64_bytes = base64.b64encode(userpass_bytes)

    return {"Authorization": f"Basic {base64_bytes.decode('ascii')}"}


@parametrize(
    "params",
    [({"start_date": "2023-01-01", "end_date": "2023-06-06", "provider": "fmp"})],
)
@pytest.mark.integration
def test_fixedincome_government_treasury_rates(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = (
        f"http://0.0.0.0:8000/api/v1/fixedincome/government/treasury_rates?{query_str}"
    )
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"date": "2023-01-01", "inflation_adjusted": True, "provider": "fred"})],
)
@pytest.mark.integration
def test_fixedincome_government_us_yield_curve(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = (
        f"http://0.0.0.0:8000/api/v1/fixedincome/government/us_yield_curve?{query_str}"
    )
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"start_date": "2023-01-01", "end_date": "2023-06-06"}),
        (
            {
                "period": "overnight",
                "provider": "fred",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
    ],
)
@pytest.mark.integration
def test_fixedincome_sofr(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/sofr?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"start_date": "2023-01-01", "end_date": "2023-06-06"}),
        (
            {
                "parameter": "volume_weighted_trimmed_mean_rate",
                "provider": "fred",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
    ],
)
@pytest.mark.integration
def test_fixedincome_rate_estr(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/rate/estr?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"start_date": "2023-01-01", "end_date": "2023-06-06"}),
        (
            {
                "parameter": "rate",
                "provider": "fred",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
    ],
)
@pytest.mark.integration
def test_fixedincome_rate_sonia(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/rate/sonia?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"start_date": "2023-01-01", "end_date": "2023-06-06"}),
        (
            {
                "parameter": "overnight",
                "provider": "fred",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
    ],
)
@pytest.mark.integration
def test_fixedincome_rate_ameribor(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/rate/ameribor?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"start_date": "2023-01-01", "end_date": "2023-06-06"}),
        (
            {
                "parameter": "weekly",
                "provider": "fred",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
    ],
)
@pytest.mark.integration
def test_fixedincome_rate_effr(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/rate/effr?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({}), ({"long_run": True, "provider": "fred"})],
)
@pytest.mark.integration
def test_fixedincome_rate_effr_forecast(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/rate/effr_forecast?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"start_date": "2023-01-01", "end_date": "2023-06-06"})],
)
@pytest.mark.integration
def test_fixedincome_rate_iorb(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/rate/iorb?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"start_date": "2023-01-01", "end_date": "2023-06-06"}),
        (
            {
                "parameter": "daily_excl_weekend",
                "provider": "fred",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
            }
        ),
    ],
)
@pytest.mark.integration
def test_fixedincome_rate_dpcredit(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/rate/dpcredit?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        (
            {
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "interest_rate_type": "lending",
            }
        )
    ],
)
@pytest.mark.integration
def test_fixedincome_rate_ecb(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/rate/ecb?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"start_date": "2023-01-01", "end_date": "2023-06-06", "index_type": "yield"}),
        (
            {
                "category": "all",
                "area": "us",
                "grade": "non_sovereign",
                "options": True,
                "provider": "fred",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "index_type": "yield",
            }
        ),
    ],
)
@pytest.mark.integration
def test_fixedincome_corporate_ice_bofa(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/corporate/ice_bofa?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"start_date": "2023-01-01", "end_date": "2023-06-06", "index_type": "aaa"})],
)
@pytest.mark.integration
def test_fixedincome_corporate_moody(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/corporate/moody?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        (
            {
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "maturity": "30d",
                "category": "financial",
                "grade": "aa",
                "provider": "fred",
            }
        )
    ],
)
@pytest.mark.integration
def test_fixedincome_corporate_commercial_paper(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = (
        f"http://0.0.0.0:8000/api/v1/fixedincome/corporate/commercial_paper?{query_str}"
    )
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        (
            {
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "maturity": [10.0],
                "category": ["spot_rate"],
                "provider": "fred",
            }
        )
    ],
)
@pytest.mark.integration
def test_fixedincome_corporate_spot_rates(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/corporate/spot_rates?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"date": "2023-01-01", "yield_curve": "spot"})],
)
@pytest.mark.integration
def test_fixedincome_corporate_hqm(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/corporate/hqm?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [({"start_date": "2023-01-01", "end_date": "2023-06-06", "maturity": "3m"})],
)
@pytest.mark.integration
def test_fixedincome_spreads_tmc(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/spreads/tmc?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        (
            {
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "maturity": "10y",
                "provider": "fred",
            }
        )
    ],
)
@pytest.mark.integration
def test_fixedincome_spreads_tmc_effr(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/spreads/tmc_effr?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        (
            {
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "maturity": "3m",
                "provider": "fred",
            }
        )
    ],
)
@pytest.mark.integration
def test_fixedincome_spreads_treasury_effr(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/spreads/treasury_effr?{query_str}"
    result = requests.get(url, headers=headers, timeout=10)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        ({"date": "2023-01-01", "yield_curve_type": "spot_rate"}),
        (
            {
                "rating": "A",
                "provider": "ecb",
                "date": "2023-01-01",
                "yield_curve_type": "spot_rate",
            }
        ),
    ],
)
@pytest.mark.integration
def test_fixedincome_government_eu_yield_curve(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = (
        f"http://0.0.0.0:8000/api/v1/fixedincome/government/eu_yield_curve?{query_str}"
    )
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@parametrize(
    "params",
    [
        (
            {
                "start_date": "2023-09-01",
                "end_date": "2023-11-16",
                "cusip": None,
                "page_size": None,
                "page_num": None,
                "security_type": None,
                "provider": "government_us",
            }
        ),
        (
            {
                "start_date": "2023-09-01",
                "end_date": "2023-11-16",
                "cusip": None,
                "page_size": None,
                "page_num": None,
                "security_type": "Bond",
                "provider": "government_us",
            }
        ),
    ],
)
@pytest.mark.integration
def test_fixedincome_government_treasury_auctions(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/fixedincome/government/treasury_auctions?{query_str}"
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "date": "2023-11-16",
                "cusip": None,
                "security_type": "bond",
                "provider": "government_us",
            }
        ),
        (
            {
                "date": None,
                "cusip": None,
                "security_type": "bill",
                "provider": "government_us",
            }
        ),
    ],
)
@pytest.mark.integration
def test_fixedincome_government_treasury_prices(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = (
        f"http://0.0.0.0:8000/api/v1/fixedincome/government/treasury_prices?{query_str}"
    )
    result = requests.get(url, headers=headers, timeout=30)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200
