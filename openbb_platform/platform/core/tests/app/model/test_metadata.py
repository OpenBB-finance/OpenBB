from datetime import datetime

import numpy as np
import pandas as pd
import pytest
from openbb_core.app.model.metadata import Metadata
from openbb_core.provider.abstract.data import Data


def test_Metadata():
    "Smoke test"
    m = Metadata(
        arguments={"test": "test"},
        route="test",
        timestamp=datetime.now(),
        duration=0,
    )
    assert m
    assert isinstance(m, Metadata)


def test_fields():
    "Smoke test"
    fields = Metadata.__fields__.keys()
    assert "arguments" in fields
    assert "duration" in fields
    assert "route" in fields
    assert "timestamp" in fields


@pytest.mark.parametrize(
    "input_data, expected_output",
    [
        # Test cases for various input types
        ({"data": Data()}, {"data": {"type": "Data", "columns": []}}),
        (
            {"data": Data(open=123, close=456)},
            {"data": {"type": "Data", "columns": ["open", "close"]}},
        ),
        (
            {"data_list": [Data(open=123, close=456), Data(volume=789)]},
            {
                "data_list": {
                    "type": "List[Data]",
                    "columns": ["open", "close", "volume"],
                }
            },
        ),
        (
            {"data_list": [Data(open=123, close=456), Data(open=321, volume=789)]},
            {
                "data_list": {
                    "type": "List[Data]",
                    "columns": ["open", "close", "volume"],
                }
            },
        ),
        (
            {"data_frame": pd.DataFrame({"A": [1, 2], "B": [3, 4]})},
            {"data_frame": {"type": "DataFrame", "columns": ["A", "B"]}},
        ),
        (
            {
                "data_frame_list": [
                    pd.DataFrame({"A": [1, 2], "B": [3, 4]}),
                    pd.DataFrame({"C": [5, 6]}),
                ],
                "data_series_list": [
                    pd.Series([1, 2], name="X"),
                    pd.Series([3, 4], name="Y"),
                ],
            },
            {
                "data_frame_list": {
                    "type": "List[DataFrame]",
                    "columns": [["A", "B"], ["C"]],
                },
                "data_series_list": {"type": "List[Series]", "columns": ["X", "Y"]},
            },
        ),
        (
            {
                "numpy_array": np.array(
                    [(1, "Alice"), (2, "Bob")], dtype=[("id", int), ("name", "U10")]
                )
            },
            {"numpy_array": {"type": "ndarray", "columns": ["id", "name"]}},
        ),
        # Test case for long string input
        (
            {
                "long_string": "This is a very long string that exceeds 80 characters in length and should be trimmed."
            },
            {
                "long_string": "This is a very long string that exceeds 80 characters in length and should be tr"
            },
        ),
    ],
)
def test_scale_arguments(input_data, expected_output):
    m = Metadata(
        arguments=input_data,
        route="test",
        timestamp=datetime.now(),
        duration=0,
    )
    arguments = m.arguments

    for arg in arguments:
        if "columns" in arguments[arg]:
            # compare the column names disregarding the order with the expected output
            assert sorted(arguments[arg]["columns"]) == sorted(
                expected_output[arg]["columns"]
            )
            assert arguments[arg]["type"] == expected_output[arg]["type"]
        else:
            assert m.arguments == expected_output
