"""Single record results must have the same table schema as multiple records."""

import pytest
from pandas.testing import assert_frame_equal

from openbb_core.app.model.obbject import OBBject


@pytest.mark.parametrize(
    "record",
    [
        {"symbol": "AAPL", "price": 42.5},
        {"date": "2026-01-01", "value": 1},
        {"symbol": "AAPL", "description": None},
    ],
)
def test_single_record_converts_like_first_row_of_multiple(record):
    one = OBBject(results=[record]).to_dataframe(index=None)
    two = OBBject(results=[record, record]).to_dataframe(index=None)
    assert_frame_equal(one, two.iloc[:1].reset_index(drop=True))


def test_single_record_supports_date_index():
    frame = OBBject(results=[{"date": "2026-01-01", "price": 42}]).to_dataframe()
    assert frame.index.name == "date"
    assert frame.loc["2026-01-01", "price"] == 42


def test_nested_table_bundle_remains_supported():
    frame = OBBject(results=[{"table": [{"value": 1}, {"value": 2}]}]).to_dataframe(
        index=None
    )
    assert frame[("table", "value")].tolist() == [1, 2]
