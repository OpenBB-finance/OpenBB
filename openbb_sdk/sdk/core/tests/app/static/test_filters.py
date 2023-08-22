"""Test the filters.py file."""

from openbb_core.app.static.filters import filter_inputs
from pandas import DataFrame


def test_filter_inputs_not_df():
    """Test filter_inputs."""
    kwargs = {"num": 1}
    kwargs = filter_inputs(**kwargs)

    assert kwargs["num"] == 1


def test_filter_inputs_df():
    """Test filter_inputs."""
    df = DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    kwargs = {"df": df}
    kwargs = filter_inputs(**kwargs)

    assert isinstance(kwargs["df"], list)
