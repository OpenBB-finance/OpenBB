"""Test the user_service.py module."""

import json
import tempfile
from pathlib import Path

import openbb_core.app.model.user_settings as user_settings_module
from openbb_core.app.service.user_service import (
    UserService,
    UserSettings,
)


def test_read_from_file_file_exists():
    """Test read default user settings."""
    result = UserService.read_from_file(path=Path("some_path"))

    assert result
    assert isinstance(result, UserSettings)


def test_write_to_file():
    """Test write default user settings."""
    # Create a temporary file for this test
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = Path(temp_file.name)

    # Create a UserSettings object with some test data
    user_settings = UserSettings()
    user_settings.credentials = {"username": "test"}  # type: ignore[assignment]
    user_settings.preferences = {"theme": "dark"}  # type: ignore[assignment]
    user_settings.defaults = {"language": "en"}  # type: ignore[assignment]

    # Write the user settings to the temporary file
    UserService.write_to_file(user_settings, temp_path)

    # Read the file and verify its contents
    with open(temp_path, encoding="utf-8") as file:
        data = json.load(file)
        assert data == {
            "credentials": {"username": "test"},
            "preferences": {"theme": "dark"},
            "defaults": {"language": "en"},
        }

    # Clean up the temporary file
    temp_path.unlink()


def test_read_from_file_with_utf8_bom(monkeypatch):
    """Test read user settings when JSON includes UTF-8 BOM."""
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = Path(temp_file.name)

    monkeypatch.setattr(
        user_settings_module,
        "USER_SETTINGS_PATH",
        str(temp_path.parent / "__nonexistent_user_settings__.json"),
    )

    baseline = UserSettings().model_dump(mode="json")
    baseline["preferences"]["chart_style"] = "light"

    temp_path.write_text(
        json.dumps(baseline),
        encoding="utf-8-sig",
    )

    result = UserService.read_from_file(path=temp_path)
    payload = result.model_dump(mode="json")
    assert isinstance(result, UserSettings)
    assert payload["preferences"].get("chart_style") == "light"

    temp_path.unlink()


def test_read_from_file_invalid_json_falls_back_to_default():
    """Test invalid JSON falls back to default settings."""
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = Path(temp_file.name)
    temp_path.write_text("{invalid-json", encoding="utf-8")

    result = UserService.read_from_file(path=temp_path)
    payload = result.model_dump()
    assert isinstance(result, UserSettings)
    assert isinstance(payload["credentials"], dict)
    assert isinstance(payload["preferences"], dict)
    assert isinstance(payload["defaults"], dict)

    temp_path.unlink()


def test_merge_dicts():
    """Test merge dicts."""
    result = UserService._merge_dicts(  # pylint: disable=protected-access
        list_of_dicts=[
            {"a": 1, "b": 2},
            {"a": 3, "b": 4},
        ]
    )

    assert result
    assert isinstance(result, dict)
    assert result["a"] == 3
    assert result["b"] == 4
