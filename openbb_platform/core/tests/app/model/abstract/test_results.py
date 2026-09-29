"""Tests for the Results model."""

from pydantic import BaseModel

from openbb_core.app.model.abstract.results import Results


class MockResults(Results):
    """Mock Results class."""


def test_results_model():
    """Test the Results model."""
    res = MockResults()

    assert isinstance(res, BaseModel)
