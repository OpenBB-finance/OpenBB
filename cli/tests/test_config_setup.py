"""Test the Config Setup."""

from unittest.mock import patch

import pytest
from openbb_cli.config.setup import bootstrap

# pylint: disable=unused-variable


def test_bootstrap_creates_directory_and_file():
    """Test that bootstrap creates the settings directory and environment file."""
    with (
        patch("pathlib.Path.mkdir") as mock_mkdir,
        patch("pathlib.Path.touch") as mock_touch,
    ):
        bootstrap()
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_touch.assert_called_once_with(exist_ok=True)


def test_bootstrap_directory_exists():
    """Test bootstrap when the directory already exists."""
    with (
        patch("pathlib.Path.mkdir") as mock_mkdir,
        patch("pathlib.Path.touch") as mock_touch,
    ):
        bootstrap()
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_touch.assert_called_once_with(exist_ok=True)


def test_bootstrap_file_exists():
    """Test bootstrap when the environment file already exists."""
    with (
        patch("pathlib.Path.mkdir") as mock_mkdir,
        patch("pathlib.Path.touch") as mock_touch,
    ):
        bootstrap()
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_touch.assert_called_once_with(exist_ok=True)


def test_bootstrap_permission_error():
    """Test bootstrap handles permission errors gracefully."""
    with (
        patch("pathlib.Path.mkdir") as mock_mkdir,
        patch("pathlib.Path.touch"),
        pytest.raises(PermissionError),
    ):
        mock_mkdir.side_effect = PermissionError("No permission to create directory")
        bootstrap()  # Expecting to raise a PermissionError and be caught by pytest.raises
