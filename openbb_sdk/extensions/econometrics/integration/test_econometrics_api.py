import pytest
import requests
from openbb_provider.utils.helpers import get_querystring


def get_token():
    return requests.post(
        "http://0.0.0.0:8000/api/v1/account/token",
        data={"username": "openbb", "password": "openbb"},
        timeout=5,
    )


@pytest.fixture(scope="session")
def headers():
    access_token = get_token().json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


@pytest.mark.parametrize(
    "params",
    [({"data": ""})],
)
@pytest.mark.integration
def test_econometrics_corr(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/econometrics/corr?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"data": "", "y_column": "", "x_columns": ""})],
)
@pytest.mark.integration
def test_econometrics_ols_summary(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/econometrics/ols_summary?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"data": "", "y_column": "", "x_columns": ""})],
)
@pytest.mark.integration
def test_econometrics_dwat(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/econometrics/dwat?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"data": "", "y_column": "", "x_columns": "", "lags": ""})],
)
@pytest.mark.integration
def test_econometrics_bgot(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/econometrics/bgot?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"data": "", "columns": ""})],
)
@pytest.mark.integration
def test_econometrics_coint(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/econometrics/coint?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"data": "", "y_column": "", "x_column": "", "lag": ""})],
)
@pytest.mark.integration
def test_econometrics_granger(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/econometrics/granger?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"data": "", "column": "", "regression": ""})],
)
@pytest.mark.integration
def test_econometrics_unitroot(params, headers):
    params = {p: v for p, v in params.items() if v}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/econometrics/unitroot?{query_str}"
    result = requests.get(url, headers=headers, timeout=5)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200
