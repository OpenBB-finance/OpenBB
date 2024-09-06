from unittest.mock import MagicMock, mock_open, patch

import pytest
from openbb_platform_api.api import (
    check_port,
    get_user_settings,
    get_widgets_json,
    main,
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
        settings = get_user_settings(login=False)
        assert settings == {
            "credentials": {},
            "preferences": {},
            "defaults": {"commands": {}},
        }


def test_get_widgets_json_no_build():
    with patch("builtins.open", mock_open(read_data="{}")), patch(
        "os.path.exists", return_value=True
    ):
        widgets_json = get_widgets_json(build=False, openapi={})
        assert widgets_json == {}


def test_main():
    with patch("sys.argv", ["api.py", "--no-build"]), patch(
        "openbb_platform_api.api.get_user_settings"
    ), patch("openbb_platform_api.api.get_widgets_json"), patch("uvicorn.run"):
        main()
        assert True  # If no exception is raised, the test passes


if __name__ == "__main__":
    pytest.main()
