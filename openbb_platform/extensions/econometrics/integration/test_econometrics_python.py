"""Test econometrics extension."""
import random

import pytest
from openbb_core.app.model.obbject import OBBject


@pytest.fixture(scope="session")
def obb(pytestconfig):
    """Fixture to setup obb."""

    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb

        return openbb.obb


stocks_symbol = random.choice(
    ["AAPL", "NVDA", "MSFT", "TSLA", "AMZN", "GOOG", "FB", "BABA", "TSM", "V"]
)
# TODO : add more crypto symbols
crypto_symbol = random.choice(["BTC"])
# TODO : add more providers
provider = random.choice(
    [
        "fmp",
    ]
)

data = {}


def get_stocks_data(symbol: str = stocks_symbol, prov: str = provider):
    import openbb  # pylint:disable=import-outside-toplevel

    if "stocks_data" in data:
        return data["stocks_data"]

    data["stocks_data"] = openbb.obb.stocks.load(symbol=symbol, provider=prov).results
    return data["stocks_data"]


def get_crypto_data(symbol: str = crypto_symbol, prov: str = provider):
    import openbb  # pylint:disable=import-outside-toplevel

    if "crypto_data" in data:
        return data["crypto_data"]

    data["crypto_data"] = openbb.obb.crypto.load(symbol=symbol, provider=prov).results
    return data["crypto_data"]


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data()}),
        ({"data": get_crypto_data()}),
    ],
)
@pytest.mark.integration
def test_econometrics_corr(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.econometrics.corr(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "y_column": "close", "x_columns": ["date"]}),
        ({"data": get_crypto_data(), "y_column": "close", "x_columns": ["date"]}),
    ],
)
@pytest.mark.integration
def test_econometrics_ols(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.econometrics.ols(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "y_column": "close", "x_columns": ["date"]}),
        ({"data": get_crypto_data(), "y_column": "close", "x_columns": ["date"]}),
    ],
)
@pytest.mark.integration
def test_econometrics_ols_summary(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.econometrics.ols_summary(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "y_column": "volume", "x_columns": ["close"]}),
        ({"data": get_crypto_data(), "y_column": "volume", "x_columns": ["close"]}),
    ],
)
@pytest.mark.integration
def test_econometrics_dwat(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.econometrics.dwat(**params)
    assert result
    assert isinstance(result, OBBject)


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "y_column": "volume",
                "x_columns": ["close"],
                "lags": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "y_column": "volume",
                "x_columns": ["close"],
                "lags": "2",
            }
        ),
    ],
)
@pytest.mark.integration
def test_econometrics_bgot(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.econometrics.bgot(**params)
    assert result
    assert isinstance(result, OBBject)


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "columns": ["close", "volume"],
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "columns": ["close", "volume"],
            }
        ),
    ],
)
@pytest.mark.integration
def test_econometrics_coint(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.econometrics.coint(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "y_column": "volume",
                "x_columns": "close",
                "lag": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "y_column": "volume",
                "x_columns": "close",
                "lag": "2",
            }
        ),
    ],
)
@pytest.mark.integration
def test_econometrics_granger(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.econometrics.granger(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "column": "close", "regression": "c"}),
        ({"data": get_crypto_data(), "column": "volume", "regression": "ctt"}),
    ],
)
@pytest.mark.integration
def test_econometrics_unitroot(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.econometrics.unitroot(**params)
    assert result
    assert isinstance(result, OBBject)


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "y_column": "close", "x_columns": ["date"]}),
        ({"data": get_crypto_data(), "y_column": "close", "x_columns": ["date"]}),
    ],
)
@pytest.mark.integration
def test_econometrics_panelre(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.econometrics.panelre(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "y_column": "close", "x_columns": ["date"]}),
        ({"data": get_crypto_data(), "y_column": "close", "x_columns": ["date"]}),
    ],
)
@pytest.mark.integration
def test_econometrics_panelbols(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.econometrics.panelbols(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "y_column": "close", "x_columns": ["date"]}),
        ({"data": get_crypto_data(), "y_column": "close", "x_columns": ["date"]}),
    ],
)
@pytest.mark.integration
def test_econometrics_panelpols(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.econometrics.panelpols(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "y_column": "close", "x_columns": ["date"]}),
        ({"data": get_crypto_data(), "y_column": "close", "x_columns": ["date"]}),
    ],
)
@pytest.mark.integration
def test_econometrics_panelols(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.econometrics.panelols(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "y_column": "close", "x_columns": ["date"]}),
        ({"data": get_crypto_data(), "y_column": "close", "x_columns": ["date"]}),
    ],
)
@pytest.mark.integration
def test_econometrics_panelfd(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.econometrics.panelfd(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "y_column": "close", "x_columns": ["date"]}),
        ({"data": get_crypto_data(), "y_column": "close", "x_columns": ["date"]}),
    ],
)
@pytest.mark.integration
def test_econometrics_panelfmac(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.econometrics.panelfmac(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
