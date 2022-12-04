import pandas as pd
import pytest
from openbb_terminal.economy import economy_helpers


def test_create_new_entry():
    df_dict = {
        "key1": pd.DataFrame([0, 1, 2, 3, 4], columns=["A"]),
        "key2": pd.DataFrame([10, 20, 30, 40, 50], columns=["Z"]),
    }
    new_dict = economy_helpers.create_new_entry(df_dict, "New=A**2 + Z")
    assert "custom" in new_dict
    assert new_dict["custom"].equals(
        pd.DataFrame([10, 21, 34, 49, 66], columns=["New"])
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_bad_create_new_entry():
    df_dict = {
        "key1": pd.DataFrame([0, 1, 2, 3, 4], columns=["A"]),
        "key2": pd.DataFrame([10, 20, 30, 40, 50], columns=["Z"]),
    }
    economy_helpers.create_new_entry(df_dict, "New=A**2 + PSKJ  + hfjijfiefj")


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_bad_create_new_entry_bad_query():
    df_dict = {
        "key1": pd.DataFrame([0, 1, 2, 3, 4], columns=["A"]),
        "key2": pd.DataFrame([10, 20, 30, 40, 50], columns=["Z"]),
    }
    economy_helpers.create_new_entry(df_dict, "New=A +")
