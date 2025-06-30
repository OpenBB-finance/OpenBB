from unittest.mock import MagicMock, mock_open, patch

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
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("HOME", "/mock/home")
    monkeypatch.setenv("USERPROFILE", "/mock/home")


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
        settings = get_user_settings(
            _login=False, current_user_settings="", user_settings_copy=""
        )
        assert settings == {
            "credentials": {},
            "preferences": {},
            "defaults": {"commands": {}},
        }


def test_get_widgets_json_no_build():
    with (
        patch("builtins.open", mock_open(read_data="{}")),
        patch("os.path.exists", return_value=True),
    ):
        widgets_json = get_widgets_json(
            _build=False, _openapi={}, widget_exclude_filter=[]
        )
        assert widgets_json == {}


def test_parse_args():
    with patch("sys.argv", ["script.py", "--help"]):
        with pytest.raises(SystemExit) as e:
            parse_args()
        assert e.type == SystemExit
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


@pytest.mark.skip("Not working yet. Asking for a fix. Mocking is messed up.")
def test_import_file_app():
    # pylint: disable=import-outside-toplevel
    from fastapi import FastAPI as RealFastAPI

    class MockFastAPI(RealFastAPI):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.add_middleware = MagicMock()

    with (
        patch("importlib.import_module") as mock_import,
        patch("pathlib.Path.exists", return_value=True),
        patch("fastapi.FastAPI", new=MockFastAPI),
        patch("openbb_core.app.service.user_service.UserService.read_from_file"),
        patch(
            "openbb_core.app.model.credentials.CredentialsLoader.load",
            return_value=MagicMock(),
        ),
        patch("openbb_core.app.service.system_service.SystemService") as mock_system,
        patch("openbb_core.api.app_loader.AppLoader.add_routers"),
    ):
        # Configure system settings mock
        mock_system.return_value.system_settings.cors.allow_origins = ["*"]
        mock_system.return_value.system_settings.cors.allow_methods = ["*"]
        mock_system.return_value.system_settings.cors.allow_headers = ["*"]

        mock_import.side_effect = ImportError
        mock_module = MagicMock()
        mock_module.app = MockFastAPI()

        result = import_app("main.py", "app", False)
        assert isinstance(result, MockFastAPI)


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


if __name__ == "__main__":
    pytest.main()
