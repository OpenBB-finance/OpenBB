"""Test qa extension."""
import random

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


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "target": "close"}),
        ({"data": get_crypto_data(), "target": "high"}),
    ],
)
@pytest.mark.integration
def test_qa_normality(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.qa.normality(**params)
    assert result
    assert isinstance(result, OBBject)


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "target": "close"}),
        ({"data": get_crypto_data(), "target": "high"}),
    ],
)
@pytest.mark.integration
def test_qa_capm(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.qa.capm(**params)
    assert result
    assert isinstance(result, OBBject)


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "target": "close",
                "threshold_start": "",
                "threshold_end": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "target": "high",
                "threshold_start": "0.1",
                "threshold_end": "1.6",
            }
        ),
    ],
)
@pytest.mark.integration
def test_qa_om(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.qa.om(**params)
    assert result
    assert isinstance(result, OBBject)


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "target": "close", "window": "5"}),
        ({"data": get_crypto_data(), "target": "high", "window": "10"}),
    ],
)
@pytest.mark.integration
def test_qa_kurtosis(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.qa.kurtosis(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "target": "close",
                "fuller_reg": "c",
                "kpss_reg": "ct",
            }
        ),
        (
            {
                "data": get_stocks_data(),
                "target": "high",
                "fuller_reg": "ct",
                "kpss_reg": "c",
            }
        ),
    ],
)
@pytest.mark.integration
def test_qa_unitroot(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.qa.unitroot(**params)
    assert result
    assert isinstance(result, OBBject)


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "target": "close", "rfr": "", "window": ""}),
        ({"data": get_crypto_data(), "target": "high", "rfr": "0.5", "window": "250"}),
    ],
)
@pytest.mark.integration
def test_qa_sh(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.qa.sh(**params)
    assert result
    assert isinstance(result, OBBject)


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "target": "close",
                "target_return": "",
                "window": "",
                "adjusted": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "target": "close",
                "target_return": "0.5",
                "window": "275",
                "adjusted": "true",
            }
        ),
    ],
)
@pytest.mark.integration
def test_qa_so(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.qa.so(**params)
    assert result
    assert isinstance(result, OBBject)


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "target": "close", "window": "220"}),
    ],
)
@pytest.mark.integration
def test_qa_skew(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.qa.skew(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "target": "close",
                "window": "10",
                "quantile_pct": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "target": "high",
                "window": "50",
                "quantile_pct": "0.6",
            }
        ),
    ],
)
@pytest.mark.integration
def test_qa_quantile(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.qa.quantile(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "target": "close"}),
        ({"data": get_crypto_data(), "target": "high"}),
    ],
)
@pytest.mark.integration
def test_qa_summary(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.qa.summary(**params)
    assert result
    assert isinstance(result, OBBject)
