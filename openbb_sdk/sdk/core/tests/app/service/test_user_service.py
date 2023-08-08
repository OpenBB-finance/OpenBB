"""Test the user_service.py module."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from openbb_core.app.service.user_service import (
    AbstractAccessTokenRepository,
    InMemoryAccessTokenRepository,
    MongoClient,
    MongoDBAccessTokenRepository,
    UserService,
    UserSettings,
)


def test_build_token_repository_with_given_repository():
    """Test build with repository."""
    mock_repository = MagicMock(spec=AbstractAccessTokenRepository)
    result = UserService.build_token_repository(
        valid_client=True, access_token_repository=mock_repository
    )

    assert result == mock_repository


def test_build_token_repository_with_mongodb_client():
    """Test build with mongodb client."""
    mock_client = MagicMock(spec=MongoClient)
    result = UserService.build_token_repository(
        valid_client=True, mongodb_client=mock_client
    )

    assert isinstance(result, MongoDBAccessTokenRepository)


def test_build_token_repository_memory():
    """Test build with in-memory access."""
    result = UserService.build_token_repository(valid_client=True)

    assert isinstance(result, InMemoryAccessTokenRepository)


def test_build_user_settings_repository_with_given_repository():
    """Test build with repository."""
    mock_repository = MagicMock(spec=AbstractAccessTokenRepository)
    result = UserService.build_user_settings_repository(
        valid_client=True, user_settings_repository=mock_repository
    )

    assert result == mock_repository


def test_build_user_settings_repository_with_mongodb_client():
    """Test build with mongodb client."""
    mock_client = MagicMock(spec=MongoClient)
    result = UserService.build_user_settings_repository(
        valid_client=True, mongodb_client=mock_client
    )

    assert result
    assert isinstance(type(result), type(MongoDBAccessTokenRepository))


def test_build_user_settings_repository_memory():
    """Test build with in-memory access."""
    result = UserService.build_user_settings_repository(valid_client=True)

    assert result
    assert isinstance(type(result), type(InMemoryAccessTokenRepository))


def test_valid_client_false():
    """Test valid client."""
    result = UserService.valid_client()

    assert result is False


def test_valid_client_true():
    """Test valid client."""
    mock_client = MagicMock(spec=MongoClient)
    result = UserService.valid_client(client=mock_client)

    assert result is True


# @pytest.mark.skip(reason="TODO")
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
    result = UserService.merge_dicts(
        list_of_dicts=[
            {"a": 1, "b": 2},
            {"a": 3, "b": 4},
        ]
    )

    assert result
    assert isinstance(result, dict)
    assert result["a"] == 3
    assert result["b"] == 4
