"""Test qa extension."""
import random
from typing import Literal

import pytest
from extensions.tests.conftest import parametrize
from openbb_core.app.model.obbject import OBBject


# pylint:disable=inconsistent-return-statements
@pytest.fixture(scope="session")
def obb(pytestconfig):
    """Fixture to setup obb."""
    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb  # pylint:disable=import-outside-toplevel

        return openbb.obb


# pylint:disable=redefined-outer-name

data: dict = {}


def get_stocks_data():
    import openbb  # pylint:disable=import-outside-toplevel

    if "stocks_data" in data:
        return data["stocks_data"]

    symbol = random.choice(["AAPL", "NVDA", "MSFT", "TSLA", "AMZN", "V"])  # noqa: S311
    provider = random.choice(["fmp", "polygon", "yfinance"])  # noqa: S311

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

    data["crypto_data"] = openbb.obb.crypto.price.historical(
        symbol=symbol, provider=provider
    ).results
    return data["crypto_data"]


def get_data(menu: Literal["equity", "crypto"]):
    funcs = {"equity": get_stocks_data, "crypto": get_crypto_data}
    return funcs[menu]()


@parametrize(
    "params, data_type",
    [
        ({"data": "", "target": "close"}, "equity"),
        ({"data": "", "target": "high"}, "crypto"),
    ],
)
@pytest.mark.integration
def test_quantitative_normality(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.quantitative.normality(**params)
    assert result
    assert isinstance(result, OBBject)


@parametrize(
    "params, data_type",
    [
        ({"data": "", "target": "close"}, "equity"),
        ({"data": "", "target": "high"}, "crypto"),
    ],
)
@pytest.mark.integration
def test_quantitative_capm(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.quantitative.capm(**params)
    assert result
    assert isinstance(result, OBBject)


@parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "target": "close",
                "threshold_start": "",
                "threshold_end": "",
            },
            "equity",
        ),
        (
            {
                "data": "",
                "target": "high",
                "threshold_start": "0.1",
                "threshold_end": "1.6",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_quantitative_omega_ratio(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.quantitative.omega_ratio(**params)
    assert result
    assert isinstance(result, OBBject)


@parametrize(
    "params, data_type",
    [
        ({"data": "", "target": "close", "window": "5"}, "equity"),
        ({"data": "", "target": "high", "window": "10"}, "crypto"),
    ],
)
@pytest.mark.integration
def test_quantitative_kurtosis(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.quantitative.kurtosis(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "target": "close",
                "fuller_reg": "c",
                "kpss_reg": "ct",
            },
            "equity",
        ),
        (
            {
                "data": "",
                "target": "high",
                "fuller_reg": "ct",
                "kpss_reg": "c",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_quantitative_unitroot_test(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.quantitative.unitroot_test(**params)
    assert result
    assert isinstance(result, OBBject)


@parametrize(
    "params, data_type",
    [
        ({"data": "", "target": "close", "rfr": "", "window": ""}, "equity"),
        ({"data": "", "target": "high", "rfr": "0.5", "window": "250"}, "crypto"),
    ],
)
@pytest.mark.integration
def test_quantitative_sharpe_ratio(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.quantitative.sharpe_ratio(**params)
    assert result
    assert isinstance(result, OBBject)


@parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "target": "close",
                "target_return": "",
                "window": "",
                "adjusted": "",
            },
            "equity",
        ),
        (
            {
                "data": "",
                "target": "close",
                "target_return": "0.5",
                "window": "275",
                "adjusted": "true",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_quantitative_sortino_ratio(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.quantitative.sortino_ratio(**params)
    assert result
    assert isinstance(result, OBBject)


@parametrize(
    "params, data_type",
    [
        ({"data": "", "target": "close", "window": "220"}, "equity"),
    ],
)
@pytest.mark.integration
def test_quantitative_skewness(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.quantitative.skewness(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "target": "close",
                "window": "10",
                "quantile_pct": "",
            },
            "equity",
        ),
        (
            {
                "data": "",
                "target": "high",
                "window": "50",
                "quantile_pct": "0.6",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_quantitative_quantile(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.quantitative.quantile(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params, data_type",
    [
        ({"data": "", "target": "close"}, "equity"),
        ({"data": "", "target": "high"}, "crypto"),
    ],
)
@pytest.mark.integration
def test_quantitative_summary(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.quantitative.summary(**params)
    assert result
    assert isinstance(result, OBBject)
