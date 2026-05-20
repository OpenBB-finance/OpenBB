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
    from openbb_core.app.provider_interface import ProviderInterface

    paths = {getattr(route, "path", "") for route in router.api_router.routes}
    model_map = ProviderInterface().map
    if "CompanyNews" in model_map:
        assert "/company" in paths
    if "WorldNews" in model_map:
        assert "/world" in paths
