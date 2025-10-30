"""Tests for the ReferenceLoader class."""

import json
from pathlib import Path

import pytest
from openbb_core.app.static.reference_loader import ReferenceLoader

# pylint: disable=W0212, W0621


@pytest.fixture(scope="function")
def reference_loader():
    """Fixture to create a ReferenceLoader instance."""
    ReferenceLoader._instances = {}
    yield ReferenceLoader
    ReferenceLoader._instances = {}


@pytest.fixture
def mock_reference_data(tmp_path):
    """Fixture to create a mock reference.json file."""
    directory = tmp_path / "assets"
    directory.mkdir(parents=True)
    reference_file = directory / "reference.json"
    mock_data = {"key": "value"}
    with open(reference_file, "w", encoding="utf-8") as f:
        json.dump(mock_data, f)
    return tmp_path


def test_load_reference_data(mock_reference_data, reference_loader):
    """Test loading of reference data."""
    loader = reference_loader(directory=mock_reference_data)
    assert loader.reference == {
        "key": "value"
    }, "Reference data should match the mock data"


def test_default_directory_load(reference_loader):
    """Test loading from the default directory."""
    # This test assumes the default directory and reference.json file exist and are correctly set up
    loader = reference_loader()
    # Perform a basic check to ensure some data is loaded; specifics will depend on the actual reference.json content
    assert (
        isinstance(loader.reference, dict) and loader.reference
    ), "Should load data from the default directory"


def test_missing_reference_file(tmp_path, reference_loader):
    """Test behavior when the reference.json file is missing."""
    loader = reference_loader(
        directory=tmp_path
    )  # tmp_path does not contain a reference.json file
    assert (
        loader.reference == {}
    ), "Should return an empty dictionary if the reference file is missing"


def test_nonexistent_directory(reference_loader):
    """Test initialization with a nonexistent directory."""
    assert (
        reference_loader(directory=Path("/nonexistent/path")).reference == {}
    ), "Should return an empty dictionary if the directory does not exist"
