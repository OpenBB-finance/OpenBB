"""Tests for the standalone CME router."""

import importlib.util
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def _load_standalone_router_module():
    """Load the CME router as if ``openbb-derivatives`` were not installed."""
    from openbb_core.app.router import Router

    import openbb_cme

    spec = importlib.util.spec_from_file_location(
        "openbb_cme_router_standalone",
        Path(openbb_cme.__file__).parent / "cme_router.py",
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load the standalone CME router.")

    module = importlib.util.module_from_spec(spec)
    original_derivatives = openbb_cme.DERIVATIVES_INSTALLED
    original_command = Router.command
    openbb_cme.DERIVATIVES_INSTALLED = False

    def _passthrough_command(self, func=None, **_kwargs):
        if func is None:
            return lambda inner: _passthrough_command(self, inner, **_kwargs)
        return func

    Router.command = _passthrough_command  # type: ignore[assignment]
    try:
        spec.loader.exec_module(module)
    finally:
        openbb_cme.DERIVATIVES_INSTALLED = original_derivatives
        Router.command = original_command  # type: ignore[assignment]
    return module


def test_provider_key_switches_to_cme_alias(monkeypatch):
    """Fetcher model names remain available without the derivatives extension."""
    import openbb_cme

    monkeypatch.setattr(openbb_cme, "DERIVATIVES_INSTALLED", False)
    assert (
        openbb_cme._key("FuturesHistorical", "CmeFuturesHistorical")
        == "CmeFuturesHistorical"
    )


def test_standalone_router_binds_all_futures_endpoints():
    """All four futures endpoints are exposed from the CME namespace."""
    module = _load_standalone_router_module()
    for name in ("historical", "curve", "instruments", "info"):
        assert callable(getattr(module, name, None)), f"missing {name}"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "endpoint_name", ("historical", "curve", "instruments", "info")
)
async def test_standalone_endpoints_delegate_to_query(endpoint_name):
    """Standalone commands delegate through the standard OpenBB query pipeline."""
    module = _load_standalone_router_module()
    endpoint = getattr(module, endpoint_name)
    sentinel = MagicMock()

    with (
        patch.object(module, "Query", new=MagicMock()),
        patch.object(
            module.OBBject,
            "from_query",
            new=AsyncMock(return_value=sentinel),
        ) as mock_from_query,
    ):
        result = await endpoint(
            cc=MagicMock(),
            provider_choices=MagicMock(),
            standard_params=MagicMock(),
            extra_params=MagicMock(),
        )

    assert result is sentinel
    mock_from_query.assert_awaited_once()
