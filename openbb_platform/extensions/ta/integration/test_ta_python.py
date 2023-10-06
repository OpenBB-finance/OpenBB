"""Test ta extension."""
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
def test_ta_atr(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.ta.atr(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
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
def test_ta_fib(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.ta.fib(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params, data_type",
    [
        ({"data": "", "index": "", "offset": ""}, "stocks"),
        ({"data": "", "index": "date", "offset": "1"}, "crypto"),
    ],
)
@pytest.mark.integration
def test_ta_obv(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.ta.obv(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params, data_type",
    [
        ({"data": "", "index": "", "length": "", "signal": ""}, "stocks"),
        ({"data": "", "index": "date", "length": "15", "signal": "2"}, "crypto"),
    ],
)
@pytest.mark.integration
def test_ta_fisher(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.ta.fisher(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
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
def test_ta_adosc(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.ta.adosc(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
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
def test_ta_bbands(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.ta.bbands(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
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
def test_ta_zlma(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.ta.zlma(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
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
def test_ta_aroon(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.ta.aroon(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
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
def test_ta_sma(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.ta.sma(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
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
def test_ta_demark(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.ta.demark(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params, data_type",
    [
        ({"data": "", "index": "", "anchor": "", "offset": ""}, "stocks"),
        ({"data": "", "index": "date", "anchor": "W", "offset": "5"}, "crypto"),
    ],
)
@pytest.mark.integration
def test_ta_vwap(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.ta.vwap(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
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
def test_ta_macd(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.ta.macd(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
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
def test_ta_hma(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.ta.hma(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
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
def test_ta_donchian(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.ta.donchian(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
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
def test_ta_ichimoku(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.ta.ichimoku(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
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
def test_ta_clenow(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.ta.clenow(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
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
def test_ta_adx(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.ta.adx(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
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
def test_ta_wma(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.ta.wma(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
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
def test_ta_cci(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.ta.cci(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
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
def test_ta_rsi(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.ta.rsi(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
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
def test_ta_stoch(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.ta.stoch(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
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
def test_ta_kc(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.ta.kc(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params, data_type",
    [
        ({"data": "", "index": "", "length": ""}, "stocks"),
        ({"data": "", "index": "date", "length": "20"}, "crypto"),
    ],
)
@pytest.mark.integration
def test_ta_cg(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.ta.cg(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
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
                "is_crypto": "true",
            },
            "crypto",
        ),
    ],
)
@pytest.mark.integration
def test_ta_cones(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.ta.cones(**params)
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
def test_ta_ema(params, data_type, obb):
    params = {p: v for p, v in params.items() if v}
    params["data"] = get_data(data_type)

    result = obb.ta.ema(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
