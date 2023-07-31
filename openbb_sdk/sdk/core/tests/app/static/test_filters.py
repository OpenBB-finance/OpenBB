"""Test the filters.py file."""

import pytest
from openbb_core.app.model.command_output import CommandOutput
from openbb_core.app.static.filters import filter_call, filter_inputs, filter_output
from pandas import DataFrame


def test_filter_call_error():
    """Test filter_call."""

    class Test:
        @filter_call
        def test(self):
            return 1 / 0

    test = Test()

    with pytest.raises(Exception):
        test.test()


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


def test_filter_output():
    """Test filter_output."""
    command_output = filter_output(CommandOutput())

    assert command_output is not None
