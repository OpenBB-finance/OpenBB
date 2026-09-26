"""Tests for ``openbb_econometrics.econometrics_views`` - the charting views.

``openbb_charting`` is an optional dependency that is not installed in the test
environment. ``EconometricsViews`` imports ``openbb_charting.charts`` lazily, so
a fake package is injected into ``sys.modules`` to exercise the wrapper.
"""

import sys
import types

import pytest

from openbb_econometrics.econometrics_views import EconometricsViews


@pytest.fixture
def fake_charting(monkeypatch):
    """Inject a fake ``openbb_charting.charts.correlation_matrix`` package tree.

    The fake ``correlation_matrix`` records the keyword arguments it received and
    returns a ``(figure, content)`` tuple, mirroring the real charting API.
    """
    calls: dict = {}

    def _correlation_matrix(**kwargs):
        calls["kwargs"] = kwargs
        return ("FAKE_FIGURE", {"chart": "correlation_matrix"})

    charting = types.ModuleType("openbb_charting")
    charts = types.ModuleType("openbb_charting.charts")
    corr_mod = types.ModuleType("openbb_charting.charts.correlation_matrix")
    corr_mod.correlation_matrix = _correlation_matrix
    charts.correlation_matrix = corr_mod
    charting.charts = charts

    monkeypatch.setitem(sys.modules, "openbb_charting", charting)
    monkeypatch.setitem(sys.modules, "openbb_charting.charts", charts)
    monkeypatch.setitem(
        sys.modules, "openbb_charting.charts.correlation_matrix", corr_mod
    )
    return calls


def test_econometrics_correlation_matrix(fake_charting):
    """The view delegates to ``openbb_charting`` and returns its tuple."""
    figure, content = EconometricsViews.econometrics_correlation_matrix(
        data=[{"a": 1.0, "b": 2.0}], method="pearson"
    )
    assert figure == "FAKE_FIGURE"
    assert content == {"chart": "correlation_matrix"}
    # The kwargs are forwarded unchanged.
    assert fake_charting["kwargs"] == {
        "data": [{"a": 1.0, "b": 2.0}],
        "method": "pearson",
    }
