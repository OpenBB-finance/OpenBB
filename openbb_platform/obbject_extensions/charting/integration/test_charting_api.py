"""Deterministic integration tests for the charting extension's API contract."""

from __future__ import annotations

import pytest
from openbb_core.api.router.commands import validate_output

from .conftest import CASES, make_obbject


@pytest.mark.integration
@pytest.mark.parametrize(
    "name, route, builder, chart_kwargs",
    CASES,
    ids=[case[0] for case in CASES],
)
def test_charting_api_contract(name, route, builder, chart_kwargs):
    """The charted OBBject serializes to the API chart shape (no ``fig``)."""
    obbject = make_obbject(route, builder())
    obbject.charting.to_chart(render=False, **chart_kwargs)
    assert obbject.chart is not None, f"{name}: charting produced no chart"

    validate_output(obbject)

    chart = obbject.chart
    assert not hasattr(chart, "fig"), f"{name}: API output must exclude 'fig'"
    assert chart.content, f"{name}: empty chart content"
    assert "data" in chart.content, f"{name}: content missing 'data'"
    assert "layout" in chart.content, f"{name}: content missing 'layout'"
    assert chart.format, f"{name}: chart missing 'format'"

    dumped = chart.model_dump(exclude_none=True, exclude_unset=True)
    assert sorted(dumped) == ["content", "format"], (
        f"{name}: API chart payload should be content + format, got {sorted(dumped)}"
    )
