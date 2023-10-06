"""Test the user_service.py module."""

from pathlib import Path

import pytest
from openbb_core.app.service.user_service import (
    UserService,
    UserSettings,
)


def test_read_default_user_settings_file_exists():
    """Test read default user settings."""
    result = UserService.read_default_user_settings(path=Path("some_path"))

    assert result
    assert isinstance(result, UserSettings)


@pytest.mark.skip(reason="TODO")
def test_write_default_user_settings():
    """Test write default user settings."""


@pytest.mark.skip(reason="TODO")
def test_update_default():
    """Test update default user settings."""


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
