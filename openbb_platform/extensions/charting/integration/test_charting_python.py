"""Test charting extension."""

import pytest
from openbb_charting.core.openbb_figure import OpenBBFigure
from openbb_core.app.model.obbject import OBBject


@pytest.fixture(scope="session")
def obb(pytestconfig):
    """Fixture to setup obb."""
    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb

        return openbb.obb


data = {}


def get_stocks_data():
    """Get stocks data."""
    import openbb  # pylint:disable=import-outside-toplevel

    if "stocks_data" in data:
        return data["stocks_data"]

    symbol = "AAPL"
    provider = "fmp"

    data["stocks_data"] = openbb.obb.stocks.load(
        symbol=symbol, provider=provider
    ).results
    return data["stocks_data"]


@pytest.mark.parametrize(
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
def test_chart_stocks_load(params, obb):
    """Test chart stocks load."""
    result = obb.stocks.load(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert result.chart.content
    assert isinstance(result.chart.fig, OpenBBFigure)


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL", "limit": 100, "chart": "True"}),
    ],
)
@pytest.mark.integration
def test_chart_stocks_multiples(params, obb):
    """Test chart stocks multiples."""
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.multiples(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert result.chart.content
    assert isinstance(result.chart.fig, OpenBBFigure)


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "fmp",
                "symbols": "AAPL",
                "limit": 20,
                "chart": "True",
            }
        ),
    ],
)
@pytest.mark.integration
def test_chart_stocks_news(params, obb):
    """Test chart stocks news."""
    params = {p: v for p, v in params.items() if v}

    result = obb.stocks.news(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert result.chart.content
    assert isinstance(result.chart.fig, OpenBBFigure)


@pytest.mark.parametrize(
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
def test_chart_ta_adx(params, obb):
    """Test chart ta adx."""
    params = {p: v for p, v in params.items() if v}

    params["data"] = get_stocks_data()

    result = obb.ta.adx(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert result.chart.content
    assert isinstance(result.chart.fig, OpenBBFigure)


@pytest.mark.parametrize(
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
def test_chart_ta_aroon(params, obb):
    """Test chart ta aroon."""
    params = {p: v for p, v in params.items() if v}

    params["data"] = get_stocks_data()

    result = obb.ta.aroon(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert result.chart.content
    assert isinstance(result.chart.fig, OpenBBFigure)


@pytest.mark.parametrize(
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
def test_chart_ta_ema(params, obb):
    """Test chart ta ema."""
    params = {p: v for p, v in params.items() if v}

    params["data"] = get_stocks_data()

    result = obb.ta.ema(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert result.chart.content
    assert isinstance(result.chart.fig, OpenBBFigure)


@pytest.mark.parametrize(
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
def test_chart_ta_hma(params, obb):
    """Test chart ta hma."""
    params = {p: v for p, v in params.items() if v}

    params["data"] = get_stocks_data()

    result = obb.ta.hma(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert result.chart.content
    assert isinstance(result.chart.fig, OpenBBFigure)


@pytest.mark.parametrize(
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
def test_chart_ta_macd(params, obb):
    """Test chart ta macd."""
    params = {p: v for p, v in params.items() if v}

    params["data"] = get_stocks_data()

    result = obb.ta.macd(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert result.chart.content
    assert isinstance(result.chart.fig, OpenBBFigure)


@pytest.mark.parametrize(
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
def test_chart_ta_rsi(params, obb):
    """Test chart ta rsi."""
    params = {p: v for p, v in params.items() if v}

    params["data"] = get_stocks_data()

    result = obb.ta.rsi(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert result.chart.content
    assert isinstance(result.chart.fig, OpenBBFigure)


@pytest.mark.parametrize(
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
def test_chart_ta_sma(params, obb):
    """Test chart ta sma."""
    params = {p: v for p, v in params.items() if v}

    params["data"] = get_stocks_data()

    result = obb.ta.sma(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert result.chart.content
    assert isinstance(result.chart.fig, OpenBBFigure)


@pytest.mark.parametrize(
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
def test_chart_ta_wma(params, obb):
    """Test chart ta wma."""
    params = {p: v for p, v in params.items() if v}

    params["data"] = get_stocks_data()

    result = obb.ta.wma(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert result.chart.content
    assert isinstance(result.chart.fig, OpenBBFigure)


@pytest.mark.parametrize(
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
def test_chart_ta_zlma(params, obb):
    """Test chart ta zlma."""
    params = {p: v for p, v in params.items() if v}

    params["data"] = get_stocks_data()

    result = obb.ta.zlma(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert result.chart.content
    assert isinstance(result.chart.fig, OpenBBFigure)
