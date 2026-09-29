"""Tests for ``openbb_econometrics.router`` - the aggregating router."""


def test_router_imports_and_aggregates():
    """Importing the router wires together every sub-router."""
    from openbb_core.app.router import Router

    from openbb_econometrics.router import router

    assert isinstance(router, Router)
    assert "router" in dir()
