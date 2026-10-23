"""Test the Empty model."""

from pydantic import BaseModel

from openbb_core.app.model.results.empty import Empty


def test_empty_model():
    """Test the Empty model."""
    empty = Empty()

    assert isinstance(empty, Empty)
    assert isinstance(empty, BaseModel)
