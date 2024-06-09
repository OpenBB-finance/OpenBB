"""Test forecast extension."""

# pylint: disable=redefined-outer-name

import random
from typing import Dict, Literal

import pytest
from openbb_core.app.model.obbject import OBBject


# pylint: disable=inconsistent-return-statements
@pytest.fixture(scope="session")
def obb(pytestconfig):
    """Fixture to setup obb."""
    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb  # pylint: disable=import-outside-toplevel

        return openbb.obb


data: Dict = {}


def get_stocks_data():
    import openbb  # pylint:disable=import-outside-toplevel

    if "stocks_data" in data:
        return data["stocks_data"]

    symbol = random.choice(["AAPL", "NVDA", "MSFT", "TSLA", "AMZN", "V"])  # noqa: S311
    provider = random.choice(["fmp", "polygon"])  # noqa: S311

    data["stocks_data"] = openbb.obb.equity.price.historical(
        symbol=symbol, provider=provider
    ).results
    return data["stocks_data"]


def get_crypto_data():
    import openbb  # pylint:disable=import-outside-toplevel

    if "crypto_data" in data:
        return data["crypto_data"]

    # TODO : add more crypto providers and symbols
    symbol = random.choice(["BTC"])  # noqa: S311
    provider = random.choice(["fmp"])  # noqa: S311

    data["crypto_data"] = openbb.obb.equity.price.historical(
        symbol=symbol, provider=provider
    ).results
    return data["crypto_data"]


def get_data(menu: Literal["stocks", "crypto"]):
    funcs = {"stocks": get_stocks_data, "crypto": get_crypto_data}
    return funcs[menu]()


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
                "lags": "14",
                "random_state": "1337",
                "metric": "mape",
                "model_name": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "target_column": "close",
                "n_predict": "6",
                "past_covariates": "",
                "train_split": "0.75",
                "forecast_horizon": "2",
                "output_chunk_length": "",
                "lags": "14",
                "random_state": "",
                "metric": "mape",
                "model_name": "",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_forecast_regression_linear_regression(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    output = obb.forecast.regression.linear_regression(**params)
    assert output
    assert isinstance(output, OBBject)
    assert any(output.results.model_dump().values())


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
def test_forecast_regression_exponential_smoothing(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    output = obb.forecast.regression.exponential_smoothing(**params)
    assert output
    assert isinstance(output, OBBject)
    assert any(output.results.model_dump().values())


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
def test_forecast_statistical_quantile_anamoly_detection(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    output = obb.forecast.statistical.quantile_anamoly_detection(**params)
    assert output
    assert isinstance(output, OBBject)
    assert any(output.results.model_dump().values())


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
def test_forecast_statistical_autoarima(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    output = obb.forecast.statistical.autoarima(**params)
    assert output
    assert isinstance(output, OBBject)
    any(output.results.model_dump().values())


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
def test_forecast_statistical_autoces(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    output = obb.forecast.statistical.autoces(**params)
    assert output
    assert isinstance(output, OBBject)
    any(output.results.model_dump().values())


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
def test_forecast_statistical_autoets(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    output = obb.forecast.statistical.autoets(**params)
    assert output
    assert isinstance(output, OBBject)
    any(output.results.model_dump().values())


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
def test_forecast_statistical_mstl(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    output = obb.forecast.statistical.mstl(**params)
    assert output
    assert isinstance(output, OBBject)
    any(output.results.model_dump().values())


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
                "input_chunk_length": "8",
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
                "input_chunk_length": "8",
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
def test_forecast_torch_brnn(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    output = obb.forecast.torch.brnn(**params)
    assert output
    assert isinstance(output, OBBject)
    any(output.results.model_dump().values())
