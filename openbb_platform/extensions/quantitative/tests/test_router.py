"""Tests for ``openbb_quantitative.router`` - the aggregating router."""

from openbb_core.app.router import Router

from openbb_quantitative.router import router


def test_router_aggregates_every_command():
    """The top-level router wires together all 19 quantitative commands."""
    assert isinstance(router, Router)
    assert len(router.api_router.routes) == 19
