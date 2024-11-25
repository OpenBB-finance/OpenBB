"""Tests for the Results model."""

from openbb_core.app.model.abstract.results import Results
from pydantic import BaseModel


class MockResults(Results):
    """Mock Results class."""


def test_results_model():
    """Test the Results model."""
    res = MockResults()

    assert isinstance(res, BaseModel)
