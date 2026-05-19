"""Integration tests for the openbb-quantitative HTTP API interface."""

import base64

import pytest
import requests
from openbb_core.env import Env

_BASE_URL = "http://127.0.0.1:8000/api/v1/quantitative"
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
    """POST a QueryParams payload to a quantitative endpoint."""
    return requests.post(
        f"{_BASE_URL}/{endpoint}", headers=get_headers(), timeout=30, json=payload
    )


@pytest.mark.integration
def test_quantitative_normality(prices_data):
    result = _post("normality", {"data": prices_data, "target": "close"})
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_quantitative_capm(prices_data):
    result = _post("capm", {"data": prices_data, "target": "close"})
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_quantitative_unitroot_test(prices_data):
    result = _post("unitroot_test", {"data": prices_data, "target": "close"})
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_quantitative_summary(prices_data):
    result = _post("summary", {"data": prices_data, "target": "close"})
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_quantitative_rolling_skew(prices_data):
    result = _post(
        "rolling/skew", {"data": prices_data, "target": "close", "window": 20}
    )
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_quantitative_rolling_variance(prices_data):
    result = _post(
        "rolling/variance", {"data": prices_data, "target": "close", "window": 20}
    )
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_quantitative_rolling_stdev(prices_data):
    result = _post(
        "rolling/stdev", {"data": prices_data, "target": "close", "window": 20}
    )
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_quantitative_rolling_kurtosis(prices_data):
    result = _post(
        "rolling/kurtosis", {"data": prices_data, "target": "close", "window": 20}
    )
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_quantitative_rolling_mean(prices_data):
    result = _post(
        "rolling/mean", {"data": prices_data, "target": "close", "window": 20}
    )
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_quantitative_rolling_quantile(prices_data):
    result = _post(
        "rolling/quantile",
        {"data": prices_data, "target": "close", "window": 20, "quantile_pct": 0.75},
    )
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_quantitative_stats_skew(prices_data):
    result = _post("stats/skew", {"data": prices_data, "target": "close"})
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_quantitative_stats_variance(prices_data):
    result = _post("stats/variance", {"data": prices_data, "target": "close"})
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_quantitative_stats_stdev(prices_data):
    result = _post("stats/stdev", {"data": prices_data, "target": "close"})
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_quantitative_stats_kurtosis(prices_data):
    result = _post("stats/kurtosis", {"data": prices_data, "target": "close"})
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_quantitative_stats_mean(prices_data):
    result = _post("stats/mean", {"data": prices_data, "target": "close"})
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_quantitative_stats_quantile(prices_data):
    result = _post(
        "stats/quantile",
        {"data": prices_data, "target": "close", "quantile_pct": 0.75},
    )
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_quantitative_performance_omega_ratio(prices_data):
    result = _post("performance/omega_ratio", {"data": prices_data, "target": "close"})
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_quantitative_performance_sharpe_ratio(prices_data):
    result = _post(
        "performance/sharpe_ratio",
        {"data": prices_data, "target": "close", "window": 20},
    )
    assert result.status_code == 200
    assert result.json()["results"]


@pytest.mark.integration
def test_quantitative_performance_sortino_ratio(prices_data):
    result = _post(
        "performance/sortino_ratio",
        {"data": prices_data, "target": "close", "window": 20},
    )
    assert result.status_code == 200
    assert result.json()["results"]
