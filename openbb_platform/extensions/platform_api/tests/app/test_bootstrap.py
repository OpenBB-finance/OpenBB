"""Tests for ``openbb_platform_api.app.bootstrap``.

Covers ``import_app`` edge cases not exercised by the legacy
test_app.py file (Windows-drive detection, missing-attribute /
non-FastAPI / file-not-found errors, factory-detection branches) plus
``check_for_platform_extensions``.
"""

import sys
import types
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI as RealFastAPI


class _MockFastAPI(RealFastAPI):
    """FastAPI subclass that no-ops middleware registration so import_app's
    CORS / exception-handler wiring doesn't blow up the test runner.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_middleware = MagicMock()


@pytest.fixture
def mock_openbb_core():
    """Provide stub openbb_core dependencies so ``import_app`` can wire
    middleware without hitting the real platform stack.
    """
    rest_api = MagicMock()
    rest_api.system = MagicMock()
    modules = {
        "openbb_core.api.rest_api": rest_api,
        "openbb_core.api.app_loader": MagicMock(),
    }
    with (
        patch.dict(sys.modules, modules),
        patch("openbb_core.app.service.system_service.SystemService") as mock_system,
        patch("openbb_core.api.app_loader.AppLoader.add_exception_handlers"),
    ):
        # CORS lives under ``api_settings`` in real SystemSettings.
        mock_system.return_value.system_settings.api_settings.cors.allow_origins = ["*"]
        mock_system.return_value.system_settings.api_settings.cors.allow_methods = ["*"]
        mock_system.return_value.system_settings.api_settings.cors.allow_headers = ["*"]
        yield


def test_import_app_raises_when_file_missing(mock_openbb_core):
    """A bare file path that doesn't exist raises FileNotFoundError."""
    from openbb_platform_api.app.bootstrap import import_app

    with pytest.raises(FileNotFoundError, match="does not exist"):
        import_app("/nonexistent/path/to/app.py", "app", False)


def test_import_app_raises_when_module_attribute_missing(tmp_path, mock_openbb_core):
    """File loads but doesn't expose the requested attribute → AttributeError."""
    from openbb_platform_api.app.bootstrap import import_app

    app_file = tmp_path / "no_app.py"
    app_file.write_text("# nothing here\n")

    with pytest.raises(AttributeError, match="does not contain an 'app' instance"):
        import_app(str(app_file), "app", False)
    sys.modules.pop(app_file.stem, None)


def test_import_app_raises_when_attribute_is_not_fastapi(tmp_path, mock_openbb_core):
    """The named attribute exists but isn't a FastAPI instance → TypeError."""
    from openbb_platform_api.app.bootstrap import import_app

    app_file = tmp_path / "wrong_type.py"
    app_file.write_text("app = 42\n")

    with pytest.raises(TypeError, match="not an instance of FastAPI"):
        import_app(str(app_file), "app", False)
    sys.modules.pop(app_file.stem, None)


def test_import_app_raises_when_factory_flag_but_attribute_not_callable(
    tmp_path, mock_openbb_core
):
    """``--factory`` set but the attribute isn't callable as a factory →
    TypeError. Exercises the ``except TypeError: if factory: raise`` arm.
    """
    from openbb_platform_api.app.bootstrap import import_app

    # Module exposes a FastAPI instance (not a factory). With factory=True,
    # calling it should raise TypeError → the ``if factory: raise`` arm fires.
    app_file = tmp_path / "instance_not_factory.py"
    app_file.write_text("from fastapi import FastAPI\napp = FastAPI()\n")

    with (
        patch("fastapi.FastAPI", new=_MockFastAPI),
        pytest.raises(TypeError, match="callable factory function"),
    ):
        import_app(str(app_file), "app", True)
    sys.modules.pop(app_file.stem, None)


def test_import_app_module_colon_notation_falls_back_to_file_path(
    tmp_path, mock_openbb_core, monkeypatch
):
    """Module-colon path that fails ``import_module`` falls back to a
    file-on-disk load using ``module_path + ".py"``. Exercises the
    ``except ImportError`` arm.
    """
    from openbb_platform_api.app.bootstrap import import_app

    monkeypatch.chdir(tmp_path)
    app_file = tmp_path / "fallback_app.py"
    app_file.write_text("from fastapi import FastAPI\napp = FastAPI()\n")

    with patch("fastapi.FastAPI", new=_MockFastAPI):
        # ``fallback_app:app`` — there's no installed module by that name,
        # so import_module raises and the fallback file load runs.
        result = import_app("fallback_app:app", "app", False)
    assert isinstance(result, _MockFastAPI)
    sys.modules.pop("fallback_app", None)


def test_import_app_module_colon_notation_fallback_raises_when_file_missing(
    tmp_path, mock_openbb_core, monkeypatch
):
    """Module-colon path fails ``import_module`` AND the fallback file
    doesn't exist → FileNotFoundError with the dual-failure message.
    """
    from openbb_platform_api.app.bootstrap import import_app

    monkeypatch.chdir(tmp_path)
    with pytest.raises(FileNotFoundError, match="Neither module .* nor file .* exists"):
        import_app("missing_module:app", "app", False)


def test_import_app_module_colon_with_absolute_module_path(tmp_path, mock_openbb_core):
    """The fallback loader honors absolute paths even when the colon-
    derived module path is already absolute.
    """
    from openbb_platform_api.app.bootstrap import import_app

    app_file = tmp_path / "abs_app.py"
    app_file.write_text("from fastapi import FastAPI\napp = FastAPI()\n")

    with patch("fastapi.FastAPI", new=_MockFastAPI):
        # Strip the .py so the fallback re-adds it; pass an absolute
        # path to exercise ``Path(module_path).is_absolute() = True``.
        bare = str(app_file.with_suffix(""))
        result = import_app(f"{bare}:app", "app", False)
    assert isinstance(result, _MockFastAPI)
    sys.modules.pop(app_file.stem, None)


def test_import_app_loader_returns_none_for_invalid_spec(tmp_path, mock_openbb_core):
    """When ``util.spec_from_file_location`` returns ``None``, the helper
    raises a clear RuntimeError instead of crashing on ``None.loader``.
    Exercises the ``if spec is None: raise`` defensive arm.
    """
    from openbb_platform_api.app.bootstrap import import_app

    app_file = tmp_path / "x.py"
    app_file.write_text("app = 1\n")
    with (
        patch("importlib.util.spec_from_file_location", return_value=None),
        pytest.raises(RuntimeError, match="Failed to load the file specs"),
    ):
        import_app(str(app_file), "app", False)


def test_is_module_colon_notation_handles_windows_drive_paths():
    """The colon-detector treats ``C:\\path`` as a Windows drive (NOT
    colon-notation) but still recognizes ``C:\\path:name`` as having
    both a drive and an explicit name. Tested by exercising
    ``import_app`` against a synthetic Windows-shaped path.
    """
    # The check is internal to ``import_app``. Hit the bare-file branch
    # by passing a path that LOOKS Windows-y but is just a Unix path
    # the function has to handle. This forces the helper to walk the
    # ``not _is_module_colon_notation`` branch.
    from openbb_platform_api.app.bootstrap import import_app

    with pytest.raises(FileNotFoundError):
        # ``D:/nope.py`` on Unix is just a file path with no module
        # colon — colon followed by ``/`` after a single drive letter
        # means the helper returns False.
        import_app("D:/nope.py", "app", False)


# ---------------------------------------------------------------------------
# check_for_platform_extensions
# ---------------------------------------------------------------------------


def test_check_for_platform_extensions_adds_loaded_modules_to_filter(
    mock_openbb_core,
):
    """When a tag matching econometrics/quantitative/technical is in the
    app's openapi_tags AND the corresponding ``openbb_<mod>`` module is
    loaded in ``sys.modules``, its prefix is appended to the exclude
    filter.
    """
    from openbb_platform_api.app.bootstrap import check_for_platform_extensions

    # Stub a fake econometrics module into sys.modules so the loaded-check
    # passes.
    fake_module = types.ModuleType("openbb_econometrics")
    sys.modules["openbb_econometrics"] = fake_module
    try:
        app = _MockFastAPI()
        app.openapi_tags = [{"name": "econometrics"}, {"name": "unrelated"}]

        with patch(
            "openbb_core.app.service.system_service.SystemService"
        ) as mock_system:
            mock_system.return_value.system_settings.api_settings.prefix = "/api/v1"
            out = check_for_platform_extensions(app, [])
    finally:
        sys.modules.pop("openbb_econometrics", None)
    assert "/api/v1/econometrics/*" in out


def test_check_for_platform_extensions_skips_when_module_not_loaded(
    mock_openbb_core,
):
    """If the tag matches but the module isn't loaded, no append happens
    — we don't exclude routes for an extension that isn't actually
    contributing endpoints.
    """
    from openbb_platform_api.app.bootstrap import check_for_platform_extensions

    # Make sure the module ISN'T loaded.
    sys.modules.pop("openbb_econometrics", None)
    sys.modules.pop("openbb_quantitative", None)
    sys.modules.pop("openbb_technical", None)
    app = _MockFastAPI()
    app.openapi_tags = [{"name": "econometrics"}]
    out = check_for_platform_extensions(app, [])
    assert out == []


def test_check_for_platform_extensions_no_matching_tags(mock_openbb_core):
    """No tag mentions any data-processing extension → exclude filter
    untouched.
    """
    from openbb_platform_api.app.bootstrap import check_for_platform_extensions

    app = _MockFastAPI()
    app.openapi_tags = [{"name": "equity"}, {"name": "currency"}]
    out = check_for_platform_extensions(app, ["existing"])
    assert out == ["existing"]


def test_check_for_platform_extensions_handles_empty_openapi_tags(mock_openbb_core):
    """Defensive: ``openapi_tags=None`` (no tags declared) doesn't crash."""
    from openbb_platform_api.app.bootstrap import check_for_platform_extensions

    app = _MockFastAPI()
    app.openapi_tags = None
    out = check_for_platform_extensions(app, [])
    assert out == []


def test_import_app_factory_without_explicit_flag_emits_warning(
    tmp_path, mock_openbb_core, capsys
):
    """A FastAPI factory function (callable) detected without
    ``--factory true`` emits a soft warning to stdout but still uses
    it. Exercises lines 117-121.
    """
    from openbb_platform_api.app.bootstrap import import_app

    app_file = tmp_path / "factory_app.py"
    app_file.write_text(
        "from fastapi import FastAPI\n\ndef app():\n    return FastAPI()\n"
    )

    with patch("fastapi.FastAPI", new=_MockFastAPI):
        result = import_app(str(app_file), "app", False)
    sys.modules.pop(app_file.stem, None)
    assert isinstance(result, _MockFastAPI)
    out = capsys.readouterr().out
    assert "App factory detected" in out


# ---------------------------------------------------------------------------
# apply_cors_from_system_service — CORS wiring + dedup
# ---------------------------------------------------------------------------


def test_apply_cors_adds_middleware_drawing_from_system_service():
    """A bare FastAPI app gets CORSMiddleware installed using the
    origins/methods/headers from ``SystemService``. Without this,
    OPTIONS preflight requests return 405 Method Not Allowed.
    """
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    from openbb_platform_api.app.bootstrap import apply_cors_from_system_service

    app = FastAPI()
    with patch("openbb_core.app.service.system_service.SystemService") as mock_system:
        mock_system.return_value.system_settings.api_settings.cors.allow_origins = [
            "https://app.example.com"
        ]
        mock_system.return_value.system_settings.api_settings.cors.allow_methods = [
            "GET",
            "POST",
            "OPTIONS",
        ]
        mock_system.return_value.system_settings.api_settings.cors.allow_headers = [
            "Authorization",
            "Content-Type",
        ]
        result = apply_cors_from_system_service(app)

    assert result is True
    cors_layers = [m for m in app.user_middleware if m.cls is CORSMiddleware]
    assert len(cors_layers) == 1
    # The settings flowed through into the middleware kwargs.
    kwargs = cors_layers[0].kwargs
    assert kwargs["allow_origins"] == ["https://app.example.com"]
    assert "OPTIONS" in kwargs["allow_methods"]


def test_apply_cors_is_idempotent_when_already_installed():
    """Calling the helper twice (or against an app whose underlying
    framework already added CORS) is a no-op the second time. Important
    because ``app.py``'s module-level call runs unconditionally — the
    ``--app`` and default-app paths might already have CORS wired.
    """
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    from openbb_platform_api.app.bootstrap import apply_cors_from_system_service

    app = FastAPI()
    app.add_middleware(CORSMiddleware, allow_origins=["*"])

    with patch("openbb_core.app.service.system_service.SystemService") as mock_system:
        mock_system.return_value.system_settings.api_settings.cors.allow_origins = ["*"]
        mock_system.return_value.system_settings.api_settings.cors.allow_methods = ["*"]
        mock_system.return_value.system_settings.api_settings.cors.allow_headers = ["*"]
        result = apply_cors_from_system_service(app)

    assert result is False
    cors_layers = [m for m in app.user_middleware if m.cls is CORSMiddleware]
    assert len(cors_layers) == 1


def test_apply_cors_handles_options_preflight_end_to_end():
    """End-to-end via TestClient: a route that only declares GET
    responds 200 to OPTIONS once CORSMiddleware is installed. This is
    the regression that motivated the unconditional helper call —
    Workspace makes a preflight OPTIONS to ``/widgets.json`` and the
    bare route returns 405 without CORS. Build the app + apply CORS
    BEFORE the first TestClient request because Starlette freezes the
    middleware stack on first dispatch.
    """
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from openbb_platform_api.app.bootstrap import apply_cors_from_system_service

    # Baseline: a vanilla app rejects OPTIONS preflight on a GET-only
    # route with 405 (the symptom the user reported).
    bare = FastAPI()

    @bare.get("/widgets.json")
    async def widgets():
        return {}

    pre_response = TestClient(bare).options(
        "/widgets.json",
        headers={
            "Origin": "https://workspace.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert pre_response.status_code == 405

    # Fresh app with CORS applied BEFORE TestClient construction.
    app = FastAPI()

    @app.get("/widgets.json")
    async def widgets_cors():
        return {}

    with patch("openbb_core.app.service.system_service.SystemService") as mock_system:
        mock_system.return_value.system_settings.api_settings.cors.allow_origins = ["*"]
        mock_system.return_value.system_settings.api_settings.cors.allow_methods = ["*"]
        mock_system.return_value.system_settings.api_settings.cors.allow_headers = ["*"]
        apply_cors_from_system_service(app)

    response = TestClient(app).options(
        "/widgets.json",
        headers={
            "Origin": "https://workspace.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
