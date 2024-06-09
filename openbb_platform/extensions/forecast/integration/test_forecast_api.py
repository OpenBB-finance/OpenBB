# pylint: disable=redefined-outer-name
import base64
import json
import random
from typing import Dict, Literal

import pytest
import requests
from openbb_core.env import Env
from openbb_core.provider.utils.helpers import get_querystring

data: Dict = {}


def get_headers():
    """Get headers."""
    if "headers" in data:
        return data["headers"]

    userpass = f"{Env().API_USERNAME}:{Env().API_PASSWORD}"
    userpass_bytes = userpass.encode("ascii")
    base64_bytes = base64.b64encode(userpass_bytes)

    data["headers"] = {"Authorization": f"Basic {base64_bytes.decode('ascii')}"}
    return data["headers"]


def get_data(menu: Literal["stocks", "crypto"]):
    """Get data either from stocks or crypto."""
    funcs = {"stocks": get_stocks_data, "crypto": get_crypto_data}
    return funcs[menu]()


def request_data(menu: str, symbol: str, provider: str):
    """Randomly pick a symbol and a provider and get data from the selected menu."""
    url = f"http://0.0.0.0:8000/api/v1/{menu}/price/historical?symbol={symbol}&provider={provider}"
    result = requests.get(url, headers=get_headers(), timeout=10)
    return result.json()["results"]


def get_stocks_data():
    """Get stocks data."""
    if "stocks_data" in data:
        return data["stocks_data"]

    symbol = random.choice(["AAPL", "NVDA", "MSFT", "TSLA", "AMZN", "V"])  # noqa: S311
    provider = random.choice(["fmp", "polygon"])  # noqa: S311

    data["stocks_data"] = request_data("equity", symbol=symbol, provider=provider)
    return data["stocks_data"]


def get_crypto_data():
    """Get crypto data."""
    if "crypto_data" in data:
        return data["crypto_data"]

    # TODO : add more crypto providers and symbols
    symbol = random.choice(["BTC"])  # noqa: S311
    provider = random.choice(["fmp"])  # noqa: S311

    data["crypto_data"] = request_data(
        menu="crypto",
        symbol=symbol,
        provider=provider,
    )
    return data["crypto_data"]


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "target_column": "close",
                "n_predict": "5",
                "past_covariates": "",
                "train_split": "0.85",
                "forecast_horizon": "5",
                "output_chunk_length": "3",
                "lags": "10",
                "random_state": "1337",
                "metric": "mape",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "target_column": "close",
                "n_predict": "3",
                "past_covariates": "",
                "train_split": "0.75",
                "forecast_horizon": "3",
                "output_chunk_length": "",
                "lags": "",
                "random_state": "",
                "metric": "mape",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_forecast_regression_linear_regression(params, data_type):
    """Test ta atr."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = (
        f"http://0.0.0.0:8000/api/v1/forecast/regression/linear_regression?{query_str}"
    )
    result = requests.post(url, headers=get_headers(), timeout=100, data=body)
    assert isinstance(result, requests.Response)
    # TODO For some reason this fails for regression model, but not for exponential smoothing
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "target_column": "close",
                "trend": "A",
                "seasonal": "A",
                "seasonal_periods": "7",
                "dampen": "F",
                "n_predict": "5",
                "start_window": "0.65",
                "forecast_horizon": "5",
                "metric": "mape",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "target_column": "close",
                "trend": "A",
                "seasonal": "A",
                "seasonal_periods": "4",
                "dampen": "F",
                "n_predict": "2",
                "start_window": "0.75",
                "forecast_horizon": "5",
                "metric": "mape",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_forecast_regression_exponential_smoothing(params, data_type):
    """Test Exponential Smoothing."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/forecast/regression/exponential_smoothing?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=100, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {"data": "", "target_column": "close", "train_split": "0.6"},
            "stocks",
        ),
        (
            {"data": "", "target_column": "close", "train_split": "0.6"},
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_forecast_statistical_quantile_anamoly_detection(params, data_type):
    """Test Quantile Anamoly Detection."""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/forecast/statistical/quantile_anamoly_detection?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=15, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "target_column": "close",
                "seasonal_periods": "",
                "n_predict": "5",
                "start_window": "",
                "forecast_horizon": "2",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "target_column": "",
                "seasonal_periods": "7",
                "n_predict": "5",
                "start_window": "0.85",
                "forecast_horizon": "5",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_forecast_statistical_autoarima(params, data_type):
    """Test AutoARIMA"""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/forecast/statistical/autoarima?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=100, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "target_column": "close",
                "seasonal_periods": "",
                "n_predict": "5",
                "start_window": "",
                "forecast_horizon": "2",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "target_column": "",
                "seasonal_periods": "7",
                "n_predict": "5",
                "start_window": "0.85",
                "forecast_horizon": "5",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_forecast_statistical_autoces(params, data_type):
    """Test AutoCES"""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/forecast/statistical/autoces?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=100, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "target_column": "close",
                "seasonal_periods": "",
                "n_predict": "5",
                "start_window": "",
                "forecast_horizon": "2",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "target_column": "",
                "seasonal_periods": "7",
                "n_predict": "5",
                "start_window": "0.85",
                "forecast_horizon": "5",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_forecast_statistical_autoets(params, data_type):
    """Test AutoETS"""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/forecast/statistical/autoets?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=100, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "target_column": "close",
                "seasonal_periods": "",
                "n_predict": "5",
                "start_window": "",
                "forecast_horizon": "2",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "target_column": "",
                "seasonal_periods": "7",
                "n_predict": "5",
                "start_window": "0.85",
                "forecast_horizon": "5",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_forecast_statistical_mstl(params, data_type):
    """Test MSTL"""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/forecast/statistical/mstl?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=100, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "target_column": "close",
                "n_predict": "5",
                "train_split": "0.85",
                "past_covariates": "",
                "forecast_horizon": "5",
                "input_chunk_length": "14",
                "output_chunk_length": "5",
                "model_type": "LSTM",
                "n_rnn_layers": "1",
                "dropout": "0.0",
                "batch_size": "32",
                "n_epochs": "1",
                "learning_rate": "1e-3",
                "model_save_name": "",
                "force_reset": "",
                "save_checkpoints": "",
                "metric": "mape",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "target_column": "close",
                "n_predict": "5",
                "train_split": "0.85",
                "past_covariates": "",
                "forecast_horizon": "5",
                "input_chunk_length": "14",
                "output_chunk_length": "5",
                "model_type": "LSTM",
                "n_rnn_layers": "1",
                "dropout": "0.0",
                "batch_size": "32",
                "n_epochs": "1",
                "learning_rate": "1e-3",
                "model_save_name": "",
                "force_reset": "",
                "save_checkpoints": "",
                "metric": "mape",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_forecast_torch_brnn(params, data_type):
    """Test BRNN"""
    params = {p: v for p, v in params.items() if v}
    body = json.dumps(get_data(data_type))

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1/forecast/torch/brnn?{query_str}"
    result = requests.post(url, headers=get_headers(), timeout=100, data=body)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200
