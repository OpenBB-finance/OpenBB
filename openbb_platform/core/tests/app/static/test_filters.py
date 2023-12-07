"""Test the filters.py file."""

import numpy as np
import pandas as pd
import pytest
from openbb_core.app.static.filters import filter_inputs
from openbb_core.provider.abstract.data import Data


def test_filter_inputs_not_df():
    """Test filter_inputs."""
    kwargs = {"num": 1}
    kwargs = filter_inputs(**kwargs)

    assert kwargs["num"] == 1


def test_filter_inputs_df():
    """Test filter_inputs."""
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    kwargs = {"data": df}
    kwargs = filter_inputs(data_processing=True, **kwargs)

    assert isinstance(kwargs["data"], list)


# Example instances of each supported type for testing
example_dict = {"a": 1, "b": 2}
example_list = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
example_series = pd.Series([1, 2, 3])
example_dataframe = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
example_ndarray = np.array([[1, 2], [3, 4]])
example_data_list_series = [pd.Series([4, 5, 6])]
example_data_list_df = [pd.DataFrame({"col3": [5, 6], "col4": [7, 8]})]

# Create a list of scenarios to test
test_data = [
    example_dict,
    example_list,
    example_series,
    example_dataframe,
    example_ndarray,
    example_data_list_series,
    example_data_list_df,
]


@pytest.mark.parametrize("input_data", test_data)
def test_filter_inputs(
    input_data,
):
    result = filter_inputs(data=input_data, data_processing=True)

    # Assert that the result is a dictionary
    assert isinstance(result, dict), "filter_inputs should return a dictionary"

    # Assert that the 'data' key is present in the result
    assert "data" in result, "Resulting dictionary should have a 'data' key"

    # Assert that the type of 'data' in the result is the expected type
    if isinstance(result["data"], list):
        assert isinstance(
            result["data"][0], Data
        ), f"The 'data' key should be a list of {Data.__name__}"
    else:
        assert isinstance(
            result["data"], Data
        ), f"The 'data' key should be of type {Data.__name__}"
