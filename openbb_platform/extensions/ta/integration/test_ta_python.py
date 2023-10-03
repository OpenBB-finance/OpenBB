"""Test ta extension."""
import pytest
from openbb_core.app.model.obbject import OBBject


@pytest.fixture(scope="session")
def obb(pytestconfig):
    """Fixture to setup obb."""

    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb

        return openbb.obb


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": "",
                "index": "",
                "length": "",
                "mamode": "",
                "drift": "",
                "offset": "",
                "return": "",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_atr(params, obb):
    result = obb.ta.atr(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": "",
                "index": "",
                "close_column": "",
                "period": "",
                "start_date": "",
                "end_date": "",
                "return": "",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_fib(params, obb):
    result = obb.ta.fib(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"data": "", "index": "", "offset": "", "return": ""}),
    ],
)
@pytest.mark.integration
def test_ta_obv(params, obb):
    result = obb.ta.obv(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"data": "", "index": "", "length": "", "signal": "", "return": ""}),
    ],
)
@pytest.mark.integration
def test_ta_fisher(params, obb):
    result = obb.ta.fisher(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"data": "", "index": "", "fast": "", "slow": "", "offset": "", "return": ""}),
    ],
)
@pytest.mark.integration
def test_ta_adosc(params, obb):
    result = obb.ta.adosc(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
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
                "return": "",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_bbands(params, obb):
    result = obb.ta.bbands(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": "",
                "target": "",
                "index": "",
                "length": "",
                "offset": "",
                "return": "",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_zlma(params, obb):
    result = obb.ta.zlma(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"data": "", "index": "", "length": "", "scalar": "", "return": ""}),
    ],
)
@pytest.mark.integration
def test_ta_aroon(params, obb):
    result = obb.ta.aroon(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": "",
                "target": "",
                "index": "",
                "length": "",
                "offset": "",
                "return": "",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_sma(params, obb):
    result = obb.ta.sma(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": "",
                "index": "",
                "target": "",
                "show_all": "",
                "asint": "",
                "offset": "",
                "return": "",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_demark(params, obb):
    result = obb.ta.demark(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"data": "", "index": "", "anchor": "", "offset": "", "return": ""}),
    ],
)
@pytest.mark.integration
def test_ta_vwap(params, obb):
    result = obb.ta.vwap(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": "",
                "target": "",
                "index": "",
                "fast": "",
                "slow": "",
                "signal": "",
                "return": "",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_macd(params, obb):
    result = obb.ta.macd(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": "",
                "target": "",
                "index": "",
                "length": "",
                "offset": "",
                "return": "",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_hma(params, obb):
    result = obb.ta.hma(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": "",
                "index": "",
                "lower_length": "",
                "upper_length": "",
                "offset": "",
                "return": "",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_donchian(params, obb):
    result = obb.ta.donchian(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
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
                "return": "",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_ichimoku(params, obb):
    result = obb.ta.ichimoku(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"data": "", "index": "", "target": "", "period": "", "return": ""}),
    ],
)
@pytest.mark.integration
def test_ta_clenow(params, obb):
    result = obb.ta.clenow(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": "",
                "index": "",
                "length": "",
                "scalar": "",
                "drift": "",
                "return": "",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_adx(params, obb):
    result = obb.ta.adx(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": "",
                "target": "",
                "index": "",
                "length": "",
                "offset": "",
                "return": "",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_wma(params, obb):
    result = obb.ta.wma(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"data": "", "index": "", "length": "", "scalar": "", "return": ""}),
    ],
)
@pytest.mark.integration
def test_ta_cci(params, obb):
    result = obb.ta.cci(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": "",
                "target": "",
                "index": "",
                "length": "",
                "scalar": "",
                "drift": "",
                "return": "",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_rsi(params, obb):
    result = obb.ta.rsi(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": "",
                "index": "",
                "fast_k_period": "",
                "slow_d_period": "",
                "slow_k_period": "",
                "return": "",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_stoch(params, obb):
    result = obb.ta.stoch(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": "",
                "index": "",
                "length": "",
                "scalar": "",
                "mamode": "",
                "offset": "",
                "return": "",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_kc(params, obb):
    result = obb.ta.kc(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"data": "", "index": "", "length": "", "return": ""}),
    ],
)
@pytest.mark.integration
def test_ta_cg(params, obb):
    result = obb.ta.cg(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": "",
                "index": "",
                "lower_q": "",
                "upper_q": "",
                "model": "",
                "is_crypto": "",
                "return": "",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_cones(params, obb):
    result = obb.ta.cones(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": "",
                "target": "",
                "index": "",
                "length": "",
                "offset": "",
                "return": "",
            }
        ),
    ],
)
@pytest.mark.integration
def test_ta_ema(params, obb):
    result = obb.ta.ema(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
