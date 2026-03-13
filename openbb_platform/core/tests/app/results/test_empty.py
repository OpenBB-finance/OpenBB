"""Test the Empty model."""

from openbb_core.app.model.results.empty import Empty
from pydantic import BaseModel


def test_empty_model():
    """Test the Empty model."""
    empty = Empty()

    assert isinstance(empty, Empty)
    assert isinstance(empty, BaseModel)
