"""Test ta extension."""
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
        (
            {
                "data": get_stocks_data(),
                "index": "",
                "length": "",
                "mamode": "",
                "drift": "",
                "offset": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "index": "date",
                "length": "15",
                "mamode": "rma",
                "drift": "2",
                "offset": "1",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_atr(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.ta.atr(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "index": "",
                "close_column": "",
                "period": "",
                "start_date": "",
                "end_date": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "index": "date",
                "close_column": "adj_close",
                "period": "125",
                "start_date": "",
                "end_date": "",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_fib(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.ta.fib(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "index": "", "offset": ""}),
        ({"data": get_crypto_data(), "index": "date", "offset": "1"}),
    ],
)
@pytest.mark.integration
def test_ta_obv(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.ta.obv(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "index": "", "length": "", "signal": ""}),
        ({"data": get_crypto_data(), "index": "date", "length": "15", "signal": "2"}),
    ],
)
@pytest.mark.integration
def test_ta_fisher(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.ta.fisher(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "index": "",
                "fast": "",
                "slow": "",
                "offset": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "index": "date",
                "fast": "5",
                "slow": "15",
                "offset": "2",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_adosc(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.ta.adosc(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "target": "",
                "index": "",
                "length": "",
                "std": "",
                "mamode": "",
                "offset": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "target": "high",
                "index": "date",
                "length": "55",
                "std": "3",
                "mamode": "wma",
                "offset": "1",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_bbands(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.ta.bbands(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "target": "",
                "index": "",
                "length": "",
                "offset": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "target": "high",
                "index": "date",
                "length": "55",
                "offset": "5",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_zlma(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.ta.zlma(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "index": "", "length": "", "scalar": ""}),
        (
            {
                "data": get_crypto_data(),
                "index": "date",
                "length": "30",
                "scalar": "110",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_aroon(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.ta.aroon(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "target": "",
                "index": "",
                "length": "",
                "offset": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "target": "high",
                "index": "date",
                "length": "55",
                "offset": "2",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_sma(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.ta.sma(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "index": "",
                "target": "",
                "show_all": "",
                "asint": "",
                "offset": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "index": "date",
                "target": "high",
                "show_all": "true",
                "asint": "true",
                "offset": "5",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_demark(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.ta.demark(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "index": "", "anchor": "", "offset": ""}),
        ({"data": get_crypto_data(), "index": "date", "anchor": "W", "offset": "5"}),
    ],
)
@pytest.mark.integration
def test_ta_vwap(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.ta.vwap(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "target": "",
                "index": "",
                "fast": "",
                "slow": "",
                "signal": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "target": "high",
                "index": "date",
                "fast": "10",
                "slow": "30",
                "signal": "10",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_macd(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.ta.macd(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "target": "",
                "index": "",
                "length": "",
                "offset": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "target": "high",
                "index": "date",
                "length": "55",
                "offset": "2",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_hma(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.ta.hma(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "index": "",
                "lower_length": "",
                "upper_length": "",
                "offset": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "index": "date",
                "lower_length": "30",
                "upper_length": "40",
                "offset": "5",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_donchian(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.ta.donchian(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "index": "",
                "conversion": "",
                "base": "",
                "lagging": "",
                "offset": "",
                "lookahead": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "index": "date",
                "conversion": "10",
                "base": "30",
                "lagging": "50",
                "offset": "30",
                "lookahead": "true",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_ichimoku(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.ta.ichimoku(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "index": "", "target": "", "period": ""}),
        (
            {
                "data": get_crypto_data(),
                "index": "date",
                "target": "close",
                "period": "95",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_clenow(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.ta.clenow(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "index": "",
                "length": "",
                "scalar": "",
                "drift": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "index": "date",
                "length": "60",
                "scalar": "90.0",
                "drift": "2",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_adx(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.ta.adx(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "target": "",
                "index": "",
                "length": "",
                "offset": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "target": "high",
                "index": "date",
                "length": "60",
                "offset": "10",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_wma(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.ta.wma(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "index": "", "length": "", "scalar": ""}),
        (
            {
                "data": get_crypto_data(),
                "index": "date",
                "length": "16",
                "scalar": "0.02",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_cci(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.ta.cci(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "target": "",
                "index": "",
                "length": "",
                "scalar": "",
                "drift": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "target": "high",
                "index": "date",
                "length": "16",
                "scalar": "90.0",
                "drift": "2",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_rsi(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.ta.rsi(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "index": "",
                "fast_k_period": "",
                "slow_d_period": "",
                "slow_k_period": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "index": "date",
                "fast_k_period": "12",
                "slow_d_period": "2",
                "slow_k_period": "2",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_stoch(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.ta.stoch(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "index": "",
                "length": "",
                "scalar": "",
                "mamode": "",
                "offset": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "index": "date",
                "length": "22",
                "scalar": "24",
                "mamode": "sma",
                "offset": "5",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_kc(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.ta.kc(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"data": get_stocks_data(), "index": "", "length": ""}),
        ({"data": get_crypto_data(), "index": "date", "length": "20"}),
    ],
)
@pytest.mark.integration
def test_ta_cg(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.ta.cg(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": get_stocks_data(),
                "index": "",
                "lower_q": "",
                "upper_q": "",
                "model": "",
                "is_crypto": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "index": "date",
                "lower_q": "0.3",
                "upper_q": "0.7",
                "model": "Parkinson",
                "is_crypto": "true",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_cones(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.ta.cones(**params)
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
                "index": "date",
                "length": "",
                "offset": "",
            }
        ),
        (
            {
                "data": get_crypto_data(),
                "target": "high",
                "index": "",
                "length": "60",
                "offset": "10",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_ema(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.ta.ema(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
