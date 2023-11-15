import pytest


@pytest.mark.skip(reason="econometrics is a python only extensions so far")
@pytest.mark.integration
def test_econometrics_corr():
    ...


@pytest.mark.skip(reason="econometrics is a python only extensions so far")
@pytest.mark.integration
def test_econometrics_ols_summary():
    ...


@pytest.mark.skip(reason="econometrics is a python only extensions so far")
@pytest.mark.integration
def test_econometrics_dwat():
    ...


@pytest.mark.skip(reason="econometrics is a python only extensions so far")
@pytest.mark.integration
def test_econometrics_bgot():
    ...


@pytest.mark.skip(reason="econometrics is a python only extensions so far")
def test_econometrics_coint():
    ...


@pytest.mark.skip(reason="econometrics is a python only extensions so far")
@pytest.mark.integration
def test_econometrics_granger():
    ...


@pytest.mark.skip(reason="econometrics is a python only extensions so far")
@pytest.mark.integration
def test_econometrics_unitroot():
    ...


@pytest.mark.parametrize(
    "params",
    [({"data": ""})],
)
@pytest.mark.integration
def test_econometrics_correlation_matrix(params, headers):
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/econometrics/correlation_matrix?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"data": "", "y_column": "", "x_columns": ""})],
)
@pytest.mark.integration
def test_econometrics_ols_regression_summary(params, headers):
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/econometrics/ols_regression_summary?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"data": "", "y_column": "", "x_columns": ""})],
)
@pytest.mark.integration
def test_econometrics_autocorrelation(params, headers):
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/econometrics/autocorrelation?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"data": "", "y_column": "", "x_columns": "", "lags": ""})],
)
@pytest.mark.integration
def test_econometrics_residual_autocorrelation(params, headers):
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = (
        f"http://0.0.0.0:8000/api/v1/econometrics/residual_autocorrelation?{query_str}"
    )
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"data": "", "columns": ""})],
)
@pytest.mark.integration
def test_econometrics_cointegration(params, headers):
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/econometrics/cointegration?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"data": "", "y_column": "", "x_column": "", "lag": ""})],
)
@pytest.mark.integration
def test_econometrics_causality(params, headers):
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/econometrics/causality?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params",
    [({"data": "", "column": "", "regression": ""})],
)
@pytest.mark.integration
def test_econometrics_unit_root(params, headers):
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(params.pop("data"))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/econometrics/unit_root?{query_str}"
    result = requests.post(url, headers=headers, timeout=10, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200
