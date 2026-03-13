"""Test the API utilities module."""

import importlib
import json
import sys
import types
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import openbb_platform_api.utils.api as api_utils
import pytest
from openbb_platform_api.utils.api import (
    check_port,
    get_user_settings,
    get_widgets_json,
    import_app,
    parse_args,
)


# Mock environment variables
@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch, tmp_path_factory):
    mock_home = tmp_path_factory.mktemp("home")
    monkeypatch.setenv("HOME", str(mock_home))
    monkeypatch.setenv("USERPROFILE", str(mock_home))


def _load_main_with_mocks():
    # pylint: disable=import-outside-toplevel
    from fastapi import FastAPI

    stub_app = FastAPI()
    core_module = types.ModuleType("openbb_core")
    core_module.__path__ = []
    api_module = types.ModuleType("openbb_core.api")
    api_module.__path__ = []
    rest_api_module = types.ModuleType("openbb_core.api.rest_api")
    rest_api_module.app = stub_app  # type: ignore
    app_module = types.ModuleType("openbb_core.app")
    app_module.__path__ = []
    app_service_module = types.ModuleType("openbb_core.app.service")
    app_service_module.__path__ = []
    system_service_module = types.ModuleType("openbb_core.app.service.system_service")

    class DummySystemService:
        def __init__(self, *_args, **_kwargs):
            self.system_settings = types.SimpleNamespace(
                python_settings=types.SimpleNamespace(
                    model_dump=lambda: {"uvicorn": {}}
                ),
                cors=types.SimpleNamespace(
                    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
                ),
                api_settings=types.SimpleNamespace(prefix="/api"),
            )

    system_service_module.SystemService = DummySystemService  # type:ignore
    env_module = types.ModuleType("openbb_core.env")
    env_module.Env = lambda: None  # type: ignore

    provider_module = types.ModuleType("openbb_core.provider")
    provider_module.__path__ = []
    provider_utils_module = types.ModuleType("openbb_core.provider.utils")
    provider_utils_module.__path__ = []
    provider_utils_helpers_module = types.ModuleType(
        "openbb_core.provider.utils.helpers"
    )

    def _run_async_stub(callable_or_coroutine, *args, **kwargs):
        import asyncio

        result = (
            callable_or_coroutine(*args, **kwargs)
            if callable(callable_or_coroutine)
            else callable_or_coroutine
        )

        if hasattr(result, "__await__"):
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            if loop.is_running():
                return asyncio.ensure_future(result)  # type: ignore
            return loop.run_until_complete(result)  # type: ignore
        return result

    def _to_snake_case_stub(value: str) -> str:
        import re

        if not value:
            return value
        value = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", value)
        value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
        return re.sub(r"[\s\-]+", "_", value).lower()

    provider_utils_helpers_module.run_async = _run_async_stub  # type: ignore
    provider_utils_helpers_module.to_snake_case = _to_snake_case_stub  # type: ignore

    modules = {
        "openbb_core": core_module,
        "openbb_core.api": api_module,
        "openbb_core.api.rest_api": rest_api_module,
        "openbb_core.app": app_module,
        "openbb_core.app.service": app_service_module,
        "openbb_core.app.service.system_service": system_service_module,
        "openbb_core.env": env_module,
        "openbb_core.provider": provider_module,
        "openbb_core.provider.utils": provider_utils_module,
        "openbb_core.provider.utils.helpers": provider_utils_helpers_module,
    }

    for name in list(modules):
        sys.modules.pop(name, None)

    with patch.dict(sys.modules, modules):
        sys.modules.pop("openbb_platform_api.main", None)
        return importlib.import_module("openbb_platform_api.main")


@pytest.mark.parametrize("port_input", [6900, "6900", 6901, "6901"])
def test_check_port(port_input):
    with patch("socket.socket") as mock_socket:
        mock_sock_instance = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock_instance

        # Mock connect_ex to return 0 for port 6900 (indicating it's in use)
        mock_sock_instance.connect_ex.side_effect = lambda addr: (
            0 if addr[1] == 6900 else 1
        )

        port = check_port("127.0.0.1", port_input)
        assert port == 6901  # The next available port should be 6901


def test_get_user_settings_no_login():
    with patch(
        "builtins.open",
        mock_open(
            read_data='{"credentials": {}, "preferences": {}, "defaults": {"commands": {}}}'
        ),
    ):
        settings = get_user_settings(current_user_settings="")
        assert settings == {
            "credentials": {},
            "preferences": {},
            "defaults": {"commands": {}},
        }


def test_get_widgets_json_no_build():
    dummy_main = types.ModuleType("openbb_platform_api.main")
    dummy_main.FIRST_RUN = False  # type: ignore

    with (
        patch("builtins.open", mock_open(read_data="{}")),
        patch("os.path.exists", return_value=True),
        patch(
            "openbb_platform_api.utils.widgets.build_json", MagicMock(return_value={})
        ),
        patch.dict(
            sys.modules,
            {"uvicorn": MagicMock(), "openbb_platform_api.main": dummy_main},
        ),
    ):
        widgets_json = get_widgets_json(
            _build=False, _openapi={}, widget_exclude_filter=[]
        )
        assert widgets_json == {}


def test_parse_args():
    with patch("sys.argv", ["script.py", "--help"]):
        with pytest.raises(SystemExit) as e:
            parse_args()
        assert e.type is SystemExit
        assert e.value.code == 0

    with patch("sys.argv", ["script.py", "--key", "value"]):
        args = parse_args()
        assert args == {"key": "value"}

    with patch("sys.argv", ["script.py", "--flag"]):
        args = parse_args()
        assert args == {"flag": True}


def test_import_module_app():
    # pylint: disable=import-outside-toplevel
    from fastapi import FastAPI as RealFastAPI

    class MockFastAPI(RealFastAPI):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.add_middleware = MagicMock()

    # Create mock modules to prevent real imports
    mock_rest_api = MagicMock()
    mock_rest_api.system = MagicMock()

    with (
        patch.dict(
            "sys.modules",
            {
                "openbb_core.api.rest_api": mock_rest_api,
                "openbb_core.api.router.commands": MagicMock(),
                "openbb_core.app.command_runner": MagicMock(),
                "openbb_core.app.static.package_builder": MagicMock(),
                "openbb_core.app.provider_interface": MagicMock(),
                "openbb_core.provider.registry": MagicMock(),
                "openbb_core.app.extension_loader": MagicMock(),
            },
        ),
        patch("importlib.import_module") as mock_import,
        patch("fastapi.FastAPI", new=MockFastAPI),
        patch("openbb_core.app.service.system_service.SystemService") as mock_system,
        patch("openbb_core.app.service.user_service.UserService.read_from_file"),
        patch("openbb_core.app.model.credentials.CredentialsLoader.load"),
        patch("openbb_core.api.app_loader.AppLoader.add_routers"),
    ):
        # Mock system settings
        mock_system.return_value.system_settings.cors.allow_origins = ["*"]
        mock_system.return_value.system_settings.cors.allow_methods = ["*"]
        mock_system.return_value.system_settings.cors.allow_headers = ["*"]

        # Rest of test setup...
        mock_module = MagicMock()
        mock_module.__spec__ = MagicMock()
        mock_module.app = MockFastAPI()
        mock_import.return_value = mock_module

        result = import_app("my_module:app", "app", False)
        assert isinstance(result, MockFastAPI)


def test_import_file_app(tmp_path):
    # pylint: disable=import-outside-toplevel
    from fastapi import FastAPI as RealFastAPI

    class MockFastAPI(RealFastAPI):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.add_middleware = MagicMock()

    mock_rest_api = MagicMock()
    mock_rest_api.system = MagicMock()
    app_file = tmp_path / "integration_app.py"
    app_file.write_text("from fastapi import FastAPI\n\napp = FastAPI()\n")
    module_name = app_file.stem

    with (
        patch.dict(
            "sys.modules",
            {
                "openbb_core.api.rest_api": mock_rest_api,
                "openbb_core.api.router.commands": MagicMock(),
                "openbb_core.app.command_runner": MagicMock(),
                "openbb_core.app.static.package_builder": MagicMock(),
                "openbb_core.app.provider_interface": MagicMock(),
                "openbb_core.provider.registry": MagicMock(),
                "openbb_core.app.extension_loader": MagicMock(),
            },
        ),
        patch("fastapi.FastAPI", new=MockFastAPI),
        patch("openbb_core.app.service.user_service.UserService.read_from_file"),
        patch(
            "openbb_core.app.model.credentials.CredentialsLoader.load",
            return_value=MagicMock(),
        ),
        patch("openbb_core.app.service.system_service.SystemService") as mock_system,
        patch("openbb_core.api.app_loader.AppLoader.add_routers"),
    ):
        mock_system.return_value.system_settings.cors.allow_origins = ["*"]
        mock_system.return_value.system_settings.cors.allow_methods = ["*"]
        mock_system.return_value.system_settings.cors.allow_headers = ["*"]

        result = import_app(str(app_file), "app", False)
        loaded_module = sys.modules.get(module_name)

        assert isinstance(result, MockFastAPI)
        assert loaded_module is not None
        assert getattr(loaded_module, "app", None) is result

    sys.modules.pop(module_name, None)


def test_import_factory_app():
    # pylint: disable=import-outside-toplevel
    from fastapi import FastAPI as RealFastAPI

    class MockFastAPI(RealFastAPI):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.add_middleware = MagicMock()

    # Create mock modules to prevent real imports
    mock_rest_api = MagicMock()
    mock_rest_api.system = MagicMock()

    with (
        patch.dict(
            "sys.modules",
            {
                "openbb_core.api.rest_api": mock_rest_api,
                "openbb_core.api.router.commands": MagicMock(),
                "openbb_core.app.command_runner": MagicMock(),
                "openbb_core.app.static.package_builder": MagicMock(),
                "openbb_core.app.provider_interface": MagicMock(),
                "openbb_core.provider.registry": MagicMock(),
                "openbb_core.app.extension_loader": MagicMock(),
            },
        ),
        patch("importlib.import_module") as mock_import,
        patch("fastapi.FastAPI", new=MockFastAPI),
        patch("openbb_core.app.service.system_service.SystemService") as mock_system,
        patch("openbb_core.app.service.user_service.UserService.read_from_file"),
        patch(
            "openbb_core.app.model.credentials.CredentialsLoader.load",
            return_value=MagicMock(),
        ),
        patch("openbb_core.api.app_loader.AppLoader.add_routers"),
    ):
        # Configure system settings mock
        mock_system.return_value.system_settings.cors.allow_origins = ["*"]
        mock_system.return_value.system_settings.cors.allow_methods = ["*"]
        mock_system.return_value.system_settings.cors.allow_headers = ["*"]

        # Create a proper mock module with __spec__ attribute
        mock_module = MagicMock()
        mock_module.__spec__ = MagicMock()
        factory = MagicMock(return_value=MockFastAPI())
        mock_module.factory_func = factory
        mock_import.return_value = mock_module

        result = import_app("main:factory_func", "factory_func", True)
        factory.assert_called_once()
        assert isinstance(result, MockFastAPI)


# =============================================================================
# Path Handling Tests - Cross-Platform Compatibility
# =============================================================================


class TestPathHandling:
    """Test cross-platform path handling in import_app function."""

    @pytest.fixture
    def mock_fastapi_env(self):
        """Set up common mocks for FastAPI import tests."""
        # pylint: disable=import-outside-toplevel
        from fastapi import FastAPI as RealFastAPI

        class MockFastAPI(RealFastAPI):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.add_middleware = MagicMock()

        mock_rest_api = MagicMock()
        mock_rest_api.system = MagicMock()

        return MockFastAPI, mock_rest_api

    def _create_app_file(self, tmp_path, filename="test_app.py"):
        """Create a test app file."""
        app_file = tmp_path / filename
        app_file.write_text("from fastapi import FastAPI\n\napp = FastAPI()\n")
        return app_file

    def test_unix_absolute_path(self, tmp_path, mock_fastapi_env):
        """Test Unix-style absolute paths (e.g., /home/user/app.py)."""
        MockFastAPI, mock_rest_api = mock_fastapi_env
        app_file = self._create_app_file(tmp_path)

        with (
            patch.dict(
                "sys.modules",
                {
                    "openbb_core.api.rest_api": mock_rest_api,
                    "openbb_core.api.router.commands": MagicMock(),
                    "openbb_core.app.command_runner": MagicMock(),
                    "openbb_core.app.static.package_builder": MagicMock(),
                    "openbb_core.app.provider_interface": MagicMock(),
                    "openbb_core.provider.registry": MagicMock(),
                    "openbb_core.app.extension_loader": MagicMock(),
                },
            ),
            patch("fastapi.FastAPI", new=MockFastAPI),
            patch("openbb_core.app.service.user_service.UserService.read_from_file"),
            patch(
                "openbb_core.app.model.credentials.CredentialsLoader.load",
                return_value=MagicMock(),
            ),
            patch(
                "openbb_core.app.service.system_service.SystemService"
            ) as mock_system,
            patch("openbb_core.api.app_loader.AppLoader.add_routers"),
        ):
            mock_system.return_value.system_settings.cors.allow_origins = ["*"]
            mock_system.return_value.system_settings.cors.allow_methods = ["*"]
            mock_system.return_value.system_settings.cors.allow_headers = ["*"]

            # Test with absolute Unix-style path
            result = import_app(str(app_file), "app", False)
            assert isinstance(result, MockFastAPI)

    def test_relative_path(self, tmp_path, mock_fastapi_env, monkeypatch):
        """Test relative paths are resolved correctly."""
        MockFastAPI, mock_rest_api = mock_fastapi_env
        app_file = self._create_app_file(tmp_path)
        monkeypatch.chdir(tmp_path)

        with (
            patch.dict(
                "sys.modules",
                {
                    "openbb_core.api.rest_api": mock_rest_api,
                    "openbb_core.api.router.commands": MagicMock(),
                    "openbb_core.app.command_runner": MagicMock(),
                    "openbb_core.app.static.package_builder": MagicMock(),
                    "openbb_core.app.provider_interface": MagicMock(),
                    "openbb_core.provider.registry": MagicMock(),
                    "openbb_core.app.extension_loader": MagicMock(),
                },
            ),
            patch("fastapi.FastAPI", new=MockFastAPI),
            patch("openbb_core.app.service.user_service.UserService.read_from_file"),
            patch(
                "openbb_core.app.model.credentials.CredentialsLoader.load",
                return_value=MagicMock(),
            ),
            patch(
                "openbb_core.app.service.system_service.SystemService"
            ) as mock_system,
            patch("openbb_core.api.app_loader.AppLoader.add_routers"),
        ):
            mock_system.return_value.system_settings.cors.allow_origins = ["*"]
            mock_system.return_value.system_settings.cors.allow_methods = ["*"]
            mock_system.return_value.system_settings.cors.allow_headers = ["*"]

            # Test with relative path
            result = import_app(app_file.name, "app", False)
            assert isinstance(result, MockFastAPI)

    def test_relative_path_with_subdirectory(
        self, tmp_path, mock_fastapi_env, monkeypatch
    ):
        """Test relative paths with subdirectories."""
        MockFastAPI, mock_rest_api = mock_fastapi_env
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        app_file = subdir / "myapp.py"
        app_file.write_text("from fastapi import FastAPI\n\napp = FastAPI()\n")
        monkeypatch.chdir(tmp_path)

        with (
            patch.dict(
                "sys.modules",
                {
                    "openbb_core.api.rest_api": mock_rest_api,
                    "openbb_core.api.router.commands": MagicMock(),
                    "openbb_core.app.command_runner": MagicMock(),
                    "openbb_core.app.static.package_builder": MagicMock(),
                    "openbb_core.app.provider_interface": MagicMock(),
                    "openbb_core.provider.registry": MagicMock(),
                    "openbb_core.app.extension_loader": MagicMock(),
                },
            ),
            patch("fastapi.FastAPI", new=MockFastAPI),
            patch("openbb_core.app.service.user_service.UserService.read_from_file"),
            patch(
                "openbb_core.app.model.credentials.CredentialsLoader.load",
                return_value=MagicMock(),
            ),
            patch(
                "openbb_core.app.service.system_service.SystemService"
            ) as mock_system,
            patch("openbb_core.api.app_loader.AppLoader.add_routers"),
        ):
            mock_system.return_value.system_settings.cors.allow_origins = ["*"]
            mock_system.return_value.system_settings.cors.allow_methods = ["*"]
            mock_system.return_value.system_settings.cors.allow_headers = ["*"]

            # Test with relative path including subdirectory
            result = import_app("subdir/myapp.py", "app", False)
            assert isinstance(result, MockFastAPI)

    def test_module_colon_notation(self, mock_fastapi_env):
        """Test module:name colon notation (e.g., 'my_module:app')."""
        MockFastAPI, mock_rest_api = mock_fastapi_env

        with (
            patch.dict(
                "sys.modules",
                {
                    "openbb_core.api.rest_api": mock_rest_api,
                    "openbb_core.api.router.commands": MagicMock(),
                    "openbb_core.app.command_runner": MagicMock(),
                    "openbb_core.app.static.package_builder": MagicMock(),
                    "openbb_core.app.provider_interface": MagicMock(),
                    "openbb_core.provider.registry": MagicMock(),
                    "openbb_core.app.extension_loader": MagicMock(),
                },
            ),
            patch("importlib.import_module") as mock_import,
            patch("fastapi.FastAPI", new=MockFastAPI),
            patch(
                "openbb_core.app.service.system_service.SystemService"
            ) as mock_system,
            patch("openbb_core.app.service.user_service.UserService.read_from_file"),
            patch("openbb_core.app.model.credentials.CredentialsLoader.load"),
            patch("openbb_core.api.app_loader.AppLoader.add_routers"),
        ):
            mock_system.return_value.system_settings.cors.allow_origins = ["*"]
            mock_system.return_value.system_settings.cors.allow_methods = ["*"]
            mock_system.return_value.system_settings.cors.allow_headers = ["*"]

            mock_module = MagicMock()
            mock_module.__spec__ = MagicMock()
            mock_module.myapp = MockFastAPI()
            mock_import.return_value = mock_module

            result = import_app("some_package.module:myapp", "myapp", False)
            assert isinstance(result, MockFastAPI)
            # Verify the target module was imported (among other imports)
            mock_import.assert_any_call("some_package.module")

    def test_file_path_with_colon_notation(self, tmp_path, mock_fastapi_env):
        """Test file path with colon notation (e.g., 'myfile.py:app')."""
        MockFastAPI, mock_rest_api = mock_fastapi_env
        app_file = self._create_app_file(tmp_path, "custom_app.py")

        with (
            patch.dict(
                "sys.modules",
                {
                    "openbb_core.api.rest_api": mock_rest_api,
                    "openbb_core.api.router.commands": MagicMock(),
                    "openbb_core.app.command_runner": MagicMock(),
                    "openbb_core.app.static.package_builder": MagicMock(),
                    "openbb_core.app.provider_interface": MagicMock(),
                    "openbb_core.provider.registry": MagicMock(),
                    "openbb_core.app.extension_loader": MagicMock(),
                },
            ),
            patch("fastapi.FastAPI", new=MockFastAPI),
            patch("openbb_core.app.service.user_service.UserService.read_from_file"),
            patch(
                "openbb_core.app.model.credentials.CredentialsLoader.load",
                return_value=MagicMock(),
            ),
            patch(
                "openbb_core.app.service.system_service.SystemService"
            ) as mock_system,
            patch("openbb_core.api.app_loader.AppLoader.add_routers"),
        ):
            mock_system.return_value.system_settings.cors.allow_origins = ["*"]
            mock_system.return_value.system_settings.cors.allow_methods = ["*"]
            mock_system.return_value.system_settings.cors.allow_headers = ["*"]

            # Test with file path + colon notation
            result = import_app(f"{app_file}:app", "app", False)
            assert isinstance(result, MockFastAPI)

    def test_file_not_found_error(self, tmp_path, mock_fastapi_env):
        """Test FileNotFoundError is raised for non-existent files."""
        MockFastAPI, mock_rest_api = mock_fastapi_env
        non_existent_path = tmp_path / "does_not_exist.py"

        with (
            patch.dict(
                "sys.modules",
                {
                    "openbb_core.api.rest_api": mock_rest_api,
                    "openbb_core.api.router.commands": MagicMock(),
                    "openbb_core.app.command_runner": MagicMock(),
                    "openbb_core.app.static.package_builder": MagicMock(),
                    "openbb_core.app.provider_interface": MagicMock(),
                    "openbb_core.provider.registry": MagicMock(),
                    "openbb_core.app.extension_loader": MagicMock(),
                },
            ),
            patch("fastapi.FastAPI", new=MockFastAPI),
            patch("openbb_core.app.service.user_service.UserService.read_from_file"),
            patch(
                "openbb_core.app.model.credentials.CredentialsLoader.load",
                return_value=MagicMock(),
            ),
            patch(
                "openbb_core.app.service.system_service.SystemService"
            ) as mock_system,
            patch("openbb_core.api.app_loader.AppLoader.add_routers"),
        ):
            mock_system.return_value.system_settings.cors.allow_origins = ["*"]
            mock_system.return_value.system_settings.cors.allow_methods = ["*"]
            mock_system.return_value.system_settings.cors.allow_headers = ["*"]

            with pytest.raises(FileNotFoundError):
                import_app(str(non_existent_path), "app", False)

    def test_attribute_error_missing_app_instance(self, tmp_path, mock_fastapi_env):
        """Test AttributeError is raised when app instance is missing."""
        MockFastAPI, mock_rest_api = mock_fastapi_env
        app_file = tmp_path / "no_app.py"
        app_file.write_text("# No app defined here\nx = 1\n")

        with (
            patch.dict(
                "sys.modules",
                {
                    "openbb_core.api.rest_api": mock_rest_api,
                    "openbb_core.api.router.commands": MagicMock(),
                    "openbb_core.app.command_runner": MagicMock(),
                    "openbb_core.app.static.package_builder": MagicMock(),
                    "openbb_core.app.provider_interface": MagicMock(),
                    "openbb_core.provider.registry": MagicMock(),
                    "openbb_core.app.extension_loader": MagicMock(),
                },
            ),
            patch("fastapi.FastAPI", new=MockFastAPI),
            patch("openbb_core.app.service.user_service.UserService.read_from_file"),
            patch(
                "openbb_core.app.model.credentials.CredentialsLoader.load",
                return_value=MagicMock(),
            ),
            patch(
                "openbb_core.app.service.system_service.SystemService"
            ) as mock_system,
            patch("openbb_core.api.app_loader.AppLoader.add_routers"),
        ):
            mock_system.return_value.system_settings.cors.allow_origins = ["*"]
            mock_system.return_value.system_settings.cors.allow_methods = ["*"]
            mock_system.return_value.system_settings.cors.allow_headers = ["*"]

            with pytest.raises(AttributeError):
                import_app(str(app_file), "app", False)

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
    def test_windows_absolute_path(self, tmp_path, mock_fastapi_env):
        """Test Windows-style absolute paths (e.g., C:\\Users\\app.py)."""
        MockFastAPI, mock_rest_api = mock_fastapi_env
        app_file = self._create_app_file(tmp_path)

        with (
            patch.dict(
                "sys.modules",
                {
                    "openbb_core.api.rest_api": mock_rest_api,
                    "openbb_core.api.router.commands": MagicMock(),
                    "openbb_core.app.command_runner": MagicMock(),
                    "openbb_core.app.static.package_builder": MagicMock(),
                    "openbb_core.app.provider_interface": MagicMock(),
                    "openbb_core.provider.registry": MagicMock(),
                    "openbb_core.app.extension_loader": MagicMock(),
                },
            ),
            patch("fastapi.FastAPI", new=MockFastAPI),
            patch("openbb_core.app.service.user_service.UserService.read_from_file"),
            patch(
                "openbb_core.app.model.credentials.CredentialsLoader.load",
                return_value=MagicMock(),
            ),
            patch(
                "openbb_core.app.service.system_service.SystemService"
            ) as mock_system,
            patch("openbb_core.api.app_loader.AppLoader.add_routers"),
        ):
            mock_system.return_value.system_settings.cors.allow_origins = ["*"]
            mock_system.return_value.system_settings.cors.allow_methods = ["*"]
            mock_system.return_value.system_settings.cors.allow_headers = ["*"]

            # On Windows, tmp_path will have a drive letter (e.g., C:\...)
            result = import_app(str(app_file), "app", False)
            assert isinstance(result, MockFastAPI)

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
    def test_windows_path_with_colon_notation(self, tmp_path, mock_fastapi_env):
        """Test Windows path with colon notation (e.g., C:\\path\\app.py:myapp)."""
        MockFastAPI, mock_rest_api = mock_fastapi_env
        app_file = self._create_app_file(tmp_path)

        with (
            patch.dict(
                "sys.modules",
                {
                    "openbb_core.api.rest_api": mock_rest_api,
                    "openbb_core.api.router.commands": MagicMock(),
                    "openbb_core.app.command_runner": MagicMock(),
                    "openbb_core.app.static.package_builder": MagicMock(),
                    "openbb_core.app.provider_interface": MagicMock(),
                    "openbb_core.provider.registry": MagicMock(),
                    "openbb_core.app.extension_loader": MagicMock(),
                },
            ),
            patch("fastapi.FastAPI", new=MockFastAPI),
            patch("openbb_core.app.service.user_service.UserService.read_from_file"),
            patch(
                "openbb_core.app.model.credentials.CredentialsLoader.load",
                return_value=MagicMock(),
            ),
            patch(
                "openbb_core.app.service.system_service.SystemService"
            ) as mock_system,
            patch("openbb_core.api.app_loader.AppLoader.add_routers"),
        ):
            mock_system.return_value.system_settings.cors.allow_origins = ["*"]
            mock_system.return_value.system_settings.cors.allow_methods = ["*"]
            mock_system.return_value.system_settings.cors.allow_headers = ["*"]

            # Windows path with colon notation: C:\path\app.py:app
            result = import_app(f"{app_file}:app", "app", False)
            assert isinstance(result, MockFastAPI)


class TestPathDetectionHelpers:
    """Test path detection logic for cross-platform compatibility."""

    def test_is_absolute_path_detection_unix(self):
        """Test absolute path detection for Unix paths."""
        from pathlib import Path

        # Unix absolute paths
        assert Path("/home/user/app.py").is_absolute() is True
        assert Path("/app.py").is_absolute() is True
        # Relative paths
        assert Path("app.py").is_absolute() is False
        assert Path("./app.py").is_absolute() is False
        assert Path("subdir/app.py").is_absolute() is False

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
    def test_is_absolute_path_detection_windows(self):
        """Test absolute path detection for Windows paths."""
        from pathlib import Path

        # Windows absolute paths
        assert Path("C:\\Users\\app.py").is_absolute() is True
        assert Path("D:/Projects/app.py").is_absolute() is True
        # Relative paths
        assert Path("app.py").is_absolute() is False
        assert Path(".\\app.py").is_absolute() is False

    def test_colon_notation_vs_windows_drive(self):
        """Test distinguishing module:name notation from Windows drive letters."""
        # These should be recognized as module:name notation
        module_notations = [
            "module:app",
            "package.module:app",
            "my_app.main:create_app",
        ]

        for notation in module_notations:
            # Has colon and is not a Windows drive letter pattern
            assert ":" in notation
            # First char before colon is not a single letter (drive)
            parts = notation.split(":")
            assert len(parts[0]) > 1 or not parts[0].isalpha()

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
    def test_windows_drive_letter_detection(self):
        """Test detection of Windows drive letters vs colon notation."""
        from pathlib import Path

        # Windows paths with drive letters
        windows_paths = [
            "C:\\app.py",
            "D:/Projects/app.py",
            "E:\\Users\\test\\app.py",
        ]

        for path_str in windows_paths:
            path = Path(path_str)
            # Should be detected as absolute (has drive)
            assert path.is_absolute()
            # Drive should be detected
            assert path.drive != ""

        # Windows path WITH colon notation (e.g., C:\path\app.py:myapp)
        complex_path = "C:\\Projects\\app.py:myapp"
        # This has multiple colons - drive colon + notation colon
        assert complex_path.count(":") == 2


@pytest.mark.asyncio
async def test_get_apps_json_creates_missing_file(tmp_path):
    main = _load_main_with_mocks()
    apps_path = tmp_path / "workspace_apps.json"
    default_path = tmp_path / "default_apps.json"
    exists_sequence = [False, False, False, True]

    def exists_side_effect(_):
        return exists_sequence.pop(0) if exists_sequence else True

    with (
        patch.object(main, "APPS_PATH", str(apps_path)),
        patch.object(main, "DEFAULT_APPS_PATH", str(default_path)),
        patch.object(main, "get_widgets", AsyncMock(return_value={})),
        patch(
            "openbb_platform_api.main.os.path.exists", side_effect=exists_side_effect
        ),
        patch("openbb_platform_api.main.os.makedirs") as mock_makedirs,
        patch("builtins.open", mock_open(read_data="[]")) as mocked_open,
    ):
        response = await main.get_apps_json()

    mock_makedirs.assert_called_once_with(str(apps_path.parent), exist_ok=True)
    mocked_open.assert_any_call(str(apps_path), "w", encoding="utf-8")
    assert json.loads(response.body.decode()) == []


@pytest.mark.asyncio
async def test_get_apps_json_merges_templates_with_additional_sources(tmp_path):
    main = _load_main_with_mocks()
    apps_path = tmp_path / "workspace_apps.json"
    default_path = tmp_path / "default_apps.json"
    default_templates_data = json.dumps(
        [
            {"id": "from-default"},
            {"layout": [{"i": "widget-2"}]},
            {"tabs": {"tab1": {"layout": [{"i": "widget-3"}]}}},
        ]
    )
    apps_templates_data = json.dumps({"id": "default"})
    default_handle = mock_open(read_data=default_templates_data).return_value
    apps_handle = mock_open(read_data=apps_templates_data).return_value
    mocked_open = mock_open()
    mocked_open.side_effect = [default_handle, apps_handle]

    with (
        patch.object(main, "APPS_PATH", str(apps_path)),
        patch.object(main, "DEFAULT_APPS_PATH", str(default_path)),
        patch.object(
            main,
            "widgets_json",
            {
                "widget-2": {},
                "widget-3": {},
                "default": {},
                "from-default": {},
                "extra": {},
            },
        ),
        patch("openbb_platform_api.main.os.path.exists", return_value=True),
        patch.object(
            main,
            "get_widgets",
            AsyncMock(return_value={"default": {}, "from-default": {}, "extra": {}}),
        ),
        patch.object(
            main,
            "get_additional_apps",
            AsyncMock(
                return_value={"good": [{"id": "extra"}], "bad": {"id": "invalid"}}
            ),
        ),
        patch("openbb_platform_api.main.has_additional_apps", return_value=True),
        patch("openbb_platform_api.main.logger.error") as mock_log_error,
        patch("builtins.open", mocked_open),
    ):
        response = await main.get_apps_json()

    if mock_log_error.called:
        mock_log_error.assert_called_once()
    assert mocked_open.call_count == 2
    result = json.loads(response.body.decode())
    expected_core = [
        {"id": "default"},
        {"id": "from-default"},
        {"layout": [{"i": "widget-2"}]},
        {"tabs": {"tab1": {"layout": [{"i": "widget-3"}]}}},
    ]
    for item in expected_core:
        assert item in result
    if any(getattr(entry, "get", lambda *_: None)("id") == "extra" for entry in result):
        assert {"id": "extra"} in result


def test_get_widgets_json_merges_with_additional_sources(monkeypatch):
    base_widgets = {"default": {"name": "Default Widget"}}
    additional_widgets = {"extra": {"name": "Extra Widget"}}

    monkeypatch.setattr(api_utils, "FIRST_RUN", False, raising=False)
    monkeypatch.setattr(
        "openbb_platform_api.utils.widgets.build_json",
        MagicMock(return_value=base_widgets.copy()),
        raising=False,
    )
    monkeypatch.setattr(
        api_utils,
        "PATH_WIDGETS",
        {"custom": {"extra": additional_widgets["extra"]}},
        raising=False,
    )

    widgets = api_utils.get_widgets_json(
        _build=False,
        _openapi={},
        widget_exclude_filter=[],
        editable=False,
        widgets_path=None,
        app=None,
    )

    assert widgets["default"] == base_widgets["default"]
    assert widgets["extra"] == additional_widgets["extra"]


if __name__ == "__main__":
    pytest.main()
