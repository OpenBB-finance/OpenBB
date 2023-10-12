"""Test econometrics extension."""
import random
from typing import Literal

import pytest
from extensions.econometrics.openbb_econometrics.utils import mock_multi_index_data
from openbb_core.app.model.obbject import OBBject


@pytest.fixture(scope="session")
def obb(pytestconfig):
    """Fixture to setup obb."""
    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb

        return openbb.obb


data = {}


def get_stocks_data():
    import openbb  # pylint:disable=import-outside-toplevel

    if "stocks_data" in data:
        return data["stocks_data"]

    symbol = random.choice(["AAPL", "NVDA", "MSFT", "TSLA", "AMZN", "V"])  # noqa: S311
    provider = random.choice(["fmp", "polygon", "yfinance"])  # noqa: S311

    data["stocks_data"] = openbb.obb.stocks.load(
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

    data["crypto_data"] = openbb.obb.crypto.load(
        symbol=symbol, provider=provider
    ).results
    return data["crypto_data"]


def get_data(menu: Literal["stocks", "crypto"]):
    funcs = {"stocks": get_stocks_data, "crypto": get_crypto_data}
    return funcs[menu]()


@pytest.mark.parametrize(
    "params, data_type",
    [
        ({"data": ""}, "stocks"),
        ({"data": ""}, "crypto"),
    ],
)
@pytest.mark.integration
def test_econometrics_corr(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}

    params["data"] = get_data(data_type)

    result = obb.econometrics.corr(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {"data": "", "y_column": "close", "x_columns": ["high"]},
            "stocks",
        ),
        (
            {"data": "", "y_column": "close", "x_columns": ["high"]},
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_econometrics_ols(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}

    params["data"] = get_data(data_type)

    result = obb.econometrics.ols(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {"data": "", "y_column": "close", "x_columns": ["high"]},
            "stocks",
        ),
        (
            {"data": "", "y_column": "close", "x_columns": ["high"]},
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_econometrics_ols_summary(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.econometrics.ols_summary(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {"data": "", "y_column": "volume", "x_columns": ["close"]},
            "stocks",
        ),
        (
            {"data": "", "y_column": "volume", "x_columns": ["close"]},
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_econometrics_dwat(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}

    params["data"] = get_data(data_type)

    result = obb.econometrics.dwat(**params)
    assert result
    assert isinstance(result, OBBject)


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "y_column": "volume",
                "x_columns": ["close"],
                "lags": "",
            },
            "stocks",
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
def test_econometrics_bgot(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}

    params["data"] = get_data(data_type)

    result = obb.econometrics.bgot(**params)
    assert result
    assert isinstance(result, OBBject)


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "columns": ["close", "volume"],
            },
            "stocks",
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
def test_econometrics_coint(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}

    params["data"] = get_data(data_type)

    result = obb.econometrics.coint(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "y_column": "volume",
                "x_column": "close",
                "lag": "",
            },
            "stocks",
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
def test_econometrics_granger(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}

    params["data"] = get_data(data_type)

    result = obb.econometrics.granger(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params, data_type",
    [
        ({"data": "", "column": "close", "regression": "c"}, "stocks"),
        (
            {"data": "", "column": "volume", "regression": "ctt"},
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_econometrics_unitroot(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}

    params["data"] = get_data(data_type)

    result = obb.econometrics.unitroot(**params)
    assert result
    assert isinstance(result, OBBject)


@pytest.mark.parametrize(
    "params",
    [
        {"data": "", "y_column": "income", "x_columns": ["age"]},
        {"data": "", "y_column": "income", "x_columns": ["age"]},
    ],
)
@pytest.mark.integration
def test_econometrics_panelre(params, obb):
    params = {p: v for p, v in params.items() if v}

    params["data"] = mock_multi_index_data()

    result = obb.econometrics.panelre(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        {"data": "", "y_column": "income", "x_columns": ["age"]},
        {"data": "", "y_column": "income", "x_columns": ["age"]},
    ],
)
@pytest.mark.integration
def test_econometrics_panelbols(params, obb):
    params = {p: v for p, v in params.items() if v}

    params["data"] = mock_multi_index_data()

    result = obb.econometrics.panelbols(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        {"data": "", "y_column": "income", "x_columns": ["age"]},
        {"data": "", "y_column": "income", "x_columns": ["age"]},
    ],
)
@pytest.mark.integration
def test_econometrics_panelpols(params, obb):
    params = {p: v for p, v in params.items() if v}

    params["data"] = mock_multi_index_data()

    result = obb.econometrics.panelpols(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        {"data": "", "y_column": "income", "x_columns": ["age"]},
        {"data": "", "y_column": "income", "x_columns": ["age"]},
    ],
)
@pytest.mark.integration
def test_econometrics_panelols(params, obb):
    params = {p: v for p, v in params.items() if v}

    params["data"] = mock_multi_index_data()

    result = obb.econometrics.panelols(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        {"data": "", "y_column": "income", "x_columns": ["age"]},
        {"data": "", "y_column": "income", "x_columns": ["age"]},
    ],
)
@pytest.mark.integration
def test_econometrics_panelfd(params, obb):
    params = {p: v for p, v in params.items() if v}

    params["data"] = mock_multi_index_data()

    result = obb.econometrics.panelfd(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        {"data": "", "y_column": "income", "x_columns": ["age"]},
        {"data": "", "y_column": "income", "x_columns": ["age"]},
    ],
)
@pytest.mark.integration
def test_econometrics_panelfmac(params, obb):
    params = {p: v for p, v in params.items() if v}

    params["data"] = mock_multi_index_data()

    result = obb.econometrics.panelfmac(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
