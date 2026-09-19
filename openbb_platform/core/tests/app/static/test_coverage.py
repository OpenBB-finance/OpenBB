"""Test the coverage.py file.

These tests do NOT depend on any external OpenBB extension packages
being installed in the environment. The ``fake_router`` fixture
(see ``conftest.py``) installs a synthetic ``Router`` containing one
real command bound to the primary fake provider/model, and replaces
the global ``RouterLoader.from_extensions`` and ``ProviderInterface``
singletons. The ``Coverage`` object then walks that synthetic router
through the real production code paths.
"""

import pytest

from openbb_core.app.command_runner import CommandRunner
from openbb_core.app.static import coverage as coverage_module
from openbb_core.app.static.app_factory import BaseApp
from openbb_core.app.static.coverage import Coverage


@pytest.fixture
def coverage(
    fake_router,
):  # noqa: ARG001 — fixture wires up RouterLoader/ProviderInterface
    """Return a ``Coverage`` over a real ``BaseApp`` and the fake router."""
    return Coverage(BaseApp(command_runner=CommandRunner()))


def test_coverage_init(coverage):
    """``Coverage`` constructs cleanly against a real ``BaseApp``."""
    assert isinstance(coverage, Coverage)


def test_coverage_providers(coverage, fake_provider_name):
    """``Coverage.providers`` returns the fake provider mapped to its routes."""
    provider_coverage = coverage.providers
    assert isinstance(provider_coverage, dict)
    assert fake_provider_name in provider_coverage
    routes = provider_coverage[fake_provider_name]
    assert routes, f"expected at least one route, got {routes!r}"


def test_coverage_commands(coverage, fake_provider_name):
    """``Coverage.commands`` maps the route to the providers that serve it."""
    command_coverage = coverage.commands
    assert isinstance(command_coverage, dict)
    assert command_coverage, "expected at least one command"
    # Every entry's value list must include our fake provider.
    assert any(
        fake_provider_name in providers for providers in command_coverage.values()
    )


def test_coverage_reference(coverage):
    """``Coverage.reference`` returns the loaded reference dict."""
    reference = coverage.reference
    assert isinstance(reference, dict)


def test_coverage_repr(coverage):
    out = repr(coverage)
    assert "/coverage" in out


def test_coverage_command_model(coverage):
    out = coverage.command_model
    assert isinstance(out, dict)
    assert out


def test_coverage_command_schemas_delegates(monkeypatch, coverage):
    seen = {}

    def _fake_get_route_schema_map(app, commands_model, filter_by_provider):
        seen["app"] = app
        seen["commands_model"] = commands_model
        seen["filter"] = filter_by_provider
        return {"ok": True}

    monkeypatch.setattr(
        coverage_module, "get_route_schema_map", _fake_get_route_schema_map
    )

    out = coverage.command_schemas(filter_by_provider="fake")
    assert out == {"ok": True}
    assert seen["app"] is coverage._app
    assert seen["commands_model"] == coverage._command_map.commands_model
    assert seen["filter"] == "fake"
