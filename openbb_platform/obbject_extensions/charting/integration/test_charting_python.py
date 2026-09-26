"""Deterministic integration tests for the charting extension (in-process)."""

from __future__ import annotations

import pytest

from openbb_charting.core.openbb_figure import OpenBBFigure

from .conftest import CASES, make_obbject


@pytest.mark.integration
@pytest.mark.parametrize(
    "name, route, builder, chart_kwargs",
    CASES,
    ids=[case[0] for case in CASES],
)
def test_charting_integration(name, route, builder, chart_kwargs):
    """The charting accessor resolves the route and populates a real chart."""
    obbject = make_obbject(route, builder())

    obbject.charting.to_chart(render=False, **chart_kwargs)

    chart = obbject.chart
    assert chart is not None, f"{name}: charting produced no chart"
    assert isinstance(chart.fig, OpenBBFigure), f"{name}: no OpenBBFigure"
    assert chart.content, f"{name}: empty chart content"
    assert "data" in chart.content, f"{name}: content missing 'data'"
    assert "layout" in chart.content, f"{name}: content missing 'layout'"
