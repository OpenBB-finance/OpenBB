"""Test econometrics extension."""

import random
from typing import Literal

import pytest
from extensions.tests.conftest import parametrize
from openbb_core.app.model.obbject import OBBject
from openbb_econometrics.utils import mock_multi_index_data


# pylint: disable=inconsistent-return-statements
@pytest.fixture(scope="session")
def obb(pytestconfig):
    """Fixture to setup obb."""
    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb  # pylint: disable=import-outside-toplevel

        return openbb.obb


# pylint: disable=redefined-outer-name

data: dict = {}


def get_stocks_data():
    """Get stocks data."""
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
    """Get crypto data."""
    import openbb  # pylint:disable=import-outside-toplevel

    if "crypto_data" in data:
        return data["crypto_data"]

    # TODO : add more crypto providers and symbols
    symbol = random.choice(["BTCUSD"])  # noqa: S311
    provider = random.choice(["fmp"])  # noqa: S311

    data["crypto_data"] = openbb.obb.crypto.price.historical(
        symbol=symbol, provider=provider
    ).results
    return data["crypto_data"]


def get_data(menu: Literal["equity", "crypto"]):
    """Get data."""
    funcs = {"equity": get_stocks_data, "crypto": get_crypto_data}
    return funcs[menu]()


@parametrize(
    "params, data_type",
    [
        ({"data": "", "method": "pearson"}, "equity"),
        ({"data": "", "method": "pearson"}, "crypto"),
    ],
)
@pytest.mark.integration
def test_econometrics_correlation_matrix(params, data_type, obb):
    """Test the econometrics correlation matrix."""
    params = {p: v for p, v in params.items() if v}

    params["data"] = get_data(data_type)

    result = obb.econometrics.correlation_matrix(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params, data_type",
    [
        (
            {"data": "", "y_column": "close", "x_columns": ["high"]},
            "equity",
        ),
        (
            {"data": "", "y_column": "close", "x_columns": ["high"]},
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_econometrics_ols_regression(params, data_type, obb):
    """Test the econometrics OLS regression."""
    params = {p: v for p, v in params.items() if v}

    params["data"] = get_data(data_type)

    result = obb.econometrics.ols_regression(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params, data_type",
    [
        (
            {"data": "", "y_column": "close", "x_columns": ["high"]},
            "equity",
        ),
        (
            {"data": "", "y_column": "close", "x_columns": ["high"]},
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_econometrics_ols_regression_summary(params, data_type, obb):
    """Test the econometrics OLS regression summary."""
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.econometrics.ols_regression_summary(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params, data_type",
    [
        (
            {"data": "", "y_column": "volume", "x_columns": ["close"]},
            "equity",
        ),
        (
            {"data": "", "y_column": "volume", "x_columns": ["close"]},
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_econometrics_autocorrelation(params, data_type, obb):
    """Test the econometrics autocorrelation."""
    params = {p: v for p, v in params.items() if v}

    params["data"] = get_data(data_type)

    result = obb.econometrics.autocorrelation(**params)
    assert result
    assert isinstance(result, OBBject)


@parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "y_column": "volume",
                "x_columns": ["close"],
                "lags": "",
            },
            "equity",
        ),
        (
            {
                "data": "",
                "y_column": "volume",
                "x_columns": ["close"],
                "lags": "2",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_econometrics_residual_autocorrelation(params, data_type, obb):
    """Test the econometrics residual autocorrelation."""
    params = {p: v for p, v in params.items() if v}

    params["data"] = get_data(data_type)

    result = obb.econometrics.residual_autocorrelation(**params)
    assert result
    assert isinstance(result, OBBject)


@parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "columns": ["close", "volume"],
            },
            "equity",
        ),
        (
            {
                "data": "",
                "columns": ["close", "volume"],
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_econometrics_cointegration(params, data_type, obb):
    """Test the econometrics cointegration."""
    params = {p: v for p, v in params.items() if v}

    params["data"] = get_data(data_type)

    result = obb.econometrics.cointegration(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "y_column": "volume",
                "x_column": "close",
                "lag": "",
            },
            "equity",
        ),
        (
            {
                "data": "",
                "y_column": "volume",
                "x_column": "close",
                "lag": "2",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_econometrics_causality(params, data_type, obb):
    """Test the econometrics causality."""
    params = {p: v for p, v in params.items() if v}

    params["data"] = get_data(data_type)

    result = obb.econometrics.causality(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params, data_type",
    [
        ({"data": "", "column": "close", "regression": "c"}, "equity"),
        (
            {"data": "", "column": "volume", "regression": "ctt"},
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_econometrics_unit_root(params, data_type, obb):
    """Test the econometrics unit root."""
    params = {p: v for p, v in params.items() if v}

    params["data"] = get_data(data_type)

    result = obb.econometrics.unit_root(**params)
    assert result
    assert isinstance(result, OBBject)


@parametrize(
    "params",
    [
        {"data": "", "y_column": "income", "x_columns": ["age"]},
        {"data": "", "y_column": "income", "x_columns": ["age"]},
    ],
)
@pytest.mark.integration
def test_econometrics_panel_random_effects(params, obb):
    """Test the econometrics panel random effects."""
    params = {p: v for p, v in params.items() if v}

    params["data"] = mock_multi_index_data()

    result = obb.econometrics.panel_random_effects(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        {"data": "", "y_column": "income", "x_columns": ["age"]},
        {"data": "", "y_column": "income", "x_columns": ["age"]},
    ],
)
@pytest.mark.integration
def test_econometrics_panel_between(params, obb):
    """Test the econometrics panel between."""
    params = {p: v for p, v in params.items() if v}

    params["data"] = mock_multi_index_data()

    result = obb.econometrics.panel_between(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        {"data": "", "y_column": "income", "x_columns": ["age"]},
        {"data": "", "y_column": "income", "x_columns": ["age"]},
    ],
)
@pytest.mark.integration
def test_econometrics_panel_pooled(params, obb):
    """Test the econometrics panel pooled."""
    params = {p: v for p, v in params.items() if v}

    params["data"] = mock_multi_index_data()

    result = obb.econometrics.panel_pooled(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        {"data": "", "y_column": "income", "x_columns": ["age"]},
        {"data": "", "y_column": "income", "x_columns": ["age"]},
    ],
)
@pytest.mark.integration
def test_econometrics_panel_fixed(params, obb):
    """Test the econometrics panel fixed."""
    params = {p: v for p, v in params.items() if v}

    params["data"] = mock_multi_index_data()

    result = obb.econometrics.panel_fixed(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        {"data": "", "y_column": "income", "x_columns": ["age"]},
        {"data": "", "y_column": "income", "x_columns": ["age"]},
    ],
)
@pytest.mark.integration
def test_econometrics_panel_first_difference(params, obb):
    """Test the econometrics panel first difference."""
    params = {p: v for p, v in params.items() if v}

    params["data"] = mock_multi_index_data()

    result = obb.econometrics.panel_first_difference(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        {"data": "", "y_column": "income", "x_columns": ["age"]},
        {"data": "", "y_column": "income", "x_columns": ["age"]},
    ],
)
@pytest.mark.integration
def test_econometrics_panel_fmac(params, obb):
    """Test the econometrics panel fmac."""
    params = {p: v for p, v in params.items() if v}

    params["data"] = mock_multi_index_data()

    result = obb.econometrics.panel_fmac(**params)
    """Test the econometrics panel fmac."""
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
