"""Test charting extension."""

import pytest
from extensions.tests.conftest import parametrize
from openbb_charting.core.openbb_figure import OpenBBFigure
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


def get_equity_data():
    """Get equity data."""
    import openbb  # pylint:disable=import-outside-toplevel

    if "stocks_data" in data:
        return data["stocks_data"]

    symbol = "AAPL"
    provider = "fmp"

    data["stocks_data"] = openbb.obb.equity.price.historical(
        symbol=symbol, provider=provider
    ).results
    return data["stocks_data"]


@parametrize(
    "params",
    [
        (
            {
                "provider": "fmp",
                "symbol": "AAPL",
                "chart": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_chart_equity_price_historical(params, obb):
    """Test chart equity price historical."""
    result = obb.equity.price.historical(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert result.chart.content
    assert isinstance(result.chart.fig, OpenBBFigure)


@parametrize(
    "params",
    [
        ({"symbol": "AAPL", "limit": 100, "chart": "True"}),
    ],
)
@pytest.mark.integration
def test_chart_equity_fundamental_multiples(params, obb):
    """Test chart equity multiples."""
    params = {p: v for p, v in params.items() if v}

    result = obb.equity.fundamental.multiples(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert result.chart.content
    assert isinstance(result.chart.fig, OpenBBFigure)


@parametrize(
    "params",
    [
        (
            {
                "data": "",
                "index": "date",
                "length": "60",
                "scalar": "90.0",
                "drift": "2",
                "chart": "True",
            }
        ),
    ],
)
@pytest.mark.integration
def test_chart_technical_adx(params, obb):
    """Test chart ta adx."""
    params = {p: v for p, v in params.items() if v}

    params["data"] = get_equity_data()

    result = obb.technical.adx(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert result.chart.content
    assert isinstance(result.chart.fig, OpenBBFigure)


@parametrize(
    "params",
    [
        (
            {
                "data": "",
                "index": "date",
                "length": "30",
                "scalar": "110",
                "chart": "True",
            }
        ),
    ],
)
@pytest.mark.integration
def test_chart_technical_aroon(params, obb):
    """Test chart ta aroon."""
    params = {p: v for p, v in params.items() if v}

    params["data"] = get_equity_data()

    result = obb.technical.aroon(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert result.chart.content
    assert isinstance(result.chart.fig, OpenBBFigure)


@parametrize(
    "params",
    [
        (
            {
                "data": "",
                "target": "high",
                "index": "",
                "length": "60",
                "offset": "10",
                "chart": "True",
            }
        ),
    ],
)
@pytest.mark.integration
def test_chart_technical_ema(params, obb):
    """Test chart ta ema."""
    params = {p: v for p, v in params.items() if v}

    params["data"] = get_equity_data()

    result = obb.technical.ema(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert result.chart.content
    assert isinstance(result.chart.fig, OpenBBFigure)


@parametrize(
    "params",
    [
        (
            {
                "data": "",
                "target": "high",
                "index": "date",
                "length": "55",
                "offset": "2",
                "chart": "True",
            }
        ),
    ],
)
@pytest.mark.integration
def test_chart_technical_hma(params, obb):
    """Test chart ta hma."""
    params = {p: v for p, v in params.items() if v}

    params["data"] = get_equity_data()

    result = obb.technical.hma(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert result.chart.content
    assert isinstance(result.chart.fig, OpenBBFigure)


@parametrize(
    "params",
    [
        (
            {
                "data": "",
                "target": "high",
                "index": "date",
                "fast": "10",
                "slow": "30",
                "signal": "10",
                "chart": "True",
            }
        ),
    ],
)
@pytest.mark.integration
def test_chart_technical_macd(params, obb):
    """Test chart ta macd."""
    params = {p: v for p, v in params.items() if v}

    params["data"] = get_equity_data()

    result = obb.technical.macd(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert result.chart.content
    assert isinstance(result.chart.fig, OpenBBFigure)


@parametrize(
    "params",
    [
        (
            {
                "data": "",
                "target": "high",
                "index": "date",
                "length": "16",
                "scalar": "90.0",
                "drift": "2",
                "chart": "True",
            }
        ),
    ],
)
@pytest.mark.integration
def test_chart_technical_rsi(params, obb):
    """Test chart ta rsi."""
    params = {p: v for p, v in params.items() if v}

    params["data"] = get_equity_data()

    result = obb.technical.rsi(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert result.chart.content
    assert isinstance(result.chart.fig, OpenBBFigure)


@parametrize(
    "params",
    [
        (
            {
                "data": "",
                "target": "high",
                "index": "date",
                "length": "55",
                "offset": "2",
                "chart": "True",
            }
        ),
    ],
)
@pytest.mark.integration
def test_chart_technical_sma(params, obb):
    """Test chart ta sma."""
    params = {p: v for p, v in params.items() if v}

    params["data"] = get_equity_data()

    result = obb.technical.sma(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert result.chart.content
    assert isinstance(result.chart.fig, OpenBBFigure)


@parametrize(
    "params",
    [
        (
            {
                "data": "",
                "target": "high",
                "index": "date",
                "length": "60",
                "offset": "10",
                "chart": "True",
            }
        ),
    ],
)
@pytest.mark.integration
def test_chart_technical_wma(params, obb):
    """Test chart ta wma."""
    params = {p: v for p, v in params.items() if v}

    params["data"] = get_equity_data()

    result = obb.technical.wma(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert result.chart.content
    assert isinstance(result.chart.fig, OpenBBFigure)


@parametrize(
    "params",
    [
        (
            {
                "data": "",
                "target": "high",
                "index": "date",
                "length": "55",
                "offset": "5",
                "chart": "True",
            }
        ),
    ],
)
@pytest.mark.integration
def test_chart_technical_zlma(params, obb):
    """Test chart ta zlma."""
    params = {p: v for p, v in params.items() if v}

    params["data"] = get_equity_data()

    result = obb.technical.zlma(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert result.chart.content
    assert isinstance(result.chart.fig, OpenBBFigure)
