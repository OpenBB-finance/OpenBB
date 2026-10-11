"""Export preparation must inspect column timezone types independently of the index."""

from datetime import date

import pandas as pd
import pytest

from openbb_cli.controllers.utils import remove_timezone_from_dataframe


@pytest.mark.parametrize("index", [None, pd.to_datetime(["2026-01-01", "2026-01-02"])])
def test_timezone_column_with_ordinary_index(index):
    frame = pd.DataFrame(
        {
            "when": pd.to_datetime(["2026-01-01T12:00Z", None]),
            "naive": pd.to_datetime(["2026-01-01T12:00", "2026-01-02T12:00"]),
        },
        index=index,
    )
    result = remove_timezone_from_dataframe(frame)
    assert result["when"].iloc[0] == date(2026, 1, 1)
    assert pd.isna(result["when"].iloc[1])
    assert result["naive"].iloc[0].hour == 12
