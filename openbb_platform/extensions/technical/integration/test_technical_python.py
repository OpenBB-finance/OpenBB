"""Test ta extension."""
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


def get_data(menu: Literal["stocks", "crypto"]):
    funcs = {"stocks": get_stocks_data, "crypto": get_crypto_data}
    return funcs[menu]()


@parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "index": "",
                "length": "",
                "mamode": "",
                "drift": "",
                "offset": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "index": "date",
                "length": "15",
                "mamode": "rma",
                "drift": "2",
                "offset": "1",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_technical_atr(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.technical.atr(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "index": "",
                "close_column": "",
                "period": "",
                "start_date": "",
                "end_date": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "index": "date",
                "close_column": "adj_close",
                "period": "125",
                "start_date": "",
                "end_date": "",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_technical_fib(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.technical.fib(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params, data_type",
    [
        ({"data": "", "index": "", "offset": ""}, "stocks"),
        ({"data": "", "index": "date", "offset": "1"}, "crypto"),
    ],
)
@pytest.mark.integration
def test_technical_obv(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.technical.obv(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params, data_type",
    [
        ({"data": "", "index": "", "length": "", "signal": ""}, "stocks"),
        ({"data": "", "index": "date", "length": "15", "signal": "2"}, "crypto"),
    ],
)
@pytest.mark.integration
def test_technical_fisher(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.technical.fisher(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "index": "",
                "fast": "",
                "slow": "",
                "offset": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "index": "date",
                "fast": "5",
                "slow": "15",
                "offset": "2",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_technical_adosc(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.technical.adosc(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "target": "",
                "index": "",
                "length": "",
                "std": "",
                "mamode": "",
                "offset": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "target": "high",
                "index": "date",
                "length": "55",
                "std": "3",
                "mamode": "wma",
                "offset": "1",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_technical_bbands(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.technical.bbands(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "target": "",
                "index": "",
                "length": "",
                "offset": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "target": "high",
                "index": "date",
                "length": "55",
                "offset": "5",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_technical_zlma(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.technical.zlma(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params, data_type",
    [
        ({"data": "", "index": "", "length": "", "scalar": ""}, "stocks"),
        (
            {
                "data": "",
                "index": "date",
                "length": "30",
                "scalar": "110",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_technical_aroon(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.technical.aroon(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "target": "",
                "index": "",
                "length": "",
                "offset": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "target": "high",
                "index": "date",
                "length": "55",
                "offset": "2",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_technical_sma(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.technical.sma(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "index": "",
                "target": "",
                "show_all": "",
                "asint": "",
                "offset": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "index": "date",
                "target": "high",
                "show_all": "true",
                "asint": "true",
                "offset": "5",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_technical_demark(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.technical.demark(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params, data_type",
    [
        ({"data": "", "index": "", "anchor": "", "offset": ""}, "stocks"),
        ({"data": "", "index": "date", "anchor": "W", "offset": "5"}, "crypto"),
    ],
)
@pytest.mark.integration
def test_technical_vwap(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.technical.vwap(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "target": "",
                "index": "",
                "fast": "",
                "slow": "",
                "signal": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "target": "high",
                "index": "date",
                "fast": "10",
                "slow": "30",
                "signal": "10",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_technical_macd(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.technical.macd(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "target": "",
                "index": "",
                "length": "",
                "offset": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "target": "high",
                "index": "date",
                "length": "55",
                "offset": "2",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_technical_hma(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.technical.hma(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "index": "",
                "lower_length": "",
                "upper_length": "",
                "offset": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "index": "date",
                "lower_length": "30",
                "upper_length": "40",
                "offset": "5",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_technical_donchian(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.technical.donchian(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "index": "",
                "conversion": "",
                "base": "",
                "lagging": "",
                "offset": "",
                "lookahead": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "index": "date",
                "conversion": "10",
                "base": "30",
                "lagging": "50",
                "offset": "30",
                "lookahead": "true",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_technical_ichimoku(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.technical.ichimoku(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params, data_type",
    [
        ({"data": "", "index": "", "target": "", "period": ""}, "stocks"),
        (
            {
                "data": "",
                "index": "date",
                "target": "close",
                "period": "95",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_technical_clenow(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.technical.clenow(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "index": "",
                "length": "",
                "scalar": "",
                "drift": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "index": "date",
                "length": "60",
                "scalar": "90.0",
                "drift": "2",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_technical_adx(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.technical.adx(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params, data_type",
    [
        ({"data": "", "index": "", "offset": ""}, "stocks"),
        ({"data": "", "index": "date", "offset": "5"}, "crypto"),
    ],
)
@pytest.mark.integration
def test_technical_ad(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.technical.ad(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "target": "",
                "index": "",
                "length": "",
                "offset": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "target": "high",
                "index": "date",
                "length": "60",
                "offset": "10",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_technical_wma(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.technical.wma(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params, data_type",
    [
        ({"data": "", "index": "", "length": "", "scalar": ""}, "stocks"),
        (
            {
                "data": "",
                "index": "date",
                "length": "16",
                "scalar": "0.02",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_technical_cci(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.technical.cci(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "target": "",
                "index": "",
                "length": "",
                "scalar": "",
                "drift": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "target": "high",
                "index": "date",
                "length": "16",
                "scalar": "90.0",
                "drift": "2",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_technical_rsi(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.technical.rsi(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "index": "",
                "fast_k_period": "",
                "slow_d_period": "",
                "slow_k_period": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "index": "date",
                "fast_k_period": "12",
                "slow_d_period": "2",
                "slow_k_period": "2",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_technical_stoch(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.technical.stoch(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "index": "",
                "length": "",
                "scalar": "",
                "mamode": "",
                "offset": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "index": "date",
                "length": "22",
                "scalar": "24",
                "mamode": "sma",
                "offset": "5",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_technical_kc(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.technical.kc(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params, data_type",
    [
        ({"data": "", "index": "", "length": ""}, "stocks"),
        ({"data": "", "index": "date", "length": "20"}, "crypto"),
    ],
)
@pytest.mark.integration
def test_technical_cg(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.technical.cg(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params, data_type",
    [
        (
            {
                "data": "",
                "index": "",
                "lower_q": "",
                "upper_q": "",
                "model": "",
                "is_crypto": "",
                "trading_periods": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "index": "date",
                "lower_q": "0.3",
                "upper_q": "0.7",
                "model": "Parkinson",
                "is_crypto": "True",
                "trading_periods": "",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_technical_cones(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.technical.cones(**params)
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
                "index": "date",
                "length": "",
                "offset": "",
            },
            "stocks",
        ),
        (
            {
                "data": "",
                "target": "high",
                "index": "",
                "length": "60",
                "offset": "10",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_technical_ema(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.technical.ema(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
