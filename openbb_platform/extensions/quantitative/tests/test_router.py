"""Tests for ``openbb_quantitative.router`` - the aggregating router."""

from openbb_core.app.router import Router

from openbb_quantitative.router import router

EXPECTED_ROUTES = {
    "/normality",
    "/capm",
    "/unitroot_test",
    "/summary",
    "/factors",
    "/risk_decomposition",
    "/attribution",
    "/rolling/skew",
    "/rolling/variance",
    "/rolling/stdev",
    "/rolling/kurtosis",
    "/rolling/mean",
    "/rolling/quantile",
    "/rolling/factors",
    "/stats/skew",
    "/stats/variance",
    "/stats/stdev",
    "/stats/kurtosis",
    "/stats/mean",
    "/stats/quantile",
    "/performance/omega_ratio",
    "/performance/sharpe_ratio",
    "/performance/sortino_ratio",
}


def test_router_aggregates_every_command():
    """The top-level router wires every quantitative command exactly once."""
    assert isinstance(router, Router)
    paths = [r.path for r in router.api_router.routes]
    assert set(paths) == EXPECTED_ROUTES
    assert len(paths) == len(EXPECTED_ROUTES)
