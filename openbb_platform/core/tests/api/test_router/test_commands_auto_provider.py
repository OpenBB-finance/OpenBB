"""Tests for service-side auto provider resolution and meta injection in API wrapper."""

import asyncio
from inspect import signature
from typing import Literal, get_args
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from openbb_core.api.router.commands import build_api_wrapper
from openbb_core.app.command_runner import CommandRunner
from openbb_core.app.model.obbject import OBBject


class TestCommandsAutoProvider:
    """Verify auto provider strategy and meta payload in command wrapper."""

    def test_wrapper_signature_allows_auto_provider(self):
        """Provider should default to auto and accept explicit auto value."""

        async def endpoint(
            symbol: str,
            provider: Literal["wind", "tushare"],
        ):
            return OBBject(results=[{"symbol": symbol, "provider": provider}])

        route = APIRoute(path="/equity/price/historical", endpoint=endpoint, methods=["GET"])
        runner = MagicMock(spec=CommandRunner)
        runner.command_map = type(
            "DummyCommandMap",
            (),
            {"command_coverage": {"/equity/price/historical": ["wind", "tushare"]}},
        )()
        runner.run = MagicMock()

        wrapped = build_api_wrapper(runner, route)
        sig = signature(wrapped)
        provider_param = sig.parameters["provider"]

        assert provider_param.default == "auto"
        literal_choices = get_args(provider_param.annotation)
        assert "auto" in literal_choices

    def test_auto_provider_fallback_and_meta_payload(self):
        """When provider=auto, wrapper should fallback and always include meta."""

        async def endpoint(
            symbol: str = "AAPL",
            provider: str | None = None,
            **kwargs,
        ):
            return OBBject(results=[{"symbol": symbol}])

        route = APIRoute(path="/equity/price/historical", endpoint=endpoint, methods=["GET"])

        runner = MagicMock(spec=CommandRunner)
        attempts = {"count": 0}

        class DummyCommandMap:
            command_coverage = {
                "/equity/price/historical": ["wind", "tushare", "yfinance"],
            }

        runner.command_map = DummyCommandMap()

        async def fake_run(path, user_settings, *args, **kwargs):
            attempts["count"] += 1
            provider = kwargs.get("standard_params", {}).get("provider")
            if provider == "wind":
                raise RuntimeError("wind failed")
            out = OBBject(results=[{"provider": provider}])
            out.provider = provider
            return out

        runner.run = fake_run

        wrapped = build_api_wrapper(runner, route)
        app = FastAPI()
        router = APIRouter()
        router.add_api_route("/equity/price/historical", wrapped, methods=["GET"])
        app.include_router(router)

        with patch(
            "openbb_core.api.router.commands.UserService.read_from_file",
            return_value={},
        ), patch(
            "openbb_core.app.model.user_settings.os.path.exists",
            return_value=False,
        ):
            client = TestClient(app, raise_server_exceptions=True)
            resp = client.get("/equity/price/historical", params={"symbol": "AAPL", "provider": "auto"})

        assert resp.status_code == 200
        data = resp.json()
        meta = data.get("extra", {}).get("meta", {})

        assert attempts["count"] == 2
        assert meta.get("provider_requested") == "auto"
        assert meta.get("provider_used") == "tushare"
        assert isinstance(meta.get("fallback_trace"), list)
        assert meta["fallback_trace"][0]["provider"] == "wind"
        assert meta["fallback_trace"][0]["status"] == "failed"
        assert meta["fallback_trace"][1]["provider"] == "tushare"
        assert meta["fallback_trace"][1]["status"] == "success"
        assert meta["selection_reason"]["mode"] == "auto"
        assert "strategy_source" in meta["selection_reason"]
        assert isinstance(meta["selection_reason"].get("scored_providers"), list)
        assert 0 <= meta.get("confidence", -1) <= 1

    def test_provider_choices_explicit_provider_is_respected(self):
        """When provider is set via provider_choices dependency, wrapper should use it."""

        async def endpoint(symbol: str = "AAPL", **kwargs):
            return OBBject(results=[{"symbol": symbol}])

        route = APIRoute(path="/equity/price/historical", endpoint=endpoint, methods=["GET"])
        runner = MagicMock(spec=CommandRunner)
        attempts = {"count": 0}

        class DummyCommandMap:
            command_coverage = {"/equity/price/historical": ["wind", "tushare", "yfinance"]}

        runner.command_map = DummyCommandMap()

        async def fake_run(path, user_settings, *args, **kwargs):
            attempts["count"] += 1
            provider = kwargs.get("standard_params", {}).get("provider")
            out = OBBject(results=[{"provider": provider}])
            out.provider = provider
            return out

        runner.run = fake_run
        wrapped = build_api_wrapper(runner, route)

        with patch(
            "openbb_core.api.router.commands.UserService.read_from_file",
            return_value={},
        ), patch(
            "openbb_core.app.model.user_settings.os.path.exists",
            return_value=False,
        ):
            out = asyncio.run(
                wrapped(
                    symbol="AAPL",
                    standard_params={},
                    extra_params={},
                    provider_choices=SimpleNamespace(provider="yfinance"),
                )
            )

        assert attempts["count"] == 1
        assert isinstance(out, OBBject)
        assert out.provider == "yfinance"
        assert out.extra["meta"]["provider_requested"] == "yfinance"
        assert out.extra["meta"]["selection_reason"]["mode"] == "explicit"
        assert "strategy_source" in out.extra["meta"]["selection_reason"]
