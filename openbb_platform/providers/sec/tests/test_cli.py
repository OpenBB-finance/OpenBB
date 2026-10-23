"""Unit tests for the ``openbb-sec`` command-line interface."""

import asyncio
import json
import os
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from openbb_sec import cli
from openbb_sec.utils import cache


@pytest.fixture(autouse=True)
def _isolate_cache_env(monkeypatch):
    """Track the cache-dir env var so writes inside ``main`` are restored."""
    monkeypatch.setenv(cache.CACHE_DIR_ENV_VAR, "__placeholder__")
    monkeypatch.delenv(cache.CACHE_DIR_ENV_VAR, raising=False)


class TestResolveCacheDirectory:
    """cli.resolve_cache_directory precedence."""

    def test_explicit_argument_wins(self):
        out = cli.resolve_cache_directory("~/x/sec", discover=False)
        assert out.endswith(os.path.join("x", "sec"))
        assert os.path.isabs(out)

    def test_env_var_override(self, monkeypatch, tmp_path):
        monkeypatch.setenv(cache.CACHE_DIR_ENV_VAR, str(tmp_path / "envcache"))
        out = cli.resolve_cache_directory(discover=False)
        assert out == str((tmp_path / "envcache").resolve())

    def test_falls_back_to_preferences(self, monkeypatch):
        monkeypatch.delenv(cache.CACHE_DIR_ENV_VAR, raising=False)
        prefs = SimpleNamespace(cache_directory="/data/openbb")
        settings = SimpleNamespace(preferences=prefs)
        monkeypatch.setattr(
            "openbb_core.app.service.user_service.UserService",
            lambda: SimpleNamespace(default_user_settings=settings),
        )
        out = cli.resolve_cache_directory(discover=False)
        assert out == os.path.join(cli._abs("/data/openbb"), "sec")

    def test_discover_loads_layered_config(self, monkeypatch, tmp_path):
        called = {}
        monkeypatch.setattr(
            "openbb_core.app.config.loader.load_layered_config",
            lambda: called.setdefault("loaded", True),
        )
        monkeypatch.setenv(cache.CACHE_DIR_ENV_VAR, str(tmp_path / "c"))
        out = cli.resolve_cache_directory(discover=True)
        assert called["loaded"] is True
        assert out == str((tmp_path / "c").resolve())


class TestCreateApp:
    """cli.create_app factory."""

    def test_adds_root_endpoints(self, monkeypatch):
        from fastapi import FastAPI

        fresh = FastAPI()
        monkeypatch.setattr("openbb_core.api.rest_api.app", fresh)
        monkeypatch.setattr(
            "openbb_sec.sec_router.get_widgets_json",
            AsyncMock(return_value={"w": 1}),
        )
        monkeypatch.setattr(
            "openbb_sec.sec_router.get_apps_json",
            AsyncMock(return_value=[{"a": 1}]),
        )
        app = cli.create_app()
        routes = {
            r.path: r
            for r in app.routes
            if getattr(r, "path", "")
            in (
                "/widgets.json",
                "/apps.json",
            )
        }
        assert set(routes) == {"/widgets.json", "/apps.json"}
        widgets = asyncio.run(routes["/widgets.json"].endpoint())
        apps = asyncio.run(routes["/apps.json"].endpoint())
        assert json.loads(bytes(widgets.body)) == {"w": 1}
        assert json.loads(bytes(apps.body)) == [{"a": 1}]

    def test_idempotent(self, monkeypatch):
        from fastapi import FastAPI

        fresh = FastAPI()
        monkeypatch.setattr("openbb_core.api.rest_api.app", fresh)
        cli.create_app()
        cli.create_app()
        count = len(
            [r for r in fresh.routes if getattr(r, "path", "") == "/widgets.json"]
        )
        assert count == 1


class TestPrintInfo:
    """cli._print_info output."""

    def test_not_created(self, capsys, tmp_path):
        cli._print_info(str(tmp_path / "missing"))
        out = capsys.readouterr().out
        assert "not created yet" in out

    def test_with_usage(self, capsys, tmp_path):
        (tmp_path / "a.bin").write_bytes(b"hello")
        cli._print_info(str(tmp_path))
        out = capsys.readouterr().out
        assert "Disk usage" in out
        assert "5 bytes" in out


class TestServe:
    """cli.serve delegation to openbb-api."""

    def test_invokes_openbb_api(self, monkeypatch):
        captured = {}

        def fake_run(command, check):
            captured["command"] = command
            captured["check"] = check
            return SimpleNamespace(returncode=0)

        monkeypatch.setattr("subprocess.run", fake_run)
        monkeypatch.setattr("importlib.util.find_spec", lambda name: object())
        rc = cli.serve(["--port", "7000"])
        assert rc == 0
        assert captured["command"][:3] == [
            sys.executable,
            "-m",
            "openbb_platform_api.main",
        ]
        assert "--app" in captured["command"]
        assert cli._APP_FACTORY in captured["command"]
        assert "--factory" in captured["command"]
        assert captured["command"][-2:] == ["--port", "7000"]

    def test_missing_openbb_api(self, monkeypatch, capsys):
        monkeypatch.setattr("importlib.util.find_spec", lambda name: None)
        rc = cli.serve([])
        assert rc == 1
        assert "openbb-api is required" in capsys.readouterr().out


class TestMain:
    """cli.main command dispatch."""

    def test_path(self, monkeypatch, capsys):
        monkeypatch.setattr(cli, "resolve_cache_directory", lambda c: "/tmp/x/sec")
        assert cli.main(["path"]) == 0
        assert capsys.readouterr().out.strip() == "/tmp/x/sec"

    def test_info(self, monkeypatch, capsys):
        monkeypatch.setattr(cli, "resolve_cache_directory", lambda c: "/tmp/x/sec")
        monkeypatch.setattr(cli, "_print_info", lambda d: print(f"INFO {d}"))
        assert cli.main(["info"]) == 0
        assert "INFO /tmp/x/sec" in capsys.readouterr().out

    def test_clear(self, monkeypatch, capsys):
        monkeypatch.setattr(cli, "resolve_cache_directory", lambda c: "/tmp/x/sec")
        monkeypatch.setattr(cache, "clear_cache", lambda: 7)
        assert cli.main(["clear"]) == 0
        assert "Cleared 7 cache entries" in capsys.readouterr().out

    def test_serve_default_with_passthrough(self, monkeypatch):
        monkeypatch.setattr(cli, "resolve_cache_directory", lambda c: "/tmp/x/sec")
        captured = {}

        def fake_serve(passthrough):
            captured["p"] = passthrough
            return 0

        monkeypatch.setattr(cli, "serve", fake_serve)
        host = "0.0.0.0"  # noqa: S104
        rc = cli.main(["--host", host, "--port", "8000", "--reload"])
        assert rc == 0
        assert captured["p"] == ["--host", host, "--port", "8000", "--reload", "true"]

    def test_serve_sets_cache_env(self, monkeypatch):
        monkeypatch.setattr(cli, "resolve_cache_directory", lambda c: "/tmp/resolved")
        monkeypatch.setattr(cli, "serve", lambda p: 0)
        cli.main([])
        assert cli.os.environ[cache.CACHE_DIR_ENV_VAR] == "/tmp/resolved"
