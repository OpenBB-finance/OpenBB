import os

import pytest
from openbb_core.app.model.system_settings import SystemSettings


def test_system_settings():
    sys = SystemSettings()
    assert isinstance(sys, SystemSettings)


def test_create_openbb_directory_directory_and_files_not_exist(tmpdir):
    # Arrange
    values = {
        "openbb_directory": str(tmpdir.join("openbb")),
        "user_settings_path": str(tmpdir.join("user_settings.json")),
        "system_settings_path": str(tmpdir.join("system_settings.json")),
    }

    # Act
    SystemSettings.create_openbb_directory(values)

    # Assert
    assert os.path.exists(values["openbb_directory"])
    assert os.path.exists(values["user_settings_path"])
    assert os.path.exists(values["system_settings_path"])


def test_create_openbb_directory_directory_exists_user_settings_missing(tmpdir):
    # Arrange
    values = {
        "openbb_directory": str(tmpdir.join("openbb")),
        "user_settings_path": str(tmpdir.join("user_settings.json")),
        "system_settings_path": str(tmpdir.join("system_settings.json")),
    }

    # Create the openbb directory
    os.makedirs(values["openbb_directory"])

    # Act
    SystemSettings.create_openbb_directory(values)

    # Assert
    assert os.path.exists(values["openbb_directory"])
    assert os.path.exists(values["user_settings_path"])
    assert os.path.exists(values["system_settings_path"])


def test_create_openbb_directory_directory_exists_system_settings_missing(tmpdir):
    # Arrange
    values = {
        "openbb_directory": str(tmpdir.join("openbb")),
        "user_settings_path": str(tmpdir.join("user_settings.json")),
        "system_settings_path": str(tmpdir.join("system_settings.json")),
    }

    # Create the openbb directory
    os.makedirs(values["openbb_directory"])

    # Create the user_settings.json file
    with open(values["user_settings_path"], "w") as f:
        f.write("{}")

    # Act
    SystemSettings.create_openbb_directory(values)

    # Assert
    assert os.path.exists(values["openbb_directory"])
    assert os.path.exists(values["user_settings_path"])
    assert os.path.exists(values["system_settings_path"])


@pytest.mark.parametrize(
    "values, expected_handlers",
    [
        # Test case: test_mode is True, logging_suppress is True
        (
            {
                "test_mode": True,
                "logging_suppress": True,
                "log_collect": True,
                "logging_handlers": [],
            },
            [],
        ),
        # Test case: test_mode is False, logging_suppress is True
        (
            {
                "test_mode": False,
                "logging_suppress": True,
                "log_collect": True,
                "logging_handlers": [],
            },
            [],
        ),
        # Test case: test_mode is False, logging_suppress is False, log_collect is True,
        # and "posthog" handler is not present in logging_handlers
        (
            {
                "test_mode": False,
                "logging_suppress": False,
                "log_collect": True,
                "logging_handlers": ["file", "console"],
            },
            ["file", "console", "posthog"],
        ),
        # Test case: test_mode is False, logging_suppress is False, log_collect is True,
        # and "posthog" handler is already present in logging_handlers
        (
            {
                "test_mode": False,
                "logging_suppress": False,
                "log_collect": True,
                "logging_handlers": ["file", "console", "posthog"],
            },
            ["file", "console", "posthog"],
        ),
    ],
)
def test_validate_posthog_handler(values, expected_handlers):
    # Act
    result = SystemSettings.validate_posthog_handler(values)

    # Assert
    assert result["logging_handlers"] == expected_handlers


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
    # Act and Assert
    if valid:
        assert SystemSettings.validate_logging_handlers(handlers) == handlers
    else:
        with pytest.raises(ValueError, match="Invalid logging handler"):
            SystemSettings.validate_logging_handlers(handlers)
