import numpy as np
import pandas as pd
import pytest
from openbb_core.app.utils import (
    basemodel_to_df,
    df_to_basemodel,
    dict_to_basemodel,
    get_target_column,
    get_target_columns,
    list_to_basemodel,
    ndarray_to_basemodel,
)
from openbb_core.provider.abstract.data import Data

df = pd.DataFrame(
    {
        "x": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "y": [5, 4, 3, 9, 44, 5, 66, 11, 777, 1],
        "z": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    },
)

df_multiindex = df.set_index(["x", "y"])

simple_base_model = [
    Data(x=i, y=j, z=k) for i in range(2) for j in range(6, 8) for k in range(10, 12)
]

multi_index_base_model = [
    Data(x=i, y=j, z=k, is_multiindex=True, multiindex_names="['x','y']")
    for i in range(2)
    for j in range(6, 8)
    for k in range(10, 12)
]


def test_df_to_basemodel():
    base_model = df_to_basemodel(df)
    assert isinstance(base_model, list)
    assert base_model[0].x == 1


def test_df_to_basemodel_multiindex():
    base_model = df_to_basemodel(df_multiindex)
    assert isinstance(base_model, list)
    assert hasattr(base_model[0], "is_multiindex")


def test_basemodel_to_df():
    df = basemodel_to_df(simple_base_model)
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (8, 3)


def test_basemodel_to_multiindex_df():
    df = basemodel_to_df(multi_index_base_model)
    assert isinstance(df, pd.DataFrame)
    assert isinstance(df.index, pd.MultiIndex)


def test_get_target_column():
    target = get_target_column(df, "x")
    assert isinstance(target, pd.Series)
    assert target[0] == 1


def test_get_target_columns():
    targets = get_target_columns(df, ["x", "y"])
    assert isinstance(targets, pd.DataFrame)
    assert targets.shape == (10, 2)


@pytest.mark.parametrize(
    "data_list, expected",
    [
        # List of dictionaries
        ([{"a": 1}, {"b": 2}], [Data(a=1), Data(b=2)]),
        # List with a single DataFrame
        ([pd.DataFrame({"c": [3, 4]})], [Data(c=3), Data(c=4)]),
        # List with mixed types
        ([{"d": 5}, pd.Series([6, 7], name="e")], [Data(d=5), Data(e=6), Data(e=7)]),
    ],
)
def test_list_to_basemodel(data_list, expected):
    result = list_to_basemodel(data_list)
    for r, e in zip(result, expected):
        assert r.model_dump() == e.model_dump()


@pytest.mark.parametrize(
    "data_dict, expected",
    [
        # Simple dictionary
        ({"a": 10}, Data(a=10)),
        # Nested dictionary (assuming Data can handle nested dicts)
        ({"b": {"c": 20}}, Data(b={"c": 20})),
        # Dictionary with list (assuming Data can handle lists)
        ({"d": [30, 40]}, Data(d=[30, 40])),
    ],
)
def test_dict_to_basemodel(data_dict, expected):
    result = dict_to_basemodel(data_dict)
    assert result.model_dump() == expected.model_dump()


@pytest.mark.parametrize(
    "array, expected",
    [
        # 2D array with single row
        (np.array([[1, 2]]), [Data(column_0=1, column_1=2)]),
        # 2D array with multiple rows
        (
            np.array([[3, 4], [5, 6]]),
            [Data(column_0=3, column_1=4), Data(column_0=5, column_1=6)],
        ),
        # 2D array with non-numeric data
        (
            np.array([["a", "b"], ["c", "d"]]),
            [Data(column_0="a", column_1="b"), Data(column_0="c", column_1="d")],
        ),
    ],
)
def test_ndarray_to_basemodel(array, expected):
    result = ndarray_to_basemodel(array)
    for r, e in zip(result, expected):
        assert r.model_dump() == e.model_dump()
