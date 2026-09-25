"""Tests for ``openbb_mcp_server.app.app.launch_mcp``."""

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def patch_app_module(monkeypatch):
    """Stub ``app.app`` so ``launch_mcp`` runs without a real FastMCP transport."""
    from openbb_mcp_server.app import app as app_module

    fake_mcp_server = MagicMock(name="MCPServer")

    monkeypatch.setattr(
        app_module,
        "create_mcp_server",
        MagicMock(return_value=fake_mcp_server),
    )
    monkeypatch.setattr(
        app_module,
        "_build_runtime_middleware",
        MagicMock(return_value=[]),
    )

    fake_mcp_service_cls = MagicMock(name="MCPServiceCls")
    fake_settings = MagicMock(name="MCPSettings")
    fake_settings.get_http_run_kwargs.return_value = {
        "uvicorn_config": {"host": "0.0.0.0", "port": "9000"}  # noqa: S104
    }
    fake_settings.get_httpx_kwargs.return_value = {}
    fake_settings.server_auth = None
    fake_mcp_service_cls.return_value.load_with_overrides.return_value = fake_settings
    monkeypatch.setattr(app_module, "MCPService", fake_mcp_service_cls)

    return {
        "module": app_module,
        "mcp_server": fake_mcp_server,
        "settings": fake_settings,
        "service_cls": fake_mcp_service_cls,
    }


def _patch_parse_args(
    monkeypatch, app_module, *, app=None, transport="streamable-http"
):
    """Stub ``parse_args`` to return the supplied dict shape."""
    monkeypatch.setattr(
        app_module,
        "parse_args",
        MagicMock(
            return_value={
                "app": app,
                "transport": transport,
                "mcp_overrides": {},
                "uvicorn_overrides": {},
            }
        ),
    )


class TestLaunchMcp:
    """Transport selection, overrides, and exit codes of ``launch_mcp``."""

    def test_launch_mcp_streamable_http_runs(self, patch_app_module, monkeypatch):
        """Streamable-HTTP transport runs with the merged middleware list."""
        app_module = patch_app_module["module"]
        _patch_parse_args(monkeypatch, app_module)
        monkeypatch.setattr(
            "openbb_mcp_server.app.config.get_bootstrapped_config",
            MagicMock(return_value={}),
        )

        app_module.launch_mcp()

        mcp_server = patch_app_module["mcp_server"]
        mcp_server.run.assert_called_once()
        kwargs = mcp_server.run.call_args.kwargs
        assert kwargs["transport"] == "streamable-http"
        assert kwargs["host"] == "0.0.0.0"  # noqa: S104
        assert kwargs["port"] == 9000
        assert isinstance(kwargs["middleware"], list)

    def test_launch_mcp_stdio_runs_via_asyncio(self, patch_app_module, monkeypatch):
        """``stdio`` transport falls into the asyncio.run(stdio_main(...)) path."""
        app_module = patch_app_module["module"]
        _patch_parse_args(monkeypatch, app_module, transport="stdio")
        monkeypatch.setattr(
            "openbb_mcp_server.app.config.get_bootstrapped_config",
            MagicMock(return_value={}),
        )

        stdio_coroutine = object()
        fake_stdio_main = MagicMock(return_value=stdio_coroutine)
        monkeypatch.setattr(app_module, "stdio_main", fake_stdio_main)
        fake_asyncio_run = MagicMock()
        monkeypatch.setattr(app_module.asyncio, "run", fake_asyncio_run)

        app_module.launch_mcp()

        fake_stdio_main.assert_called_once_with(patch_app_module["mcp_server"])
        fake_asyncio_run.assert_called_once_with(stdio_coroutine)

    def test_launch_mcp_uses_imported_app_when_provided(
        self, patch_app_module, monkeypatch
    ):
        """A non-None ``app`` from ``parse_args`` overrides the default REST app."""
        app_module = patch_app_module["module"]
        user_app = MagicMock(name="UserApp")
        _patch_parse_args(monkeypatch, app_module, app=user_app)
        monkeypatch.setattr(
            "openbb_mcp_server.app.config.get_bootstrapped_config",
            MagicMock(return_value={}),
        )

        app_module.launch_mcp()
        create = app_module.create_mcp_server
        assert create.call_args.args[1] is user_app

    def test_launch_mcp_keyboard_interrupt_exits_cleanly(
        self, patch_app_module, monkeypatch
    ):
        """``KeyboardInterrupt`` from the MCP server exits with code 0."""
        app_module = patch_app_module["module"]
        _patch_parse_args(monkeypatch, app_module)
        monkeypatch.setattr(
            "openbb_mcp_server.app.config.get_bootstrapped_config",
            MagicMock(return_value={}),
        )
        patch_app_module["mcp_server"].run.side_effect = KeyboardInterrupt

        with pytest.raises(SystemExit) as excinfo:
            app_module.launch_mcp()
        assert excinfo.value.code == 0

    def test_launch_mcp_general_exception_exits_one(
        self, patch_app_module, monkeypatch
    ):
        """Generic exceptions from the MCP server exit with code 1."""
        app_module = patch_app_module["module"]
        _patch_parse_args(monkeypatch, app_module)
        monkeypatch.setattr(
            "openbb_mcp_server.app.config.get_bootstrapped_config",
            MagicMock(return_value={}),
        )
        patch_app_module["mcp_server"].run.side_effect = RuntimeError("boom")

        with pytest.raises(SystemExit) as excinfo:
            app_module.launch_mcp()
        assert excinfo.value.code == 1

    def test_launch_mcp_routes_hook_middleware_into_run_kwargs(
        self, patch_app_module, monkeypatch
    ):
        """Auth + middleware hooks flow into the ``mcp.run(middleware=...)`` list."""
        app_module = patch_app_module["module"]
        _patch_parse_args(monkeypatch, app_module)
        monkeypatch.setattr(
            "openbb_mcp_server.app.config.get_bootstrapped_config",
            MagicMock(
                return_value={
                    "mcp": {
                        "auth": {"hooks": ["x:auth"]},
                        "middleware": {"hooks": ["x:mw"]},
                    }
                }
            ),
        )
        monkeypatch.setattr(
            "openbb_mcp_server.app.middleware.build_hook_middleware",
            MagicMock(return_value=["AUTH_MW", "MW_MW"]),
        )

        app_module.launch_mcp()

        mcp_server = patch_app_module["mcp_server"]
        middleware = mcp_server.run.call_args.kwargs["middleware"]
        assert "AUTH_MW" in middleware
        assert "MW_MW" in middleware

    def test_launch_mcp_passes_extra_uvicorn_kwargs(
        self, patch_app_module, monkeypatch
    ):
        """Non-host/port uvicorn config flows through under ``uvicorn_config``."""
        app_module = patch_app_module["module"]
        _patch_parse_args(monkeypatch, app_module)
        monkeypatch.setattr(
            "openbb_mcp_server.app.config.get_bootstrapped_config",
            MagicMock(return_value={}),
        )
        patch_app_module["settings"].get_http_run_kwargs.return_value = {
            "uvicorn_config": {
                "host": "0.0.0.0",  # noqa: S104
                "port": 9000,
                "log_level": "debug",
            }
        }

        app_module.launch_mcp()

        kwargs = patch_app_module["mcp_server"].run.call_args.kwargs
        assert kwargs["uvicorn_config"] == {"log_level": "debug"}

    def test_launch_mcp_without_host_or_port(self, patch_app_module, monkeypatch):
        """A uvicorn config without host or port passes only the remaining options."""
        app_module = patch_app_module["module"]
        _patch_parse_args(monkeypatch, app_module)
        monkeypatch.setattr(
            "openbb_mcp_server.app.config.get_bootstrapped_config",
            MagicMock(return_value={}),
        )
        patch_app_module["settings"].get_http_run_kwargs.return_value = {
            "uvicorn_config": {"log_level": "debug"}
        }

        app_module.launch_mcp()

        kwargs = patch_app_module["mcp_server"].run.call_args.kwargs
        assert "host" not in kwargs
        assert "port" not in kwargs
        assert kwargs["uvicorn_config"] == {"log_level": "debug"}

    def test_launch_mcp_omits_uvicorn_config_when_empty(
        self, patch_app_module, monkeypatch
    ):
        """Empty ``http_run_kwargs`` omits ``uvicorn_config`` from the run call."""
        app_module = patch_app_module["module"]
        _patch_parse_args(monkeypatch, app_module)
        monkeypatch.setattr(
            "openbb_mcp_server.app.config.get_bootstrapped_config",
            MagicMock(return_value={}),
        )
        patch_app_module["settings"].get_http_run_kwargs.return_value = {}

        app_module.launch_mcp()

        kwargs = patch_app_module["mcp_server"].run.call_args.kwargs
        assert "uvicorn_config" not in kwargs
