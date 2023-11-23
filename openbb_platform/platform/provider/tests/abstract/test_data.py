"""Test the Data."""

# pylint: disable=C2801

import pytest
from openbb_core.provider.abstract.data import Data, check_int


def test_check_int_valid():
    """Test if the check_int function returns the value when it is an int."""
    assert check_int(10) == 10


def test_check_int_invalid():
    """Test if the check_int function raises an error when the value is not an int."""
    with pytest.raises(TypeError):
        check_int("not_an_integer")


def test_data_model():
    """Test the Data model."""
    some_data = Data(test="test")

    assert some_data.test == "test"
    assert not some_data.__alias_dict__
    assert some_data.__repr__() == "Data(test=test)"
    assert some_data.model_dump() == {"test": "test"}


def test_data_model_alias():
    """Test the Data model with an alias."""

    class SomeData(Data):
        """Some data."""

        __alias_dict__ = {"test_alias": "test"}

    some_data = SomeData(test="Hello")

    assert some_data.__alias_dict__ == {"test_alias": "test"}
    assert some_data.__repr__() == "SomeData(test_alias=Hello)"
    assert some_data.model_dump() == {"test_alias": "Hello"}
    assert some_data.test_alias == "Hello"
