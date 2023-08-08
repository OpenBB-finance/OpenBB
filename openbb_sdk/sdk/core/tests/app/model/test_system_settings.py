import os
from unittest.mock import patch

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


@pytest.mark.parametrize(
    "commit_hash, expected_result",
    [
        # Test case: Valid commit hash provided
        ("1234567890", "1234567890"),
        # Test case: Empty commit hash, mocked get_commit_hash returns "abcdef1234"
        ("", "abcdef1234"),
    ],
)
def test_validate_commit_hash(commit_hash, expected_result):
    with patch(
        "openbb_core.app.model.system_settings.get_commit_hash",
        return_value="abcdef1234",
    ):
        # Act
        result = SystemSettings.validate_commit_hash(commit_hash)

        # Assert
        assert result == expected_result


@patch("openbb_core.app.model.system_settings.get_branch", return_value="main")
@pytest.mark.parametrize(
    "branch, commit_hash, expected_branch",
    [
        # Test case: Empty branch, non-empty commit hash
        ("", "abcdef1234", "main"),
        # Test case: Non-empty branch, non-empty commit hash
        ("feature-branch", "abcdef1234", "feature-branch"),
        # Test case: Empty branch, empty commit hash
        ("", "", ""),
        # Test case: Non-empty branch, empty commit hash
        ("feature-branch", "", "feature-branch"),
    ],
)
def test_validate_branch(mock_get_branch, branch, commit_hash, expected_branch):
    # Arrange
    values = {
        "logging_branch": branch,
        "logging_commit_hash": commit_hash,
    }

    # Act
    result = SystemSettings.validate_branch(values)

    # Assert
    assert result["logging_branch"] == expected_branch

    # Ensure that get_branch was called with the correct commit_hash
    if not branch and commit_hash:
        mock_get_branch.assert_called_once_with(commit_hash)
    else:
        mock_get_branch.assert_not_called()
