"""Router tests."""

from openbb_core.app.router import Router

from openbb_news.router import router


def test_router_aggregates_rss_commands():
    assert isinstance(router, Router)
    paths = {getattr(route, "path", "") for route in router.api_router.routes}
    assert "/rss" in paths
    assert "/rss_providers" in paths
    assert "/rss_feeds" in paths


def test_router_aggregates_provider_news_commands():
    paths = {getattr(route, "path", "") for route in router.api_router.routes}
    assert "/world" in paths
    assert "/company" in paths
