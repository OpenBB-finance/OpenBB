"""Tests for the SystemSettings class."""

import os
from pathlib import Path

import pytest

from openbb_core.app.model.system_settings import SystemSettings


def test_system_settings():
    """Test the SystemSettings class."""
    sys = SystemSettings()
    assert isinstance(sys, SystemSettings)


def test_system_settings_repr():
    """Test __repr__ returns formatted string with class name and fields."""
    sys = SystemSettings()
    result = repr(sys)
    assert "SystemSettings" in result
    assert "openbb_directory" in result


def test_create_openbb_directory_directory_and_files_not_exist(tmpdir, monkeypatch):
    """Test the create_openbb_directory method."""
    # Arrange
    obb_dir = str(tmpdir.join("openbb"))
    user_settings = str(tmpdir.join("user_settings.json"))
    system_settings = str(tmpdir.join("system_settings.json"))

    monkeypatch.setenv("OPENBB_DIRECTORY", obb_dir)
    monkeypatch.setenv("USER_SETTINGS_PATH", user_settings)
    monkeypatch.setenv("SYSTEM_SETTINGS_PATH", system_settings)

    # Act - The validator runs automatically during instantiation
    sys = SystemSettings(
        openbb_directory=obb_dir,
        user_settings_path=user_settings,
        system_settings_path=system_settings,
    )

    # Assert
    assert os.path.exists(sys.openbb_directory)
    assert os.path.exists(sys.user_settings_path)
    assert os.path.exists(sys.system_settings_path)


def test_create_openbb_directory_directory_exists_user_settings_missing(tmpdir):
    """Test the create_openbb_directory method."""
    # Arrange
    obb_dir = str(tmpdir.join("openbb"))
    user_settings = str(tmpdir.join("user_settings.json"))
    system_settings = str(tmpdir.join("system_settings.json"))

    # Create the openbb directory
    Path(obb_dir).mkdir(parents=True, exist_ok=True)

    # Act - The validator runs automatically during instantiation
    sys = SystemSettings(
        openbb_directory=obb_dir,
        user_settings_path=user_settings,
        system_settings_path=system_settings,
    )

    # Assert
    assert os.path.exists(sys.openbb_directory)
    assert os.path.exists(sys.user_settings_path)
    assert os.path.exists(sys.system_settings_path)


def test_create_openbb_directory_directory_exists_system_settings_missing(tmpdir):
    """Test the create_openbb_directory method."""
    # Arrange
    obb_dir = str(tmpdir.join("openbb"))
    user_settings = str(tmpdir.join("user_settings.json"))
    system_settings = str(tmpdir.join("system_settings.json"))

    # Create the openbb directory
    Path(obb_dir).mkdir(parents=True, exist_ok=True)

    # Create the user_settings.json file
    with open(user_settings, "w") as f:
        f.write("{}")

    # Act - The validator runs automatically during instantiation
    sys = SystemSettings(
        openbb_directory=obb_dir,
        user_settings_path=user_settings,
        system_settings_path=system_settings,
    )

    # Assert
    assert os.path.exists(sys.openbb_directory)
    assert os.path.exists(sys.user_settings_path)
    assert os.path.exists(sys.system_settings_path)


@pytest.mark.parametrize(
    "handlers, valid",
    [
        # Test case: Valid handlers
        (["stdout", "file", "noop"], True),
        # Test case: Invalid handler
        (["stdout", "invalid_handler", "file"], False),
        # Test case: Empty list of handlers
        ([], True),
        # Test case: Repeated valid handlers
        (["stdout", "stderr", "stdout", "noop", "stderr"], True),
    ],
)
def test_validate_logging_handlers(handlers, valid):
    """Test the validate_logging_handlers method."""
    # Act and Assert
    if valid:
        assert SystemSettings.validate_logging_handlers(handlers) == handlers  # type: ignore[call-arg]
    else:
        with pytest.raises(ValueError, match="Invalid logging handler"):
            SystemSettings.validate_logging_handlers(handlers)  # type: ignore[call-arg]
