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
    result = obb.stocks.load(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert result.chart.content
    assert isinstance(result.chart.fig, OpenBBFigure)


@pytest.mark.parametrize(
    "params",
    [
        ({"chart": "True"}),
    ],
)
@pytest.mark.integration
def test_chart_stocks_multiples(params, obb):
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
        ({"chart": "True"}),
    ],
)
@pytest.mark.integration
def test_chart_stocks_news(params, obb):
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
        ({"chart": "True"}),
    ],
)
@pytest.mark.integration
def test_chart_ta_adx(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.ta.adx(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert result.chart.content
    assert isinstance(result.chart.fig, OpenBBFigure)


@pytest.mark.parametrize(
    "params",
    [
        ({"chart": "True"}),
    ],
)
@pytest.mark.integration
def test_chart_ta_aroon(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.ta.aroon(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert result.chart.content
    assert isinstance(result.chart.fig, OpenBBFigure)


@pytest.mark.parametrize(
    "params",
    [
        ({"chart": "True"}),
    ],
)
@pytest.mark.integration
def test_chart_ta_ema(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.ta.ema(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert result.chart.content
    assert isinstance(result.chart.fig, OpenBBFigure)


@pytest.mark.parametrize(
    "params",
    [
        ({"chart": "True"}),
    ],
)
@pytest.mark.integration
def test_chart_ta_hma(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.ta.hma(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert result.chart.content
    assert isinstance(result.chart.fig, OpenBBFigure)


@pytest.mark.parametrize(
    "params",
    [
        ({"chart": "True"}),
    ],
)
@pytest.mark.integration
def test_chart_ta_macd(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.ta.macd(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert result.chart.content
    assert isinstance(result.chart.fig, OpenBBFigure)


@pytest.mark.parametrize(
    "params",
    [
        ({"chart": "True"}),
    ],
)
@pytest.mark.integration
def test_chart_ta_rsi(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.ta.rsi(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert result.chart.content
    assert isinstance(result.chart.fig, OpenBBFigure)


@pytest.mark.parametrize(
    "params",
    [
        ({"chart": "True"}),
    ],
)
@pytest.mark.integration
def test_chart_ta_sma(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.ta.sma(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert result.chart.content
    assert isinstance(result.chart.fig, OpenBBFigure)


@pytest.mark.parametrize(
    "params",
    [
        ({"chart": "True"}),
    ],
)
@pytest.mark.integration
def test_chart_ta_wma(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.ta.wma(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert result.chart.content
    assert isinstance(result.chart.fig, OpenBBFigure)


@pytest.mark.parametrize(
    "params",
    [
        ({"chart": "True"}),
    ],
)
@pytest.mark.integration
def test_chart_ta_zlma(params, obb):
    params = {p: v for p, v in params.items() if v}

    result = obb.ta.zlma(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert result.chart.content
    assert isinstance(result.chart.fig, OpenBBFigure)
