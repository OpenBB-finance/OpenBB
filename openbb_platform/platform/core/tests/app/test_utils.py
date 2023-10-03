import pandas as pd
from openbb_core.app.utils import (
    basemodel_to_df,
    df_to_basemodel,
    get_target_column,
    get_target_columns,
)
from openbb_provider.abstract.data import Data

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
