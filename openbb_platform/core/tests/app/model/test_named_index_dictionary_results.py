"""A genuine column named index is user data, not a conversion artifact."""

import pandas as pd
import pytest

from openbb_core.app.model.obbject import OBBject


@pytest.mark.parametrize(
    "results",
    [
        pd.DataFrame({"index": ["S&P 500", "NASDAQ"], "value": [1, 2]}),
        [{"index": "S&P 500", "value": 1}, {"index": "NASDAQ", "value": 2}],
    ],
)
def test_named_index_column_is_not_dropped(results):
    assert OBBject(results=results).to_dict() == {
        "index": ["S&P 500", "NASDAQ"],
        "value": [1, 2],
    }


def test_scalar_dictionary_synthetic_labels_remain_hidden():
    assert OBBject(results={"a": 1, "b": 2}).to_dict() == {0: [1, 2]}
