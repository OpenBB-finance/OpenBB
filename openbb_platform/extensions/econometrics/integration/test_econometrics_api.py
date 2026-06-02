"""Integration tests for the openbb-econometrics HTTP API interface."""

import base64

import pytest
import requests
from openbb_core.env import Env

_BASE_URL = "http://127.0.0.1:8000/api/v1/econometrics"
_headers: dict = {}


def get_headers():
    """Build the Basic-auth headers for the local API server."""
    if _headers:
        return _headers

    userpass = f"{Env().API_USERNAME}:{Env().API_PASSWORD}"
    base64_bytes = base64.b64encode(userpass.encode("ascii"))
    _headers["Authorization"] = f"Basic {base64_bytes.decode('ascii')}"
    return _headers


def _post(endpoint: str, payload: dict) -> requests.Response:
    """POST a QueryParams payload to an econometrics endpoint."""
    return requests.post(
        f"{_BASE_URL}/{endpoint}", headers=get_headers(), timeout=30, json=payload
    )


@pytest.mark.integration
def test_econometrics_correlation_matrix(timeseries_data):
    result = _post("correlation_matrix", {"data": timeseries_data, "method": "pearson"})
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_econometrics_summary_statistics(timeseries_data):
    result = _post("summary_statistics", {"data": timeseries_data})
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_econometrics_ols_regression(timeseries_data):
    result = _post(
        "ols_regression",
        {"data": timeseries_data, "y_column": "close", "x_columns": ["high", "low"]},
    )
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_econometrics_ols_regression_summary(timeseries_data):
    result = _post(
        "ols_regression_summary",
        {"data": timeseries_data, "y_column": "close", "x_columns": ["high", "low"]},
    )
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_econometrics_autocorrelation(timeseries_data):
    result = _post(
        "autocorrelation",
        {"data": timeseries_data, "y_column": "close", "x_columns": ["open"]},
    )
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_econometrics_residual_autocorrelation(timeseries_data):
    result = _post(
        "residual_autocorrelation",
        {
            "data": timeseries_data,
            "y_column": "close",
            "x_columns": ["open"],
            "lags": 4,
        },
    )
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_econometrics_heteroskedasticity(timeseries_data):
    result = _post(
        "heteroskedasticity",
        {"data": timeseries_data, "y_column": "close", "x_columns": ["open"]},
    )
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_econometrics_normality(timeseries_data):
    result = _post(
        "normality",
        {"data": timeseries_data, "y_column": "close", "x_columns": ["open"]},
    )
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_econometrics_variance_inflation_factor(timeseries_data):
    result = _post(
        "variance_inflation_factor",
        {"data": timeseries_data, "columns": ["open", "high", "low"]},
    )
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_econometrics_unit_root(timeseries_data):
    result = _post(
        "unit_root", {"data": timeseries_data, "column": "close", "regression": "c"}
    )
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_econometrics_kpss(timeseries_data):
    result = _post(
        "kpss", {"data": timeseries_data, "column": "close", "regression": "c"}
    )
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_econometrics_cointegration(timeseries_data):
    result = _post(
        "cointegration", {"data": timeseries_data, "columns": ["open", "close"]}
    )
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_econometrics_cointegration_johansen(timeseries_data):
    result = _post(
        "cointegration_johansen",
        {"data": timeseries_data, "columns": ["open", "high", "close"]},
    )
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_econometrics_causality(timeseries_data):
    result = _post(
        "causality",
        {
            "data": timeseries_data,
            "y_column": "close",
            "x_column": "volume",
            "lag": 3,
        },
    )
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_econometrics_garch(timeseries_data):
    result = _post(
        "garch", {"data": timeseries_data, "column": "close", "p": 1, "q": 1}
    )
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_econometrics_panel_random_effects(panel_data):
    result = _post(
        "panel_random_effects",
        {"data": panel_data, "y_column": "income", "x_columns": ["age", "education"]},
    )
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_econometrics_panel_between(panel_data):
    result = _post(
        "panel_between",
        {"data": panel_data, "y_column": "income", "x_columns": ["age", "education"]},
    )
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_econometrics_panel_pooled(panel_data):
    result = _post(
        "panel_pooled",
        {"data": panel_data, "y_column": "income", "x_columns": ["age", "education"]},
    )
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_econometrics_panel_fixed(panel_data):
    result = _post(
        "panel_fixed",
        {"data": panel_data, "y_column": "income", "x_columns": ["age", "education"]},
    )
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_econometrics_panel_first_difference(panel_data):
    result = _post(
        "panel_first_difference",
        {"data": panel_data, "y_column": "income", "x_columns": ["age"]},
    )
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_econometrics_panel_fmac(panel_data):
    result = _post(
        "panel_fmac",
        {"data": panel_data, "y_column": "income", "x_columns": ["age", "education"]},
    )
    assert result.status_code == 200
    assert result.json()["results"]
