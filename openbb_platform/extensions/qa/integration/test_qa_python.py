"""Test qa extension."""
import random
from typing import Literal

import pytest
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
    provider = random.choice(["fmp", "intrinio", "polygon", "yfinance"])  # noqa: S311

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
        ({"data": "", "target": "close"}, "stocks"),
        ({"data": "", "target": "high"}, "crypto"),
    ],
)
@pytest.mark.integration
def test_qa_normality(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.qa.normality(**params)
    assert result
    assert isinstance(result, OBBject)


@pytest.mark.parametrize(
    "params, data_type",
    [
        ({"data": "", "target": "close"}, "stocks"),
        ({"data": "", "target": "high"}, "crypto"),
    ],
)
@pytest.mark.integration
def test_qa_capm(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.qa.capm(**params)
    assert result
    assert isinstance(result, OBBject)


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "target": "close",
                "threshold_start": "",
                "threshold_end": "",
            },
            "stocks",
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
def test_qa_om(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.qa.om(**params)
    assert result
    assert isinstance(result, OBBject)


@pytest.mark.parametrize(
    "params, data_type",
    [
        ({"data": "", "target": "close", "window": "5"}, "stocks"),
        ({"data": "", "target": "high", "window": "10"}, "crypto"),
    ],
)
@pytest.mark.integration
def test_qa_kurtosis(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.qa.kurtosis(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "target": "close",
                "fuller_reg": "c",
                "kpss_reg": "ct",
            },
            "stocks",
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
def test_qa_unitroot(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.qa.unitroot(**params)
    assert result
    assert isinstance(result, OBBject)


@pytest.mark.parametrize(
    "params, data_type",
    [
        ({"data": "", "target": "close", "rfr": "", "window": ""}, "stocks"),
        ({"data": "", "target": "high", "rfr": "0.5", "window": "250"}, "crypto"),
    ],
)
@pytest.mark.integration
def test_qa_sh(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.qa.sh(**params)
    assert result
    assert isinstance(result, OBBject)


@pytest.mark.parametrize(
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
            "stocks",
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
def test_qa_so(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.qa.so(**params)
    assert result
    assert isinstance(result, OBBject)


@pytest.mark.parametrize(
    "params, data_type",
    [
        ({"data": "", "target": "close", "window": "220"}, "stocks"),
    ],
)
@pytest.mark.integration
def test_qa_skew(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.qa.skew(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "target": "close",
                "window": "10",
                "quantile_pct": "",
            },
            "stocks",
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
def test_qa_quantile(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.qa.quantile(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params, data_type",
    [
        ({"data": "", "target": "close"}, "stocks"),
        ({"data": "", "target": "high"}, "crypto"),
    ],
)
@pytest.mark.integration
def test_qa_summary(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.qa.summary(**params)
    assert result
    assert isinstance(result, OBBject)
