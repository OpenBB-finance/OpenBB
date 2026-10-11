"""Nullable dates must serialize without changing source frames."""

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from openbb_core.app.utils import df_to_basemodel


@pytest.mark.parametrize(
    "dates,expected",
    [
        (["2026-01-02", None], ["2026-01-02", None]),
        ([None, None], [None, None]),
        (["2026-01-02T12:30:00", None], ["2026-01-02T12:30:00.000", None]),
    ],
)
def test_nullable_date_records(dates, expected):
    frame = pd.DataFrame({"date": dates, "value": [1, 2]})
    original = frame.copy(deep=True)
    records = [item.model_dump() for item in df_to_basemodel(frame)]
    assert [item["date"] for item in records] == expected
    assert_frame_equal(frame, original)


def test_nonnullable_date_only_control():
    frame = pd.DataFrame({"date": ["2026-01-02"], "value": [1]})
    assert df_to_basemodel(frame)[0].model_dump()["date"] == "2026-01-02"
